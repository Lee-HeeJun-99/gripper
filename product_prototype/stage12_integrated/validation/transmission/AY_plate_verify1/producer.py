"""Imported direct plate geometry, contact footprint, service and connector falsification."""
import sys,json,shutil,itertools,math
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,translate,volume,solid_count,bounds,overlap,cyl,cut
from OCP.BRepCheck import BRepCheck_Analyzer
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'validation/transmission/AY_plate_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAY_direct_plate1/summary.json';d=json.loads(src.read_text());parent=json.loads((REPO/d['parent']['path']).read_text());assert sha(REPO/d['parent']['path'])==d['parent']['SHA256']
assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values())
dump(out/'inputs.json',dict(candidate=ref(src),parent=d['parent'],producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(ROOT/'scripts/baseline_registry.py')]))
p={n:read(REPO/r['path']) for n,r in d['part_references'].items()};checks={'input_hashes':True,'same_count':len(p)==254};meshes=[]
for n in d['changed']:
 s=p[n];checks[n+'_solid']=BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
 v=[];edges={};ori={};sv=0
 for line in (src.parent/(n+'.stl')).read_text().splitlines():
  if line.strip().startswith('vertex'):v.append(tuple(round(float(x),9) for x in line.split()[1:]))
 for j in range(0,len(v),3):
  a,b,c=v[j:j+3];sv+=a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0])
  for x,y in ((a,b),(b,c),(c,a)):
   k=tuple(sorted((x,y)));edges[k]=edges.get(k,0)+1;ori[k]=ori.get(k,0)+(1 if x<y else -1)
 ok=bool(edges) and all(x==2 for x in edges.values()) and all(x==0 for x in ori.values()) and sv>0;checks[n+'_mesh']=ok;meshes.append(dict(part=n,closed_oriented_positive=ok,volume_mm3=sv/6))
plate=p['PALM_BASE_ADAPTER'];palm=p['PALM'];bb={n:bounds(s) for n,s in p.items()};hits=[];pairs=0
for n,m in itertools.combinations(p,2):
 if n not in d['changed'] and m not in d['changed']:continue
 assert not (ROOT/'runtime/STOP').exists()
 if overlap(bb[n],bb[m]):
  pairs+=1;v=common(p[n],p[m])
  if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
checks['nominal_context_clear']=not hits
# Lift plate .001 into Palm: actual shared finite planar bearing footprint.
area=common(translate(plate,0,0,.001),palm)/.001;checks['finite_palm_bearing_footprint']=area>100
# Required negative control: misplaced plate penetrates Palm.
checks['misplaced_plate_rejected']=common(translate(plate,0,0,1),palm)>1e-8
stops=[];escapes=[];tools=[]
for i,(x,y) in enumerate(d['bolt_centers_mm']):
 b=p[f'PALM_BOLT_{i}'];n=p[f'PALM_NUT_{i}']
 stops.append(dict(bolt=i,head_down_into_palm_mm3=common(translate(b,0,0,-.2),palm),nut_up_into_plate_mm3=common(translate(n,0,0,.2),plate)))
 escapes.append(dict(bolt=i,upward_shift_mm=1,bolt_nut_intersection_mm3=common(translate(b,0,0,1),n)))
 # Finite round socket workspace envelope; actual tool and hex geometry unknown.
 tool=cyl(5,(x,y,-40),16.7);coll=[]
 for name,s in p.items():
  if name==f'PALM_NUT_{i}':continue
  if overlap(bounds(tool),bb[name]):
   v=common(tool,s)
   if v>1e-8:coll.append(dict(part=name,common_mm3=v))
 tools.append(dict(bolt=i,hits=coll))
checks['conditional_head_and_nut_stops']=all(r['head_down_into_palm_mm3']>1e-8 and r['nut_up_into_plate_mm3']>1e-8 for r in stops)
checks['sampled_socket_workspace']=all(not r['hits'] for r in tools)
old=read(REPO/parent['part_references']['PALM_BASE_ADAPTER']['path'])
# Three noncollinear axial connector points resist z,rx,ry only if retained.
# Transverse bearing after clearance additionally needed for x,y,rz; no zero-gap/full wrench closure claim.
r=dict(status='DIRECT_PLATE_CAPACITY_NOT_QUALIFIED',candidate=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),checks=checks,meshes=meshes,interferences=hits,exact_intersection_pairs=pairs,palm_contact_area_mm2=area,plate_volume_mm3=volume(plate),old_adapter_volume_mm3=volume(old),geometric_volume_change_mm3=volume(plate)-volume(old),old_adapter_bounds_mm=bounds(old),plate_bounds_mm=bounds(plate),stops=stops,bolt_nut_uplift=escapes,socket_workspaces=tools,actual_thread_retention_demonstrated=all(r['bolt_nut_intersection_mm3']>1e-8 for r in escapes),six_DOF_capacity_qualified=False,whole_system_release=False,limitations=['Smooth bolt/nut bores allow axial escape: actual thread connector/rating still required','Axial three-point bearing alone lacks x,y,rz restraint; shank clearance .21mm precludes zero-motion claim','Finite external plate lower face and four machine holes declared; machine fasteners/compliance absent','No loaded equilibrium, actual demands/material, strength/preload/friction/convergence','Static retained cable context only; no swept service/CCD/full installed assembly','Round socket envelope is a workspace contrast, not actual hex/thread/tool qualification'])
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],checks=checks,area=area,escape=escapes,hits=hits)));raise SystemExit(2)
