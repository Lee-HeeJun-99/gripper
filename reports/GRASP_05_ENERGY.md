# GRASP 05 — 에너지 검증

**PASS:** 신규 접촉의 평면 stick/slip 이산 에너지 항등식, 비음수 소산, 순수한 history query.
**FAIL:** 단순 Beam `.5 dᵀKlocal d` 후보를 일반 유한 회전의 정확한 potential로 사용하는 방법.
**BLOCKED:** 전체 beam+구동+마찰+접촉+Rayleigh+시간변화 제어의 폐합 에너지 수지.
미구현 에너지를0으로 두거나 단위검사를 전체 에너지 보존 PASS로 처리하지 않았다.

`diagnostics/grasp/BeamEnergyProbe.cpp`는 설치 SDK의 공개 beam data/local stiffness,
실제 BeamFEM 변위 convention으로 후보E를 구성하고 독립적으로 위치/회전을 perturb하여 −dE와 addForce를 비교한다.
원본 SOFA를 덮어쓰지 않았다. `audits/beam/result.json`의 status PASS는 **프로브 실행 성공**이며
후보 potential의 일반적 타당성 PASS가 아니다.

|amplitude 연구변위|후보 에너지 F·mm|최대 force-gradient 차이|peak force/torque 수치|
|---|---:|---:|---:|
|0|0|0|0|
|.001|4.266681068e-11|3.28592558e-13|2.13333335e-6|
|.01|4.268106822e-9|3.29495748e-10|2.13333468e-5|
|.1|4.410682077e-7|3.29497254e-7|.00032950406|
|.4|1.051339466e-5|2.10809889e-5|.00527187605|

표는 병진·회전이 섞인 진단 최대값이며 서로 다른 단위의 성분을 통합한 엄밀한 norm이라고 주장하지 않는다.
작은 변형에서는 근사적으로 일치하지만 변형 증가에 따라 차이가 커진다.
corotational frame의 미분/현재 force convention을 포함하지 않은 단순E를 정확한 전체 potential로 채택하지 않았다.
구조 force FD/힘평형 PASS와 에너지 potential의 전역 타당성은 별도다.

계산되는 신규 항목: normal penalty E, tangential elastic E,return mapping D,
접촉 해제 시 소실되는 elastic E,기존 LayerNetwork/RoutedCable의 계산 가능한 부분.
평면 접촉 이산 외부일3.044e-5,마찰D2.7555e-5,algorithmic term1.625e-7은 별도항으로 검증했다.
curved moving contact에서의 전체 제어일/beam E/Rayleigh 실제적분의 폐합은 미확인이다.
접촉 CSV의 누적D는 실제 시퀀스에서 감소/NaN을 검사했지만 그것만으로 총에너지 보존이 성립하지 않는다.

동적 식의 필요한 형태는 `Δ(K+U)=W_external+W_actuator+W_parameter−D_friction−D_damping−D_numerical`.
구동·압력 ON/OFF가 있는 장면에 무구동 보존식을 적용하지 않는다. 변수압력에서의 저장 에너지 변화도 일로 추적해야 한다.
다음은 BeamFEM의 실제 corotational force에 일관된 energy/observer 또는 경로의존성을 판별하는 work-loop 검증,
그 다음 실제 actuator/normal/contact work와 감쇠일을 함께 적분하는 부분부터 진행한다.
