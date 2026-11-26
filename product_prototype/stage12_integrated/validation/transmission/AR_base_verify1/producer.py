"""Reimport actual finite external mount and test retained-contact failure modes."""
import sys,json,shutil
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,translate,volume,solid_count
from OCP.BRepCheck import BRepCheck_Analyzer
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'validation/transmission/AR_base_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAR_base2/summary.json';d=json.loads(src.read_text());refs=d['part_references']
assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
dump(out/'inputs.json',dict(candidate=ref(src),parts=refs,producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py')]))
p={n:read(REPO/r['path']) for n,r in refs.items()};checks={'input_hashes':True,'nominal_interference':not d['interferences']};meshes=[]
for n in d['changed']:
 s=p[n];checks[n+'_valid_single_solid']=BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
 v=[];edges={}
 for line in (src.parent/(n+'.stl')).read_text().splitlines():
  if line.strip().startswith('vertex'):v.append(tuple(round(float(x),9) for x in line.split()[1:]))
 for j in range(0,len(v),3):
  a,b,c=v[j:j+3]
  for x,y in ((a,b),(b,c),(c,a)):
   k=tuple(sorted((x,y)));edges[k]=edges.get(k,0)+1
 checks[n+'_closed_STL']=bool(edges) and all(x==2 for x in edges.values())
rows=[];adapter=p['PALM_BASE_ADAPTER'];base=p['EXTERNAL_BASE'];bolts=[p[f'BASE_BOLT_{i}'] for i in range(4)]
for axis in range(3):
 for sign in (-1,1):
  ds=(.25,.261) if axis<2 else ((.09,.101) if sign>0 else (0,.001))
  samples=[]
  for dist in ds:
   shift=[0,0,0];shift[axis]=sign*dist;s=translate(adapter,*shift)
   samples.append(dict(displacement_mm=shift,base_mm3=common(s,base),bolts_mm3=[common(s,b) for b in bolts]))
  ok=samples[0]['base_mm3']+sum(samples[0]['bolts_mm3'])<1e-8 and samples[1]['base_mm3']+sum(samples[1]['bolts_mm3'])>1e-8
  checks[f'adapter_stop_{axis}_{sign}']=ok;rows.append(dict(axis=axis,sign=sign,samples=samples,passed=ok))
# Crucial distinct link: can the smooth bolt pull out of the smooth nut?
thread=[]
for i,b in enumerate(bolts):
 v=common(translate(b,0,0,1),p[f'BASE_NUT_{i}']);thread.append(dict(bolt=i,upward_shift_mm=1,nut_intersection_mm3=v))
checks['actual_bolt_nut_uplift_retention']=all(r['nut_intersection_mm3']>1e-8 for r in thread)
r=dict(status='EXTERNAL_MOUNT_NOT_QUALIFIED',candidate=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),checks=checks,adapter_stops=rows,bolt_nut_uplift=thread,actual_capacity_qualified=False,whole_system_release=False,limitations=['Adapter stops with bolts held fixed do not prove bolts are retained to base','Smooth nut bores cannot replace actual thread flank engagement','Base lower face is an explicit unqualified machine boundary, not hidden fixed Palm nodes','No strength, material, preload, loaded6DOF equilibrium or continuous assembly/tool certification'])
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],checks=checks,bolt_nut_uplift=thread)));raise SystemExit(2)
