"""Evidence-backed stabilization reports; failures and research scope stay explicit."""
import csv
import json
import subprocess
from pathlib import Path
from stabilization_common import ROOT,OUT,BUILD,SOFA,sha,write_json

R=ROOT/'reports';E=R/'stabilization_evidence'
def load(name):return json.loads((OUT/name).read_text())
def write(name,text):(R/name).write_text(text.strip()+'\n')
def table(records):
    rows=['|실험|원시 판정|처짐 mm|상대 잔차|','|---|---|---:|---:|']
    for name,r in records.items():rows.append(f"|{name}|{r.get('status','NOT RUN')}|{r.get('tip_deflection_mm','—')}|{r.get('relative_residual','—')}|")
    return '\n\n'+'\n'.join(rows)+'\n\n'
def main():
    E.mkdir(exist_ok=True);code=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    static=load('static/summary.json');gate=load('grasp/gate.json');candidates=load('eight_search/validation.json');audit=load('force_audit.json')
    summaries=['originals.json','force_audit.json','lsan_result.json','dependencies/summary.json','dependencies/python_smoke/result.json','memory/result.json','mass_energy_probe/result.json',
               'newton/summary.json','static/summary.json','static_extras/summary.json','static_controls/summary.json','regression/summary.json','eight_search/proxy_summary.json','eight_search/validation.json',
               'grasp/gate_v1_sampling.json','grasp/gate.json','grasp/suite_summary.json','grasp/refinement_summary.json','grasp/fine_summary.json','grasp/fast_fine_summary.json','energy_audit.json','contact_v1_build_identity.json','fast_regression.json',
               'compensated_cold/summary.json','compensated_followup/summary.json','compensated_checks.json','position_resolution.json','binary_source_versions.json']
    raw_map={}
    for name in summaries:
        p=OUT/name
        if p.exists():
            target=E/name.replace('/','__');target.write_bytes(p.read_bytes());raw_map[str(target.relative_to(ROOT))]=dict(raw=str(p),sha256=sha(p))
    trial_rows=[]
    for p in sorted(OUT.rglob('metrics.json')):
        relative=str(p.relative_to(OUT));target=E/relative.replace('/','__');target.write_bytes(p.read_bytes());r=json.loads(p.read_text());raw_map[str(target.relative_to(ROOT))]=dict(raw=str(p),sha256=sha(p))
        group=relative.split('/')[0];name=str(p.parent.relative_to(OUT));final=gate['experiments'].get(p.parent.name,{}).get('status',r.get('status')) if group=='grasp' else r.get('status')
        trial_rows.append(dict(experiment=name,raw_status=r.get('status'),canonical_gate=final,deflection_mm=r.get('tip_deflection_mm'),residual=r.get('relative_residual'),hold_displacement_mm=gate['experiments'].get(p.parent.name,{}).get('displacement_mm'),binary_sha256=r.get('binary_sha256')))
    for name in ['contact_actual_speed_test.log','sanitized_actual_speed_test.log','contact_v2_test_final.log','fast_test.log','fast_asan_test.log','lsan_test.log','python_tests.log','inherited_python_tests.log','memory/stdout.log','mass_energy_probe/stdout.log','mass_energy_probe/stderr.log','dependencies/abi.log','dependencies/pip.log','dependencies/python312_offline.log','dependencies/python_smoke/stdout.log','dependencies/python_smoke/stderr.log','build.log','build_retry.log','contact_v2_build_final.log','probe_build.log','probe_build_retry.log','fast_build.log','fast_asan_build.log']:
        p=OUT/name
        if p.exists():target=E/name.replace('/','__');target.write_bytes(p.read_bytes());raw_map[str(target.relative_to(ROOT))]=dict(raw=str(p),sha256=sha(p))
    for p in OUT.glob('compensated_*.log'):
        target=E/p.name;target.write_bytes(p.read_bytes());raw_map[str(target.relative_to(ROOT))]=dict(raw=str(p),sha256=sha(p))
    for name in ('solver_matrix/static/solver.tsv','solver_matrix/dynamic_steady_short/solver.tsv','resolution_probe/standard_correct_reference/compensation.csv','resolution_probe/compensated_correct_reference/compensation.csv'):
        p=OUT/name
        if p.exists():
            target=E/name.replace('/','__');target.write_bytes(p.read_bytes());raw_map[str(target.relative_to(ROOT))]=dict(raw=str(p),sha256=sha(p))
    with (E/'trials.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=trial_rows[0]);writer.writeheader();writer.writerows(trial_rows)
    common='''
## 공통 증거/범위

실물 측정값0건. 연구 단위 F/mm/s와 기존 E=250, A≈.732233mm², I=.0426667mm⁴를 사용한다.
기존 plugin/integrated/finite_rotation/multilayer 원본과 골든 파일을 변경하지 않았다.
raw: `results/stabilization_20261115/`; 작은 증거: `reports/stabilization_evidence/`.
설정/명령은 실험별 config.json/command.json/scene.scn, 결과는 metrics.json과 artifact hashes.
정적 잔차<1e-3, 병진/각속도<1e-5, tail drift<1e-4를 유지했다.
실행 성공과 평형/파지 검증을 구분한다. EXPERIMENTAL은 실물 인증이나 전체 모델 PASS가 아니다.
기존45 gate는 이전 소스/바이너리 무결성으로 승계하며 신규 모델에 합산하지 않는다.
'''
    write('STABILIZATION_01_RESIDUAL_SOLVER.md','''# 잔차 및 Solver

**힘 합산/정적 평형 PASS; 보상 합산 Euler cold-start 회귀 PASS. 기존 표준 Euler 실패는 보존.**

독립 SolverTelemetry의 실제 Ax-b 상대 잔차≈8.77e-16인데 재구성 정적 잔차는.00118188이었다.
동일 조건의 최악 X좌표70mm에서 dt*v=-8.64e-15mm, ULP=1.42e-14mm였다.
장기 실행에서는 증분이.212ULP까지 작아졌다. 좌표 반올림으로 소실되는 Euler 증분을
long-double carry에 누적하는 별도 CompensatedEulerPositions를 구현했다.
힘/목표 위치/허용오차를 읽어 보정하는 방식이 아니며 회전과 고정 루트는 그대로다.
자유 물체/접촉/정적 solver에는 helper가 사용을 금지한다. 파지 장면에 적용하지 않았다.
24000개의1e-15mm 증분 단위시험에서 naive는 전부 소실, compensated 오차0이었다.
같은 warm 시작의 잔차.00118188→1.33529e-5, 이후 독립 cold-start9조건 모두 PASS.
초기 warm helper가 seed를 rest로 해석한 분석 오류는 수정 후 별도 디렉터리에서 재검증했고
수정 전 원시 결과는 보존했다. 실제 정적 힘 잔차와 solver native residual은 다른 양이다.
별도 ForceAudit가 각 실제 ForceField를 zero-velocity scratch에 호출했다.
기존 recorder 합과 최대 차이는 검사한 장면에서0이다. 이는 힘 회계 검증이지 BeamFEM의 독립 구현은 아니다.
BeamFEM/LayerNetwork/RoutedCable/ConstantForceField/UniformMass를 분리했다.
중력은 장면에 명시적으로0, 케이블은 제약이 아닌 에너지 기반 힘, 접촉은 이 정적 비교 장면에는 없다.
고정 루트의 반력은 별도 합산하고 자유 DOF 잔차에 넣지 않았다.
병진 분모 F_ref/layers, 모멘트 분모 F_ref*100/layers. 작은 하중 분모를 증가시키지 않았다.

8층 기본 absolute free force7.60030e-12, moment1.90477e-13.
작은 T absolute force2.01701e-13; length3.57694e-13; wire-pressure2.58278e-13.
최대 병진 잔차는 X방향 내부 축력 상쇄에서 관측됐다. 긴 동적 실행의 실패를 힘 누락으로 설명할 근거는 없다.
이 증거는 검사한 구조 Euler 장면의 정밀도 장애를 설명하며 모든 SOFA 장면에 일반화하지 않는다.

StaticSolver+NewtonRaphsonSolver는 실제 SDK API로 실행했다. EigenSparseLU, SparseLDL,
CG(Iterative plugin 선로딩), SparseLU(CSparseSolvers 선로딩) 대조를 수행했다.
CG/SparseLU 최초 등록 실패는 보존하고 필요한 플러그인을 먼저 로딩한 새 실험에서 재검증했다.
대칭 solver는 대칭 planar spring 장면에서만 사용한다. 비대칭 spatial/contact Jacobian에는 LU를 유지한다.

최초20-step(.02s) 정적 시험은 tail에 초기 상태가 포함돼 drift=1로 FAIL.
.15s continuation은 같은 .1s tail 기준으로 PASS(허용오차 변경 아님).
length의 더 엄격한 mixed-DOF L2 stop은 내부 Newton 경고를 남겼다.
별도 length_inf_sufficient_stop은 L2 threshold=F_ref/layers*1e-3로,
각 force DOF의 기존 infinity-norm 기준을 충족시키는 충분 조건을 사용했다.
외부 물리 기준/분모를 바꾸지 않고 경고 없는 재실행을 확인했다.
'''+table(static)+common)
    write('STABILIZATION_02_MEMORY.md','''# MappingGraph 수명

**동일 프로세스 plateau FAIL; 공식 원인/수정 확인 PASS; 패치 엔진 실행 BLOCKED.**
기존 weak_ptr9/9 및 최소 장면4/4 생존 증거를 무결성 검증 후 활용했다.
이번에는 같은 프로세스에서120000step→unload/trim→reload→120000step을 실제 실행했다.
live heap846256→83443056(60000)→166003056(120000)→165848624(unload),
reload 후166017520→248605504→331165504→331010080(unload) bytes.
마지막 구간 증가율1376 bytes/step, FD5 유지, PSS/RSS/Private_Dirty도 함께 기록했다.
unload/malloc_trim이 live allocation을 거의 해제하지 못했다. allocator cache만의 현상이 아니다.

공식 [이슈6230](https://github.com/sofa-framework/sofa/issues/6230)과
[PR6259](https://github.com/sofa-framework/sofa/pull/6259)는 부모 back-reference를 weak_ptr로 바꾸는 수정이다.
PR은2026-09-03 master에1c8a469로 병합됐다. 이 내용은 외부 출처이며 이번 패치 실행 결과가 아니다.
설치 SDK는 여전히 양방향 shared_ptr이다. public API는 const adjacency만 제공한다.
원본 SDK 덮어쓰기/private 강제 해제를 하지 않았다. 호환되는 전체 source build 확보가 필요하며
헤더만 바꿔 기존 바이너리 ABI와 섞지 않는다. 실제 수정 SDK 비교는 NOT RUN.
bounded child4GiB/180s 및 kill/reap를 유지한다. 수 시간 안정성은 NOT RUN.
LSan 재시도는 실제 ptrace fatal error(exit1)로 BLOCKED. ASan/UBSan detect_leaks=0와 구분한다.
'''+common)
    write('STABILIZATION_03_MULTILAYER.md','''# 100mm8층

**Newton 정적 family PASS; compensated cold dynamic family PASS. 표준 Euler 실패는 보존.**
8층 총 질량8e-5, 각 층의 단면/재료 동일(총 재료량 증가 비교).
고정 총 재료량8층 비교는 이번 NOT RUN이며 과거 실패를 변경하지 않았다.
FREE/k1/k10/k100, halfdt/quarterdt/21node/반복/18s 정적 continuation을 실행했다.
정적 solver의 dt는 가상 continuation 간격이다. 이것을 관성 동역학의 dt 수렴이라고 부르지 않는다.
기존 Euler18s/halfdt/mesh 실패는 별도 원시 증거 그대로 유지한다.
원래 rest geometry와 cold start를 유지했고 이번 정적 family는 독립 FEM seed를 사용하지 않았다.
독립 EB FEM과 같은 EA/EI/연결 위치를 쓴8층 static grid와 비교했다.
static ON/OFF 비 약6.47221548은 같은8층의 동일하중 평형끼리 계산했다.
2/4층 새 audit-plugin 회귀는 기존 처짐과 일치했다. 양을 늘린8층을 동일 재료량 최적이라고 주장하지 않는다.
'''+table(static)+table(load('static_extras/summary.json'))+'\n## 보상 합산 cold-start 실제 실행\n'+table(load('compensated_cold/summary.json')['records'])+'\n추가 수렴 판정: `'+json.dumps(load('compensated_checks.json'))+'`\n'+common)
    write('STABILIZATION_04_TENDON_JAMMING.md','''# Tendon / pressure history

작은 tension/길이제어/pressure+tendon의 **정적 및 보상 합산 cold dynamic 평형 PASS**.
실제18s 잔차는 각각.0001625883841/.0003576944441/.00003401176252로 기존1e-3 미만이다.
표준 Euler 실패는 별도 보존하며 마찰 경로별 결과를 섞지 않는다.
원래 routed cable 에너지/힘 커널은 재작성하지 않았다. Static loading은 friction의
history를 동적 loading과 다르게 만들므로 서로 다른 tip 결과를 단순 회귀 오류로 해석하지 않는다.
LayerNetwork force/Jacobian 호출은 history를 누적하지 않고 AnimateEnd에만 commit한다(기존 검증 승계).

2핑거 실제 장면: tension0→.5s 구동→3s pressureON→6s 외력→하중해제→pressureOFF→tendonOFF.
pressure는 prescribed p*A, 같은 정지/운동mu 가정인 층간 slider다. 실제 vacuum/contact opening solve가 아니다.
각 finger100mm2층, 각 layer tension.001, offset±.2, pressureON.001F/mm²는 연구 가정이다.
양쪽 finger의 와이어는 독립 요소이고 object의 위치를 보정하거나 고정하지 않는다.
기본 α=.2, 정상방향 재시험 α=2는 기록된 수치 감쇠 변화이며 물성/하중/잔차 조건은 유지한다.
감쇠 변형의 과도응답을 기존 값과 같은 동역학이라고 주장하지 않는다.
복원/해제의 실제 데이터는 contact.csv/object.csv/state.txt에 있다.
실제 와이어 마찰/모터 stroke/3D pressure friction은 NOT RUN.
'''+common)
    grasp_lines=['|장면|최종 gate|이동 mm|object 잔차|실패 항목|','|---|---|---:|---:|---|']
    for name,r in gate['experiments'].items():grasp_lines.append(f"|{name}|{r['status']}|{r.get('displacement_mm','—')}|{r.get('object_force_residual','—')}|{','.join(k for k,v in r.get('bounded_hold_checks',{}).items() if not v) or r.get('reason','—')}|")
    write('STABILIZATION_05_GRASPING.md','''# 자유 물체 / opposing fingers

**자유6DOF/분포마찰/제한적 유지 구현 EXPERIMENTAL; 전체 파지 인증 미완료.**
Sphere/infinite-cylinder/cube SDF, reference-length trapezoidal line quadrature를 사용했다.
실제2D필름 연속 표면/네이티브 triangle collision pipeline은 NOT RUN.
kinetic friction Ft=-mu*Fn*vt/sqrt(vt²+v0²), v0=1e-5. 정지 stick이 아니라 creep 모델이다.
위치/속도 Jacobian, 실제 SOFA K/B 및 kFactor/bFactor, action-reaction/objectivity/소산 검사 PASS.
현재 실험값 v0와 creep-scale velocity의 FD도 별도 검사했다(절대오차 허용1e-7 유지).

object6DOF는 자유이며4개의 finger roots만 고정했다. 각 finger의 Y/rotX/rotZ는
명시된 planar guide이다. 이를 완전3D soft finger라고 부르지 않는다.
actual Mass API: 첫 node9.09091e-7, object.0001, total.00014,
object mass-matrix diagonal transl.0001/rot.001을 확인했다.
두 BaseMass 오류와 첫 DiagonalMass template/link 오류는 FAIL로 보존/제외했다.

이전 negative-control.001mm 기준은 유지한다. 새 연구 geometry는5mm 반지름의1%인.05mm
탄성 이동을 허용하지만 속도/각속도<1e-5, object 및 finger 힘/모멘트 잔차<1e-3,
접촉 지속을 동시에 요구한다. displacement만으로 성공으로 만들지 않는다.
1e-6 외력은 측정된 µ*sum(Fn) 약3e-6의 유의미한 비율이다.
mu0와4e-6 overload는 병진이.05mm보다 작아도 velocity/force gate에서 FAIL이다.
±X/±Y 기본 유지와 ±Z의 연장/감쇠 조건은 별도 실험이다(조건 혼합 인증 금지).
Coarse mesh/quad 실패를 보존하고 finer hold-only 시험을 별도 수행했다.
180s timeout 이후의 incomplete release를 성공으로 인정하지 않았다.
성능 수정은 마찰 wrench의1차 Jacobian에 필요 없는2차 Hessian 계산을 제거한 것이다.
수학 모델/하중/tolerance를 변경하지 않았다. 기본1201프레임 X/V/R 최대 차이 모두0,
관측 wall time55.57→46.10s(통제된 hardware benchmark 아님).
Release/ASan/UBSan 검사 후 별도 fast 바이너리로 고해상도 조건을 재실행했고
이전 slow timeout과 원시 결과는 보존했다. fine/dt 전체 인증은 최종 gate의 범위만 인정한다.
Cylinder endcaps/box seam/토크 외력 envelope/정확한 정지마찰은 미검증이다.

'''+ '\n'.join(grasp_lines)+'\n\nConvergence: `'+json.dumps(gate['convergence_checks'])+'`\n'+common)
    write('STABILIZATION_06_ENERGY_AUDIT.md','''# 통합 에너지 감사

**접촉 힘/토크/소산 법칙 PASS; 전체 에너지 수지 BLOCKED.**
정상접촉 E=.5*w*kn*min(gap,0)², friction power=-mu*Fn*|vt|²/sqrt(|vt|²+v0²)<=0.
actual component의 Jx/Jv와 action-reaction/net moment를 검사했다. 마찰을 보존 에너지 Hessian으로 해석하지 않는다.
raw rigid velocities 및 실제 질량/관성으로 kinetic energy를 계산하고,
sampled cable work=-∫T d(sum(length)), 외부하중 일=F*Δu, 두 friction dissipations를 기록했다.
이 값은 time-sampled numerical work이며 정확한 연속 적분 또는 측정 에너지가 아니다.
시간변화 T*length의 parameter work를 beam stored energy로 혼동하지 않았다.

실제 deformed scene의 BeamFEM getPotentialEnergy 호출은 'not implemented' 경고를 냈다.
따라서 Beam elastic energy와 Rayleigh dissipation을0으로 넣지 않았다.
전역 energy closure는 BLOCKED이며 component_energy는 layer/cable/normal penalty만 포함한다.
중력은 장면에 명시적으로0이다. 가상의 비보존력 에너지 보존 성공을 주장하지 않는다.
단위별 partial measured work는 energy_audit.json에 있다. 실물 모터/진공 전력은 NOT RUN.
'''+common)
    candidate_text='\n'.join(f"- k={row['design']['config']['k']}, points={row['design']['config']['points']}, ratio={row['actual_ratio']}, slip={row['actual_slip']}, static-approved={row['approved_for_static_scope']}" for row in candidates['candidates'])
    write('STABILIZATION_07_OPTIMIZATION.md','''# 최적화

**Optuna BLOCKED(실제0Trial), 추가 결정론적8층 static proxy15개 + 후보3개 검증.**
격리 pip retry0/8s, pip cache, DNS/프록시, Conda offline 재검사 모두 의존성을 확보하지 못했다.
3 smoke/24 Optuna/실제 Optuna pruning·resume는 NOT RUN이다. host DNS 장애를 패키지 비호환으로 잘못 분류하지 않는다.
이전30개 결정론적 grid/SQLite guard 결과는 소스 무결성을 확인한 이전 증거이며 새 Optuna 결과가 아니다.

새8층 grid는k(.01,.1,1,10,100)×연결 패턴3개, seed11. dt는 설계변수가 아니다.
같은 재료/하중의 static Newton family를 gate로 사용하며 dynamic/grasp family와 구분한다.
SQLite에 proxy를 보존했다. 후보마다 static base/repeat/halfdt/21node/6s 연장,
정적 잔차와 tip/slip 수렴을 검사했다. 모든 작은 gate/설정/원시 해시는 보존한다.
세 번째 complexity 목적은 원래 stiffness/slip 목적과 별도 연구 비용이다.
정지마찰/전체3D 파지/미검증 목적함수는 여전히 최적화 차단이다. 전역 최적성은 주장하지 않는다.

'''+candidate_text+common)
    write('STABILIZATION_08_SOFAPYTHON3.md','''# SofaPython3

**BLOCKED.** ldd에서 libpython3.12.so.1.0 not found. Conda offline 런타임 설치는 캐시 부재로 실패.
isolated dependency 경로를 사용했으며 system Python/가짜 ABI symlink를 변경하지 않았다.
새 Python smoke는 exit0이어도 실제 plugin/scene ERROR를 냈으므로 FAIL이다.
원본 FREE/전단 Python 비교는 NOT RUN. XML/C++ 실험은 별도로 실제 실행했다.
재개 조건: 정상 network 또는 CPython3.12 공유 런타임/stdlib 및 호환 NumPy의 offline packages.
'''+common)
    write('STABILIZATION_09_FULL_VALIDATION.md','''# 회귀/전체 검증

- 이전 전체 증거: 작업 전1061개 hash 검사 불일치0. 인수인계56개도 새 byte-for-byte PASS.
- 기존30mm/600시점/45gate 및 finite kernel은 소스·바이너리 불변의 이전 검증을 승계한다.
- 새 isolated audit plugin으로2/4층 실행 회귀 PASS. 기존 모델/골든 수정 없음.
- C++ release clean build, actual18DOF Jx/Jv/K/B/kFactor/bFactor/objectivity PASS.
- ASan/UBSan own-unit PASS(detect_leaks=0); LSan 재시도 ptrace fatal BLOCKED; 전체 SOFA sanitizer NOT RUN.
- 새 Python5개 및 기존 integrated Python8개 실제 실행. 일부 테스트는 actual campaign fixtures를 사용한다.
- 초기 registration/build/mass/template 실패 로그는 보존한다. FAIL 삭제/재분류 성공 없음.
- 8층 static 및 compensated cold dynamic PASS, original standard-Euler FAIL 보존. Contact/grasp는 EXPERIMENTAL, 전체 energy BLOCKED.
- source/binary/artifact/report manifest는 STABILIZATION_EVIDENCE_MANIFEST.json.

세부 신규 checks는 grasp/gate.json 및 eight_search/validation.json을 따른다.
기존45gate에 신규 개수를 더해서 전체 모델이 인증된 것처럼 표현하지 않는다.
'''+common)
    approved=sum(row['approved_for_static_scope'] for row in candidates['candidates'])
    final=f'''# ReGrip 안정화 실행 보고

기준 `830fd3d00186fd9e772be802c27de7ca2100ecde`.
브랜치 `development/regrip-grasp-stabilization`; code commit `{code}`.
최종 문서 commit은 이 보고서를 포함하는 descendant(`git log -1 --format=%H`)로 확인한다.
원격 push/강제 push/이력 재작성 없음. 이전 브랜치/원본/골든 보존.

## 작업 전후

|항목|이번 결과|
|---|---|
|잔차 회계|PASS: 실제 구성요소 합과 recorder 차이0|
|8층|static Newton 및 보상 합산 cold dynamic PASS; 표준 Euler 실패 보존|
|작은 wire/length/pressure|static 및 compensated cold dynamic PASS; 마찰 경로 차이 분리|
|2/4층 회귀|새 audit binary 실행 PASS|
|메모리|FAIL:2×120000step 후 live heap331165504bytes, FD5|
|공식 메모리 수정|PR6259 확인, 설치본/패치 실행은 미변경/BLOCKED|
|분포 접촉/마찰|C++ full18DOF/Jx/Jv/API/objectivity/소산 PASS, kernel 범위 한정|
|2핑거/free object|실제 실행 EXPERIMENTAL, 일부 조건 FAIL; 전체 파지 미인증|
|8층 fallback 탐색|15proxy,3Pareto, static-approved{approved}/3; Optuna 아님|
|Optuna|BLOCKED,0Trial|
|SofaPython3|BLOCKED, 원본Python NOT RUN|
|전체 에너지|BLOCKED, BeamFEM API 미구현/감쇠 수지 미확보|

수정 파일: models/stabilization, diagnostics/stabilization, tools/stabilization_*, tests/test_stabilization*.
기존 integrated/finite_rotation/FEM/plugin은 read-only로 유지했다.
수정한 오류: sub-ULP Euler 위치 증분 소실, warm 분석의 rest-reference 혼동, plugin wrapper 등록명 치환, 미선행 plugin등록, 중복 BaseMass,
DiagonalMass의 실제 두-template/explicit links, event-time sample window의 dt 비교 편향.
기존 실패와 수정 전후 raw를 모두 보존했다.

## 핵심 수치/범위

8층 static k100 ON/OFF≈6.47221548, Hermite slip≈8.98388108e-8mm.
이는 재료량이 증가한8층 static spring model이며 실제 진공 성능값이 아니다.
보상 합산 cold8층 처짐.00060356765483mm, 잔차1.64997286e-5.
halfdt/21node/18s 잔차2.15210501e-5/1.98673897e-5/1.45721222e-5,
반복 tip 차이0;2/4층 기존 tip와 차이 각각3.61e-16/4.23e-16mm.
모든 힘/모멘트 기준은 유지하며 sub-ULP 증분 보상은 자유 물체에는 사용하지 않았다.
기본 free-object +X 이동6.54322072e-6mm, mu0 약.0178247mm,
overload 약.012645mm. 후자의 이동이.05mm보다 작아도 force/velocity에서 FAIL.
기본±Z는 transient FAIL, 연장/α=2 damping 연구 조건은 별도 평가한다.
정확한 최종 gate와 모든 방향/수렴 결과는 STABILIZATION_05_GRASPING.md.
coarse mesh/quad 실패 및 fine timeout을 숨기지 않았다. 고해상도 hold-only에는 release NOT RUN.

## 한계/미완료

정확한 static stick, finite cylinder caps, 진짜 필름 surface/contact torque,
완전3D unconstrained soft fingers, 전체 beam/damping energy closure,
수정 SDK 비교, 실제 물성/압력/마찰/하드웨어 파지는 미완료다.
모듈 검사 PASS를 전체 물리모델/실물 성능 PASS로 합산하지 않는다.
이번 실행은 worker≤2, child4GiB/180s, 신규 출력 고유 경로로 제한했다.
fine-grid full sequence timeout 후 제한을 늘리지 않고 hold-only 범위를 별도 검증했다.
추가 미검증 파지 최적화는 실행하지 않고 차단했다. 재개 명령은 NEXT_TASKS.
'''
    write('STABILIZATION_FINAL_REPORT.md',final+common)
    write('STABILIZATION_CURRENT_STATUS.md',final.split('## 핵심 수치/범위')[0]+'\n최신 수치와 미검증 범위는 FINAL 및01..09 보고서를 참조한다.\n')
    write('STABILIZATION_NEXT_TASKS.md','''# 재개 지점

1. 정확한 정지/운동 마찰과 객관적 history transport를 독립 검증 후 통합. 현 kinetic creep를 static stick으로 부르지 않는다.
2. fine hold-only의 mesh/quad/dt/전체 release 수렴 및 동일 damping에서6방향 envelope. 아직 전체 파지 optimizer 금지.
3. BeamFEM force/energy 및 Rayleigh damping의 전체 수지. API미구현을0으로 대체하지 않는다.
4. 검증된 structural compensated Euler 범위를 유지하고 복잡한 제약/접촉에는 별도 수학 검증 전 적용 금지.
5. 공식 MappingGraph1c8a469를 포함한 matched SDK를 별도 full build로 확보하고60k/120k 및 골든 회귀.
6. network/offline packages 확보 시 Optuna3+24, CPython3.12/SofaPython3 원본 장면 복구.
7. 실제 E/필름두께/마찰/압력/경로 측정 후 연구 입력의 불확실성 축소.

## 재현(새 출력 루트, 기존 결과 덮어쓰기 금지)

```bash
cd /home/ubuntu/LHJ/ReGrip
export PYTHONPATH=.:tools OPENBLAS_NUM_THREADS=1
export REGRIP_STABILIZATION_OUT=$PWD/results/stabilization_new
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
cmake -S models/stabilization -B build/stabilization_20261115/plugin -DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00 -DCMAKE_BUILD_TYPE=Release
cmake --build build/stabilization_20261115/plugin -j2
cmake -S models/stabilization -B build/stabilization_20261115/contact_v2 -DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00 -DCMAKE_BUILD_TYPE=Release
cmake --build build/stabilization_20261115/contact_v2 -j2
build/stabilization_20261115/contact_v2/test_stabilization_contact
$PY tools/stabilization_dependencies.py
$PY tools/stabilization_trials.py static
$PY tools/stabilization_static_extras.py
$PY tools/stabilization_trials.py regression
$PY tools/stabilization_compensated_suite.py
$PY tools/stabilization_compensated_followup.py
$PY tools/stabilization_compensated_checks.py
$PY tools/stabilization_audit.py
$PY tools/stabilization_eight_search.py
$PY tools/stabilization_grasp.py sphere_x_valid
$PY tools/stabilization_grasp_suite.py
$PY tools/stabilization_grasp_refine.py
$PY tools/stabilization_grasp_fine.py
$PY tools/stabilization_fast_fine.py
$PY tools/stabilization_grasp_gate.py
$PY tools/stabilization_energy.py
$PY -m unittest discover -s tests -p test_stabilization.py
```

Memory/probe CMake는 diagnostics/stabilization, 실제 process 명령은 저장된command.json/result.json을 따른다.
추가 바이너리는 같은 CMake source를 별도 build/stabilization_20261115/compensated,
telemetry, contact_fast 디렉터리에 configure 후 각각 ReGripCompensated/test_compensated,
ReGripTelemetry, ReGripDistributed/test_stabilization_contact target으로 빌드한다.
fast 실행 시 REGRIP_CONTACT_PLUGIN=$PWD/build/stabilization_20261115/contact_fast/libReGripDistributed.so를 설정한다.
위 명령은 현재 소스의 새 실행이며 수정 전 실패 로그를 덮어쓰지 않는다.
외부 의존성과 원본 실행의 BLOCKED가 해소되기 전 성공으로 기록하지 않는다.
''')
    progress=R/'STABILIZATION_PROGRESS.md';prefix=progress.read_text().split('\n## Final campaign snapshot')[0];progress.write_text(prefix+'\n## Final campaign snapshot\n\n'+final.split('## 작업 전후')[1].split('수정 파일:')[0]+'\nDetails: FINAL,01..09,NEXT_TASKS.\n')
    # Scientific figures use actual measured trajectories; no generated/fabricated data.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(7,3.5))
    for name in ('sphere_x_valid','sphere_mu_zero','sphere_z_positive','sphere_z_long_damped'):
        p=OUT/'grasp'/name/'object.csv'
        if p.exists():
            with p.open() as stream:rows=list(csv.DictReader(stream))
            axis='object_z' if '_z_' in name else 'object_x';origin=float(rows[0][axis]);ax.plot([float(r['time']) for r in rows],[float(r[axis])-origin for r in rows],label=name)
    ax.set_xlabel('time [s]');ax.set_ylabel('object motion [mm]');ax.legend(fontsize=7);fig.tight_layout();fig.savefig(E/'object_motion.png',dpi=130);plt.close(fig)
    sources={str(p.relative_to(ROOT)):sha(p) for folder in ('models/stabilization','diagnostics/stabilization') for p in (ROOT/folder).rglob('*') if p.is_file()}
    for pattern in ('tools/stabilization_*.py','tests/test_stabilization*','tests/test_compensated.cpp'):sources.update({str(p.relative_to(ROOT)):sha(p) for p in ROOT.glob(pattern) if p.is_file()})
    for p in (ROOT/'models/integrated').glob('*'):
        if p.is_file():sources[str(p.relative_to(ROOT))]=sha(p)
    binaries={str(p.relative_to(ROOT)):sha(p) for p in (BUILD/'plugin/libReGripStabilization.so',BUILD/'audit_stage.so',BUILD/'contact_v1.so',BUILD/'contact_v2/libReGripDistributed.so',BUILD/'contact_v2/test_stabilization_contact',BUILD/'contact_fast/libReGripDistributed.so',BUILD/'contact_fast/test_stabilization_contact',BUILD/'sanitized/test_stabilization_contact',BUILD/'sanitized_fast/test_stabilization_contact',BUILD/'memory/memory_lifetime',BUILD/'memory/mass_energy_probe') if p.exists()}
    for name in ('compensated/libReGripCompensated.so','compensated/test_compensated','telemetry/libReGripTelemetry.so','telemetry_v1.so'):
        p=BUILD/name
        if p.exists():binaries[str(p.relative_to(ROOT))]=sha(p)
    write_json(R/'STABILIZATION_EVIDENCE_MANIFEST.json',dict(baseline_commit='830fd3d00186fd9e772be802c27de7ca2100ecde',code_commit=code,source_sha256=sources,binary_sha256=binaries,
        report_sha256={str(p.relative_to(ROOT)):sha(p) for p in R.glob('STABILIZATION_*.md')},evidence_sha256={str(p.relative_to(ROOT)):sha(p) for p in E.iterdir() if p.is_file()},raw_evidence=raw_map,raw_root=str(OUT),
        scope='per-trial statuses retain historical failures; canonical grasp gate supersedes weak translation-only claims'))
    print('Stabilization reports/evidence generated',len(trial_rows),'trial records')

if __name__=='__main__':main()
