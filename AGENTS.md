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
