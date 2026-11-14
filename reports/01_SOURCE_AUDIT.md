# 01 — 소스 및 과거 결과 감사

이번 실행: `results/revalidation_20261114T132734Z`. 시작 커밋 `8ee78f0c84d042812537655583cb98ed037f310e`, 검증 중 dirty=true. 별도 브랜치와 소스/바이너리 SHA256으로 추적한다. 과거 `results/physics_validation`은 회귀 비교 인용에만 사용했고 이번 gate의 성공값을 재사용하지 않았다.

원본 보존: **PASS**. 외부 ZIP 및 내부 ZIP의 56개 원본 항목을 바이트 비교했다. 인수인계·골든 파일은 수정하지 않았다.
과거 gate의 소스 해시는 68e5acc 소스와 일치했고 기존 두 바이너리 해시도 일치했다.
단, 과거 개별 실행은 519bd5e+dirty=true로 기록되어 깨끗한 커밋 단위의 완전한 provenance는 아니었다. 이번 trial에는 소스 해시, 바이너리 해시, 설정·명령·artifact 해시를 남긴다.

| 버전 | 목적 및 구현 | 검증 범위 / 알려진 한계 |
| --- | --- | --- |
| V106 | 독립 정적 Euler–Bernoulli+축 FEM, 사각 A, u/w/phi 자유도 | NumPy 정적 해법; SOFA 또는 진공 재밍 결과가 아님 |
| V109 | 22 Rigid3d, BeamFEM, SparseLDL, 매핑 계면 | FREE 과도응답 골든; Python 전단 조립 SIGABRT는 문서 이력이며 이번에는 Python 미로딩으로 재현 불가 |
| V110 | C++ 접선 전단 에너지/힘/강성행렬 | 초기 API 수정 후 이전 시험은 k=.1의 100개 검사만 포함; 이번에 k=0..100의 600개 검사와 무효 입력 검사를 추가 |

실제 발견한 문제: 고강성의 에너지-힘 미분 불일치, NaN 강성 전파, null matrix SIGSEGV.
이전 성공을 그대로 확대 해석하지 않고 FAIL 로그를 보존한 뒤 수정했다.
실행 경로에는 골든 응답을 결과로 복사하는 코드가 없다. 골든 읽기는 회귀 비교, 독립 정적 기준 및 그림 생성에만 사용한다.
기존 그래프/후보 스크립트의 고정된 옛 결과 경로는 명시적 --results 입력과 해시 검증으로 보강했다.
명령 로그: `results/revalidation_20261114T132734Z/commands/`. 핵심 작은 증거 사본: `reports/revalidation_evidence/`.
