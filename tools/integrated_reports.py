"""Render measured campaign evidence without turning failures into performance.

Raw outputs stay ignored; compact evidence and SHA manifests are publishable.
Run after all workers finish. Reports identify historical v1 and hardened v2.
"""
import csv
import hashlib
import json
from pathlib import Path
import subprocess
from integrated_common import ROOT,OUT,BUILD,sha,write_json

REPORTS=ROOT/'reports'
EVIDENCE=REPORTS/'integrated_evidence'

def load(relative):
    return json.loads((OUT/relative).read_text())

def compact(value):
    if isinstance(value,dict):
        return {k:compact(v) for k,v in value.items() if k!='proc_samples'}
    if isinstance(value,list):return [compact(v) for v in value]
    return value

def text_report(name,body):
    (REPORTS/name).write_text(body.strip()+'\n')

def measured_table(records,final_status=None):
    lines=['|실험|판정|처짐 mm|상대 잔차|최종 속도 mm/s|최대 회전 rad|',
           '|---|---|---:|---:|---:|---:|']
    for name,r in records.items():
        status=r.get('status','NOT RUN')
        if final_status and final_status.get(name,status)!=status:status+=' → '+final_status[name]+' (strict)'
        lines.append('|'+ '|'.join([name,status]+[f'{r[k]:.10g}' if isinstance(r.get(k),(int,float)) else '—' for k in ('tip_deflection_mm','relative_residual','final_velocity','max_rotation_rad')])+'|')
    return '\n\n'+'\n'.join(lines)+'\n\n'

