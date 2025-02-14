import os
import sys
import pycuda.autoinit
import pycuda.driver as cuda
import numpy as np
import zipfile
from pycuda.compiler import SourceModule
import time
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import psutil

class Logger:
    def __init__(self, name="password_cracker"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 현재 스크립트의 실행 경로를 기준으로 로그 디렉토리 생성
        current_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(current_dir, "logs")
        
        # 로그 디렉토리가 없으면 생성
        try:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            self.log_dir = log_dir
        except Exception as e:
            print(f"로그 디렉토리 생성 실패: {e}")
            # 로그 디렉토리 생성 실패시 현재 디렉토리에 생성
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            self.log_dir = log_dir
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
        file_handler = RotatingFileHandler(
            f"{log_dir}/cracker_{timestamp}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, msg):
        self.logger.debug(msg)
    
    def info(self, msg):
        self.logger.info(msg)
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def error(self, msg):
        self.logger.error(msg)

def setup_environment():
    """Visual Studio 컴파일러 환경 설정"""
    logger = Logger()
    possible_vs_paths = [
        r"C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC",
        r"C:\Program Files\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC",
        r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC"
    ]
    
    for base_path in possible_vs_paths:
        if os.path.exists(base_path):
            versions = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
            if versions:
                latest_version = sorted(versions)[-1]
                compiler_path = os.path.join(base_path, latest_version, "bin", "Hostx64", "x64")
                if os.path.exists(os.path.join(compiler_path, "cl.exe")):
                    os.environ['PATH'] = compiler_path + ';' + os.environ['PATH']
                    logger.info(f"✅ 컴파일러 경로 설정 완료: {compiler_path}")
                    return True
    
    logger.error("❌ Visual Studio C++ 컴파일러를 찾을 수 없습니다.")
    return False

kernel_code = """
extern "C" {
__global__ void try_passwords(const char* charset,
                            const int charset_size,
                            const unsigned long long start_idx,
                            const unsigned long long total_combinations,
                            char* output,
                            unsigned long long* output_indices,
                            const int max_length,
                            int* found) {
    const unsigned long long tid = blockIdx.x * blockDim.x + threadIdx.x;
    const unsigned long long password_idx = start_idx + tid;
    
    if (password_idx >= total_combinations) return;
    
    __shared__ char shared_charset[256];
    if (threadIdx.x < charset_size) {
        shared_charset[threadIdx.x] = charset[threadIdx.x];
    }
    __syncthreads();
    
    char password[15];
    unsigned long long temp = password_idx;
    
    #pragma unroll
    for(int i = 0; i < 15; i++) {
        if(temp > 0 || i == 0) {
            password[i] = shared_charset[temp % charset_size];
            temp /= charset_size;
        } else {
            password[i] = shared_charset[0];
        }
    }
    
    if(tid < gridDim.x * blockDim.x) {
        #pragma unroll
        for(int i = 0; i < 15; i++) {
            output[tid * 15 + i] = password[i];
        }
        output_indices[tid] = password_idx;
    }
}
}
"""

class GPUPasswordCracker:
    def __init__(self, zip_path, charset):
        self.logger = Logger()
        self.zip_path = zip_path
        self.charset = charset
        self.charset_bytes = np.array(list(charset.encode("utf-8")), dtype=np.uint8)
        self.charset_size = len(self.charset_bytes)
        
        # RTX 3090 최적화 설정
        self.threads_per_block = 1024
        self.blocks = 16384
        self.batch_size = self.threads_per_block * self.blocks
        self.num_streams = 4
        self.buffer_multiplier = 2
        
        self.start_time = time.time()
        self.last_status_time = self.start_time
        self.passwords_tested = 0
        
        self.setup_gpu()
        
    def setup_gpu(self):
        try:
            compiler_options = [
                '-Xcompiler', '/utf8',
                '--use_fast_math',
                '-O3'
            ]
            
            self.mod = SourceModule(kernel_code, options=compiler_options)
            self.try_passwords = self.mod.get_function("try_passwords")
            
            self.streams = [cuda.Stream() for _ in range(self.num_streams)]
            
            buffer_size = self.batch_size * self.buffer_multiplier
            single_buffer_size_mb = (buffer_size * 15) / (1024 * 1024)
            total_buffer_size_mb = single_buffer_size_mb * self.num_streams
            
            self.logger.info(f"단일 버퍼 크기: {single_buffer_size_mb:.2f}MB")
            self.logger.info(f"총 버퍼 크기: {total_buffer_size_mb:.2f}MB")
            
            self.charset_gpu = cuda.mem_alloc(self.charset_bytes.nbytes)
            cuda.memcpy_htod(self.charset_gpu, self.charset_bytes)
            
            self.output_gpus = [cuda.mem_alloc(buffer_size * 15) for _ in range(self.num_streams)]
            self.output_indices_gpus = [cuda.mem_alloc(buffer_size * 8) for _ in range(self.num_streams)]
            self.found_gpus = [cuda.mem_alloc(4) for _ in range(self.num_streams)]
            
            self.pinned_outputs = [cuda.pagelocked_empty(buffer_size * 15, dtype=np.uint8) for _ in range(self.num_streams)]
            self.pinned_indices = [cuda.pagelocked_empty(buffer_size, dtype=np.uint64) for _ in range(self.num_streams)]
            
            self.logger.info("✅ GPU 초기화 완료")
            self.log_gpu_info()
        except Exception as e:
            self.logger.error(f"❌ GPU 초기화 실패: {str(e)}")
            raise
    
    def log_gpu_info(self):
        try:
            gpu = cuda.Device(0)
            gpu_name = gpu.name()
            gpu_memory_total = gpu.total_memory() / (1024**2)
            
            self.logger.info("\n=== GPU 상세 정보 ===")
            self.logger.info(f"🎮 GPU: {gpu_name}")
            self.logger.info(f"💾 총 메모리: {gpu_memory_total:.0f}MB")
            self.logger.info(f"🧮 스레드/블록: {self.threads_per_block}")
            self.logger.info(f"📦 블록 수: {self.blocks}")
            self.logger.info(f"🔄 스트림 수: {self.num_streams}")
            self.logger.info(f"⚡ 배치 크기: {self.batch_size:,}")
            self.logger.info(f"📈 버퍼 배수: {self.buffer_multiplier}x")
            total_buffer = (self.batch_size * self.buffer_multiplier * 15 * self.num_streams) / (1024**2)
            self.logger.info(f"🔋 총 버퍼 크기: {total_buffer:.1f}MB")
            self.logger.info("==================\n")
        except Exception as e:
            self.logger.error(f"GPU 정보 조회 실패: {str(e)}")
    
    def log_status(self, force=False):
        current_time = time.time()
        if force or (current_time - self.last_status_time) >= 5:
            elapsed = current_time - self.start_time
            passwords_per_second = self.passwords_tested / elapsed if elapsed > 0 else 0
            
            try:
                gpu = cuda.Device(0)
                total_memory = gpu.total_memory()
                free_memory = gpu.get_attribute(cuda.device_attribute.TOTAL_CONSTANT_MEMORY)
                used_memory = total_memory - free_memory
                
                status_msg = f"""
======== 진행 상황 ========
⏱️ 경과 시간: {elapsed:.1f}초
🔑 시도한 암호 수: {self.passwords_tested:,}
⚡ 초당 처리량: {passwords_per_second:,.0f} 암호/초
💾 GPU 메모리 사용: {used_memory / (1024**2):.1f}MB / {total_memory / (1024**2):.1f}MB
🔥 GPU 사용률: {self.get_gpu_utilization()}%
=========================
"""
                self.logger.info(status_msg)
                self.last_status_time = current_time
            except Exception as e:
                self.logger.error(f"상태 로깅 실패: {str(e)}")
    
    def get_gpu_utilization(self):
        try:
            gpu = cuda.Device(0)
            return gpu.get_attribute(cuda.device_attribute.GPU_UTIL_RATE)
        except:
            return 0
    
    def extract_zip(self, password):
        try:
            with zipfile.ZipFile(self.zip_path, 'r') as zf:
                zf.extractall(pwd=password.encode('utf-8'))
            return True
        except:
            return False

    def crack(self, max_attempts=1000000000):
        self.logger.info("🚀 암호 해독 시작...")
        
        try:
            stream_idx = 0
            batch_size = self.batch_size * self.buffer_multiplier
            
            for batch_num in range(0, max_attempts, batch_size):
                stream = self.streams[stream_idx]
                
                self.try_passwords(
                    self.charset_gpu,
                    np.int32(self.charset_size),
                    np.uint64(batch_num),
                    np.uint64(max_attempts),
                    self.output_gpus[stream_idx],
                    self.output_indices_gpus[stream_idx],
                    np.int32(15),
                    self.found_gpus[stream_idx],
                    block=(self.threads_per_block, 1, 1),
                    grid=(self.blocks, 1),
                    stream=stream
                )
                
                cuda.memcpy_dtoh_async(self.pinned_outputs[stream_idx], self.output_gpus[stream_idx], stream)
                cuda.memcpy_dtoh_async(self.pinned_indices[stream_idx], self.output_indices_gpus[stream_idx], stream)
                
                stream.synchronize()
                
                passwords_chunk = self.pinned_outputs[stream_idx]
                
                for i in range(0, len(passwords_chunk), 15):
                    password = ''.join(chr(c) for c in passwords_chunk[i:i+15] if c != 0)
                    self.passwords_tested += 1
                    
                    if self.extract_zip(password):
                        self.log_status(force=True)
                        self.logger.info(f"\n✅ 성공! 암호 찾음: {password}")
                        return password
                    
                    self.log_status()
                
                stream_idx = (stream_idx + 1) % self.num_streams
            
            self.logger.info("❌ 암호를 찾지 못했습니다.")
            return None
            
        except Exception as e:
            self.logger.error(f"🚨 오류 발생: {str(e)}")
            raise

if __name__ == "__main__":
    logger = Logger()
    
    if not setup_environment():
        sys.exit(1)

    zip_path = r"C:\Users\users\Downloads\1.zip"  # 실제 ZIP 파일 경로로 수정하세요
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[{]}|;:'\",<.>/?"

    try:
        cracker = GPUPasswordCracker(zip_path, charset)
        found_password = cracker.crack()
        
        if found_password:
            logger.info(f"🎉 최종 성공: 암호는 {found_password}")
        else:
            logger.info("🚨 암호를 찾지 못했습니다.")
            
    except Exception as e:
        logger.error(f"🚨 치명적 오류 발생: {str(e)}")
        raise
