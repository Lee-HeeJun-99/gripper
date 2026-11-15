# GRASP 07 — 실제 Optuna

**PASS:** 격리 Optuna4.6 설치,smoke3+재개24=27시도,완료24/중복PRUNED3/FAIL0,
SQLite/seed/실패 주입 및 planar Pareto 재검증.
**BLOCKED:** 파지 목적함수 최적화(접촉 공간수렴/6DOF wrench/전체 energy gate 미완료).
이 결과는 검증된 기존30mm 강성·미끄럼 모델이며100mm 파지 최적화로 표시하지 않는다.

초기 sandbox DNS 차단과 외부 실제 의존성 부재를 구분했고 허용된 네트워크 실행으로 복구했다.
`.python-deps/grasp` 안에만 설치; base Conda/system Python 변경 없음.
Optuna API는 [공식4.6 문서](https://optuna.readthedocs.io/en/v4.6.0/reference/generated/optuna.create_study.html)에 따라
SQLite study/resume를 사용한다. 기존tools/optimize.py와 physical gate/binary hashes는 우회하지 않았다.
별도 mechanisms study는 COMPLETE/FAIL/PRUNED를 실제 생성,실패value없음,seed11 반복 일치 PASS.
PRUNED의 intermediate가 저장될 수 있지만 COMPLETE 성능/Pareto로 사용하지 않는다.

`optuna_v2/actual/study.sqlite3`,seed11,실제 SOFA3s 정적 평형. 탐색 k/연결점 개수/위치,
dt=.0005 고정. 동일 설계 hash 중복은PRUNED. 목적은 강성비 최대/최대 X slip 정규화값 최소.
OFF/ON 동일 하중.0001/재료/solver,평형 없으면 목적값 없음. OFF도 반복시 fresh isolated실행했다.

## 실제 Pareto (이 샘플링 범위 내)

trial21: k=40.726591919135586,연결점9개,
indices[1,2,3,4,5,7,8,9,10],positions[3,6,9,12,15,21,24,27,30]mm.
강성비1.6644125301035089,normalized slip.022238971286411335.
ON 처짐.025346732623485607mm,최대X slip1.8764089581679855e-5mm,
상대 정적잔차5.491728361124715e-7,최대회전.0012938286898871985rad,최대속도3.34750640349e-12.
연결9개는 복잡도/비용 지표이며 목적함수를 임의로 바꾸지 않았다.
기존전점 k100의 약1.676배와 비슷한 포화 영역이지 전역최적/실물최적이라는 주장이 아니다.
실제 trial별 비용/runtime/잔차/설계hash는SQLite attrs 및 metrics에 있다.

원래 후보 재실행/21노드 동일 물리위치 mesh검증 PASS.
추가독립 `candidate_extra`는 OFF/ON각각 실행:

|검사|강성비|normalized slip|판정|
|---|---:|---:|---|
|dt .00025,3s|1.6644125301035733|.022238972010640238|PASS|
|dt .0005,9s(6s연장)|1.6644125301035089|.022238971286411335|PASS|

추가 비교 진단선.5%,실제 최대변화3.2566e-8이며 수치허용오차를 완화하지 않았다.
OFF 유연성은 전단OFF 조건에서 동일하게 유지된다. k가물성을 바꾸지 않는 연구 스프링 모델의 결과다.
실제PET 압력/마찰/제작/파지 지지외력의 최적설계가 아니다.
Pareto의 접촉 Quadrature/해제/6방향 검사는 **해당없는30mm 모델**이며 파지후보에 적용한 것으로 표시하지 않는다.