def main():
    EVIDENCE.mkdir(exist_ok=True)
    current=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    start=load('start.json'); baseline=load('legacy_baseline/comparison.json')
    multi=load('multilayer/summary.json');tendon=load('tendon/summary.json');friction=load('friction/summary.json');contact=load('contact/summary.json')
    candidates=load('candidate_validation/summary.json');study=load('search_hermite/summary.json');warm=load('warmstart/summary.json')
    dependency=load('dependencies/environment/summary.json');finite=load('finite_beam/summary.json')
    audit=load('residual_audit/summary.json')['records']
    strict_retry=load('strict_residual_retry/summary.json')
    strict={group:{k.split('/')[1]:v['strict_status'] for k,v in audit.items() if k.startswith(group+'/')} for group in ('tendon','friction','contact')}
    paths=['start.json','originals.json','dependencies/environment/summary.json','memory/summary.json','minimal_engine/result.json','diagnostic_hardening/minimal_engine/result.json',
           'legacy_baseline/comparison.json','legacy_baseline_repeat/comparison.json','sensitivity/summary.json',
           'finite_metric_correction/summary.json','finite_metric_correction_rerun/summary.json','residual_audit/summary.json','strict_residual_retry/summary.json',
           'multilayer/summary.json','tendon/summary.json','friction/summary.json',
           'contact/summary.json','grasp_gate.json','finite_beam/summary.json','objective_connector/summary.json',
           'solver_retry/summary.json','warmstart/summary.json','additional_convergence/summary.json',
           'search_hermite/summary.json','search_checks/summary.json','candidate_validation/summary.json',
           'regression/automation/result.json','regression/optimization_guards_release/result.json',
           'invalid_before.json','invalid_after.json','hardening_regression/summary.json']
    evidence_map={}
    for relative in paths:
        if not (OUT/relative).exists():continue
        target=EVIDENCE/(relative.replace('/','__'))
        write_json(target,compact(load(relative)))
        evidence_map[str(target.relative_to(ROOT))]=dict(sha256=sha(target),raw=str(OUT/relative),raw_sha256=sha(OUT/relative))
    # Every completed/new failed trial retains its own identity and raw artifact hashes.
    for raw in sorted((OUT/'candidate_validation').glob('*/summary.json')):
        target=EVIDENCE/str(raw.relative_to(OUT)).replace('/','__')
        write_json(target,compact(json.loads(raw.read_text())))
        evidence_map[str(target.relative_to(ROOT))]=dict(sha256=sha(target),raw=str(raw),raw_sha256=sha(raw))
    for relative in ['graph_ownership.log','minimal_engine/stdout.log','allocation_short/stderr.log',
                     'build_v1/test.log','build_v1/manifest.json','build_v1_asan/test.log','extra_test.log','extra_asan_test.log',
                     'previous_finite_cpp.log','legacy_cpp.log','python_tests.log','python_tests_final.log',
                     'build_v2/test.log','build_v2/manifest.json','build_v2_asan/test.log',
                     'extra_v2.log','extra_asan_v2.log','diagnostic_build_final.log','diagnostic_hardening/minimal_engine/stdout.log',
                     'dependencies/environment/python_abi_0.log','dependencies/environment/python_scene.log']:
        p=OUT/relative
        if not p.exists():continue
        target=EVIDENCE/relative.replace('/','__');target.write_bytes(p.read_bytes())
        evidence_map[str(target.relative_to(ROOT))]=dict(sha256=sha(target),raw=str(p),raw_sha256=sha(p))
    allrows=[]
    for group,data in [('multilayer',multi['records']),('tendon',tendon['records']),('friction',friction['records']),('contact',contact['records']),('finite_beam',finite),('warmstart',warm)]:
        for name,r in data.items():allrows.append(dict(group=group,name=name,final_strict_status=strict.get(group,{}).get(name,r.get('status')),**{k:r.get(k) for k in ('status','tip_deflection_mm','relative_residual','final_velocity','max_rotation_rad','max_interface_slip_mm','object_displacement_mm','binary_sha256')}))
    with (EVIDENCE/'trial_metrics.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=allrows[0].keys());writer.writeheader();writer.writerows(allrows)
    # A standard scientific figure, not an artistic or fabricated bitmap.
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(9,3.5))
    for L in (2,4,8):
        values=[multi['records'][f'L{L}_k{k}']['tip_deflection_mm'] for k in (0,1,100)]
        axes[0].plot([0,1,100],[values[0]/v for v in values],marker='o',label=f'{L} layers'+(' (coarse only)' if L==8 else ''))
    axes[0].set_xscale('symlog',linthresh=.5);axes[0].set_xlabel('point shear k [F/mm]');axes[0].set_ylabel('OFF / ON deflection');axes[0].legend()
    for row in candidates['candidates']:
        if row['approved_for_scope']:
            axes[1].scatter(row['actual_reconstructed_slip'],row['actual_SOFA_stiffness_ratio'])
    axes[1].set_xlabel('reconstructed slip [mm]');axes[1].set_ylabel('SOFA candidate stiffness ratio');axes[1].set_xscale('log')
    fig.tight_layout();fig.savefig(EVIDENCE/'comparison.png',dpi=140);plt.close(fig)
    approved=sum(r['approved_for_scope'] for r in candidates['candidates'])
    scope='''
## 공통 범위 및 판정

모든 신규 수치는 연구 단위 F, mm, s의 시뮬레이션이며 실물 측정값은 없다.
원본 `plugin/`, `models/finite_rotation/`, `models/multilayer/beam.py`, 골든 데이터는 변경하지 않았다.
기존 45개 gate는 시작 manifest 무결성을 확인한 **이전 검증**이며 새 모델의 인증으로 합산하지 않는다.
신규 평형 판정은 sampled static residual <1e-3, 최종 병진/각속도 <1e-5,
tail relative drift <1e-4이다. 실패를 숨기기 위해 하중·재료·허용오차를 바꾸지 않았다.
평면 slider/선형 연결은 회전 <.005 rad 및 |qx|,|qz|<1e-8만 인정한다.
초기 v1의 nonzero-load residual floor 때문에 일부 tiny-cable PASS는 강화 감사에서 FAIL로 바뀌었다.
최종 판정은 residual_audit/strict_residual_retry가 우선하며 과거 raw의 상태를 수정하지 않는다.
Raw 위치: `results/integrated_20261115/`; 작은 증거: `reports/integrated_evidence/`.
`metrics.json`은 소스/바이너리 해시, 설정, 명령, 로그, 원시 상태 파일 해시를 포함한다.
PASS는 명시된 검사만 의미하며 EXPERIMENTAL transient의 프로그램 종료는 평형 PASS가 아니다.
'''
    text_report('INTEGRATED_01_MEMORY.md','''# SOFA 메모리 진단

**원인 재현 PASS / 동일 프로세스 plateau FAIL / 외부 엔진 수정 NOT RUN.**

60000 step FREE에서 mallinfo2 live_heap=195384912 bytes, unload 후194904800 bytes.
malloc_trim으로 live allocation은 제거되지 않는다. RSS만 보고 leak으로 단정하지 않았다.
별도 operator new/delete 추적(직접 malloc/aligned 제외)의 stack이
`MappingGraph::build`, `makeMappingGraphNode`, `addEdge`를 지목한다.
SDK BaseMappingGraphNode의 부모·자식 모두 shared_ptr이다. 공개 API graph.clear 후
weak_ptr 9/9 생존, beam/observer/new ForceField가 없는 mass-only 최소 장면에서도4/4 생존.
최소 장면60000 step 종료 live_heap83443728 bytes, unload83289648 bytes.
이 특정 ownership retention은 확인됐지만 모든 메모리 증가가 이 경로뿐이라는 증명은 아니다.

원래10000 step allocation tracing은150s timeout/SIGKILL로 FAIL;1500 step 재시도는 성공(skipped=0).
이전 empty/mass/beam/implicit/explicit/FREE/coupled 대조군은 이전 증거로 보존했다.
이번에는 allocator default/trim, native driver, graph clear, mass-only 최소 재현을 추가했다.
Finite field/recorder 각각의 수 시간 plateau, 전체 엔진 LSan은 NOT RUN.
프로젝트 ASan/UBSan은 detect_leaks=0 범위만 PASS이며 배포 SOFA는 instrument하지 않았다.

외부 SDK·엔진 바이너리/시스템은 수정하지 않았다. 안전한 우회는 실험별 bounded child:
주소 공간4GiB, wall timeout180s, 최대120000 step/60s(일반 runner), 종료 후 reap.
이는 같은 프로세스의 leak 수정이 아니며 장시간 안정성 인증도 아니다.
FD/PSS/Private_Dirty 샘플과 allocator 통계는 memory/summary.json에 남는다.

재현: `python tools/integrated_memory.py`, `python tools/integrated_minimal.py`
(출력 루트를 새로 지정하고 진단 바이너리를 먼저 빌드). 최소 장면은
`scenes/integrated/minimal_mapping_graph.scn`; 외부 엔진 이슈로 제출 가능한 재현이다.
'''+scope)
    text_report('INTEGRATED_02_OPTUNA.md',f'''# Optuna 및 대체 탐색

**Optuna BLOCKED, 실제 Optuna Trial=0.** pypi.org/files.pythonhosted.org/repo.anaconda.com DNS 실패.
프록시/pip index 환경 설정 없음, 로컬 wheel 후보0. 격리 pip --target 재시도와
Conda offline/online 모두 실패했다. 시스템 Python 변경/정책 우회는 하지 않았다.
실제 Optuna의3 smoke/24 trial, pruning, SQLite study는 NOT RUN이다.

별도 결정론적 EB FEM grid는30개 물리 설계 완료+고장 주입1개 실패이다.
seed11, layers2/4, k=(.01,.1,1,10,100), 연결점패턴=(5,10)/(2,4,6,8,10)/(1..10).
고정 dt는 SOFA 후보 검증 변수이며 탐색 변수가 아니다. 동일 F=1e-6, 재료 E=250,
동일 family의 FREE 기준을 사용한다. 8층 및 미평형 equal-material family는 차단했다.

SQLite physical-design unique hash, source/binary identity, 실패 objective=None,
실제 SIGTERM 후 resume, seed 반복, 손상 metric/result hash 거부 등7/7 workflow 검사 PASS.
이는 Optuna 검사로 계수하지 않는다. 기존 nodal metric study와 새 Hermite metric study를 분리했다.
원래 stiffness↑/slip↓를 유지하고 complexity=(layers-1)*pointcount↓는 별도 연구 목적이다.
총 재료량이 다른2/4층 결과를 동일 재료 설계 우열로 해석하지 않는다.

Hermite Pareto6개 중 현재 완료{len(candidates['candidates'])}개, SOFA 독립 재검증 승인{approved}개.
대리 FEM 탐색 결과 자체를 SOFA/Optuna 최적화라고 주장하지 않는다.
후보마다 base/repeat/dt절반/21노드(연결 물리 위치 고정)/18s(+6s), 평형과 미끄럼을 확인했다.
명령: `python tools/integrated_search.py --help`, `python tools/integrated_candidates.py`.
정확한 설정/목적함수/모든 실패는 search_hermite/summary.json 및 candidate_validation에 보존했다.
'''+scope)
    text_report('INTEGRATED_03_SOFAPYTHON3.md','''# SofaPython3 복구

**BLOCKED.** 실제 libSofaPython3.so의 ldd에서 libpython3.12.so.1.0 not found를 재확인.
기존 Python3.10을3.12로 위장하거나 symlink하지 않았다. CPython3.12와 NumPy의 격리
Conda 복구는 offline 캐시 부재 및 online DNS 장애로 실패했다.
`runSofa --noautoload --tmp -g batch -a -n 3 -l SofaPython3 scenes/python_smoke.py`
종료 코드0이어도 오류 로그가 있으므로 실패이며, 시간 적분 성공으로 인정하지 않는다.
원본 V1.0.9 FREE/V1.1.0 Python 비교는 NOT RUN. XML/C++ 실제 실행은 별도로 계속했다.
필요 조건: 허용된 네트워크 또는 CPython3.12 공유 런타임/stdlib 및 ABI호환 NumPy offline package.
재개: 새 출력 루트에서 `python tools/next_environment.py`, 이후 `tools/revalidate_python.py` 검토.
정확한 명령·exit·ABI log는 dependencies/environment/summary.json을 참조한다.
'''+scope)
    text_report('INTEGRATED_04_FINITE_ROTATION.md','''# 유한 회전 및 구조 검증

독립 기존 finite kernel은 SO(3) 지수 chart와 회전된 attachment point를 쓴다.
에너지의 chart Hessian은 대칭이지만 공간 torque Jacobian은 connection 항을 포함한다:
`F=-dE/d(delta)`, `J=-H-.5*skew(torque)`(각 회전 block).
일반 공간 Jacobian의 비대칭을 에너지 비보존 오류로 혼동하지 않았다.
기존60상태 실제 실행 PASS: energy FD1.92619e-11, spatial Jacobian FD6.05088e-11,
objectivity4.85723e-17, net moment4.16334e-17. invalid-input 의도적ERROR와 성공을 구분했다.
신규120상태 contact/cable kernel 및 실제 API kFactor/6DOF 검사 PASS,
전체 routed cable18DOF FD도 energy1.51464e-11/J9.49002e-11로 PASS.
원래 작은 회전 `s=du-h*(theta_l+theta_u)/2` 극한과 좌표 정의는 유지한다.
EB에서는 phi=dw/dx, SOFA y회전은 R_y(theta)e_x=(cos(theta),0,-sin(theta))라
theta=-phi이다. 따라서 EB식 du+h*(phi_l+phi_u)/2와 같은 에너지다.
노드별 변환 T=diag(1,1,-1)에 대해 f_SOFA=T^T f_EB, K_SOFA=T^T K_EB T이며
회전 부호만 달라졌다는 설명을 실제 `beam.py`의 B행렬 및 quaternion 복원과 대조했다.

SOFA pure-end-moment **uncoupled BeamFEM**를 독립 circular-arc elastica와 비교했다.
theta=.004/.1/.5 rad, large21node 및 halfdt 모두 선언1% 오차 이내 PASS.
theta=.5 tip24.4931894386mm, 상대오차.000396260, 21node24.4859755502mm,
halfdt24.4931894390mm. 이 검사는 큰 회전 전단/필름/접촉 전체의 인증이 아니다.
별도 objective_connector/summary.json은 실제 유한 회전 연결의 로딩·적분·평형 결과를 기록한다.
작은 회전 coupled tip.009290642533mm, moderate tip4.475530251109mm,
halfdt4.475530251202mm 모두 평형 PASS. 이는 특정 연구 하중의2층 연결 검증이다.
최종 검토에서 postprocessor가 mode2에도 평면 slip 식을 쓰던 문제를 발견했다.
역사 raw/metrics는 보존하고 정확한 `t_lower dot (p_u+R_u*a_u-p_l-R_l*a_l)`로 별도 재분석했다.
moderate 최종 exact slip.003496672754612mm, C++ recorder와 전시점 최대 차이1.04e-17mm.
평형·처짐 판정은 이 지표 수정으로 바뀌지 않는다. 이전 finite raw의 평면 slip 숫자는 성능에서 제외한다.
유한 회전 마찰은 구현하지 않았으며 planar slider에 큰 회전 결과를 섞지 않았다.
직접적인 공간회전 변환 검사는 kernel에서 수행했으며 전체 고정중력/경계 장면의 임의 회전은 NOT RUN.
'''+measured_table(finite)+scope)
    text_report('INTEGRATED_05_MULTILAYER.md','''# 100mm 다층 SOFA

실제2→4→8층 Rigid3 BeamFEM+LayerNetwork 장면, 모든 층 독립 DOF/클램프/동일 총 하중.
기존 등가 원형 A≈.732233mm², I=8*.4³/12mm⁴, E=250, nu=.32를 유지한다.
A와 I를 혼동해 사각 A=3.2mm² 모델의 강성비와 동일 조건이라고 해석하지 않는다.

추가 재료 비교: 2/4/8층 각층 단면 동일. 2층k0/k100 tip.0156281995228/.00929173481387mm
(비1.681946),4층 .00781409989937/.00237996738245(비약3.2833).
8층 coarse는 .00390704996693/.000603567654830이나 halfdt/mesh/18s에서
잔차 기준 FAIL이므로 수렴된 성능으로 인정하지 않고 optimizer eligibility에서 제외했다.
LU→LDL 변경, 시간 연장, 독립 static seed도8층 승인을 만들지 못했다.
2층 추가 mesh/halfdt/repeat/18s 및4층 후보 수렴은 별도 실제 실행했다.

전체 초기 다층 suite73/83 checks: 모든 실행 성공과 물리 평형 성공은 다르다.
equal-total-material은 원형 bar 단면 합 일정의 별도 연구(반지름 sqrt(2/L), I~(2/L)^2)이며
총 필름 두께/stack height 고정과 다르다. cold4/8층 실패를 보존했다.
독립 EB seed 초기화는 rest_position을 원래 상태로 유지한 후 실제SOFA 적분했으며
그 결과를 cold transient 수렴으로 둔갑시키지 않았다.

미끄럼 aliasing: 2층 coarse nodal1.018e-7mm vs fine3.363e-7mm.
별도 Hermite EB reconstruction으로 coarse3.36209e-7/fine3.36300e-7mm.
보간 극값을 직접 측정값이라고 부르지 않고 기존 nodal 지표도 보존했다.
모든 상태가 아니라 stride20 sampled trajectory이며 최고 회전/속도의 sampling 한계가 있다.
'''+measured_table(multi['records'])+'\n\n## 별도 정적 seed 실행\n\n'+measured_table(warm)+scope)
    text_report('INTEGRATED_06_TENDON.md','''# SOFA routed tendon

**연구용 구현/초기 선언 검사18/18 PASS; 강화 잔차 감사에서 일부 FAIL, 실제 와이어 성능 EXPERIMENTAL.**
초기 F_ref에1e-6 하한이 있어 tiny cable load의 상대 잔차를 과소평가했다.
최종 분석기는 nonzero-load floor를 제거했다(하중/tolerance 완화 아님).
small T1e-6 tail residual.00871474 및 length control.00585318로1e-3 기준 FAIL.
T1e-5 tail.000842208, T1e-4 .000142102는 강화 기준 PASS.
과거 표의 PASS는 당시 정의이며 최종 물리 승인에는 residual_audit/strict_residual_retry가 우선한다.
18s 독립 재실행도 별도 기록하며 초기 결과/CSV를 덮어쓰지 않는다.
SoftRobots 플러그인 로딩은 실제 성공했지만 CableConstraint는 Vec3/Vec2 계열이므로
Rigid3 재료 guide에 맞는 독립 RoutedCable을 구현했다. SoftRobots 케이블 결과로 주장하지 않는다.
`a_i=p_i+R_i*(0,0,offsetZ)`, `ell=sum norm(a_(i+1)-a_i)`.
prescribed tension E=T*ell, 수축 E=.5kc max(ell-rest+shortening,0)².
힘·torque·consistent spatial tangent는 정확한 에너지 미분이며 전체 cable FD를 통과했다.
T0, 증가, small-moment EB limit, 길이 제어, 해제 복원을 실제 실행했다.
guide offset−.2mm는 연구 가정. 접촉면 와이어 마찰/실제 actuator stroke/motor energy는 NOT RUN.
release는 transient EXPERIMENTAL이며 강성비에 사용하지 않는다.
'''+measured_table(tendon['records'],strict['tendon'])+'\n\n## 강화 잔차 및18s 재실행\n\n'+measured_table(strict_retry)+scope)
    text_report('INTEGRATED_07_JAMMING.md','''# Prescribed pressure 마찰 연구

**독립 slider·초기 SOFA 선언 검사20/20 PASS; wire_jamming 강화 잔차 FAIL, 실제 진공 재밍 EXPERIMENTAL.**
순수 pressure/force 실험은 강화 잔차도 PASS. wire_jamming은 작은 구동력 정규화의
floor를 제거하면 tail residual.001457>1e-3로 FAIL이며 성능값으로 승인하지 않는다.
N_i=p*A_i, Fcap=mu*N_i, elastic-perfectly-plastic return mapping.
tributary area는 연결점 사이를 분할한 width8mm × length100mm의 가정이다.
정지/운동 mu동일, solver force/tangent 조회는 history를 바꾸지 않고 AnimateEnd에만 commit한다.
단일 slider cycle work balance5.55e-17, 소산 비음성·단조성 PASS.
pressure0 FREE 일치, high-pressure stick은 k1 탄성 결과와 일치, p/mu 변화,
30s ON/OFF/하중 cycle과 tendon 결합을 실행했다.
component energy는 전체 BeamFEM 에너지/구동 일/감쇠를 포함하지 않는다.
전체 closed-system energy audit, 분리된 정지/동마찰계수, 접촉 opening/법선압력 solve,
실제 PET mu·vacuum leakage·손상·실측 이력은 NOT RUN이다.
normal_k는 별도 작은 평면 bilateral confinement이지 vacuum solver가 아니다.
현재 cap=mu*p*A라서 마찰 제한만 관측하면 mu와 p를 독립 식별할 수 없다(수학적 모델 한계).
'''+measured_table(friction['records'],strict['friction'])+scope)
    text_report('INTEGRATED_08_GRASPING.md','''# 접촉 및 파지 gate

**접촉 kernel/고정 물체 응답 PASS; 자유 물체 hold FAIL; 안정 파지 NOT RUN.**
Sphere/infinite local-y cylinder/box signed-distance penalty 에너지와 힘·토크·Jacobian을 검증했다.
고정 물체3종에서 접촉 발생과 실제 변형을 확인했지만 물체 고정으로 파지가 증명되지는 않는다.
현재 평면 y=0에서 sphere/cylinder가 같은 결과인 것은 예상되며 유한 cylinder endcap 검증이 아니다.
충돌 검출과 힘 응답은 추가 C++ 시험에서 각각 독립적으로 검사했다.

자유 물체 negative control:6s, object F=1e-7, 이동1.4409853133441768mm,
사전 정의 hold limit.001mm를 초과하여 FAIL. 정적 평형도 미달한다.
접촉 node sampling, box edge 비매끄러움, 물체 tangential friction 부재,
3방향 외력 envelope/다중 핑거 enclosure 부재로 안정 파지·지지 외력은 인정하지 않는다.
`tools/integrated_grasp_gate.py`가 고정 물체를 성능에서 제외하고 full grasp optimizer를 차단한다.
작은 하중에서 움직임이 작아도 자의적으로 성공 판정을 내리지 않는다.
'''+measured_table(contact['records'])+scope)
    candidate_lines=['|후보|층/연결점수|SOFA 강성비|재구성 미끄럼 mm|승인|','|---|---|---:|---:|---|']
    for row in candidates['candidates']:
        c=row['design']['config'];candidate_lines.append(f"|{row['design']['design_sha256'][:12]}|{c['layers']}/{len(c['connectors'])}|{row['actual_SOFA_stiffness_ratio']}|{row['actual_reconstructed_slip']}|{row['approved_for_scope']}|")
    text_report('INTEGRATED_09_OPTIMIZATION.md',f'''# 설계 탐색 및 승인 범위

**정적 EB 결정론적 grid30개 + SOFA Pareto 재검증; Optuna/통합 파지 최적화 BLOCKED.**
검증 완료 후보{approved}/{len(candidates['candidates'])}. 최적성은 이 discrete grid에 한정하며
실제 제작 최적 설계·전역 최적·진공 파지 최적이라고 주장하지 않는다.
각 후보의 실행 로그/설정/모든 gate는 candidate_validation/<id>/decision.json에 있다.
기존2목적 stiffness/slip와 별도 complexity 목적을 분리해서 해석한다.
k100은 이 grid 상한이며 k포화의 전역 증거는 아니다. 저k와10→100 차이는 study전체표에 남는다.
조건수는 혼합 mm/rad 좌표의 raw 행렬값으로 차원독립 안정성 인증에 사용하지 않는다.

별도 independent EB FEM +/-10% OAT15개 민감도 연구(실측 불확실성 분포 아님):
4층k100의 h(centroid gap) 변화에 강성비2.95890..3.60769,
A변화3.11745..3.43991, I변화3.13171..3.45842,
E변화3.28137..3.28393, k변화3.28123..3.28381이다.
고k 부근 k보다 geometry/EA/EI에 민감하며 독립 A/I 변경은 실제 단면 형상의 제조가능성 보장이 아니다.

'''+ '\n'.join(candidate_lines)+'''

물성/압력/레이어두께/와이어경로/파지외력을 동시에 최적화하는 단계는 BLOCKED:
자유 물체 파지 gate와 실측 범위가 아직 확보되지 않았다. 독립 모듈 연구를 통합 파지 인증으로 합산하지 않는다.
실패 trial에 가짜 목적값을 주지 않았고 모든 정적 seed/solver 재시도는 별도 기록이다.
'''+scope)
    summary=f'''# ReGrip 통합 개발 최종 실행 보고

기준 commit `ba8e0e515bd9c06c75e764dfe1dc09670e614c77`.
브랜치 `development/regrip-integrated-system`; 보고서 생성 시 code commit `{current}`.
문서/manifest commit SHA는 `git log -1 --format=%H`로 확인(자기참조 hash는 넣지 않음).
원격 push/이력 재작성 없음. 이전 검증 branch/main/골든 보존.

## 결과

|대상|판정|새 실행 근거|
|---|---|---|
|이전 NEXT manifest 무결성|PASS|불일치0, start.json|
|기존600시점 FREE 회귀|PASS|독립2회; 처짐 max error1.38778e-16, 속도1.41553e-14, 원래 tolerance1e-10+1e-6abs(golden)|
|기존 C++/finite kernel|PASS|600상태/60상태 실제 실행|
|기존45 gate|이전 PASS 유지|무결성 확인; 이번 전체45개 재실행 아님|
|기존 automation/guard|PASS|20/11개 새 실행|
|신규 Python 계약 검사|PASS|8개 실제 실행, skip0|
|메모리 원인 재현|PASS|MappingGraph ownership cycle, 최소장면4/4 retained|
|동일 process plateau|FAIL|live heap 증가 지속; 엔진 미수정|
|C++ 신규 수학/API|PASS|120상태+전체 cable FD+ASan/UBSan, LSan제외|
|100mm2/4층|PASS(선언 범위)|동일 조건 SOFA/EB 비교 및 후보 수렴|
|8층 수렴|FAIL|coarse실행과 달리 halfdt/mesh/18s 잔차 미달|
|와이어/압력 마찰|EXPERIMENTAL / 일부 FAIL|nonzero load 잔차 강화 후 tiny tension/length/wire-pressure 평형 미달|
|고정 물체 접촉|PASS(선언 범위)|3형상 검출/응답|
|자유 물체 파지|FAIL|1.440985mm 이동 >.001mm hold gate|
|Optuna/SofaPython3|BLOCKED|DNS/캐시부재, libpython3.12없음; Optuna0 trial|
|결정론적 grid|PASS|30완료/주입실패1, workflow7/7|
|SOFA Pareto 후보|{approved}/{len(candidates['candidates'])} 승인|원래 위치/halfdt/mesh/repeat/+6s|
|전체 파지 설계 최적화|BLOCKED|grasp gate 미달, 조작한 성능값 없음|

인수인계 archive member56개도 실제 byte-for-byte 재검사 PASS(originals.json).
수정 전 guard 실패와 수정 후 ASan/UBSan 및 실제 SOFA3장면 회귀 PASS.
별도 유한 회전 slip 후처리 식 수정은 C++ recorder 전시점 대조로 검증했다.
tiny cable load 잔차의1e-6 하한도 제거했다. 초기18/18,20/20 선언 검사 결과를
최종 물리 인증으로 그대로 재사용하지 않으며 residual_audit가 우선한다.

## 측정과 한계

100mm2층 FREE/ON .0156281995228/.00929173481387mm, 비1.681946.
4층 FREE/ON .00781409989937/.00237996738245mm(재료량 증가 비교).
T1e-4 routed tip .00468096413837mm; high-pressure slider .0100308675154mm.
순수 moment theta=.5rad BeamFEM tip24.4931894386mm는 별도 구조 실험이며
30mm 작은 평면 모델의 검증 범위 확장이 아니다.
실측 PET/압력/마찰/장비 데이터는0건이다. independent FEM, 수학 검증, SOFA 출력,
가정된 파라미터를 각 상세 보고서에서 구분했다.

수정 파일은 `git diff --stat ba8e0e5..HEAD`와 manifest 참조.
신규 `models/integrated/`, `diagnostics/integrated*`, `tools/integrated_*`, tests만 추가했다.
초기 컴파일 실패, profiling timeout,8층 실패, invalid-input 수정 전후 증거를 보존했다.
별도 입력 검사는 수정 전 stride0 SIGFPE(exit−8), NaN contact 입력2개 미거부를 재현했다.
v2에서 zero-stride guard, NaN 검사, finite+planar-confinement 금지, 미선택 노드 회전범위 검사,
부분 CSV 덮어쓰기 금지 및 엄격한 JSON 타입 검사를 추가했다. 수정 전 결과는 v1 manifest에 귀속한다.

## 재현 환경/명령

Ubuntu22.04.5/GCC11.4/CMake3.22.1/SOFA26.06,
분석 Python `/home/ubuntu/miniconda3/envs/robot_ws/bin/python`3.10.20.
전체 명령 순서는 `INTEGRATED_NEXT_TASKS.md`와 각 raw command.json에 있다.
설정에는 모델/하중/경계/mesh/dt/solver, 결과에는 git dirty/source/binary 해시를 남긴다.
v1 결과는 v1 manifest에 귀속하며 입력 guard 수정 뒤 v2와 자동 혼합하지 않는다.
작은 증거/CSV/비교그림은 integrated_evidence, 큰 raw/빌드/SQLite는 ignored results에 보존한다.

## 남은 개발

엔진 MappingGraph lifetime 패치의 외부 버전 검증,8층 수치 정밀도/잔차 원인,
Optuna/CPython offline 의존성, 물체 마찰/다방향 enclosure/외력검증,
접촉 mesh/dt 수렴, 정상압력·필름 개구 모델, 실제 물성/마찰/케이블 계측이 필요하다.
현재 시스템은 연구용 기반이며 사용자 최종 요구의 검증된 통합 실물 그리퍼는 **미완료**다.
검증되지 않은 grasp optimizer를 실행해 수치를 만드는 대신 eligibility gate로 차단했다.
'''
    text_report('INTEGRATED_FINAL_REPORT.md',summary+scope)
    text_report('INTEGRATED_CURRENT_STATUS.md',summary.split('## 측정과 한계')[0]+'''
진행 상태/실패 목록은 INTEGRATED_FINAL_REPORT 및 INTEGRATED_01..09 참조.
raw 출력은 덮어쓰지 않는다. 작업 종료 후 잔류 SOFA child가 없는지 확인한다.
''')
    text_report('INTEGRATED_NEXT_TASKS.md','''# 재개 우선순위 및 명령

1. MappingGraph 공유소유권 cycle을 외부 SOFA 이슈/수정 SDK에서 해결하고 최소60000step 재검증.
   기존SDK를 직접 고치거나 private member를 해제하지 않는다. bounded process 우회 유지.
2.8층 residual floor 원인 규명(물리조건/tolerance 고정), force balance·solver conditioning 분석.
   기존 실패 raw를 보존하고 새 campaign root에서 독립 재시도.
3.허용된 네트워크/offline wheels가 생기면 Optuna/CPython3.12 격리 설치.
   실제 Optuna3+24 및 원본 Python 장면은 여전히 해야 함.
4.현재 point-contact 연구를 continuous surface sampling/물체 마찰/기하학적 enclosure로 확장,
   자유 물체3방향 외력, 반복/수렴/해제까지 통과하기 전 grasp optimization 금지.
5.실측 PET E/두께/마찰/압력분포/와이어 경로 입력 후 불확실성 분석.

## 재현 명령(새 출력 루트 필수)

```bash
cd /home/ubuntu/LHJ/ReGrip
export PYTHONPATH=.:tools
export OPENBLAS_NUM_THREADS=1
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
export REGRIP_INTEGRATED_OUT=$PWD/results/integrated_new_campaign
$PY tools/integrated_build.py --logs "$REGRIP_INTEGRATED_OUT/build"
$PY tools/integrated_build.py --sanitize --logs "$REGRIP_INTEGRATED_OUT/build_asan"
cmake -S diagnostics/integrated -B build/integrated_20261115/diagnostics -DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00
cmake --build build/integrated_20261115/diagnostics -j2
$PY tools/integrated_memory.py
$PY tools/integrated_minimal.py
$PY tools/integrated_suites.py multilayer
$PY tools/integrated_suites.py tendon
$PY tools/integrated_suites.py friction
$PY tools/integrated_suites.py contact
$PY tools/integrated_grasp_gate.py
$PY tools/integrated_finite.py
$PY tools/integrated_objective.py
$PY tools/integrated_finite_metrics.py
$PY tools/integrated_residual_audit.py
$PY tools/integrated_residual_retry.py
$PY tools/integrated_sensitivity.py
$PY tools/integrated_additional.py
$PY tools/integrated_search.py --out "$REGRIP_INTEGRATED_OUT/search_hermite" --metric hermite --limit 3 --inject-failure
$PY tools/integrated_search.py --out "$REGRIP_INTEGRATED_OUT/search_hermite" --metric hermite --limit 30 --inject-failure
$PY tools/integrated_search_checks.py
$PY tools/integrated_candidates.py
$PY -m unittest discover -s tests -p test_integrated_python.py
```

search CLI의 --metric hermite와 새 SQLite 경로를 사용한다. v1 결과를 v2study에 섞지 않는다.
위 명령은 원본 v1의 재실행이 아니라 현재 guard-hardening 소스의 새 campaign이다.
동일 process plateau/8층/자유 파지 실패가 재현되면 성공으로 만들기 위해 허용오차를 바꾸지 않는다.
''')
    progress=REPORTS/'INTEGRATED_PROGRESS.md'
    previous=progress.read_text().split('\n## 통합 실행 종결 기록')[0]
    progress.write_text(previous+'\n## 통합 실행 종결 기록\n\n'+summary.split('## 결과')[1].split('## 측정과 한계')[0]+'\n상세 명령/실패/재개점은 INTEGRATED_01..09 및 FINAL/NEXT_TASKS에 보존했다.\n')
    sources={str(p.relative_to(ROOT)):sha(p) for folder in ['models/integrated','diagnostics/integrated','diagnostics/integrated_extra'] for p in (ROOT/folder).rglob('*') if p.is_file()}
    for pattern in ['tools/integrated_*.py','tests/test_integrated*']:
        sources.update({str(p.relative_to(ROOT)):sha(p) for p in ROOT.glob(pattern) if p.is_file()})
    for path in ['README.md','.gitignore','scenes/integrated/minimal_mapping_graph.scn','models/finite_rotation/Kernel.h','plugin/src/TangentialRigidForceField.cpp']:
        sources[path]=sha(ROOT/path)
    binaries={str(p.relative_to(ROOT)):sha(p) for p in [BUILD/'plugin/libReGripIntegrated.so',BUILD/'archive_v1/libReGripIntegrated.so',BUILD/'diagnostics/integrated_driver',BUILD/'extra/test_integrated_extra',BUILD/'extra/test_integrated_invalid'] if p.is_file()}
    reports={str(p.relative_to(ROOT)):sha(p) for p in REPORTS.glob('INTEGRATED_*.md')}
    small={str(p.relative_to(ROOT)):sha(p) for p in EVIDENCE.iterdir() if p.is_file()}
    write_json(REPORTS/'INTEGRATED_EVIDENCE_MANIFEST.json',dict(start_commit='ba8e0e515bd9c06c75e764dfe1dc09670e614c77',code_commit=current,
        branch='development/regrip-integrated-system',source_sha256=sources,binary_sha256=binaries,evidence_sha256=small,report_sha256=reports,
        raw_evidence=evidence_map,raw_root=str(OUT),binary_manifests=['reports/integrated_evidence/build_v1__manifest.json','reports/integrated_evidence/build_v2__manifest.json'],
        scope='historical v1 trial artifacts remain separately bound; report generation does not reclassify failures'))
    print('Reports generated; approved',approved,'/',len(candidates['candidates']))

if __name__=='__main__':main()
