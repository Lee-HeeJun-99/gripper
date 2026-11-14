# 09 — SofaPython3 복구

이번 실행: `results/revalidation_20261114T132734Z`. 시작 커밋 `8ee78f0c84d042812537655583cb98ed037f310e`, 검증 중 dirty=true. 별도 브랜치와 소스/바이너리 SHA256으로 추적한다. 과거 `results/physics_validation`은 회귀 비교 인용에만 사용했고 이번 gate의 성공값을 재사용하지 않았다.

**BLOCKED**: SOFA 패키지의 SofaPython3 바인딩은 CPython 3.12용이고 libpython3.12.so.1.0가 없다.
readelf NEEDED 및 ldd를 재확인했고 로컬 runtime 검색/오프라인 Conda 생성/온라인 생성이 모두 해결하지 못했다.
오프라인은 Python=3.12/NumPy 패키지 미발견, 온라인은 DNS 실패다.
시스템 Python을 덮어쓰거나 다른 ABI 라이브러리의 symlink로 위장하지 않았다.

원본 V109 Python 파일들을 새 RUN/python_original_scene 폴더로 복사하여 FREE와 전단 장면을 실제로 요청했다.
두 명령 exit=0이지만 플러그인과 Python scene 로딩 ERROR가 있어 **성공이 아니다**.
장면 초기화, 기계적 상태, 적분, CSV 및 XML과의 수치 비교는 NOT RUN이다.
이번 C++/XML 결과와 Python 원본 결과를 직접 비교했다고 주장하지 않는다.
필요한 것은 CPython 3.12 공유 런타임+표준 라이브러리, 호환 NumPy 및 환경 분리다.
Python 3.10/3.14용 확장으로 대체할 수 없다.
명령·실패사유는 revalidation_evidence/python_recovery.json과 RUN/commands/original_python_*.log,
python312_offline.log, python312_online.log에 있다. Conda 전체 환경 진단 로그는 로컬에만 보존했다.
