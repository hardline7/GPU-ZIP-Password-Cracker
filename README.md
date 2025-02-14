# GPU ZIP Password Cracker

NVIDIA GPU를 활용한 고성능 ZIP 파일 비밀번호 크래커입니다. CUDA 병렬 처리를 통해 빠른 속도로 ZIP 파일의 비밀번호를 찾을 수 있습니다.

## 🚀 주요 기능

- NVIDIA CUDA를 활용한 GPU 병렬 처리
- 실시간 진행 상황 모니터링
- 자동 로그 기록
- 멀티스트림 처리로 성능 최적화
- 상세한 GPU 사용 현황 표시

## ⚙️ 시스템 요구사항

- Windows 10/11
- NVIDIA GPU (CUDA 지원)
- Python 3.8 이상
- Visual Studio 2019 또는 2022 (C++ 빌드 도구 포함)
- NVIDIA CUDA Toolkit 11.0 이상

## 📥 설치 방법

1. **Python 설치**
   - [Python 공식 웹사이트](https://www.python.org/downloads/)에서 Python 3.8 이상 버전 설치
   - 설치 시 "Add Python to PATH" 옵션 체크

2. **Visual Studio 설치**
   - [Visual Studio 다운로드](https://visualstudio.microsoft.com/downloads/)
   - "Desktop development with C++" 워크로드 선택 설치
   ```powershell
   # 설치 확인
   cl.exe
   ```

3. **CUDA Toolkit 설치**
   - [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-toolkit) 다운로드 및 설치
   ```powershell
   # 설치 확인
   nvcc --version
   ```

4. **프로젝트 클론 및 의존성 설치**
   ```bash
   git clone https://github.com/your-username/gpu-zip-cracker.git
   cd gpu-zip-cracker
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

## 💻 사용 방법

1. **환경 준비**
   - 비밀번호를 찾을 ZIP 파일을 준비합니다.
   - 가상환경이 활성화되어 있는지 확인합니다.
   ```bash
   .\venv\Scripts\activate
   ```

2. **코드 설정**
   - `zip_path` 변수를 본인의 ZIP 파일 경로로 수정합니다.
   ```python
   zip_path = r"C:\Path\To\Your\File.zip"  # 본인의 ZIP 파일 경로로 수정
   ```
   
   - 필요한 경우 `charset` 변수를 수정하여 검색할 문자셋을 조정합니다.
   ```python
   charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[{]}|;:'\",<.>/?"
   ```

3. **실행**
   ```bash
   python password_cracker.py
   ```

4. **로그 확인**
   - 프로그램 실행 시 생성되는 `logs` 폴더에서 상세 로그를 확인할 수 있습니다.
   - 콘솔에서 실시간 진행 상황을 모니터링할 수 있습니다.

## 📊 GPU별 성능 최적화 설정

각 GPU 시리즈별 권장 설정값입니다. 실제 환경에 따라 미세 조정이 필요할 수 있습니다.

### GTX 10 시리즈
```python
# GTX 1060 (6GB)
self.threads_per_block = 256
self.blocks = 4096
self.num_streams = 2
self.buffer_multiplier = 1

# GTX 1070 (8GB)
self.threads_per_block = 512
self.blocks = 6144
self.num_streams = 2
self.buffer_multiplier = 1

# GTX 1080 / 1080 Ti (8GB/11GB)
self.threads_per_block = 512
self.blocks = 8192
self.num_streams = 3
self.buffer_multiplier = 2
```

### RTX 20 시리즈
```python
# RTX 2060 (6GB)
self.threads_per_block = 512
self.blocks = 6144
self.num_streams = 2
self.buffer_multiplier = 1

# RTX 2070 (8GB)
self.threads_per_block = 512
self.blocks = 8192
self.num_streams = 3
self.buffer_multiplier = 2

# RTX 2080 / 2080 Ti (8GB/11GB)
self.threads_per_block = 1024
self.blocks = 8192
self.num_streams = 3
self.buffer_multiplier = 2
```

### RTX 30 시리즈
```python
# RTX 3060 (12GB)
self.threads_per_block = 512
self.blocks = 8192
self.num_streams = 3
self.buffer_multiplier = 2

# RTX 3070 (8GB)
self.threads_per_block = 1024
self.blocks = 8192
self.num_streams = 3
self.buffer_multiplier = 2

# RTX 3080 (10GB)
self.threads_per_block = 1024
self.blocks = 12288
self.num_streams = 4
self.buffer_multiplier = 2

# RTX 3090 (24GB)
self.threads_per_block = 1024
self.blocks = 16384
self.num_streams = 4
self.buffer_multiplier = 2
```

### RTX 40 시리즈
```python
# RTX 4060 (8GB)
self.threads_per_block = 512
self.blocks = 8192
self.num_streams = 3
self.buffer_multiplier = 2

# RTX 4070 (12GB)
self.threads_per_block = 1024
self.blocks = 12288
self.num_streams = 4
self.buffer_multiplier = 2

# RTX 4080 (16GB)
self.threads_per_block = 1024
self.blocks = 16384
self.num_streams = 4
self.buffer_multiplier = 2

# RTX 4090 (24GB)
self.threads_per_block = 1024
self.blocks = 24576
self.num_streams = 6
self.buffer_multiplier = 3
```

### 최적화 가이드라인

1. **메모리 관련**
   - `blocks` × `threads_per_block` × `buffer_multiplier` × 15bytes가 GPU 메모리 사용량의 주요 요소입니다
   - GPU 메모리의 80% 이내로 사용하는 것을 권장합니다
   - 메모리 부족 오류 발생 시 우선적으로 `blocks` 값을 줄이세요

2. **성능 관련**
   - `threads_per_block`은 GPU 아키텍처의 워프 크기(32)의 배수로 설정하는 것이 좋습니다
   - GPU 사용률이 낮을 경우 `num_streams` 값을 증가시켜 보세요
   - 최신 GPU일수록 더 큰 `threads_per_block` 값을 효율적으로 처리할 수 있습니다

3. **발열 관련**
   - 과도한 `num_streams` 값은 GPU 발열을 증가시킬 수 있습니다
   - 장시간 실행 시 `buffer_multiplier` 값을 낮추는 것이 안정성에 도움될 수 있습니다

4. **자동 설정 스크립트**
```python
def get_optimal_settings(gpu_name):
    gpu_name = gpu_name.lower()
    
    # 기본값 (안전한 설정)
    settings = {
        'threads_per_block': 256,
        'blocks': 4096,
        'num_streams': 2,
        'buffer_multiplier': 1
    }
    
    # GPU 메모리에 따른 설정 조정
    memory_gb = get_gpu_memory()  # GPU 메모리 크기 (GB)
    
    if memory_gb >= 20:  # 3090, 4090 등 고용량
        settings.update({
            'threads_per_block': 1024,
            'blocks': 16384,
            'num_streams': 4,
            'buffer_multiplier': 2
        })
    elif memory_gb >= 10:  # 3080, 4080 등 중상급
        settings.update({
            'threads_per_block': 1024,
            'blocks': 12288,
            'num_streams': 4,
            'buffer_multiplier': 2
        })
    elif memory_gb >= 8:  # 3070, 2080 등 중급
        settings.update({
            'threads_per_block': 512,
            'blocks': 8192,
            'num_streams': 3,
            'buffer_multiplier': 2
        })
    
    return settings
```

주의: 위 설정값들은 참고용이며, 실제 성능은 시스템 환경에 따라 다를 수 있습니다. 점진적으로 값을 조정하면서 최적의 설정을 찾는 것을 권장합니다.

## 🔍 문제 해결

1. **CUDA 초기화 실패**
   ```
   ERROR: CUDA driver version is insufficient for CUDA runtime version
   ```
   - NVIDIA 드라이버 업데이트 필요
   - CUDA Toolkit 재설치 시도

2. **메모리 부족 오류**
   ```
   ERROR: out of memory
   ```
   - `blocks` 값을 줄여서 시도
   - 다른 GPU 프로세스 종료 후 시도

3. **컴파일러 오류**
   ```
   ERROR: Microsoft Visual C++ 14.0 or greater is required
   ```
   - Visual Studio C++ 빌드 도구 설치 필요

4. **CUDA 호환성 문제**
   - NVIDIA GPU 드라이버 업데이트
   - CUDA Toolkit 버전 확인
   - Visual Studio 버전 호환성 확인

## 📝 라이선스

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## ⚠️ 주의사항

- 본 도구는 합법적인 용도로만 사용해야 합니다.
- 자신의 파일이 아닌 경우 사용하지 마세요.
- GPU 과부하에 주의하세요.
- 정기적으로 GPU 온도를 모니터링하세요.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
