import json,hashlib,pathlib,subprocess,math,shutil,time
R=pathlib.Path.cwd();B=R/'product_prototype/stage12_integrated';HEAD='ee1619871d20dd9199b234dedf755df334f1828d'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':str(p.relative_to(R)),'SHA256':sha(p)}
def load(p):return json.loads(p.read_text())
def dump(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,allow_nan=False)+'\n')
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==HEAD
before=load(B/'runtime/goal_authorized_20261127_7/checkpoint_before6.json');old=set(before['preexisting_untracked']);assert before['HEAD']==HEAD
assert not(B/'runtime/STOP').exists();pins={p:sha(R/p)==h for p,h in load(B/'runtime/goal_authorized_20261127_7/ledger.json')['source_pins'].items()};assert all(pins.values());q=load(B/'INTEGRATED_TASKS.json');assert not any(t['status']=='RUNNING' for t in q['tasks']);assert load(B/'NEXT_TASK.json')['next']['id']=='goal_primary_gravity_port_interfaces'
executions=[load(p) for p in sorted((B/'validation/integrated/primary_cycle7').glob('*_execution.json'))];assert len(executions)==43 and all(e['reaped'] and not e['timeout'] for e in executions)
# Match actual live analysis commands, not unrelated external manager or shell strings.
analyses={e['command'][1] for e in executions};live=[]
for line in subprocess.check_output(['ps','-eo','pid=,comm=,args='],text=True).splitlines():
 fields=line.strip().split(None,2)
 if len(fields)==3 and fields[1].startswith('python') and any((' '+p+' ') in (' '+fields[2]+' ') for p in analyses):live.append(fields)
