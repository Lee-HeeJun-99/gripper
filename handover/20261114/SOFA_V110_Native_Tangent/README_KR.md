# V1.1.0 — Native Tangential Rigid ForceField (연구용, 실제 SOFA 미컴파일)

## 목표
V1.0.9의 첫 스텝 `SIGABRT` (BaseForceField::buildStiffnessMatrix) 원인 후보인 Python ForceField의 직접 행렬 조립 경로를 제거합니다. 이전 정상 기준과 동일한 통합 `Rigid3d` 22개 + `BeamFEMForceField` + `SparseLDLSolver` 장면을 사용하며, C++ `TangentialRigidForceField`가 **자유도에 직접** `addForce`, `addDForce`, `buildStiffnessMatrix`를 적용합니다. 매핑 하위 ForceField가 없어 매핑된 강성 행렬 조립 문제를 분리할 수 있습니다.

## 물리적 범위 (중요)
- 기준은 가로 X 길이 30 mm, 두 PET 층 중심간 거리 `h=0.4 mm`, 11노드/층, 단면 등가 반경과 동일한 Z 끝단 하중입니다.
- 각 접촉점의 작은 회전 가정 하 X 상대 변위: `s = (x_upper-x_lower) - h/2 * (theta_y_upper+theta_y_lower)`.
- 회전은 `theta_y ≈ 2*q_y` (단위 쿼터니언, 초기 방향 항등, `|theta| << 1`)이며 보의 회전이 커지면 물리적/미분 일관성이 깨집니다.
- 힘은 `f = -k b^T s`, 위치에 대한 Jacobian은 `df/dq = -k b^T b`. 구현에 사용한 각 DOF 순서는 `lower_x, lower_rot_y, upper_x, upper_rot_y`이고 `b=(-1,-h/2,+1,-h/2)`입니다.
- `buildStiffnessMatrix`는 이를 **6 DOF/node**의 global rigid state block에 직접 쌓습니다. 이 행렬은 SOFA의 `df/dx`이며 음의 부호입니다. `kFactor` 스케일은 SOFA가 적용합니다.
- 압력·마찰·접촉·재밍 전이·동적 큰 회전·비선형 정확 탄젠트는 포함되지 않습니다. 실제 PET 재밍의 4배 강성 입증이 아닙니다.

## 구성
- `src/TangentialRigidForceField.cpp`: C++ 힘/강성/에너지
- `src/initPlugin.cpp`: SOFA 플러그인 export/register
- `CMakeLists.txt`, `build_windows.ps1`: Visual Studio 2022 x64 컴파일
- `scenes/`: FREE, K=0.01/0.1/1.0, dt 대조 총 6장면
- `tests/test_math_v110.py`: SOFA 없는 독립 finite difference 검사
- `compare_V110.py`: 각 CSV 요약

## 사전 준비
Windows에 **Visual Studio 2022 C++ Desktop Development**, CMake, 그리고 **SOFA v26.06.00 C++ 개발용 헤더와 CMake package**가 필요합니다. SOFA의 실행 전용 배포본에는 SDK 헤더/CMake config가 없을 수 있으므로 configure 오류는 환경 구성 부족일 수 있습니다. C++ 빌드는 해당 SOFA 실행 DLL과 같은 아키텍처/컴파일러/런타임 및 ABI에 맞추어야 합니다.

## 1. 수학적 검증 (먼저)
```powershell
conda activate sofa_clean
cd 'C:\Users\lhj\Desktop\SOFA_V110_Native_Tangent'
python .\tests\test_math_v110.py
```

## 2. C++ 빌드
```powershell
cd 'C:\Users\lhj\Desktop\SOFA_V110_Native_Tangent'
.\build_windows.ps1
```

CMake는 설치 위치 `C:\Users\lhj\SOFA\v26.06.00`를 참조합니다. 빌드 실패 시 `build` 초기 오류와 SOFA 헤더 존재 여부부터 확인해야 합니다. 생성 DLL 예상 위치: `build\bin\Release\SofaTangentialV110.dll` (CMake/Visual Studio에 따라 다를 수 있음).

**주의: 이 ZIP은 Windows SOFA C++ 컴파일이나 실행 성공을 주장하지 않습니다.** API/ABI에 따른 소규모 수정이 필요할 수 있습니다. 빌드 실패 시 오류 로그를 전달해야 합니다.

## 3. 플러그인 등록
빌드 완료 후 DLL을 `C:\Users\lhj\SOFA\v26.06.00\bin\`으로 복사하고 SOFA의 PluginManager가 `SofaTangentialV110`를 찾는지 확인합니다. 해당 DLL이 의존하는 다른 컴파일 DLL도 설치된 SOFA와 ABI가 일치해야 합니다. SOFA가 찾지 못하면 `RequiredPlugin` 로딩 로그로 우선 확인합니다.

## 4. 장면 실행
```powershell
conda activate sofa_clean
cd 'C:\Users\lhj\SOFA\v26.06.00\bin'
$folder='C:\Users\lhj\Desktop\SOFA_V110_Native_Tangent\scenes'
.\runSofa.exe -l SofaPython3 (Join-Path $folder '00_FREE.py')
```
0.30초까지 실행하여 **끝단 처짐 약 `0.041214 mm`** (기존 V1.0.9 FREE와 동일)를 먼저 확인합니다.

이후 별도 SOFA 창에서 아래 순서로 실행합니다.
```powershell
.\runSofa.exe -l SofaPython3 (Join-Path $folder '01_TAN_K001.py')
.\runSofa.exe -l SofaPython3 (Join-Path $folder '02_TAN_K01.py')
.\runSofa.exe -l SofaPython3 (Join-Path $folder '03_TAN_K1.py')
```
0.30초 전에 `INVALID_*`가 나오거나 크래시가 발생하면 그 즉시 해당 실험 중단. 로그를 보존하세요.

## 5. 비교표
```powershell
cd 'C:\Users\lhj\Desktop\SOFA_V110_Native_Tangent'
python .\compare_V110.py
```
비교 기준: (1) FREE 기준 응답 일치 (2) `K` 증가에 따른 미끄럼 감소 (3) 굽힘 처짐 감소 (4) dt 변경 일관성 (5) 발산/크래시 여부. **완료 표시만으로 정적 평형은 증명되지 않습니다.**

## 수치 감사
- `test_math_v110.py`에서 에너지 gradient, 힘 Jacobian, PSD 확인 (100 무작위 상태)
- 나중에 C++ SOFA 플러그인 `assembleKMatrix()` 추출로 Jacobian 원소/부호 검증 필요
- `Rigid3d` 회전 접선공간이 6D이므로 쿼터니언 7D 좌표와 다름. 작은 회전 근사에서만 정합성을 보장합니다.
- 안전장치: 큰 처짐 기록되면 해당 장면 실험 중단. CSV 기록기는 SOFA 애니메이션을 강제 종료하지 않음.

## 참고 문서
- https://sofa-framework.github.io/doc/programming-with-sofa/api-overview/matrix-assembly-api/
- https://sofa-framework.github.io/doc/programming-with-sofa/create-your-plugin/
- https://sofa-framework.github.io/doc/plugins/build-a-plugin-from-sources/
