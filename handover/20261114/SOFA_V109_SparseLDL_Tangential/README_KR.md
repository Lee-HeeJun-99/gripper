# V1.0.9 — SparseLDL 기반 접선 ForceField 분리 검증

## 목적
V1.0.8 결과: FREE 통합 보 + SparseLDL 처짐 0.04121379 mm (0.3초), FREE 통합 보 + CG 처짐 0.00003136 mm. 따라서 V1.0.9는 **보 구조, 하중, 솔버를 고정하고 Python 접선 ForceField의 유무 및 강성만 변화**시킵니다.

## 주의: SOFA 직접 솔버와 Python 커스텀 ForceField
- `addForce`는 힘, `addDForce`는 행렬-벡터 연산을 위한 콜백입니다. 하지만 **직접 솔버 SparseLDL가 요구하는 전역 강성 행렬에 Python ForceField의 접선 강성이 자동 조립된다는 보장은 없습니다.**
- 이 코드에는 C++ 네이티브 `buildStiffnessMatrix`/직접 행렬 조립 구현이 없습니다. 힘이 적용되더라도 암시적 적분의 접선 행렬은 불완전할 수 있습니다.
- 따라서 K에 따른 응답 차이는 **예비 실험**이고, 수렴/에너지/시간 간격 재현성 검증 또는 네이티브 ForceField 도입 전에는 최종 물리 검증으로 취급하지 마세요.
- 접선은 전역 X축만 의미합니다. 실제 굽힘 상태에 따른 로컬 접선, 접촉 유지, 마찰, 재밍은 구현되지 않았습니다.
- `COMPLETE`는 0.3초 실행 성공입니다. 정적 평형을 뜻하지 않습니다.

## 실험 목록
| 순서 | 장면 | K | dt (초) | 끝단 반대방향 X힘 |
|---|---|---:|---:|---:|
| 0 | `00_FREE_LDL.py` | 0 | 0.0005 | 0 |
| 1 | `01_TAN_K001_LDL.py` | 0.01 | 0.0005 | 0 |
| 2 | `02_TAN_K01_LDL.py` | 0.1 | 0.0005 | 0 |
| 3 | `03_TAN_K1_LDL.py` | 1.0 | 0.0005 | 0 |
| 4 | `04_FREE_LDL_AXIAL.py` | 0 | 0.0005 | 1e-05 |
| 5 | `05_TAN_K001_LDL_AXIAL.py` | 0.01 | 0.0005 | 1e-05 |
| 6 | `06_TAN_K01_LDL_AXIAL.py` | 0.1 | 0.0005 | 1e-05 |
| 7 | `07_TAN_K1_LDL_AXIAL.py` | 1.0 | 0.0005 | 1e-05 |
| 8 | `08_TAN_K001_LDL_DT025.py` | 0.01 | 0.00025 | 0 |
| 9 | `09_FREE_LDL_DT025.py` | 0 | 0.00025 | 0 |

## Windows 실행
압축을 바탕화면에 해제합니다. SOFA v26.06, SofaPython3, conda `sofa_clean` (numpy 1.26.x) 기존 환경 기준.

```powershell
conda activate sofa_clean
cd 'C:\Users\lhj\SOFA\v26.06.00\bin'
$folder = 'C:\Users\lhj\Desktop\SOFA_V109_SparseLDL_Tangential'
.\runSofa.exe -l SofaPython3 (Join-Path $folder '00_FREE_LDL.py')
.\runSofa.exe -l SofaPython3 (Join-Path $folder '01_TAN_K001_LDL.py')
```

**각 명령은 별도 SOFA 실행이며 Play를 누르고 0.30초까지 확인한 뒤 종료**하세요. 같은 방식으로 `02`~`09`를 하나씩 실행합니다. `INVALID_*` 메시지가 발생하면 진행을 중단하고 로그를 확인합니다. 장면 내부 기록기는 물리 시뮬레이션을 자동 종료시키지 않으므로 창도 닫아야 합니다.

아래 명령으로 비교표 생성:

```powershell
cd 'C:\Users\lhj\Desktop\SOFA_V109_SparseLDL_Tangential'
python .\compare_V109.py
```

## 검증 게이트
1. 00 FREE 0.3초 처짐 약 0.041214 mm를 재현하지 못하면 나머지 K 실험을 해석하지 않습니다.
2. 01 K=0.01 접선 케이스를 우선 실행하고, `max_applied_shear_force`와 `nonzero_force_calls`가 양수인지 확인합니다.
3. 이후 02 (0.1), 03 (1.0)를 진행합니다. 강성 증가 후 불안정해지면 추가로 진행하지 않습니다.
4. 04 FREE_AXIAL과 05~07의 X축 외력 대조 실험에서 slip 억제를 비교합니다.
5. 08/09 dt=.00025 비교에서는 결과 일치 및 안정성을 확인합니다.

`result_V109_*.csv`가 생성됩니다. 추가 열: `max_applied_shear_force`, `nonzero_force_calls`, `last_kfactor`. 힘 값은 k × 최대 상대 X 변위로 산출한 **근사 크기**이지 매핑 반력/솔버 전역 강성 조립 검증이 아닙니다.

## 한계 및 권장 후속
네이티브 C++ ForceField 또는 SOFA에 등록되는 탄성 구성요소가 전역 강성 행렬에 접선 항을 포함하는지 검사해야 합니다. Python 정적 FEM V1.0.6과 강성비 비교는 SOFA 솔버-강성 조립을 확인한 뒤 수행하세요.

본 패키지는 소스 정적 검사와 압축 무결성 확인만 수행할 수 있습니다. Windows runSofa 직접 실행은 이 환경에서 확인되지 않았습니다.
