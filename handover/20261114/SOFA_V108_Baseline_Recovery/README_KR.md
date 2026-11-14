# SOFA V1.0.8 — 보 FEM 기준 복원 및 접선 ForceField 단계별 검증

## 핵심 목적
V1.0.7에서 FREE 변위가 V1.0.5의 약 1/1314만큼 작고, K값을 바꿔도 동일했습니다. 그래서 **정상 실행=물리 검증 성공**으로 보지 않습니다.

이 패키지는 다음을 분리합니다.
1. **00:** V1.0.5의 기존 FREE 장면을 소스 수준에서 그대로 재실행 (두 개 별도 `Rigid3d`, `SparseLDLSolver`).
2. **01:** 하나의 22 노드 `Rigid3d`로 합친 FREE 모델, 단 `SparseLDLSolver` 유지. 00과 비교해 보 상태 통합의 영향 확인.
3. **02:** 01의 보/하중은 그대로 두고 `CGLinearSolver`로 바꿈. 솔버 영향 확인.
4. **03/04:** 02에 `ForceFieldVec3d` 접선 연결 추가. K=0.01 / 1 비교.
5. **05/06:** 연결 없는 통합 FREE 및 K=1 접선 모델에 양 끝단 반대 방향의 X축 추가 힘을 주어 `x` 상대 미끄럼과 반력이 생기는지 확인.
6. **07:** K=.01, dt=.00025의 시간간격 확인.

## 중요한 구현 한계
- **00 기준 장면은 보가 별도 상태이고, 01~07은 하나의 22노드 기계 상태로 통합되어 있습니다.** 따라서 00~01에서 기준 처짐이 달라지는 경우, 02~07 수치를 강성 전환 실험의 성공으로 해석할 수 없습니다.
- V1.0.7의 `TangentialPairForceField`를 그대로 사용합니다. `addForce`, `addDForce` 함수가 호출되는 것만으로 SOFA 시스템에 물리력이 전달된다고 단정할 수 없습니다.
- **접선 모델은 전역 X축의 상대 이동만 억제합니다.** 회전하는 보의 국소 접선, 접촉 유지, 마찰, 재밍 구현은 아닙니다.
- 00은 `sofa_v105_reference.py` 기록기를 사용해 `result_V105_V108_00_REFERENCE.csv`를 생성합니다. 나머지는 `result_V108_*.csv`를 생성합니다.
- 모든 장면의 `COMPLETE`는 0.30초 실행 완료를 의미하며 정적 평형을 의미하지 않습니다. 속도 및 시간응답을 함께 확인하세요.

## 장면

| 파일 | 모드 | 솔버 | K | X축 대조 하중 | dt |
|---|---|---|---:|---:|---:|
| 00_REFERENCE_V105.py | 별도 보 FREE | SparseLDL | 0 | 0 | .0005 |
| 01_COMBINED_FREE_LDL.py | 통합 보 FREE | SparseLDL | 0 | 0 | .0005 |
| 02_COMBINED_FREE_CG.py | 통합 보 FREE | CG | 0 | 0 | .0005 |
| 03_COMBINED_TAN_K001_CG.py | 통합 보 접선 | CG | .01 | 0 | .0005 |
| 04_COMBINED_TAN_K1_CG.py | 통합 보 접선 | CG | 1 | 0 | .0005 |
| 05_COMBINED_FREE_CG_AXIAL.py | 통합 보 FREE | CG | 0 | 1e-5 | .0005 |
| 06_COMBINED_TAN_K1_CG_AXIAL.py | 통합 보 접선 | CG | 1 | 1e-5 | .0005 |
| 07_COMBINED_TAN_K001_DT025.py | 통합 보 접선 | CG | .01 | 0 | .00025 |

## Windows PowerShell 실행
압축을 바탕화면에 풀고 다음과 같이 실행합니다. 각 장면마다 새 SOFA 프로세스를 띄우고 **Play**를 눌러 0.30초까지 진행합니다.

```powershell
conda activate sofa_clean
cd 'C:\Users\lhj\SOFA\v26.06.00\bin'
$folder = 'C:\Users\lhj\Desktop\SOFA_V108_Baseline_Recovery'
.\runSofa.exe -l SofaPython3 (Join-Path $folder '00_REFERENCE_V105.py')
.\runSofa.exe -l SofaPython3 (Join-Path $folder '01_COMBINED_FREE_LDL.py')
.\runSofa.exe -l SofaPython3 (Join-Path $folder '02_COMBINED_FREE_CG.py')
```

먼저 기준 FREE 모델 3개 결과를 비교하세요. **00에서 약 0.041214 mm가 재현되지 않거나, 01/02가 비정상적이면 나머지를 진행할 필요 없습니다.** 기준 모델의 변화 원인 분석이 우선입니다.

```powershell
.\runSofa.exe -l SofaPython3 (Join-Path $folder '03_COMBINED_TAN_K001_CG.py')
.\runSofa.exe -l SofaPython3 (Join-Path $folder '04_COMBINED_TAN_K1_CG.py')
.\runSofa.exe -l SofaPython3 (Join-Path $folder '05_COMBINED_FREE_CG_AXIAL.py')
.\runSofa.exe -l SofaPython3 (Join-Path $folder '06_COMBINED_TAN_K1_CG_AXIAL.py')
.\runSofa.exe -l SofaPython3 (Join-Path $folder '07_COMBINED_TAN_K001_DT025.py')
```

결과 비교:
```powershell
cd 'C:\Users\lhj\Desktop\SOFA_V108_Baseline_Recovery'
python .\compare_V108.py
```
`comparison_V108.csv`는 01~07을 요약합니다. 00의 결과는 `result_V105_V108_00_REFERENCE.csv`로 생성됩니다.

## 판단표
- **00 정상, 01 비정상:** 두 보를 하나의 `Rigid3d` 및 한 `BeamFEMForceField`로 합친 구조/토폴로지 영향 우선. 접선 모델 결과 해석 보류.
- **00/01 정상, 02 비정상:** CG 솔버 설정과 `BeamFEMForceField` 조합 검토.
- **00/01/02 정상, 03/04 차이가 없음:** 접선력 값/매핑 전달/힘-탄성 행렬 결합 조사.
- **05 FREE에서 미끄럼 > 0, 06에서 미끄럼 감소:** 외력에 대한 접선 반력이 작동한 정황. 단, 다른 물리량 일관성·평형 검증 필요.
- **05/06 모두 미끄럼 0:** mapped position 동기화 및 actual axial response부터 조사.

## 검증 범위
- 정적 Python 문법과 ZIP 무결성 검사만 수행합니다.
- Windows SOFA v26.06 런타임 및 SOFA 물리 동작은 제작 환경에서 검증할 수 없습니다.
- 1회에서 실행 실패시 화면 로그를 보내주시면 문제를 짚을 수 있습니다.
