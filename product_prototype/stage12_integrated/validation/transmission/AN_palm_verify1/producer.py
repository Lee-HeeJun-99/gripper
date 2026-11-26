"""Independent reimport and finite attachment stops. No capacity certification."""
import sys,json,shutil,math
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,translate,rotate,bounds,overlap,volume,solid_count
from OCP.BRepCheck import BRepCheck_Analyzer
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'validation/transmission/AN_palm_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAN_palm2/summary.json';d=json.loads(src.read_text());refs=d['part_references']
assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
dump(out/'inputs.json',dict(candidate=ref(src),parts=refs,producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')]))
parts={n:read(REPO/r['path']) for n,r in refs.items()};checks={'input_hashes':True,'nominal_interference':not d['interferences'],'part_count':len(parts)==254};meshes=[]
for n in d['changed']:
 s=parts[n];checks[n+'_solid']=BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
 verts=[];edges={}
 for line in (ROOT/'cad/exports/revAN_palm2'/f'{n}.stl').read_text().splitlines():
  if line.strip().startswith('vertex'):verts.append(tuple(round(float(x),9) for x in line.split()[1:]))
 for j in range(0,len(verts),3):
  a,b,c=verts[j:j+3]
  for v,w in ((a,b),(b,c),(c,a)):
   k=tuple(sorted((v,w)));edges[k]=edges.get(k,0)+1
 ok=bool(edges) and all(v==2 for v in edges.values());checks[n+'_closed_STL']=ok;meshes.append(dict(part=n,triangles=len(verts)//3,closed=ok))
palm=parts['PALM'];base=parts['PALM_BASE_ADAPTER'];bolts=[parts[f'PALM_BOLT_{i}'] for i in range(3)]
stops=[]
for axis in (0,1,2):
 for sign in (-1,1):
  # Separate tests retain nominal hardware, move only Palm relative to adapter.
  distances=(.20,.211) if axis<2 else ((.09,.101) if sign>0 else (0,.001))
  rows=[]
  for dist in distances:
   v=[0,0,0];v[axis]=sign*dist;s=translate(palm,*v)
   rows.append(dict(displacement_mm=v,base_mm3=common(s,base),bolt_mm3=[common(s,b) for b in bolts]))
  clear=rows[0]['base_mm3']+sum(rows[0]['bolt_mm3']);hit=rows[1]['base_mm3']+sum(rows[1]['bolt_mm3'])
  ok=clear<1e-8 and hit>1e-8;checks[f'stop_axis{axis}_{sign}']=ok;stops.append(dict(axis=axis,sign=sign,samples=rows,passed=ok))
for sign in (-1,1):
 rows=[]
 for a in (.45,.50):
  s=rotate(palm,sign*a);rows.append(dict(angle_deg=sign*a,bolt_mm3=[common(s,b) for b in bolts]))
 ok=sum(rows[0]['bolt_mm3'])<1e-8 and sum(rows[1]['bolt_mm3'])>1e-8;checks[f'torsion_stop_{sign}']=ok;stops.append(dict(axis='Rz',sign=sign,samples=rows,passed=ok))
# Geometry negative control: removing bolt heads/shanks loses upward retention.
checks['removed_bolts_lose_uplift']=common(translate(palm,0,0,1),base)<1e-8
# Rank and signed wrench feasibility of ideal bilateral attachment directions.
# These directions are NOT simultaneously engaged contacts in the clearance assembly.
columns=[]
for x,y in d['bolt_centers_mm']:
 r=np.array([x,y,-9.5])
 for normal in ([1,0,0],[0,1,0],[0,0,1]):
  f=np.array(normal);w=np.r_[f,np.cross(r,f)/25]
  columns.extend([w,-w])
W=np.array(columns).T;rank=int(np.linalg.matrix_rank(W));checks['conditional_rank6']=rank==6
loads=[]
for axis in range(6):
 for sign in (-1,1):
  target=np.eye(6)[axis]*sign;res=linprog(np.ones(W.shape[1]),A_eq=W,b_eq=-target,bounds=(0,None),method='highs')
  err=float(np.max(np.abs(W@res.x+target))) if res.success else None
  loads.append(dict(axis=axis,sign=sign,solver_success=res.success,residual=err,coefficients=res.x.tolist() if res.success else None))
checks['conditional_12_wrench_balance']=all(x['solver_success'] and x['residual']<1e-10 for x in loads)
# Actual ordered insertion samples against all previously installed assembly constituents.
installed={n:s for n,s in parts.items() if n not in d['changed'] or n=='PALM'};sequence=[]
for name,shifts in [('PALM_BASE_ADAPTER',[-40,-20,-5,0])]+[(f'PALM_BOLT_{i}',[32,16,4,0]) for i in range(3)]+[(f'PALM_NUT_{i}',[-12,-6,-2,0]) for i in range(3)]:
 rows=[]
 for z in shifts:
  s=translate(parts[name],0,0,z);bb=bounds(s);hits=[]
  for n,t in installed.items():
   if overlap(bb,bounds(t)):
    v=common(s,t)
    if v>1e-8:hits.append(dict(part=n,intersection_mm3=v))
  rows.append(dict(shift_Z_mm=z,hits=hits))
 sequence.append(dict(part=name,samples=rows));installed[name]=parts[name]
checks['ordered_assembly_samples']=all(not r['hits'] for s in sequence for r in s['samples'])
r=dict(status='BOUNDED_ATTACHMENT_VERIFICATION_PASS' if all(checks.values()) else 'BOUNDED_ATTACHMENT_VERIFICATION_FAIL',candidate=ref(src),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),checks=checks,meshes=meshes,stops=stops,conditional_wrench_rank=rank,conditional_wrench_tests=loads,ordered_assembly_samples=sequence,actual_capacity_qualified=False,whole_system_release=False,limitations=['Rigid clearance stop tests and ideal bilateral wrench algebra are different conditions; not actual12direction elastic equilibrium','No rated threads/preload/material/strength; round nut envelopes not final tool-compatible hardware','External flange holes define interface only; machine/ground fasteners not yet implemented','Sampled insertion is not continuous assembly/tool path proof','Axial/radial play, bolt bending, Palm hole bearing and flange flexibility require loaded contact/mesh1%','No dynamic/global energy or system release'])
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],checks=checks)));raise SystemExit(0 if all(checks.values()) else 2)
