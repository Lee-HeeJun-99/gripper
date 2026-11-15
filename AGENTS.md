# ReGrip 작업 규칙

- 인수인계 원본은 보존하고 수령 시 파일 해시와 출처를 기록한다.
- V1.0.9 FREE 기준 모델의 Ubuntu 검증 전에는 C++ ForceField 작업 및 최적화를 진행하지 않는다.
- 빈 smoke scene을 기준 FEM 검증으로 취급하지 않는다.
- 종료 코드 0만으로 성공 처리하지 않는다. SOFA 오류 로그, 실행 횟수, 출력 지표를 확인한다.
- dt는 수치 수렴성 변수로 관리한다. 동일 하중과 정적 평형이 확인된 실험만 강성비를 계산한다.
- 실패, timeout, NaN/Inf, 발산 및 평형 미달 실험에 성능 보상을 부여하지 않는다.
- 변경은 이 저장소 Git으로 관리한다. 검증되지 않은 결과를 성공으로 기록하지 않는다.

## GRASP 후속 연구

- 최신 재개 지점은 reports/GRASP_CURRENT_STATUS.md와 GRASP_NEXT_TASKS.md다.
- elastic penalty stick을 정확한 무슬립 Lagrange constraint로,6방향 힘시험을6DOF wrench closure로 부르지 않는다.
- 공간 접촉수렴/전체에너지/자유파지 gate 미통과 시 파지 목적 최적화를 차단한다.
- MappingGraph 패치는 별도 matched-source SDK에만 적용한다. 헤더만 교체하거나 설치 엔진과 ABI를 혼합하지 않는다.
- historical raw/SQLite/binary는 불변. 새 trial/out 이름을 사용하고 build/raw/env는 외장디스크 내부에 둔다.

## CLOSURE 후속 연구 (2026-11-15)

- 최신 상태/재개는 reports/CLOSURE_CURRENT_STATUS.md와 CLOSURE_NEXT_TASKS.md를 우선한다. 과거 GRASP 기록은 보존한다.
- models/closure와 closure_frame은 별도 연구 모델이다. 기존 원본/골든/45gate/물리 구현은 변경하지 않는다.
- 접촉 적분,고정 material-history 간격,Beam 메시,dt를 각각 수렴 검사한다. 2핑거 +Fx PASS를 3핑거 토크 인증으로 전용하지 않는다.
- Rank6,cone closure,측정법선력 제한 LP,실제12방향 유지·복원은 서로 다른 조건이다.
- FrameLayer 기준회전은 trial동안 고정. 상대 planar .005rad 한계를 유지하고 object6DOF를 숨겨 고정하지 않는다.
- 실제 Beam 닫힌 경로 순환일이 확인됐다. 임의 potential/.5dKd 또는 미구현 에너지0으로 전체 에너지 PASS를 만들지 않는다.
- Native constraint multiplier는 해당 implicit 설정에서 impulse다. Jᵀλ/dt로 물리 force/moment를 검증한다.
- 장시간 physics child 동시4개 이하,기본각4GiB/480s; ASan은 virtual shadow 대신별도2GiB RSS/60s. timeout원본보존.

## CONSERVATIVE BEAM 후속 연구

- 최신 상태/재개는 reports/CONSERVATIVE_BEAM_CURRENT_STATUS.md와 CONSERVATIVE_BEAM_NEXT_TASKS.md. 과거 결과는 보존한다.
- models/conservative_beam은 별도 midpoint SO(3) rod. 기존 BeamFEM/골든/45gate를 수정하지 않는다. 상대 요소회전2.8rad branch 제한과 기존 FrameLayer .005rad planar 제한을 구분한다.
- 공간 force Jacobian은 대칭 chart Hessian과 다르다. 검증된 비대칭 접선을 대칭전용 solver에 넘기지 않는다.
- v1 prototype/v2 compiled manifest를 보존한다. queued prototype working-tree snapshot을 compiled-source 증거로 오인하지 않는다. 새 실험은 바이너리/compiled source/transitive dependency guard를 통과해야 한다.
- contact/history/dt 수렴 FAIL와 전체 coupled-energy 미완료 때문에100mm 파지 최적화는 BLOCKED다. 독립 linear FEM 구조 Optuna를 실제 SOFA 파지 trial이라고 부르지 않는다.
- Native 부모 constraint Jacobian은 projective DOF가 제거될 수 있다. 전체 guide 반력은 원래 자식 표면 Jacobian에서 물리 impulse를 복원해야 하며 외력을 임의 상쇄해 채우지 않는다.
- 메모리120000steps/2reload PASS는240000연속/수시간/지속접촉 무누수 인증이 아니다. 구조 전용 compensated translation을 자유물체/회전에 무검증 적용하지 않는다.
