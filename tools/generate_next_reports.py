"""Publish compact actual evidence and clearly scope the bounded development run."""
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
from verification_common import ROOT,BUILD,SOFA,sha,write_json,source_hashes
from research_trial import model_hashes,FINITE
from next_common import NEXT

REPORT=ROOT/'reports';EVIDENCE=REPORT/'next_evidence'

def read(path):return json.loads(Path(path).read_text())
def text(name,body):(REPORT/name).write_text(body.strip()+'\n')
def copy(source,target):
    target=EVIDENCE/target;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,row))+' |\n' for row in rows)

def main():
    EVIDENCE.mkdir(exist_ok=False)
    env=read(NEXT/'environment/summary.json');sofa=read(NEXT/'sofa/summary.json');static=read(NEXT/'static_certified/static/summary.json')
    soak=read(NEXT/'stability/summary.json');memory=read(NEXT/'memory_controls/summary.json');headless=read(NEXT/'headless/summary.json')
    finite=read(NEXT/'final_finite/gate.json');obj=read(NEXT/'final_finite/objectivity/summary.json');limit=read(NEXT/'small_load_limit/summary.json')
    quality=read(NEXT/'quality_reported/summary.json');revision=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    files={
        'environment/summary.json':'environment.json','automation/result.json':'automation.json',
        'optimization_guards_release/result.json':'optimization_guards.json','optuna_smoke/status.json':'optuna_smoke.json',
        'optuna_24/status.json':'optuna_24.json','stability/summary.json':'stability.json',
        'memory_controls/summary.json':'memory_controls.json','memory_isolation/summary.json':'memory_isolation_initial.json',
        'memory_isolation_fixed/summary.json':'memory_isolation_fixed.json','headless/summary.json':'headless.json',
        'sofa/gate.json':'extension_gate.json','final_finite/gate.json':'finite_gate.json',
        'final_finite/objectivity/summary.json':'objectivity.json','small_load_limit/summary.json':'small_load_limit.json',
        'quality_reported/summary.json':'quality.json','static_certified/static/summary.json':'static_research.json',
        'static_certified/static/summary.csv':'static_research.csv','build_certified/unit.log':'finite_unit.log',
        'build_certified/build_manifest.json':'finite_build_manifest.json','build_hardened_sanitized/unit.log':'finite_asan_ubsan.log',
        'finite_rotation/build_initial_fail.log':'finite_initial_build_fail.log',
        'final_wrapper_regression/metrics.json':'wrapper_regression.json','contract_sofa/metrics.json':'contract_sofa.json'}
    for source,target in files.items():copy(NEXT/source,target)
    for pattern in ('test_research_models.py','test_experiment_contract.py','test_research_runner.py'):copy(NEXT/'quality_reported'/(pattern+'.log'),pattern+'.log')
    for name in ('pip_install','pip_cache','pip_config_keys','python312_offline','python312_online','python_scene'):
        copy(NEXT/'environment'/(name+'.log'),'environment/'+name+'.log')
    cases=[]
    for folder in (NEXT/'sofa',NEXT/'final_finite',NEXT/'small_load_limit'):
        for path in sorted(folder.glob('*/metrics.json')):
            r=read(path);name=folder.name+'_'+path.parent.name
            copy(path,'metrics/'+name+'.json')
            # Full raw/CSV remains local. Recheck every declared artifact digest.
            for filename,digest in r['artifacts'].items():
                if sha(path.parent/filename)!=digest:raise RuntimeError('corrupt new experiment '+str(path))
            cases.append(dict(case=name,status=r['status'],length_mm=r['config']['length_mm'],k=r['config']['k'],
                load=r['config']['load'],dt=r['config']['dt'],nodes=r['config']['n'],duration=r['config']['duration'],
                tip_mm=r.get('tip_deflection_mm'),max_x_slip_mm=r.get('max_x_slip_mm'),residual=r.get('relative_residual'),
                rotation_rad=r.get('max_rotation_rad'),runtime_s=r['runtime_s'],metrics=str(path.relative_to(ROOT))))
    with (EVIDENCE/'sofa_measurements.csv').open('x') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(cases[0]));writer.writeheader();writer.writerows(cases)
    off,on=sofa['L100_free'],sofa['L100_on'];ratio=off['tip_deflection_mm']/on['tip_deflection_mm']
    case_table=table(['SOFA case','tip mm','X slip mm','relative residual','status'],[
        [name,f"{r['tip_deflection_mm']:.12g}",f"{r['max_x_slip_mm']:.12g}",f"{r['relative_residual']:.6g}",r['status']] for name,r in sofa.items()])
    memtable=table(['control / 60000 steps','RSS growth KiB','completed'],[[r['case'],r['growth_kib'],r['completion']] for r in memory['cases']])
    common=f"기준 60f41cf; 개발 코드 커밋 `{revision}`. 실행 중 dirty 상태는 개별 JSON에 그대로 기록했다.\n원본/골든 보존, push 없음. 증거: `reports/next_evidence/`; raw/명령/전체 로그: `{NEXT.relative_to(ROOT)}/`.\n"
    text('NEXT_01_OPTUNA.md',f'''# NEXT 01 — Optuna

{common}

**BLOCKED**, 실제 trial **0**. 이번에도 격리 pip 설치와 실제 --trials 3 / --trials 24 진입을 요청했으나 의존성 단계에서 중단됐다.
DNS pypi.org/files.pythonhosted.org/repo.anaconda.com 모두 temporary failure. Python 패키지 호환성 충돌로 확정한 것이 아니다.
Optuna/runtime 오프라인 후보 {len(env['local_candidates'])}개. pip 설정/프록시는 값 대신 존재 여부만 기록했다(인증정보 비공개).
시스템 Python/Conda 환경은 덮어쓰지 않았다.

기존 45 gate의 source/binary/artifact 무결성과 11개 objective/guard 검사를 다시 통과했다.
실제 sampler, SQLite, 중단·재개, 실패 Trial, Pareto 재검증은 **BLOCKED/NOT RUN**.
소스에 seed=11이 있어도 실제 Optuna 재현성 검증을 통과했다고 주장하지 않는다.

별도 정적 FEM에서 k 5개×연결 패턴 4개=20개를 결정론적으로 열거했다.
현재 제한된 격자의 비지배 후보 {len(static['pareto'])}개: `{json.dumps(static['pareto'],ensure_ascii=False)}`.
이는 **Optuna가 아니고 SOFA 최적화도 아니다**. 두 목적이 함께 k/연결점 증가를 선호하므로 경계 후보가 지배하는 결과이며 전역 최적성을 주장하지 않는다.
dt는 탐색에 넣지 않았다. 실측 없는 진공압/마찰/와이어 설계의 최적값도 없다.

설치·재개 명령은 NEXT_TASKS.md. 동일 하중/평형/모델해시 gate를 우회하지 않는다.
''')
    text('NEXT_02_SOFAPYTHON3.md',f'''# NEXT 02 — SofaPython3

{common}

**BLOCKED**. CPython 3.12 ABI, `libpython3.12.so.1.0` 미발견을 ldd로 재확인했다.
프로젝트 내부 `.venv-sofa-next` 대상 Conda offline/online 생성은 패키지 부재/DNS 실패로 해결되지 않았다.
Python 3.10/다른 ABI 공유 라이브러리를 symlink로 위장하지 않았다.

실제 smoke 명령은 environment.json의 python_scene.command에 있다. exit=0이어도 ERROR/scene loading 실패여서 PASS가 아니다.
원본 V109/V110 FREE·전단 CSV 직접 비교는 **NOT RUN**. 이전 실패를 이번 성공으로 재사용하지 않았다.
이번에는 실패한 원본 실행을 반복하지 않고 smoke/ABI 차단 확인 후 XML/C++ 독립 개발을 계속했다.
해결에 필요한 것은 공유 런타임뿐 아니라 CPython3.12 표준 라이브러리 및 호환 NumPy다.
''')
    text('NEXT_03_STABILITY.md',f'''# NEXT 03 — 안정성

{common}

**PASS(부분)**: 기존 자동화 20개와 guard 11개 재실행, 새로운 JSON/실험 계약/무효 인자 검사,
30초 simulated-time SOFA 및 12개 .05초 독립 실행의 자식 reap/FD 균형/해시 검사.
짧은 실행은 모두 not_converged이며 유효 강성값이 없다. 실제 wall time {soak['wall_seconds']:.3f} s.
원시 stability.json의 passed=true는 명시된 프로세스/FD/상한 6개 검사만 뜻한다. **메모리 plateau PASS가 아니다**.

**FAIL: 장시간 RSS plateau / 무한 연속 실행 준비 상태**.
장시간 child RSS {soak['samples'][0]['rss_kib']}→{soak['samples'][-1]['rss_kib']} KiB,
peak {soak['peak_child_rss_kib']} KiB, FD peak {soak['peak_child_fds']}. 후반 RSS range {soak['late_rss_range_kib']} KiB.
FD leak은 보이지 않았지만 단계에 따라 RSS가 증가해 시간을 무한 연장하지 않았다.

{memtable}

별도 headless driver에서도 clear_timer=0/{1000}의 증가량은 각각
{headless['cases']['0']['growth_kib']}/{headless['cases']['1000']['growth_kib']} KiB였다.
따라서 BatchGUI/타이머/신규 전단/관측기 하나의 원인으로 단정하지 않는다.
빈 animation scene은 증가 0, 질량+implicit 및 beam+explicit 기계 장면에서도 증가했다.
첫 explicit 대조는 RequiredPlugin 순서 오류로 FAIL(exit0에도 ERROR); 플러그인을 앞에 배치한 새 실험에서 실행 성공했다.
allocator가 보유한 high-water 메모리인지 누수인지, 정확한 할당 stack은 **미확인**이다. valgrind/heaptrack 없음.
배포 엔진 수정이나 임의 물리 변경으로 숨기지 않았다. native driver의 k100 3초 처짐 회귀는 PASS지만 RSS 문제는 해결하지 못했다.

상한: child 주소 공간 4 GiB, soak RSS 512 MiB/FD256/output512 MiB watchdog,
wall120 s, 반복12회, 총 반복 wall240 s 제한. 신규 연구 runner 최대120000 steps/60초 simulation/41 nodes.
무제한 실행/실패 성능 보상 없음. ASan/UBSan은 신규 컴포넌트 단위 범위 PASS(detect_leaks=0),
전체 SOFA instrumentation **NOT RUN**, LSan의 기존 ptrace 장애 **BLOCKED**. 수 시간 soak **NOT RUN**.
''')
    text('NEXT_04_PHYSICS_MODEL.md',f'''# NEXT 04 — 물리 모델

{common}

기존 30 mm 평면 에너지와 SOFA 회전 정의는 변경하지 않았다. `phi_EB=dw/dx≈-theta_y`.
평면각은 `2 atan2(qy,qw)`이고 기존 s=Delta u-h/2(theta_l+theta_u), E=k*s²/2의 gradient/Hessian은 그 정의 안에서 일치한다.
기존 45 gate를 새 모델 인증으로 확대하지 않는다.

**EXPERIMENTAL** 별도 `FiniteRotationShear`:
`d=p_u+R_u*a_u-p_l-R_l*a_l`, `t=R_l*e_x`, `s=t dot d`, `E=k*s²/2`.
물질 attachment와 tangent를 같이 회전시켜 강체 운동 객관성을 갖는다. lower tangent 선택은 신규 구성 가정이다.
정확한 SO(3) local retraction의 2차 AD로 힘/국소 Hessian을 구했다.
대칭 변분 Hessian과 공간 토크 Jacobian은 다르며 후자는 `-H-0.5*skew(torque)` 연결항을 갖는다.
실제 공간 힘 FD를 검사했고 nonsymmetric EigenSparseLU를 사용한다. 모든 상태에서 PSD/행렬 대칭을 주장하지 않는다.
수식·선택·제약: `models/finite_rotation/README.md`.

**PASS(검사 범위)**: 60개 무작위 유한 회전, 12 DOF 모든 힘/접선 FD,
에너지 FD 1.92619e-11(<1e-9), 공간 Jacobian FD 6.05088e-11(<1e-8),
객관성 4.85723e-17(<1e-13), 모멘트 4.16334e-17(<1e-13), H 대칭,
실제 addForce/addDForce/kFactor/buildStiffnessMatrix/6DOF, NaN differential/null matrix 안전 거부.
첫 컴파일 alias Base 충돌은 Inherit로 수정했고 실패 로그도 보존했다.
단위 probe의 ERROR는 의도한 invalid-input 진단이며 실제 SOFA 정상 실행의 ERROR 허용이 아니다.
별도 ASan/UBSan PASS. component gate `{finite['passed']}`.

SOFA 기본/절반dt/21노드 동일 연결점 3개 실행 + 전체 장면 강체 좌표 변환 PASS.
변환 최대 절대차 `{json.dumps(obj['maximum_absolute_errors'])}`,
허용오차 `{json.dumps(obj['tolerances'])}`. 전 시점 위치/속도/quaternion/잔차/매핑 상태를 비교했다.
하중1e-4에서 planar 대비 처짐 차이 {limit['high_relative_difference']:.9g},
하중1e-5에서 {limit['low_relative_difference']:.9g}: 작은 변형 극한에서 수렴했다.
큰 회전 커널 검사는 유한 방향 상태의 수학적 검사이며 큰 변형 그리퍼의 접촉/재료 인증이 아니다.

독립 다층 FEM은 EA/EI 분리, EB/Timoshenko, 메시/해석해/동일 A 기준을 시험했다.
사각 A=3.2와 원형 A≈.732233을 혼합해 강성비를 같은 실물 결과로 해석하지 않는다.
전체 BeamFEM 비선형 동적 에너지 수지, 다층 3D SOFA 및 실제 필름은 **NOT RUN**.
''')
    static100=[r for r in static['cases'] if r['case'].startswith('L100')]
    text('NEXT_05_GRIPPER_100MM.md',f'''# NEXT 05 — 100 mm 연구 확장

{common}

**EXPERIMENTAL**, 수치 검증된 길이 확장이며 실제 그리퍼 제작/성능 검증이 아니다.
기존30mm 골든/하중/단면은 그대로 보존했다. 별도 비교 실험은 양쪽 길이에 같은 F=1e-6를 적용했다.
이는 작은 회전 영역에서 길이 효과를 분리하기 위한 연구 하중이며 실제 파지 하중 사양이 아니다.
E250, 동일 원형 등가 A/I, 층간격.4를 상속했다. 동적 총질량2e-5는 고정 연구값이며 100mm 실물 질량으로 보정하지 않았다.

{case_table}

100mm FREE/ON 강성비 **{ratio:.12g}**, 같은 평형/하중에서 계산했다.
FREE 길이 처짐비 {off['tip_deflection_mm']/sofa['L30_free']['tip_deflection_mm']:.12g}, EB cubic 예측 {(100/30)**3:.12g}.
dt/시간 .1%, 메시1%, 반복1e-10 상대 기준 유지. 21노드는 동일10개 물리 연결 위치를 사용했다.
전체 small-planar 회전<.005와 기존 속도1e-5/잔차1e-3/drift1e-4 평형 조건 유지.
모든 표의 수치는 새 SOFA 실행 측정값이며 해석 추정이 아니다.

정적 연구 FEM 39개(L30/60/100, 1/2/4/8층, k0/1/100 + wire/contact/Timoshenko) 및 20개 제한 설계 열거 수행.
아래는 **독립 FEM 계산값(SOFA 아님)**:

{table(['case','tip mm','small rotation'],[[r['case'],f"{r['deflection_mm']:.12g}",r['small_rotation_validated']] for r in static100])}

와이어는 T*e 이상적 팁 모멘트, 접촉은 알려진 gap의 평면 penalty이며 각각 해석해 단위 검사 PASS.
압력 마찰은 prescribed N=p*A, cap=mu*N, elastic/plastic return mapping으로 별도 구현했다.
constant-pressure load loop에서 비음수 소산/잔차 및 단일 slider work balance를 검사했다.
JSON 상태 중단/재개와 모델/상태 해시 불일치 거부도 실제 Python 계산에서 검사했다(Optuna/SOFA 재개 아님).
±20% 민감도와 A∝t,I∝t³의 두께 일관 변화는 가정된 탐색 범위이며 실측 신뢰구간이 아니다.
L/E/I/load 영향과 k의 포화 민감도를 따로 기록했다.

미확정 물성·와이어 경로·진공압·마찰·밀도·체결은 `models/gripper_100mm/assumptions.json`의 null로 보존했다.
반지름50mm/1~8핑거는 목표 구조만 기록했다. multi-finger assembly/카트리지 외피/3D tendon/3D object contact/
seal·압력 분포/실물 안정 파지는 **NOT RUN**. full pressure-work thermodynamics나 PET 성능을 검증했다고 주장하지 않는다.
''')
    text('FINAL_DEVELOPMENT_REPORT.md',f'''# ReGrip 다음 단계 개발 최종 보고서

종합 상태: **EXPERIMENTAL / 부분 완료**, 외부 의존성 **BLOCKED**, 장시간 메모리 plateau **FAIL**.
PASS는 실제 시험 범위만, FAIL은 실제 실패, BLOCKED는 외부 의존성, NOT RUN은 미실행을 뜻한다.

## 1. 브랜치·코드·환경

{common}

Ubuntu22.04.5/SOFA26.06/GCC11.4/CMake3.22.1/Python3.10.20/NumPy1.26.4.
최종 문서 커밋은 이 보고서를 포함하므로 `git log -1 --format=%H`와 최종 응답으로 확인한다.
전체 새 소스/바이너리/증거 해시는 NEXT_EVIDENCE_MANIFEST.json에 있다. 기존 manifest도 그대로 검증했다.

## 2. 기존 브랜치 대비 변경

기존 plugin/골든/native_scene/run_trial/trial_validation 물리 코드는 수정하지 않았다.
새 models/finite_rotation(별도 C++), models/multilayer(독립 정적 FEM), models/gripper_100mm(미확정 입력),
experiments/(모델 라벨·JSON 계약), tools/next_*(bounded 검증/보고/진단), diagnostics/headless(대조 실행)를 추가했다.
중간 코드 커밋 702c5a7/7a11ed1을 보존했다. 원본56개 재검사 PASS, 원격 작업 없음.

## 3. 새로 해결한 문제

유한3D attachment 에너지와 공간 Jacobian을 독립 구현했다. 모델/실험 혼합 없이 길이·다층 연구가 가능해졌다.
잘못된 JSON/비정수 step/NaN differential/중복 출력/손상 checkpoint를 거부한다.
실행 루트 `REGRIP_NEXT_OUT`으로 새 세션의 덮어쓰기 방지 및 재개 지점을 지원한다.
RSS 증가를 새로 검출했지만 해결했다고 표시하지 않는다.

## 4. 기존 모델 보존·C++ 안정성

기존45 gate는 소스·바이너리·raw artifact 무결성을 검증해 유지했다(45개 전체 재실행이 아님).
기존 자동화20/guard11 재실행 PASS. 신규 C++60 상태/API/수치미분/ASan·UBSan PASS.
전체 SOFA ASan 및 LSan는 별도 미실행/차단이며 메모리 누수 없음 인증이 아니다.

## 5. 신규 수학·SOFA 검증

새 3D component gate PASS; 전체 장면의 전 시점 강체 좌표 변환도 PASS.
새 모델의 대칭 Hessian과 nonsymmetric 공간 tangent를 구분한다. 세부 수식/예산은 NEXT_04.
Python 연구/계약/runner 검사 17개 PASS. 전체 lint/type 분석 NOT RUN.

## 6. 100 mm 실제 SOFA 측정

F1e-6에서 FREE={off['tip_deflection_mm']:.15g} mm, k100={on['tip_deflection_mm']:.15g} mm,
강성비={ratio:.12g}, ON X slip={on['max_x_slip_mm']:.12g} mm.
dt/동일 연결 위치 메시/반복/18초 연장 PASS. 상태·잔차·회전은 측정 CSV와 NEXT_05에 있다.
이 수치를 실물 그리퍼 성능으로 확대 해석하지 않는다.

## 7. Optuna 및 후보

BLOCKED, 실제0trial. sampler/SQLite/중단 재개/Pareto 검증 NOT RUN.
대신 별도 정적 FEM 20점 결정론적 열거에서 비지배 후보1개를 얻었다. Optuna 또는 SOFA 최적값이 아니다.
제한된 연구 탐색일 뿐 전역 최적성 없음. dt는 설계 변수 아님.

## 8. SofaPython3

BLOCKED, CPython3.12 공유 runtime/stdlib/NumPy 미확보. exit0의 장면 로딩 실패를 확인했다.
원본 FREE/전단 대 이식본 직접 비교 NOT RUN.

## 9. 다층·와이어·접촉·진공 연구

독립 정적 FEM 39case, EB/Timoshenko 해석해, 이상적 tip moment 및 penalty contact 계산/검사 PASS.
압력-마찰 cap 및 hysteresis/dissipation, JSON checkpoint 재개 검사 PASS(가정된 연구 모델).
실측 물성/압력·seal·와이어 경로/3D 물체 접촉/실제 안정 파지는 NOT RUN.

## 10. 장시간 안정성 실패·잔여 문제

30초 simulation +12회 child 정리/FD PASS, **RSS plateau FAIL**.
새 ForceField·관측기를 제거한 기계 장면과 native driver에서도 단계별 RSS 증가가 남았다.
기계 상태가 없는 empty scene은 증가0이었다. 정확한 allocation owner/해제 지연 대 진짜 누수는 미확인.
물리 결과를 조작하지 않고 상한에서 종료했다. 장시간 수 시간 검증은 NOT RUN이다.

## 11. 재현 및 다음 우선순위

NEXT_TASKS.md의 새 경로 명령을 사용한다. 실제 명령은 각 trial command.json, build *.command.json에 있다.
우선순위: 할당 profiler/엔진 원인 분리 → 의존성 복구와 실제 Optuna smoke →24회/Pareto →
원본 Python 비교 → 다층3D/와이어·접촉 통합 → 실측 보정. 기존 검증 정의는 보존한다.
설정 JSON: experiments/baseline/research_100mm.json, experiments/convergence/sofa_100mm.json.
raw는 로컬에 보존하고 Git에는 작은 JSON/CSV/그림/로그만 둔다.

## 12. 근거와 한계

NEXT_01~05, next_evidence/sofa_measurements.csv, static_research.json, finite_unit.log,
finite_asan_ubsan.log, objectivity.json, stability.json 및 memory_controls.json 참조.
이번 실행은 bounded numerical research 기반을 확장했지만 전체 실물 그리퍼/Optuna 목표를 완료하지 않았다.
외부 패키지 차단과 지속 RSS 증가로 무제한/시간 단위 실행은 보류했고, 세션 재개 경로를 남겼다.
''')
    text('CURRENT_STATUS.md',f'''# 현재 상태

브랜치 `development/regrip-next-phase`, 개발 코드 `{revision}`. 문서 포함 최신 커밋은 git log -1 참조.

- PASS: 기존 증거/45 gate 무결성 유지, 자동화20/guard11 재실행, 신규 Python17 검사.
- PASS(수치 범위): 3D C++60상태/API/ASan·UBSan, finite SOFA dt/메시/강체좌표 변환, 100mm SOFA 수렴.
- 측정: 100mm FREE {off['tip_deflection_mm']:.12g} mm / ON {on['tip_deflection_mm']:.12g} mm / ratio {ratio:.12g}.
- EXPERIMENTAL: 다층 정적FEM/이상적wire/contact/prescribed-pressure friction; 실물 검증 아님.
- BLOCKED: Optuna0trial, Python3.12/SofaPython3(저장소 DNS 실패/로컬 패키지 부재).
- FAIL: 장시간 RSS plateau; 기계적 SOFA 대조에서도 증가. 자식/FD 정리는 PASS이나 메모리 안전성 전체 인증 없음.
- NOT RUN: 수 시간 soak/전체 엔진 ASan·LSan/다층3D와 실제 와이어·물체접촉·진공 seal·실물 파지.

다음 작업: NEXT_TASKS.md. 상세/실제 로그: FINAL_DEVELOPMENT_REPORT.md, NEXT_01~05, next_evidence/.
원본·골든·기준 브랜치 보존, push 없음. 현재 작업을 완료된 실물 설계로 표현하지 않는다.
''')
    with (REPORT/'CONTINUOUS_DEVELOPMENT_LOG.md').open('a') as stream:stream.write(f'''
## 최종 delta 실행 기록

- 코드 {revision}; 100mm SOFA ratio {ratio:.12g}; finite C++/SOFA/객관성 검사 PASS.
- 신규 invalid differential guard 및 JSON checkpoint 해시/중단 재개 검사 후 영향 범위 재실행.
- 최종17 Python 검사 PASS, 39 FEM case/20 deterministic enumeration. 실제 Optuna0trial.
- 장시간 RSS 증가 FAIL 발견. writer/전단 제거, native driver, timer clear, empty/mass/explicit 대조 수행.
- explicit 첫 로딩 FAIL은 plugin 순서를 고친 새 폴더에서 재검증. 원시 실패 로그 보존.
- 기존45 gate는 무결성 재확인해 유지했고 전체 재실행으로 과장하지 않음. 원본56 항목 재확인.
- 마지막 작업은 작은 evidence/CSV/그림과 manifest의 local Git 보존. 바이너리/raw/cache/venv 미추적.
''')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    figures=REPORT/'next_figures';figures.mkdir(exist_ok=True)
    fig,ax=plt.subplots()
    for name in ('L100_free','L100_on'):
        with (NEXT/'sofa'/name/'timeseries.csv').open() as stream:rows=list(csv.DictReader(stream))[::50]
        ax.plot([float(r['time']) for r in rows],[float(r['tip']) for r in rows],label=name)
    ax.set(xlabel='Time (s)',ylabel='Tip deflection (mm)',title='SOFA 100 mm research beam, F=1e-6 model units');ax.legend();fig.tight_layout();fig.savefig(figures/'sofa_100mm.png');plt.close(fig)
    fig,ax=plt.subplots()
    for p,rows in static['pressure_cycles'].items():ax.plot([r['deflection_mm'] for r in rows],[r['load'] for r in rows],label='p='+p)
    ax.set(xlabel='Tip deflection (mm)',ylabel='Load (model F)',title='Independent FEM + prescribed-pressure slider, NOT SOFA/PET');ax.legend();fig.tight_layout();fig.savefig(figures/'friction_research.png');plt.close(fig)
    binaries=[SOFA/'bin/runSofa-26.06.00',BUILD/'plugin/bin/libSofaTangentialV110.so',BUILD/'diagnostics/libReGripDiagnostics.so',FINITE,ROOT/'build/next_headless/regrip_headless']
    sources=source_hashes();sources.update(model_hashes())
    write_json(REPORT/'NEXT_EVIDENCE_MANIFEST.json',dict(code_commit=revision,baseline='60f41cfcbf64c94e26a02324526900c4ef69eb15',
        old_manifest_sha256=sha(REPORT/'REVALIDATION_EVIDENCE_MANIFEST.json'),source_sha256=sources,
        binary_sha256={str(p):sha(p) for p in binaries},
        evidence_sha256={str(p.relative_to(ROOT)):sha(p) for p in EVIDENCE.rglob('*') if p.is_file()},
        report_sha256={str(p.relative_to(ROOT)):sha(p) for p in list(REPORT.glob('NEXT_0*.md'))+[REPORT/'FINAL_DEVELOPMENT_REPORT.md',REPORT/'CURRENT_STATUS.md',REPORT/'CONTINUOUS_DEVELOPMENT_LOG.md',REPORT/'NEXT_TASKS.md']},
        figure_sha256={str(p.relative_to(ROOT)):sha(p) for p in figures.glob('*.png')}))
    print('Reports and compact evidence generated. Overall EXPERIMENTAL/BLOCKED; RSS plateau FAIL.')

if __name__=='__main__':main()
