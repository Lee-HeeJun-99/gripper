# NEXT 02 — SofaPython3

기준 60f41cf; 개발 코드 커밋 `96174a2ec8c1b75c2f11f607bdecb1d986b148f2`. 실행 중 dirty 상태는 개별 JSON에 그대로 기록했다.
원본/골든 보존, push 없음. 증거: `reports/next_evidence/`; raw/명령/전체 로그: `results/next_phase/`.


**BLOCKED**. CPython 3.12 ABI, `libpython3.12.so.1.0` 미발견을 ldd로 재확인했다.
프로젝트 내부 `.venv-sofa-next` 대상 Conda offline/online 생성은 패키지 부재/DNS 실패로 해결되지 않았다.
Python 3.10/다른 ABI 공유 라이브러리를 symlink로 위장하지 않았다.

실제 smoke 명령은 environment.json의 python_scene.command에 있다. exit=0이어도 ERROR/scene loading 실패여서 PASS가 아니다.
원본 V109/V110 FREE·전단 CSV 직접 비교는 **NOT RUN**. 이전 실패를 이번 성공으로 재사용하지 않았다.
이번에는 실패한 원본 실행을 반복하지 않고 smoke/ABI 차단 확인 후 XML/C++ 독립 개발을 계속했다.
해결에 필요한 것은 공유 런타임뿐 아니라 CPython3.12 표준 라이브러리 및 호환 NumPy다.