assert not live,live
release=B/'validation/integrated/primaryP1_release10/summary.json';assert load(release)['status']=='INTEGRATED_NOT_QUALIFIED' and len(load(release)['errors'])==24
candidate=B/'cad/exports/primaryP1_fixture15/summary.json';cad=load(candidate);assert cad['parts']==78 and all(sha(R/r['path'])==r['SHA256'] for r in cad['part_references'].values());g=B/'models/primary_system_gate_state8.json';assert len(load(g)['gates'])==22 and all(r['status']=='UNQUALIFIED' for r in load(g)['gates'])
# Terminal handoff records the extra final audit separately from the immutable main42-child result.
close=B/'validation/integrated/primaryP1_cycle7_closeout';close.mkdir(exist_ok=False);shutil.copyfile(__file__,close/'producer.py')
checks={'HEAD_matches':True,'source_pins_unchanged':all(pins.values()),'all78actualCAD_hashes_unchanged':True,'all22system_gates_UNQUALIFIED':True,'queue_no_RUNNING':True,'analysis_children_reaped':True,'live_owned_analysis_children_zero':not live,'runtime_STOP_absent':True,'final_actual_release_NOT_QUALIFIED':True,'prior_untracked_files_still_present':all((R/p).is_file() for p in old),'no_staged_files':not subprocess.check_output(['git','diff','--cached','--name-only'],text=True).strip()};assert all(checks.values())
r={'status':'ACTUAL_P1_CYCLE7_EXACT_BYTE_HANDOFF_READY_NOT_RELEASE','task_id':'goal_primary_gravity_loaded_chain','starting_HEAD':HEAD,'candidate_reference':ref(candidate),'main_result':ref(B/'validation/integrated/primary_cycle7/summary.json'),'final_release':ref(release),'final_release_execution':ref(B/'validation/integrated/primary_cycle7/release10_execution.json'),'system_gate_state':ref(g),'primary_state':ref(B/'PRIMARY_PRODUCT.json'),'NEXT_TASK':ref(B/'NEXT_TASK.json'),'checks':checks,'source_pins_unchanged':pins,'recorded_children_reaped':len(executions),'recorded_child_seconds':sum(e['elapsed_s'] for e in executions),'timeouts':0,'owned_analysis_children_running':0,'running_queue_tasks':0,'newly_qualified_system_gate_ids':[],'remaining_system_gate_count':22,'whole_system_release':False,'global_energy_qualified':False,'Stage3_authorized':False,'hardware_status':'HARDWARE_NOT_MEASURED','save_status':'PENDING_SUPERVISOR_EXACT_SAVE','next_task_id':'goal_primary_gravity_port_interfaces','producer':ref(close/'producer.py')};dump(close/'summary.json',r)
current=load(B/'CURRENT_CANDIDATE.json');current['latest_closeout']=ref(close/'summary.json');dump(B/'CURRENT_CANDIDATE.json',current)
p=B/'CHECKPOINT.md';s=p.read_text();s=s.replace('closeout includes the subsequent final release audit and final exact count.','closeout includes the subsequent final release audit:43children reaped,\n407.094633childseconds total,0timeouts,0ownedchildren/0RUNNINGtasks.');p.write_text(s)
# Exact delta is from the external Supervisor's actual session-start snapshot.
changed=set(subprocess.check_output(['git','diff','HEAD','--name-only','--no-renames','-z']).decode().split('\0'))-{''};untracked=set(subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z']).decode().split('\0'))-{''};names=sorted(changed|(untracked-old));assert not(set(names)&old)
records=[]
for name in names:
 p=R/name;assert name.startswith('product_prototype/stage12_integrated/') and '/runtime/' not in name;assert p.is_file() and p.stat().st_size<50000000 and not p.is_symlink();assert p.name not in ('surface.csv','detector.csv','response_rows.csv','layer_pairs.csv');records.append(ref(p))
result_paths=['validation/integrated/primary_cycle7/summary.json','validation/integrated/primaryP1_cycle7_closeout/summary.json','validation/integrated/primaryP1_gravity_failures1/summary.json','validation/finger/primaryP1_gravity_cat_verify1/summary.json','validation/finger/primaryP1_gravity_cat_demand_verify1/summary.json','validation/finger/primaryP1_gravity_controls1/summary.json','validation/transmission/primaryP1_gravity_cat_ports1/summary.json','validation/transmission/primaryP1_gravity_cat_demand_ports2/summary.json','validation/integrated/primaryP1_gravity_cat_massload1/summary.json','validation/integrated/primaryP1_gravity_joint5_1/summary.json','validation/integrated/primaryP1_gravity_joint_verify1/summary.json','validation/integrated/primaryP1_gravity_wire_verify2/summary.json','validation/integrated/primaryP1_gravity_cat_loaded1/summary.json','validation/integrated/primaryP1_gravity_cat_demand_loaded1/summary.json','validation/integrated/primaryP1_release10/summary.json']
results=[ref(B/p) for p in result_paths];assert all(r in records for r in results)
def finite(v):
 if isinstance(v,float):return math.isfinite(v)
 if isinstance(v,list):return all(finite(a) for a in v)
 if isinstance(v,dict):return all(finite(a) for a in v.values())
 return True
assert all(isinstance(load(R/r['path']).get('status'),str) and finite(load(R/r['path'])) for r in results)
actual=[p for p in names if '/scripts/' in p or p.endswith('primary_system_gate_state8.json')]+[r['path'] for row in load(B/'validation/integrated/primaryP1_gravity_wire_verify2/summary.json')['rows'] for r in (row['wire_STEP'],row['wire_STL'])];assert len(actual)==len(set(actual)) and all(p in names for p in actual)
request={'expected_HEAD':HEAD,'message':'Validate same P1 gravity-loaded Finger, free swivel and massive cable; verify actual loaded solids and paired loads; retain release blockers','files':records,'results':results,'engineering_progress':{'category':'ACTUAL_PRODUCT_VALIDATION','task_id':'goal_primary_gravity_loaded_chain','mechanism':'Same78partP1: actualCADmassslices/conservativegravity,freeSwivel and massive drum-tangent cable. Independently verify matched-loadRod/contact/string states,newloadedWIREsolids,17%higherconditionaltorque,pairedRoot/Motorwrenches and newGroundjoint; preserve wrongfirstTmetadata/otherfailures and all22unqualifiedgates.','system_gate_ids':['physical_mass_inertia','continuous_load_path','root_palm_strength','numerical_convergence','cad_model_match','changed_stage1_revalidation','qualified_worst_case','motor_alignment_reactions'],'actual_change_files':actual,'candidate_reference':ref(candidate),'next_task_id':'goal_primary_gravity_port_interfaces','strategy_change':True}}
assert len(request['message'])<=160 and '\n' not in request['message'];destination=B/'runtime/goal_authorized_20261127_7/save_request6.json';assert not destination.exists();dump(destination,request)
# Last byte check, no Git staging/commit or supervisor import/execution.
assert all(sha(R/r['path'])==r['SHA256'] for r in records);assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==HEAD
print(json.dumps({'save_request':str(destination.relative_to(R)),'files':len(records),'results':len(results),'total_file_bytes':sum((R/r['path']).stat().st_size for r in records),'children_reaped':43,'child_seconds':r['recorded_child_seconds'],'checks':checks,'source_pins_unchanged':True}))
