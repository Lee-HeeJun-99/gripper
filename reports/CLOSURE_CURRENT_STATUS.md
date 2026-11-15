# CLOSURE 현재 상태

전체목표 미완료. **전체 물리 인증 FAIL,100mm 최적화 BLOCKED**. 유한 실험을 종료하고
실제 실패 원인/재개 명령을 저장했다. 실행 중인 campaign/방치 프로세스는 없다.

작업브랜치 `development/regrip-contact-closure-optimization`, 검증 코드d3a343df197d0cd4cfc4f2164ba0e76ea8e2f00a.
최종 문서 커밋은 `git log -1 --format=%H`로 확인. 원격push/이력재작성 없음.

- PASS: 2핑거+Fx active-interval Gauss 공간/메시/dt/history/반복11검사,기존1%기준 유지.
- PASS 하위범위: 3핑거 동일12방향 힘·토크/국소잔차/24s해제·복원. 전체 힘·모멘트 인증은 아님.
- FAIL: 2핑거±Tz,3핑거 토크의 공간/dt/history수렴,41노드고차3개실험480s timeout.
- FAIL: 3핑거 전체Y모멘트평형,실제 field분리에서Beam−2.26294389207e-5force·mm 확인.
- FAIL/BLOCKED: Beam닫힌경로순환일≠0,일관된 전체potential/에너지폐합 미확보.
- EXPERIMENTAL: Native3D sphere gripper는 양의수치스킨.001/.0005mm에서지속접촉·잔차하위검사통과.
  buffer변위차.00712443% PASS지만삼각형/dt/전체12wrench/모든형상은미검증.
- PASS: Python73,C++신규3개/기존5개,신규커널ASan/UBSan/LSan,실제600시점FREE×2,
  원본Python FREE/전단과XML transient동등성,matchedSDK adaptive mechanics240000step/2reload boundedmemory.
- PASS: 실제2401frame 선택적재생; GUI미실행. 과거30mm Optuna24COMPLETE/3PRUNED는별도이전결과.
- NOT RUN: 실물측정/PET검증/실제진공압/하드웨어/100mm 최적화,Native/3finger 장시간메모리.

Raw4.8GiB수준은 외장디스크 `ReGrip/results/closure_20261115`에만 보존,Git제외.
작은 CSV/JSON/그래프/해시는 `reports/closure_evidence`와CLOSURE_EVIDENCE_MANIFEST.
기존원본/골든/compiled물리소스/이전바이너리·SQLite·raw보존. README/AGENTS/.gitignore만의
의도된메타데이터변화는과거엄격검증기의오류와구분(`legacy_integrity.json`).

가장 먼저 할 일: 원본을보존한 별도 에너지·객관성 기반beam 모델,실제moment balance,
그후3핑거접촉/history수렴·비용개선. 파지최적화 gate 우회 금지.
