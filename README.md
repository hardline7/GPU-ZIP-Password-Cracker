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

## 📊 성능 최적화

프로그램의 성능은 GPU 성능과 설정에 따라 달라질 수 있습니다. 다음 변수들을 조정하여 최적화할 수 있습니다:

```python
self.threads_per_block = 1024  # GPU 스레드 수
self.blocks = 16384           # 블록 수
self.num_streams = 4         # CUDA 스트림 수
self.buffer_multiplier = 2   # 버퍼 크기 배수
```

- RTX 3090 기준으로 최적화되어 있으며, 다른 GPU의 경우 값을 조정해야 할 수 있습니다.
- 메모리 부족 오류 발생 시 `blocks` 값을 줄여보세요.
- GPU 사용률이 낮다면 `num_streams`를 증가시켜보세요.

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
