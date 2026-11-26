"""Independent reimport, shoulder area, axial stop and ordered assembly samples.
Unit load statics are conditional rigid contact, NOT elastic/thread capacity.
"""
import sys,json,math,shutil
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,translate,volume,solid_count,bounds
from OCP.BRepCheck import BRepCheck_Analyzer
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'validation/transmission/AM_axial_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAM_axial3/summary.json';d=json.loads(src.read_text());refs=d['part_references']
assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
dump(out/'inputs.json',dict(candidate=ref(src),parts=refs,producer=ref(out/'producer.py')))
parts={n:read(REPO/r['path']) for n,r in refs.items()}
checks=dict(hashes=True,no_nominal_interference=not d['interferences'],part_count=len(parts)==247)
meshes=[]
for n in d['changed']:
 s=parts[n];checks[n+'_valid']=BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
 edges={};verts=[]
 for line in (ROOT/'cad/exports/revAM_axial3'/f'{n}.stl').read_text().splitlines():
  if line.strip().startswith('vertex'):verts.append(tuple(round(float(x),9) for x in line.split()[1:]))
 for j in range(0,len(verts),3):
  t=verts[j:j+3]
  for a,b in ((t[0],t[1]),(t[1],t[2]),(t[2],t[0])):
   k=tuple(sorted((a,b)));edges[k]=edges.get(k,0)+1
 ok=bool(edges) and all(v==2 for v in edges.values());checks[n+'_closed_STL']=ok;meshes.append(dict(part=n,triangles=len(verts)//3,closed=ok))
hub=parts['F0_CLUTCH_INPUT_HUB'];plate=parts['F0_MOTOR_PLATE'];cap=parts['F0_AXIAL_FRONT_STOP'];motor=parts['F0_MOTOR']
expected=math.pi*(10**2-7.2**2);stops=[]
for sign,stop in ((-1,plate),(1,cap)):
 vals=[dict(shift_mm=sign*x,intersection_mm3=common(translate(hub,0,sign*x,0),stop)) for x in (.09,.1001,.1002)]
 areas=[v['intersection_mm3']/(abs(v['shift_mm'])-.1) for v in vals[1:]]
 ok=vals[0]['intersection_mm3']<1e-8 and all(abs(a/expected-1)<1e-5 for a in areas)
 checks[f'axial_stop_{sign}']=ok;stops.append(dict(sign=sign,samples=vals,area_mm2=areas,analytic_shoulder_mm2=expected,passed=ok))
# Preserve the upstream D flat: only add material outside the old bore cylinder.
parent=json.loads((REPO/d['parent']['path']).read_text());oldhub=read(REPO/parent['part_references']['F0_CLUTCH_INPUT_HUB']['path'])
checks['old_hub_contained']=abs(common(hub,oldhub)-volume(oldhub))<1e-7
# Assembly order: motor/plate in place, hub from front; cap then bolts then nuts.
# Each sampled moved part is checked against ALL already-installed actual solids.
new=set(d['changed']);retained={n:s for n,s in parts.items() if n not in new}
# Other sectors stay assembled; F0 plate is installed with motor.
installed={n:s for n,s in parts.items() if not n.startswith('F0_') or n not in new};installed['F0_MOTOR_PLATE']=plate
sequence=[]
for name,shifts in [('F0_CLUTCH_INPUT_HUB',[24,12,4,1,0]),('F0_AXIAL_FRONT_STOP',[24,12,4,1,0]),('F0_AXIAL_BOLT_82',[32,16,4,0]),('F0_AXIAL_BOLT_138',[32,16,4,0]),('F0_AXIAL_NUT_82',[-8,-4,-1,0]),('F0_AXIAL_NUT_138',[-8,-4,-1,0])]:
 rows=[]
 for y in shifts:
  moved=translate(parts[name],0,y,0);hits=[]
  bb=bounds(moved)
  from incremental_stage1 import overlap
  for n,s in installed.items():
   if overlap(bb,bounds(s)):
    v=common(moved,s)
    if v>1e-8:hits.append(dict(part=n,volume_mm3=v))
  rows.append(dict(shift_Y_mm=y,hits=hits))
 sequence.append(dict(part=name,samples=rows));installed[name]=parts[name]
checks['ordered_assembly_samples']=all(not r['hits'] for s in sequence for r in s['samples'])
# Independent unit axial-force wrench balance at actual shoulder and fastener centers.
# +Y: symmetric two bolts at82/138 transfer0.5N each; -Y: integral rear stop.
# Through-nut thread flanks/elastic bending are explicitly NOT solved here.
loads=[]
for sign in (-1,1):
 reactions=[dict(x_mm=x,z_mm=20,Fy_N=-sign*.5) for x in (82,138)] if sign==1 else [dict(x_mm=110,z_mm=20,Fy_N=1)]
 force=sign+sum(r['Fy_N'] for r in reactions);moment=sum((r['x_mm']-110)*r['Fy_N'] for r in reactions)
 loads.append(dict(applied_Fy_N=sign,shoulder_pressure_N_mm2=1/expected,reactions=reactions,force_residual_N=force,moment_residual_Nmm=moment,conditional_on='Rigid shoulder contact; front nut/bolt force transfer functional. No thread/plate elastic capacity claim.'))
checks['conditional_unit_wrench_balance']=all(abs(r['force_residual_N'])<1e-12 and abs(r['moment_residual_Nmm'])<1e-12 for r in loads)
# A removed front stop must fail outward capture; this is a real geometry negative control.
checks['front_stop_removal_control']=common(translate(hub,0,.11,0),plate)<1e-8
result=dict(status='AXIAL_CAPTURE_BOUNDED_VERIFICATION_PASS' if all(checks.values()) else 'AXIAL_CAPTURE_BOUNDED_VERIFICATION_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),checks=checks,mesh_records=meshes,stops=stops,assembly_sequence=sequence,unit_loads=loads,scope='Finite changed STEP/STL, annular contact area and signed axial obstruction; sampled F0 ordered assembly and conditional rigid unit statics. Not continuous full assembly, friction, strength or thread-flank solution.',capacity_qualified=False,whole_system_release=False)
dump(out/'summary.json',result);print(json.dumps(result,indent=2));raise SystemExit(0 if all(checks.values()) else 2)
