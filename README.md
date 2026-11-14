# ReGrip Ubuntu 개발 준비

현재 상태: 환경 점검 일부 완료. 인수인계 패키지 부재와 Python 3.12 런타임 부재로 기준 모델 검증 대기.

```bash
cd /home/ubuntu/LHJ/ReGrip
/usr/bin/python3 tools/check_environment.py
```

결과는 `results/<UTC 실행시각>/environment.csv` 및 개별 로그와 명령 JSON으로 보존된다.
현재 Python 관련 점검 실패로 명령 종료 코드 1이 예상된다.
`SOFA_ROOT`로 설치 경로를 변경할 수 있다. 실행 파일명은 현재 설치 버전에 맞춘다.
`scenes/`의 두 파일은 환경 점검용 빈 scene이며 ReGrip FEM 모델이 아니다.

필요한 입력: V0.8~V1.1.0 소스, 인수인계 MD, mesh/설정/실행 명령, Windows 원본 결과.
실제 모델과 플러그인 소스 수령 후 기준 검증을 먼저 수행한다.
현재 C++ 빌드 시스템, 물리 실험 자동화, Optuna, 비교 그래프 및 최적 파라미터는 미구현이다.

Python 설치 재시도 예시(네트워크가 가능한 사용자 터미널):

```bash
CONDA_PKGS_DIRS=/home/ubuntu/LHJ/ReGrip/.conda-pkgs conda create --prefix /home/ubuntu/LHJ/ReGrip/.venv-sofa python=3.12 numpy --yes
```

설치 후에는 해당 환경의 `bin`을 PATH에, `lib`를 LD_LIBRARY_PATH에 추가하고
외부 ROS 등의 PYTHONPATH/PYTHONHOME 간섭을 제거한 별도 프로세스에서 재검증해야 한다.
Python 3.10/3.14 라이브러리를 3.12 이름으로 심볼릭 링크하지 않는다.

자세한 증거와 미완료 항목은 `VALIDATION.md`, `PROGRESS.md`에 기록했다.
