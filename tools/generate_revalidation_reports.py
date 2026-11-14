"""Build the requested numbered reports from new run artifacts, preserving history."""
import csv
import json
import math
from pathlib import Path
import shutil
import subprocess
from verification_common import ROOT,RUN,BUILD,PHYSICS,sha,source_hashes,write_json


def read(path):return json.loads(Path(path).read_text())


def main():
    reports=ROOT/'reports';evidence=reports/'revalidation_evidence'
    evidence.mkdir(exist_ok=False)
    phy=PHYSICS;gate=read(phy/'gate.json');baseline=read(phy/'baseline/comparison.json')
    environment=read(RUN/'environment.json');source=read(RUN/'source_audit.json')
    automation=read(RUN/'automation_release/result.json');guards=read(RUN/'optimization_guards_release/result.json')
    quality=read(RUN/'quality_release.json');python=read(RUN/'python_recovery.json')
    rows=[];measured={}
    for directory in (phy,RUN/'extra_physics_release'):
        for path in sorted(directory.glob('*/metrics.json')):
            r=read(path);name=path.parent.name;measured[name]=r
            (evidence/'metrics').mkdir(exist_ok=True)
            shutil.copyfile(path,evidence/'metrics'/(name+'.json'))
            if r['status']!='complete':continue
            rows.append(dict(case=name,k=r['config']['k'],connector_count=len(r['config']['connectors'] or range(1,r['config']['n'])),
                dt=r['config']['dt'],nodes=r['config']['n'],load=r['config']['load'],duration=r['config']['duration'],
                tip_deflection_mm=r['tip_deflection_mm'],stiffness_ratio=None,max_x_slip_mm=r['max_x_slip_mm'],
                relative_residual=r['relative_residual'],tip_velocity_z_mm_s=r['tip_velocity_z_mm_s'],
                max_rotation_rad=r['max_rotation_rad'],runtime_s=r['runtime_s'],status='PASS',metrics_path=str(path.relative_to(ROOT))))
    free=measured['free'];high=measured['k100'];ratio=high['effective_stiffness']/free['effective_stiffness']
    for row in rows:
        if row['load']==free['config']['load'] and row['nodes']==11:
            row['stiffness_ratio']=free['tip_deflection_mm']/row['tip_deflection_mm']
    with (evidence/'measured_experiments.csv').open('x',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    for path,name in [(phy/'gate.json','physics_gate.json'),(phy/'baseline/comparison.json','baseline_comparison.json'),
                      (phy/'baseline_repeat_check.json','baseline_repeat.json'),(RUN/'source_audit.json','source_audit.json'),
                      (RUN/'environment.json','environment.json'),(RUN/'automation_release/result.json','automation_final.json'),
                      (RUN/'automation/result.json','automation_initial.json'),(RUN/'optimization_guards_release/result.json','optimization_guards.json'),
                      (RUN/'python_recovery.json','python_recovery.json'),(RUN/'quality_release.json','quality.json'),
                      (RUN/'smoke_release/status.json','optuna_smoke.json'),(RUN/'optimization24_release/status.json','optuna_24.json'),
                      (BUILD/'build_manifest.json','build_manifest.json'),
                      (phy/'native_test.log','cpp_native.log'),(RUN/'commands/asan_address_undefined.log','asan_ubsan.log'),
                      (RUN/'build_asan/ctest.log','leak_sanitizer_blocked.log'),(RUN/'automation_release/unittest.log','automation_tests.log'),
                      (RUN/'optimization_guards_release/unittest.log','optimization_guard_tests.log')]:
        shutil.copyfile(path,evidence/name)
    cpp_cases={p.stem:read(p) for p in (RUN/'commands').glob('*.json') if p.stem.startswith(('before_','after_','asan_'))}
    write_json(evidence/'cpp_probes.json',cpp_cases)
    write_json(evidence/'final_source_sha256.json',source_hashes())
    static={}
    for folder in ('tools','tests','reference_fem','scenes'):
        for path in (ROOT/folder).glob('*.py'):
            compile(path.read_text(),str(path),'exec');static[str(path.relative_to(ROOT))]='PASS'
    write_json(evidence/'final_python_syntax.json',static)
    start='8ee78f0c84d042812537655583cb98ed037f310e'
    common=f"이번 실행: `{RUN.relative_to(ROOT)}`. 시작 커밋 `{start}`, 검증 중 dirty=true. 별도 브랜치와 소스/바이너리 SHA256으로 추적한다. 과거 `results/physics_validation`은 회귀 비교 인용에만 사용했고 이번 gate의 성공값을 재사용하지 않았다.\n"
    logref=f"명령 로그: `{RUN.relative_to(ROOT)}/commands/`. 핵심 작은 증거 사본: `reports/revalidation_evidence/`.\n"
    statuses="PASS=실행·통과, FAIL=실행·실패, BLOCKED=환경·의존성 차단, NOT RUN=미실행, NOT APPLICABLE=현재 연구모델 대상 아님.\n"
    def save(name,body):
        target=reports/name
        if target.exists():raise FileExistsError(target)
        target.write_text(body)
    save('01_SOURCE_AUDIT.md',f'''# 01 — 소스 및 과거 결과 감사

{common}
원본 보존: **PASS**. 외부 ZIP 및 내부 ZIP의 {source['archive_members']}개 원본 항목을 바이트 비교했다. 인수인계·골든 파일은 수정하지 않았다.
과거 gate의 소스 해시는 68e5acc 소스와 일치했고 기존 두 바이너리 해시도 일치했다.
단, 과거 개별 실행은 519bd5e+dirty=true로 기록되어 깨끗한 커밋 단위의 완전한 provenance는 아니었다. 이번 trial에는 소스 해시, 바이너리 해시, 설정·명령·artifact 해시를 남긴다.

| 버전 | 목적 및 구현 | 검증 범위 / 알려진 한계 |
| --- | --- | --- |
| V106 | 독립 정적 Euler–Bernoulli+축 FEM, 사각 A, u/w/phi 자유도 | NumPy 정적 해법; SOFA 또는 진공 재밍 결과가 아님 |
| V109 | 22 Rigid3d, BeamFEM, SparseLDL, 매핑 계면 | FREE 과도응답 골든; Python 전단 조립 SIGABRT는 문서 이력이며 이번에는 Python 미로딩으로 재현 불가 |
| V110 | C++ 접선 전단 에너지/힘/강성행렬 | 초기 API 수정 후 이전 시험은 k=.1의 100개 검사만 포함; 이번에 k=0..100의 600개 검사와 무효 입력 검사를 추가 |

실제 발견한 문제: 고강성의 에너지-힘 미분 불일치, NaN 강성 전파, null matrix SIGSEGV.
이전 성공을 그대로 확대 해석하지 않고 FAIL 로그를 보존한 뒤 수정했다.
실행 경로에는 골든 응답을 결과로 복사하는 코드가 없다. 골든 읽기는 회귀 비교, 독립 정적 기준 및 그림 생성에만 사용한다.
기존 그래프/후보 스크립트의 고정된 옛 결과 경로는 명시적 --results 입력과 해시 검증으로 보강했다.
{logref}''')
    save('02_ENVIRONMENT_VALIDATION.md',f'''# 02 — 환경 재검증

{common}
Ubuntu 22.04.5, Linux 6.8.0-138-generic, GCC/G++ 11.4.0, CMake 3.22.1을 실제 명령으로 재확인했다.
SOFA: `/home/ubuntu/SOFA/v26.06.00`; include 및 lib/cmake의 SDK로 clean build와 링크를 확인했다.
CPython 분석 환경: `/home/ubuntu/miniconda3/envs/robot_ws/bin/python` 3.10.20.
NumPy {environment['packages']['numpy']}, SciPy {environment['packages']['scipy']}, Matplotlib {environment['packages']['matplotlib']}; Optuna 미설치.
시스템 Python 3.10.12와 기본 Conda Python 3.14.6을 변경하지 않았다.
자원 snapshot: 논리 CPU 20, RAM 31 GiB/가용 약 21 GiB, 디스크 가용 약 63 GiB. 전체 실험 데이터는 프로젝트 내부에 보존했다.

| 항목 | 상태 | 증거 |
| --- | --- | --- |
| SDK, 플러그인 의존성 | PASS | final_plugin_ldd / final_diagnostics_ldd 로그, 누락 없음 |
| C++ ABI | PASS(사용 경로) | compiler `{quality['compiler_abi']}`, 실제 .so 로딩·계산 수행 |
| SofaPython3 | BLOCKED | CPython 3.12 ABI, libpython3.12.so.1.0 not found |
| Optuna 설치 | BLOCKED | pip exit 1; 배포본 없음. curl exit 6, DNS lookup exit 2 |
| 로컬 캐시 | BLOCKED | Python 3.12/Optuna wheel 미발견. 일부 권한 없는 폴더는 읽지 못했으며 우회하지 않음 |

Conda 오프라인 생성은 PackagesNotFoundInChannelsError, 온라인 생성은 repo.anaconda.com DNS 오류였다.
isolated pip와 프로젝트 내부 --target을 사용했고 시스템 재설치나 Python 대체는 하지 않았다.
환경 기본 pip 실패와 직접 DNS 증거를 구분하며 pip 메시지 하나만으로 원인을 단정하지 않는다.
{logref}''')
    cpp=(phy/'native_test.log').read_text().strip()
    save('03_CPP_FORCEFIELD_VALIDATION.md',f'''# 03 — C++ ForceField 및 관측기

{common}
**PASS**: 깨끗한 `build/revalidation_20261114_final`에서 두 프로젝트 configure/compile, CTest 및 실제 batch 로딩.
컴파일 옵션 -Wall -Wextra -Wpedantic; 해당 clean build 로그에서 warning/error를 찾지 못했다.
초기 재빌드/교정 빌드/최종 빌드는 서로 다른 디렉터리이며 기존 build와 원본 소스는 유지했다.

## 재현한 실패와 수정

| 입력 / 검사 | 수정 전 | 수정 후 |
| --- | --- | --- |
| k=100, theta=.0049 에너지 FD | FAIL, 오차 1.20056e-9 > 기존 1e-9 | PASS, 오차 2.09197e-16 |
| NaN stiffness | FAIL, nonfinite force | PASS, 오류 보고 후 거부 |
| null matrix | FAIL, exit -11(SIGSEGV) | PASS, 오류 보고 후 거부 |
| 음수 k, n=0, 잘못된/중복 연결점, 비정규 quaternion, 범위 밖 회전, null MechanicalParams | 과거 미검사 | PASS, 안전한 거부 |

원래 의도한 식 `s=Delta u-h/2*(theta_l+theta_u)`, `E=1/2*k*s²`를 유지했다.
이전의 `theta≈2*q_y`는 실제 SOFA 각도 좌표가 아니므로 힘에 누락된 cos(theta/2) 차이를 만들었다.
작업 사본에서는 평면 각도를 `2*atan2(q_y,q_w)`로 복원하여 기존 선형-in-angle 식과 상수 Jacobian `-k*b^T*b`가 일치하도록 고쳤다.
이는 저장 quaternion 근사를 바로잡는 수정이며, 물성·하중·허용오차를 바꾸지 않았다. 원본 V110 ZIP/소스는 유지했다.
엄밀한 에너지 함수는 이전 q 기반 근사와 O(theta³)의 slip 차이가 있으므로 결과 차이도 숨기지 않고 06 보고서에서 비교한다.

```
{cpp}
```

기존 에너지 FD 1e-9, 접선 FD 1e-7, kFactor 1e-14 예산을 유지했다.
힘 부호, y/z 직접 힘 0, y 모멘트, 실제 addDForce, 6-DOF 조립, 대칭, PSD 및 연결점 선택을 검사했다.
행렬 식은 조립 시 추가 kFactor를 적용하지 않으며 addDForce에만 인자 kFactor를 한 번 곱한다.

오른손 좌표계에서 `Ry(theta)e_x=(cos(theta),0,-sin(theta))`이므로 V106의 `phi=dw/dx≈-theta_y`.
따라서 V106의 `Delta u+h/2*(phi_l+phi_u)`와 V110 부호는 일치한다.
실제 매핑의 sin(theta)와 선형 전단식 theta의 차이는 남는다. 이번 인증은 작은 평면 회전(<.005 rad, qx/qz<1e-8)에 한정하며 정확한 3D/큰 회전 모델을 인증하지 않는다.

관측기는 기계적 벡터를 직접 수정하지 않고 scratch 힘을 합산하지만 ForceField 내부 캐시가 갱신될 수 있다. 이 경로를 포함한 FREE 회귀와 장시간 결과를 재검증했다.
관측기 기존 파일 덮어쓰기를 거부하고 실제 context 시간을 기록한다.

ASan+UBSan 계측 C++ 단위 검사: **PASS**, detect_leaks=0, UBSAN halt_on_error=1.
LeakSanitizer: **BLOCKED**(ptrace 환경 fatal error). 누수 미검출로 바꾸어 보고하지 않는다.
SOFA 배포 라이브러리 전체의 재계측: **NOT RUN**. 계측 단위 범위와 프로세스/FD 검사 범위를 구분한다.
{logref}''')
    errorrows='\n'.join(f"| {name} | {v['max_abs_error']:.6g} | {'PASS' if v['passed'] else 'FAIL'} |" for name,v in baseline['errors'].items())
    save('04_BASELINE_REGRESSION.md',f'''# 04 — V109 FREE 회귀

{common}
**PASS**: 최종 clean-build 관측기로 두 번 독립 600스텝 실행. CSV는 byte-identical이다.
dt=.0005 s, t=.3 s, 처짐 {baseline['errors']['tip_deflection_mm']['final_actual']:.17g} mm,
최대 X slip {baseline['errors']['max_x_slip_mm']['final_actual']:.17g} mm,
끝단 vz {baseline['errors']['tip_velocity_z_mm_s']['final_actual']:.17g} mm/s.
허용오차 `1e-10 + 1e-6*abs(golden)`를 유지했다. 작은 0 근처 값에는 절대오차 바닥이, 큰 값에는 1 ppm 상대오차가 적용된다.
실제 차이가 이 예산보다 매우 작아 현재 비교에는 적절하며 허용오차를 완화하지 않았다. 이는 물리 정확도나 dt 수렴성 인증 자체는 아니다.

| 전체 600개 시점 지표 | 최대 절대차 | 상태 |
| --- | --- | --- |
{errorrows}

AST로 원본 장면의 상수·초기 위치·topology·하중을 추출하여 XML의 질량, E/nu/radius,
고정 루트, 하중 노드, 감쇠, solver, mapping과 비교한 14개 구조 검사가 모두 PASS다.
원본은 시각화/불필요 iterative 플러그인과 Python Recorder가 추가되어 있고 XML은 native 관측기로 대체되어 있다.
이 차이를 물리 일치로 가정만 하지 않고 골든의 가용 지표로 검증했다.
**NOT RUN**: Windows의 모든 22노드 raw 위치/속도 벡터와 직접 비교. 제공 CSV에 raw 벡터가 없고 파생 지표만 있어 비교 자료가 부족하다.
모든 raw 벡터를 비교했다고 주장하지 않는다. 이번 raw 벡터는 별도 보존했고 root/mapping/유한값/시점 검사에 사용했다.
원본 Python 직접 비교는 09의 BLOCKED 항목이다.
실행 명령과 설정은 `{phy.relative_to(ROOT)}/baseline/command.json`, `scene.scn`, `comparison.json`.
0.3초는 여전히 평형이 아니므로 이 값을 강성비의 분모로 사용하지 않았다.
''')
    save('05_PHYSICS_VALIDATION.md',f'''# 05 — 전체 물리·수치 재검증

{common}
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
''')
    table='\n'.join(f"| {measured[name]['config']['k'] or 0:g} | {measured[name]['tip_deflection_mm']:.11g} | {measured[name]['effective_stiffness']/free['effective_stiffness']:.9g} | {measured[name]['max_x_slip_mm']:.9g} | {measured[name]['relative_residual']:.5g} |" for name in ['free','k001','k01','k1','k10','k100'])
    old=read(ROOT/'results/physics_validation/k100/metrics.json')
    change=high['tip_deflection_mm']-old['tip_deflection_mm']
    area=math.pi*(4*(8*.4**3/12)/math.pi)**.5
    save('06_STIFFNESS_AND_SLIP.md',f'''# 06 — 강성 전환 및 미끄럼

{common}
모든 아래 값은 같은 F=.0001 모델 힘 단위의 **평형**에서 새로 측정했다.

| k | 처짐 mm | 강성비 | 최대 X slip mm | 정규화 잔차 |
| --- | --- | --- | --- | --- |
{table}

k=100 강성비 {ratio:.12g}, slip 감소율 {100*(1-high['max_x_slip_mm']/free['max_x_slip_mm']):.9g}%.
최종 속도, 최대 회전, 실행시간 및 나머지 case는 동봉 측정 CSV와 metrics JSON 참조.
이전 k=100 처짐 0.0251703342975253과의 차이는 {change:.9g} mm로, 회전 좌표 복원의 수정에 따른 새 측정값이다.
이전 수치를 그대로 복사하거나 골든 모델의 물성을 변경하지 않았다.

사각 단면 A=3.2 mm², I=.0426666666667 mm⁴.
동일 I를 만드는 기존 SOFA 원형 등가 단면의 A={area:.12g} mm².
두 모델은 EI가 같아 FREE 굽힘이 일치하지만 EA가 다르므로 결합 시 축방향 힘 전달과 ON 강성이 다르다.
독립 정적 비교기에서 원형 A를 적용하면 SOFA와 기존 .5% 이내로 일치한다.
완전 결합 연속체 근사는 `1+A*h²/(4I)`로 사각 단면 4, 원형 등가 약 {1+area*.4**2/(4*(8*.4**3/12)):.9g}다.
유한 노드 정적 FEM의 약 3.9702와 1.6836은 이 한계에 접근한다.
이는 재밍 압력의 차이가 아니라 등가 축단면적/이산화의 차이다.
원형 단면은 연구용 등가 모델이며 실제 8×.4 mm PET 단면이나 실제 겹침 형상으로 간주하지 않는다.

V106 phi와 SOFA theta_y의 부호는 03의 오른손 회전으로 확인했다.
계면 실제 변환은 sin(theta), 현 접선 연구모델은 theta의 선형화를 사용하므로 O(theta³) 오차와 작은 회전 범위 제한을 유지한다.
고정 sweep 후보는 reports/revalidated_sweep_candidate.json에 저장했고 Optuna 최적값으로 표시하지 않았다.
''')
    save('07_AUTOMATION_VALIDATION.md',f'''# 07 — 자동 실행 및 결과 무결성

{common}
**PASS**: 최종 자동화 시험 {automation['tests']}개, failures=0/errors=0.
초기 19개 시험 중 2개는 기대 메시지 문자열이 실제 사유와 달라 FAIL이었다. 분류 범주는 맞았으며 assertion을 실제 진단 문자열에 맞추고,
계면 속도 NaN 검사도 추가하여 20개를 새 디렉터리에서 다시 수행했다. 초기 FAIL JSON과 최종 로그를 모두 보존했다.

추가된 처리: finite 입력 검사, 폴더 원자적 소유권, 실행 전 명령/설정/소스 해시 저장,
실행 중 incomplete 기록, C++ 소스와 실제 빌드 바이너리 manifest 검증, stdout/stderr 분리, timeout/KeyboardInterrupt의 프로세스 그룹 종료 및 wait,
중간 시점 검사, root/mapping/범위 검사, CSV 및 전체 artifact SHA256 무결성 검사.
기존/부분 생성 디렉터리는 재사용하지 않으며 재시작은 새 디렉터리로 수행한다.
실험 결과를 재사용할 때는 manifest와 설정/바이너리를 다시 확인한다.

| 검사 | 시험 방식 / 결과 |
| --- | --- |
| timeout / interrupted | 실제 SOFA 자식 종료, 유효 강성 없음, wait 후 PID 소멸 PASS |
| crash | 별도 fault 프로세스의 SIGSEGV, 비정상 종료 거부 PASS |
| 로그-only ERROR | 실제 runSofa의 없는 플러그인, exit=0인데도 거부 PASS |
| NaN/Inf, diverged, invalid_physics | 새 정상 SOFA raw 출력의 명시적 손상 fixture, 올바른 분류 PASS |
| not_converged | 실제 .01초 SOFA 실행, execution_completed=true / stiffness=None PASS |
| 중복 실행 | 같은 폴더에 두 독립 CLI 실행, 하나만 소유권 획득 PASS |
| 손상 CSV / 누락 파일 / 비단조 시점 | manifest/parser가 거부 PASS |
| 프로세스·FD | 24회 launcher 반복 후 자식 모두 reap, FD 수 동일 PASS |

6초 연장 SOFA에서도 완료/평형을 확인했다. 수 시간 또는 수천 회 장시간 soak: **NOT RUN**.
상한/물리 범위 검사는 실행 후 출력 평가이므로 모든 발산의 즉시 중단을 보장하지 않는다.
주소 공간 제한 4 GiB, 기본 timeout 60초는 유지했다.
각 실험의 Git/dirty/소스/.so/config/명령/stdout/stderr/시간/시계열/지표/실패사유/평형 판정은 로컬 raw 디렉터리에 있다.
raw와 대용량 CSV는 Git에 추가하지 않았다.
''')
    save('08_OPTUNA_OPTIMIZATION.md',f'''# 08 — Optuna 최적화

{common}
**BLOCKED**: Optuna 미설치. 이번 isolated pip 설치도 exit=1이며 DNS/네트워크 및 오프라인 캐시 조사에서 설치 가능한 패키지를 확보하지 못했다.
3-trial smoke와 24-trial 명령은 각각 실제로 실행했으나 의존성 검사에서 중단됐다.
실제 Optuna trial 수 **0**, SQLite study 없음, Pareto 후보 없음, Optuna 최적값 없음.
독립 고정 sweep 결과를 Optuna 결과로 바꾸어 보고하지 않는다.

| 요구 사항 | 상태 |
| --- | --- |
| 물리 gate/소스/바이너리/결과 무결성 차단 | PASS, 의존성 없는 {guards['tests']}개 시험 |
| 실제 OFF/ON 평형 측정에서 목적함수 재계산 | PASS |
| 실패/미평형/NaN/상이한 하중의 성능값 거부 | PASS |
| 3회 sampler/trial, SQLite, 중단/재개 | BLOCKED / NOT RUN |
| 최소 24회 본 최적화 | BLOCKED / NOT RUN |
| Pareto 생성 및 후보 dt/6초/21노드/반복 검증 | NOT RUN(코드 경로만 준비됨) |

탐색 변수는 k, 1~10개 결합점 및 3 mm 격자 위치이며 dt는 제안 변수에 없다.
목적함수는 평형 OFF/ON 강성비 최대화와 OFF 기준 최대 X 미끄럼 최소화다.
각 후보의 dt 절반/6초, Pareto의 21노드/독립 반복을 요구하며 실패에는 성능값 없이 prune한다.
study identity에 소스와 optimizer 해시를 추가했고 변경된 metrics 및 중복 설계를 거부하도록 보강했다.
실제 Optuna API 경로는 실행하지 못했으므로 sampler 상태의 재개 재현성, 중단 복구 및 동시 study 동작은 검증된 것으로 주장하지 않는다.
seed=11은 설정되어 있으나 중단 재개가 연속 실행과 동일한 제안 순서를 만드는지는 추가 검증해야 한다.

재개(패키지를 격리 경로에 확보한 후):
```
REGRIP_BUILD_ROOT={BUILD} PYTHONPATH={ROOT}/.python-deps /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/optimize.py --gate {phy}/gate.json --out results/optuna_new --trials 3
```
smoke/restart 검증 후 별도 study/output에서 --trials 24를 수행해야 한다.
결합점 위치·개수는 현재 격자의 이산 변수, k는 [0.01,100] 범위의 연속 변수다.
이 제한된 혼합 탐색 공간의 결과만 보고하며 전역 최적성을 주장하지 않는다.
''')
    save('09_SOFAPYTHON3_RECOVERY.md',f'''# 09 — SofaPython3 복구

{common}
**BLOCKED**: SOFA 패키지의 SofaPython3 바인딩은 CPython 3.12용이고 libpython3.12.so.1.0가 없다.
readelf NEEDED 및 ldd를 재확인했고 로컬 runtime 검색/오프라인 Conda 생성/온라인 생성이 모두 해결하지 못했다.
오프라인은 Python=3.12/NumPy 패키지 미발견, 온라인은 DNS 실패다.
시스템 Python을 덮어쓰거나 다른 ABI 라이브러리의 symlink로 위장하지 않았다.

원본 V109 Python 파일들을 새 RUN/python_original_scene 폴더로 복사하여 FREE와 전단 장면을 실제로 요청했다.
두 명령 exit=0이지만 플러그인과 Python scene 로딩 ERROR가 있어 **성공이 아니다**.
장면 초기화, 기계적 상태, 적분, CSV 및 XML과의 수치 비교는 NOT RUN이다.
이번 C++/XML 결과와 Python 원본 결과를 직접 비교했다고 주장하지 않는다.
필요한 것은 CPython 3.12 공유 런타임+표준 라이브러리, 호환 NumPy 및 환경 분리다.
Python 3.10/3.14용 확장으로 대체할 수 없다.
명령·실패사유는 revalidation_evidence/python_recovery.json과 RUN/commands/original_python_*.log,
python312_offline.log, python312_online.log에 있다. Conda 전체 환경 진단 로그는 로컬에만 보존했다.
''')
    save('10_FINAL_CODE_REVIEW.md',f'''# 10 — 최종 코드·재현성 검토

{common}
**PASS(검사 범위)**: Python {len(static)}개 파일 syntax compile, C++ warning-enabled clean build,
6개 강성에 걸친 총 600개 상태 단위 검사, 20개 자동화 및 {guards['tests']}개 최적화 guard 검사.
Ruff/전체 type/lint 분석은 도구 미설치로 NOT RUN이다. 단순 syntax 검사를 전체 정적 분석이라고 부르지 않는다.

발견하여 수정한 항목: C++ 회전 좌표-에너지 미분 불일치, 무효 입력과 null pointer,
기존 상태 파일 덮어쓰기, runner 비유한 인자/불완전 시점/출력 디렉터리 경쟁/중단 자식 누수,
개별 source 해시 부재, 손상 CSV 검출 부재, 미검증 gate의 불완전 fingerprint 및 옛 고정 보고서 경로.
관련 실패와 회귀를 새 로그에 남겼으며 물성/하중/허용오차를 완화하지 않았다.

골든 기준은 비교에만 사용했고 실제 응답은 SOFA raw 벡터에서 계산한다.
FEM 독립 기준은 NumPy 방정식을 실제 풀어 얻으며 기존 숫자를 결과로 반환하지 않는다.
과거 보고서·후보는 보존하고 새 비교에는 명시적인 최신 결과 디렉터리를 전달했다.
기존 문서의 theta≈2*q_y 및 기존 100개 검사 설명은 역사적 기록이다. 최신 구현/시험의 범위는 03을 따른다.

단위: x,h,L=mm, t=s, 힘=모델 F 단위, E=F/mm², k=F/mm, 모멘트=F·mm,
질량=F·s²/mm, 에너지=F·mm. 실제 PET와의 단위/물성 보정은 NOT RUN이다.
고정 루트/하중/대응 매핑은 AST-XML 및 실행 상태에서 별도 확인했다.
매우 큰 회전/3D의 에너지 객관성, 실제 진공 압력·마찰, 필름 손상·파지는 현재 인증의 대상이 아니다.

잔여 사항: 전체 BeamFEM 에너지 API 미구현, Windows raw 벡터 부재, full-engine ASan 미실행,
LSan ptrace 제약, 장시간 soak 미실행, Optuna sampler/SQLite 실제 경로 미검증, SofaPython3 미복구.
이 범위는 FAIL을 숨긴 것이 아니라 증거가 없는 항목을 NOT RUN/BLOCKED로 분리한 것이다.
원본 파일은 마지막 manifest 검사에서도 확인하고 대용량 raw/캐시/의존성은 Git 제외한다.
''')
    names=['01_SOURCE_AUDIT.md','02_ENVIRONMENT_VALIDATION.md','03_CPP_FORCEFIELD_VALIDATION.md','04_BASELINE_REGRESSION.md',
           '05_PHYSICS_VALIDATION.md','06_STIFFNESS_AND_SLIP.md','07_AUTOMATION_VALIDATION.md','08_OPTUNA_OPTIMIZATION.md',
           '09_SOFAPYTHON3_RECOVERY.md','10_FINAL_CODE_REVIEW.md']
    links='\n'.join(f'- [{name}]({name})' for name in names)
    save('FINAL_VERIFICATION_REPORT.md',f'''# ReGrip 최종 재검증 보고서

종합 상태: **BLOCKED / 부분 완료**. 접선 연구모델의 재검증과 자동화 보강은 완료했으나,
실제 Optuna 최적화와 원본 SofaPython3 복구는 외부 의존성 문제로 완료하지 못했다.
{statuses}
{common}

## 1. 소스와 실행 환경

검증 브랜치 verification/full-revalidation-20261114. Ubuntu 22.04.5, SOFA 26.06.00,
GCC/G++ 11.4, CMake 3.22.1, 분석 Python 3.10.20/NumPy 1.26.4.
최종 C++ 플러그인 SHA256 `{gate['plugin_sha256']}`,
관측기 `{gate['diagnostics_sha256']}`.
시작 커밋은 위 값이며 최종 로컬 커밋은 응답과 git log에 보고한다. 실행 중 dirty 상태와 소스 해시를 숨기지 않았다.

## 2. 이전 상태와 새 검증

| 항목 | 이번 결과 |
| --- | --- |
| 원본/골든 보존 | PASS, 56개 archive member 바이트 일치 |
| C++ clean build / 등록 / 로딩 | PASS |
| 힘/에너지/Jacobian/kFactor/입력 안전성 | PASS, k=0..100의 600개 무작위 검사 + 고장 probe |
| FREE 600개 시점 회귀 2회 | PASS, 기존 오차 예산 유지, 동일 CSV |
| 기존 물리 gate | PASS, 45/45 새 실제 실행 |
| 추가 반복/힘·모멘트 균형 | PASS |
| 자동화 | PASS, 최종 20개 검사 |
| 최적화 guard/목적함수 | PASS, 실제 새 측정값 사용 {guards['tests']}개 검사 |
| ASan/UBSan 단위 검사 | PASS; LSan는 BLOCKED |
| Optuna 3회 smoke / 24회 본 탐색 | BLOCKED, 실제 trial 0 |
| Pareto 후보/검증 | NOT RUN, 후보 없음 |
| SofaPython3 | BLOCKED, CPython 3.12 런타임 부재 |
| 실물 진공/파지/100 mm 핑거 | NOT APPLICABLE(이번 연구모델 검증 범위 밖) |

## 3. 수정과 수학적 근거

수정 전 high-k 에너지 FD FAIL, NaN force FAIL, null matrix SIGSEGV를 실제 재현했다.
작업 C++의 각도 복원을 2*atan2(qy,qw)로 맞춰 원래 선형 각도 전단식에 힘과 행렬을 일치시켰다.
원본 V110 자료는 변경하지 않았다. 물성·하중·회귀 허용오차도 변경하지 않았다.
runner와 관측기의 입력/출력/중단/무결성/해시 처리를 보강했다.
정적/수치 gate, baseline, 20개 자동화 검사를 수정 후 새 폴더에서 다시 실행했다.

## 4. C++ 빌드 및 플러그인 로딩

깨끗한 별도 디렉터리에서 두 .so와 실제 C++ 테스트를 빌드하고 runSofa 로딩을 확인했다.
소스-바이너리 manifest 불일치와 무효 입력은 실행 전에 거부한다.
실제 힘·미분력·조립 행렬을 k=0~100의 총 600개 무작위 평면 상태에서 검사했다.
상세 수치와 ASan/UBSan/LSan 범위는 03 보고서 및 revalidation_evidence/cpp_native.log 참조.

## 5. FREE 기준 회귀

FREE 0.3초 처짐 {baseline['errors']['tip_deflection_mm']['final_actual']:.17g} mm,
X slip {baseline['errors']['max_x_slip_mm']['final_actual']:.17g} mm,
vz {baseline['errors']['tip_velocity_z_mm_s']['final_actual']:.17g} mm/s.
전체 시점 최대 처짐 차이 {baseline['errors']['tip_deflection_mm']['max_abs_error']:.6g} mm.
회귀 허용오차는 1e-10+1e-6|golden|다.

## 6. 수학·물리·수치 검증

FREE 3초 평형 처짐 {free['tip_deflection_mm']:.17g} mm.
k=100 평형 처짐 {high['tip_deflection_mm']:.17g} mm,
강성비 {ratio:.12g}, 최대 X slip {high['max_x_slip_mm']:.12g} mm,
잔차 {high['relative_residual']:.9g}, 최대 회전 {high['max_rotation_rad']:.9g} rad.
이는 **고정 sweep 결과**이며 Optuna 최적값이 아니다.
사각 A=3.2와 원형 등가 A≈.732233의 EA 차이가 약 3.97배 대 1.68배 차이를 설명한다.

## 7. 자동 시뮬레이션·로그·설정·재현 명령

실험 19개 평형 gate + 추가 4개 설계/고강성 반복 실험의 지표 CSV:
[measured_experiments.csv](revalidation_evidence/measured_experiments.csv).
각 행에 metrics 경로가 있고 그 디렉터리에 config.json, command.json, stdout.log, stderr.log,
raw 상태, timeseries.csv, metrics.json 및 artifact SHA256이 있다.
작은 핵심 JSON/단위 로그는 [revalidation_evidence](revalidation_evidence/)에 Git 관리한다.
큰 raw/시계열/빌드/의존성은 ignored 로컬에 남겼다.

```
/usr/bin/python3 tools/build.py --build-root build/revalidation_new --logs results/revalidation_new/build
REGRIP_BUILD_ROOT=$PWD/build/revalidation_new /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/validate_physics.py --out results/revalidation_new/physics
```

위 새 경로는 예시이며 이미 생성된 실험 경로를 덮어쓰지 않는다.
이번 실제 경로는 `{BUILD}`와 `{phy}`다. gate/로그에는 실제 명령이 있다.
물리 gate와 artifact 해시 검증 없이 최적화를 재개하지 않는다.

## 8. Optuna 설치 및 최적화

isolated pip 설치, 로컬 wheel/캐시 조사 및 3/24-trial 명령을 실제로 시도했다.
Optuna 의존성 부재로 실제 trial은 0회다. SQLite 저장·중단 재개·sampler 경로는 NOT RUN이다.
{guards['tests']}개 의존성 없는 guard/목적함수 검사는 통과했지만 이를 실제 최적화로 계산하지 않는다.

## 9. Pareto 후보 비교

Optuna Pareto 후보는 생성되지 않아 비교는 NOT RUN이다.
k=100, 연결점 10개는 고정 sweep에서의 후보일 뿐이며 최적값·전역 최적값이 아니다.
해당 고정 후보의 dt/메시/6초 연장/독립 반복 검사는 별도로 통과했다.

## 10. SofaPython3 복구

CPython 3.12 ABI와 libpython3.12.so.1.0 부재를 재확인했다.
오프라인 Conda는 패키지를 찾지 못했고 온라인 설치는 DNS 실패였다.
원본 Python 장면의 복사본을 실행 요청했으나 로딩 ERROR로 실패했으며 exit=0을 성공으로 처리하지 않았다.
원본 Python의 기계적 상태·CSV·XML과의 직접 비교는 BLOCKED/NOT RUN이다.

## 11. 잔여 문제 및 미검증 항목

Windows raw 상태 벡터 부재, 전체 BeamFEM 에너지 API 미구현, LSan ptrace 제약,
장시간 soak 미실행, 실제 Optuna sampler·SQLite 재개 경로와 SofaPython3가 남아 있다.
작은 평면 회전 범위 외의 3D/큰 회전, 실제 PET 단위·마찰·진공·파지 성능은 인증하지 않았다.

## 12. 다음 개발 단계와 우선순위

1. 외부 패키지를 쓸 수 있는 환경/오프라인 wheel로 Optuna 및 의존성을 확보한다.
2. 3회 smoke에서 SQLite/중단 재개/실패/prune/Pareto 경로를 실제 확인한 뒤 최소 24회 본 최적화를 실행한다.
3. Pareto 후보 dt 절반/6초/21노드/반복을 확인한다. 현재 후보가 없으므로 비교 표를 꾸미지 않았다.
4. CPython 3.12 공유 런타임+표준 라이브러리+NumPy를 프로젝트 내부에 복구해 원본 Python을 비교한다.
5. full BeamFEM 에너지, 큰 회전/3D, 실제 PET 단위·마찰·진공 보정은 별도 연구로 수행한다.

Windows CSV는 raw 22노드 상태를 제공하지 않아 파생 지표 회귀까지만 가능했다.
3D 큰 회전과 실물 성능은 주장하지 않는다. LSan, 긴 soak 및 Optuna 실제 API 경로의 미검증도 남는다.
원격 push/이력 재작성/원격 브랜치 삭제/시스템 전체 변경은 수행하지 않았다.

## 상세 보고서

{links}
''')
    manifest={str(p.relative_to(ROOT)):sha(p) for p in evidence.rglob('*') if p.is_file()}
    write_json(reports/'REVALIDATION_EVIDENCE_MANIFEST.json',dict(run=str(RUN.relative_to(ROOT)),files=manifest,
        report_sha256={name:sha(reports/name) for name in names+['FINAL_VERIFICATION_REPORT.md']}))
    print('wrote',len(names)+1,'reports;',len(rows),'measured equilibrium experiments')


if __name__=='__main__':main()
