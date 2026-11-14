# 10 — 최종 코드·재현성 검토

이번 실행: `results/revalidation_20261114T132734Z`. 시작 커밋 `8ee78f0c84d042812537655583cb98ed037f310e`, 검증 중 dirty=true. 별도 브랜치와 소스/바이너리 SHA256으로 추적한다. 과거 `results/physics_validation`은 회귀 비교 인용에만 사용했고 이번 gate의 성공값을 재사용하지 않았다.

**PASS(검사 범위)**: Python 25개 파일 syntax compile, C++ warning-enabled clean build,
6개 강성에 걸친 총 600개 상태 단위 검사, 20개 자동화 및 11개 최적화 guard 검사.
Ruff/전체 type/lint 분석은 도구 미설치로 NOT RUN이다. 단순 syntax 검사를 전체 정적 분석이라고 부르지 않는다.

발견하여 수정한 항목: C++ 회전 좌표-에너지 미분 불일치, 무효 입력과 null pointer,
기존 상태 파일 덮어쓰기, runner 비유한 인자/불완전 시점/출력 디렉터리 경쟁/중단 자식 누수,
개별 source 해시 부재, 손상 CSV 검출 부재, 미검증 gate의 불완전 fingerprint 및 옛 고정 보고서 경로.
관련 실패와 회귀를 새 로그에 남겼으며 물성/하중/허용오차를 완화하지 않았다.

골든 기준은 비교에만 사용했고 실제 응답은 SOFA raw 벡터에서 계산한다.
FEM 독립 기준은 NumPy 방정식을 실제 풀어 얻으며 기존 숫자를 결과로 반환하지 않는다.
과거 보고서·후보는 보존하고 새 비교에는 명시적인 최신 결과 디렉터리를 전달했다.
기존 문서의 theta≈2*q_y 및 기존 100개 검사 설명은 역사적 기록이다. 최신 구현/시험의 범위는 03을 따른다.

단위: x,h,L=mm, t=s, 힘=모델 F 단위, E=F/mm², k=F/mm, 모멘트=F·mm,
질량=F·s²/mm, 에너지=F·mm. 실제 PET와의 단위/물성 보정은 NOT RUN이다.
고정 루트/하중/대응 매핑은 AST-XML 및 실행 상태에서 별도 확인했다.
매우 큰 회전/3D의 에너지 객관성, 실제 진공 압력·마찰, 필름 손상·파지는 현재 인증의 대상이 아니다.

잔여 사항: 전체 BeamFEM 에너지 API 미구현, Windows raw 벡터 부재, full-engine ASan 미실행,
LSan ptrace 제약, 장시간 soak 미실행, Optuna sampler/SQLite 실제 경로 미검증, SofaPython3 미복구.
이 범위는 FAIL을 숨긴 것이 아니라 증거가 없는 항목을 NOT RUN/BLOCKED로 분리한 것이다.
원본 파일은 마지막 manifest 검사에서도 확인하고 대용량 raw/캐시/의존성은 Git 제외한다.
