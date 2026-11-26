"""Reimport grooved nipple, sever neck and test actual cable-side fragment escape.
Geometry is not a fracture model. Positive post-cut stop rejects ideal disconnect.
"""
import sys,json,shutil,math
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,translate,rotate,bounds,overlap,volume,solid_count,box,cut
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'validation/overload/AP_fuse_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAP_tendon_fuse2/summary.json';d=json.loads(src.read_text());p=json.loads((REPO/d['parent']['path']).read_text())
assert sha(REPO/d['parent']['path'])==d['parent']['SHA256']
assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values())
dump(out/'inputs.json',dict(candidate=ref(src),parent=d['parent'],parts=d['part_references'],producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(ROOT/'scripts/baseline_registry.py')],acceptance=dict(intersection_mm3_max=1e-8,area_error_mm2_max=1e-6,escape='Cable-side fragment must not form another positive stop under +X tensile travel; samples cannot certify continuous escape')))
checks={'all_input_hashes':True,'nominal_interference':not d['interferences'],'part_count':len(d['part_references'])==254};rows=[]
for i in range(3):
 name=f'F{i}_DRUM_FACTORY_NIPPLE';s=rotate(read(REPO/d['part_references'][name]['path']),-120*i)
 checks[name+'_solid']=BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
 verts=[];edges={}
 for line in (src.parent/(name+'.stl')).read_text().splitlines():
  if line.strip().startswith('vertex'):verts.append(tuple(round(float(x),9) for x in line.split()[1:]))
 for j in range(0,len(verts),3):
  a,b,c=verts[j:j+3]
  for v,w in ((a,b),(b,c),(c,a)):
   k=tuple(sorted((v,w)));edges[k]=edges.get(k,0)+1
 checks[name+'_closed_STL']=bool(edges) and all(v==2 for v in edges.values())
 section=BRepAlgoAPI_Common(s,box(108.4995,-3,5, .001,6,8)).Shape();area=volume(section)/.001
 checks[name+'_neck_area']=abs(area-math.pi*(.5**2-.25**2))<1e-6
 old=rotate(read(REPO/p['part_references'][name]['path']),-120*i)
 checks[name+'_removed_volume']=abs(volume(old)-volume(s)-math.pi*(1.4**2-.5**2))<1e-6
 # Remove entire one-mm neck: optimistic complete fracture. Head and stem should separate.
 severed=cut(s,box(108,-3,5,1,6,8));fragment=BRepAlgoAPI_Common(severed,box(109,-3,5,4,6,8)).Shape()
 checks[name+'_severed_two_solids']=solid_count(severed)==2
 drum=rotate(read(REPO/d['part_references'][f'F{i}_DRUM']['path']),-120*i)
 cap=rotate(read(REPO/d['part_references'][f'F{i}_DRUM_NIPPLE_CAP']['path']),-120*i)
 samples=[]
 for dx in (0,.01,.1,.5,1.,2.,4.):
  assert not (ROOT/'runtime/STOP').exists()
  q=translate(fragment,dx,0,0)
  samples.append(dict(translation_X_mm=dx,drum_intersection_mm3=common(q,drum),cap_intersection_mm3=common(q,cap)))
 escape=all(max(v['drum_intersection_mm3'],v['cap_intersection_mm3'])<=1e-8 for v in samples)
 rows.append(dict(part=name,neck_area_mm2=area,nominal_mean_axial_MPa_per_N=1/area,fragment_bounds_mm=bounds(fragment),severed_solids=solid_count(severed),escape_samples=samples,escape_passed=escape,fracture_load_N=None,allowable_MPa=None))
# Preserve finite post-break collision as a physical rejection, distinct from CAD validity.
r=dict(status='FUSE_DISCONNECT_REJECTED' if not all(x['escape_passed'] for x in rows) else 'FUSE_DISCONNECT_UNQUALIFIED',candidate=ref(src),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),geometry_checks=checks,geometry_checks_passed=all(checks.values()),rows=rows,mechanism_qualified=False,whole_system_release=False,
 limitations=['Complete neck removal is an optimistic geometric contrast, not fracture simulation','Cable bore/swage internals unresolved: cable anchorage could also bypass neck','Recontact can transmit continuing motor work; previous ideal zero-torque disconnect energy cannot be assigned to this device','Unknown material, fracture scatter, drag, cable/piece inertia and released strain energy; no protected load maximum','Sampled fragment path is not continuous CCD, assembly tooling or global energy qualification'])
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],checks=checks,rows=rows)));raise SystemExit(2 if not all(x['escape_passed'] for x in rows) or not all(checks.values()) else 0)
