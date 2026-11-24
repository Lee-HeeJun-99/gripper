"""Same physical coupon in mm/kg/s; test no-contact equivalence before contact."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def flat(x):return ' '.join(format(float(v),'.17g') for v in np.asarray(x).ravel())
def read(p):return list(csv.DictReader(p.open()))
def transform(root,scale=1000.):
 changes=[]
 def put(n,key,value):
  before=n.get(key);n.set(key,value);changes.append(dict(component=n.tag,name=n.get('name'),field=key,before=before,after=value))
 for node in root.iter():
  if node.tag=='Node' and node.get('gravity') is not None:put(node,'gravity',flat(np.fromstring(node.get('gravity'),sep=' ')*scale))
  if node.tag in ('MechanicalObject','MeshTopology') and node.get('position') is not None:
   width=7 if node.get('template','').startswith('Rigid3') else 3;q=np.fromstring(node.get('position'),sep=' ').reshape(-1,width);q[:,:3]*=scale;put(node,'position',flat(q))
  if node.tag=='BeamInterpolation':
   put(node,'radius',str(float(node.get('radius'))*scale));put(node,'defaultYoungModulus',str(float(node.get('defaultYoungModulus'))/scale))
  if node.tag=='AdaptiveBeamForceFieldAndMass':put(node,'massDensity',str(float(node.get('massDensity'))/scale**3))
  if node.tag=='AdaptiveBeamMapping':
   assert node.get('useCurvAbs')=='0';q=np.fromstring(node.get('points'),sep=' ').reshape(-1,3);q[:,1:]*=scale;put(node,'points',flat(q))
  if node.tag=='LinearMovementProjectiveConstraint':
   q=np.fromstring(node.get('movements'),sep=' ').reshape(-1,6);q[:,:3]*=scale;put(node,'movements',flat(q))
  if node.tag in ('MinProximityIntersection','LocalMinDistance'):
   for key in ('alarmDistance','contactDistance'):put(node,key,str(float(node.get(key))*scale))
  if node.tag=='BlockGaussSeidelConstraintSolver':put(node,'tolerance',str(float(node.get('tolerance'))*scale))
 return changes
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--guide',action='store_true');p.add_argument('--contract-case');p.add_argument('--steps',type=int,default=1200);a=p.parse_args();assert 0<a.steps<=1200;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 if a.guide:
  assert a.contract_case;contract=json.loads((BASE/'results'/a.contract_case/'summary.json').read_text());assert contract['status']=='PASS_NO_CONTACT_PHYSICAL_UNITS_API_ONLY' and contract['outputs']==1200
 src=BASE/'results/wire_contact_policy1616' if a.guide else BASE/'results/current_turn_wire1614/no_guide_control';root=ET.parse(src/'scene.scn').getroot();changes=transform(root)
 for n in root.iter():
  for k,value in list(n.attrib.items()):n.set(k,value.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');pre=dict(source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),dimension_transform=dict(length=1000,mass=1,time=1,Young_modulus=.001,density=1e-9,force=1000,torque=1000000,impulse=1000,angular_impulse=1000000),mapping_note='useCurvAbs0 firstpointcoordinate dimensionless beamIndex+barycentric;ONLYlocal y/z offsets scale. Rigid quaternions/rotations/rad/s unchanged.',tolerance_note='Same physical normal-gap solver tolerance1e-12m=1e-9mm;dt/maxiterations/geometry/material/BC unchanged. Other hardcoded Native epsilons are NOT unitinvariant;this is a units contract,not pure dedup-only fix.',raw_units='mm/kg/s. Existing logger CSV column labels mentionSI but numeric Raw is NOTSI. Normalize only in separateanalysis;never rewrite Raw.',changes=changes,steps=a.steps,memory_GiB=4,child_limit_s=420,SDK='/home/ubuntu/SOFA/v26.06.00',binary_sha256={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')});(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',str(out/'scene.scn')],out/'process',420);new=read(out/'states.csv') if (out/'states.csv').exists() else [];logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));ok=proc['exit_code']==0 and '[ERROR]'not in logs and len(new)==a.steps;err={}
 if ok and not a.guide:
  for file,keys in [('states.csv',('rigid_q','rigid_v')),('surface.csv',('q','v'))]:
   old=read(src/file)[:a.steps];actual=read(out/file);assert [r['time_s'] for r in old]==[r['time_s'] for r in actual]
   for key in keys:
    worst=0.
    for x,y in zip(old,actual):
     q=np.fromstring(y[key],sep=' ');reference=np.fromstring(x[key],sep=' ')
     if key.startswith('rigid_'):q=q.reshape(-1,7 if key=='rigid_q' else 6);q[:,:3]/=1000;q=q.ravel()
     else:q=q/1000
     worst=max(worst,float(abs(q-reference).max()))
    err[file+':'+key]=worst
  ok=ok and max(err.values())<=1e-12
 status=('NATIVE_MM_CONTACT_PREFIX_COMPLETED_ONLY' if a.guide else 'PASS_NO_CONTACT_PHYSICAL_UNITS_API_ONLY') if ok else 'FAIL_NATIVE_UNITS_CONTRACT';d=dict(status=status,guide=a.guide,process=proc,outputs=len(new),SI_normalized_maximum_errors=err,physical_validation='NOT QUALIFIED',raw_units='mm/kg/s NOTSI despiteinheritedloggerheaders',source_sha256=sha(Path(__file__)),scope='No-contact q/v equivalence only;ifcontactenabled actual solid/row/force audit required. Not materials/time/mesh/fullgraspPASS. NoSDK edits,newsolver,alteredactualgeometry/material/force orrelaxedphysical tolerance.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
