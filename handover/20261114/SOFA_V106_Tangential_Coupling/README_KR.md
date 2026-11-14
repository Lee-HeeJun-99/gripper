# V1.0.6 — 접선 전용 층간 결합 기준 모델

## 산출물 및 검증 수준

- `tangential_fem_v106.py`: **실행 및 수치 검사 완료**. 독립 Python 2층 Euler–Bernoulli 보 + 축방향 변형 FEM. 각 층의 접촉면 **X 방향 상대 미끄럼**만 연결. 법선(Z) 상대 변위에 대한 강성항 없음.
- `comparison_V106_static.csv`, `slips_V106_static.csv`: 위 Python 모델에서 생성한 결과. SOFA 실행값이 아님.
- `00_SOFA_FREE_REFERENCE.py`, `01_SOFA_DISTANCE_REFERENCE.py`, `sofa_v105_reference.py`: V1.0.5에서 사용한 기존 SOFA 기준 장면의 복사본. **SOFA 접선 전용 연결 장면이 아님.** 실제 Windows v26.06에서 이번 패키지 경로로 실행 확인하지 못함.
- `compare_sofa_v106.py`: V105 과도 응답 결과를 열어 확인하는 보조 도구. 정적 강성 비교로 해석 금지.

## 접선 연결식

층간 접선 상대 변위는 중립축 병진과 회전을 모두 포함합니다.

`slip_i = u_upper,i - u_lower,i + (h/2)*(theta_upper,i + theta_lower,i)`

`E_interface = 0.5 * Σ(k_i * slip_i²)`

연결 강성 행렬은 `Σ(k_i * b_i^T b_i)`로 구성합니다. 이는 비음의 에너지를 가지는 보존적 선형 접선 연결입니다. 반면 과거 SOFA 3D 거리 스프링은 X·Y·Z를 모두 구속했습니다.

## 실행

```powershell
conda activate sofa_clean
cd 'C:\Users\lhj\Desktop\SOFA_V106_Tangential_Coupling'
python .\tangential_fem_v106.py
```

`PASS`가 출력되면 `comparison_V106_static.csv`, `slips_V106_static.csv`가 생성됩니다.

기존 SOFA 기준 장면도 재현하고 싶을 때만:

```powershell
cd 'C:\Users\lhj\SOFA\v26.06.00\bin'
$folder = 'C:\Users\lhj\Desktop\SOFA_V106_Tangential_Coupling'
.\runSofa.exe -l SofaPython3 (Join-Path $folder '00_SOFA_FREE_REFERENCE.py')
.\runSofa.exe -l SofaPython3 (Join-Path $folder '01_SOFA_DISTANCE_REFERENCE.py')
```

SOFA를 0.30초까지 실행하며 결과 이름은 기존 V105 접두어로 기록됩니다. 각 장면은 종료 후 별도로 실행합니다. SOFA 결과를 비교할 때는 중간 속도가 0이 아닌 과도 응답임에 유의하십시오.

## 기대되는 Python 계산 결과

- k=0: 독립 두 층 강성 = 약 0.00237037
- k=0.01: 독립 두 층 대비 약 1.0098배
- k=1: 약 1.728배
- k=10: 약 3.228배
- k=100: 약 3.867배
- k=1e6: 약 3.970배

높은 연결 강성에서 이론 4배에 근접하지만, 이산 스프링을 10개만 설치하므로 강성비는 정확히 4가 아닙니다. 완전 결합 극한값의 공간 수렴성도 별도 검증 대상입니다.

## 제한 및 다음 단계

1. 이 모델은 작은 변형의 **선형 접선 전단 결합** 검증 모델입니다. 접촉면의 실제 압착, 마찰, 진공 재밍은 구현하지 않았습니다.
2. SOFA에서 동일한 X 방향만 전달하는 인터랙션은 이번 패키지에 **아직 구현하지 않았습니다**. 따라서 Python 결과를 SOFA에서 달성했다고 해석하면 안 됩니다.
3. 다음 SOFA 구현은 커스텀 편미분/강성행렬까지 일관되게 제공하는 ForceField 또는 방향을 선택적으로 제한하는 검증된 컴포넌트를 사용해야 합니다. Python Controller가 매 프레임 `Data.value`를 수정해 힘을 주입하는 방식은 과거 SIGSEGV가 있어 피합니다.
4. 비교 시 각 층의 강체 회전으로 인한 접촉면 상대 운동을 포함해야 합니다. 단순 중심선 X 좌표차만으로 접선 미끄럼을 계산하면 안 됩니다.
