# 05 — 전체 물리·수치 재검증

이번 실행: `results/revalidation_20261114T132734Z`. 시작 커밋 `8ee78f0c84d042812537655583cb98ed037f310e`, 검증 중 dirty=true. 별도 브랜치와 소스/바이너리 SHA256으로 추적한다. 과거 `results/physics_validation`은 회귀 비교 인용에만 사용했고 이번 gate의 성공값을 재사용하지 않았다.

**PASS**: 기존 45개 gate를 새로운 실제 SOFA 실행으로 재평가했으며 최종 결과는 45/45다.
추가 baseline 반복, 힘 균형, 모멘트 균형 3항목도 PASS다.
검사기를 강화하고 C++ 소스-바이너리 build manifest를 도입한 뒤 `physics_release`에서 19개 평형 실험을 전부 새로 실행했다. 앞선 진단용 실행의 PASS 상태를 복사하지 않았다.

평형 조건은 기존 마지막 .1초의 모든 자유 병진 속도 <1e-5 mm/s,
정규화 정적 잔차 <1e-3, 처짐 drift<1e-4를 유지했다. 추가로 각속도<1e-5 rad/s를 요구했다.
힘 잔차는 F/2, 모멘트는 F*L/2로 정규화한다. 반력의 전체 힘·모멘트 균형도 확인했다.
원본 root 고정, RigidMapping 변환, quaternion norm/회전 범위, 시점 전체와 모든 기록 벡터 유한성을 검사한다.
결합 에너지 gradient/Jacobian은 C++ 실제 구현에서 검사했으며 모델 데이터는 골든에서 생성하지 않았다.

dt 절반/두 배, k=1 및 100 메시 11→21(연결점 위치 동일), 반복, 3→6초, 절반 하중을 검사했다.
허용오차는 dt/시간 .1%, mesh 1%, 하중 선형성 .5%, 정적 기준 .5%로 기존 값을 유지했다.
추가 연결점 2개/5개 실험과 k=100 독립 반복/6초 연장도 평형에 도달했다.
전체 측정값·시간·잔차·속도·회전·PASS 상태는 revalidation_evidence/measured_experiments.csv에 있다.

실패 분류는 07 보고서의 20개 시험에서 검증했다. NaN/Inf·발산·invalid_physics는 명시적인 출력 손상 재생,
timeout/중단/짧은 미평형/로그-only 오류는 실제 프로세스 또는 SOFA 실행이다.
고장 주입을 정상 물리 실험이나 실제 solver 발산 재현으로 부르지 않는다.
Sofa BeamFEM의 getPotentialEnergy는 SDK에서 미구현이므로 **전체 보의 비선형 동적 에너지 수지: NOT RUN**.
전단 에너지의 보존적 미분 검사와 전체 시스템 에너지 검사를 구분한다.
