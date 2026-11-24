"""Finite annular eyelets AND actual-anchor support hulls replace sphere proxies.
New physical geometry candidate,not collision removal,calibrated inertia or Holding.
"""
import argparse,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from native_bending_coupon import guarded
from finite_guide_coupon import eyelet
from mechanism_candidates import world,width,guide_outboard,guide_normal
def flat(x):return ' '.join(format(float(v),'.17g') for v in np.asarray(x).ravel())
def run_three(root,out,src,quality,parts,steps,duration,forecast,configuration_source=None):
 import csv
 for file in ('config.json','mesh.json','holding_protocol.json'):(out/file).write_bytes((src/file).read_bytes())
 if configuration_source is not None:(out/'config.json').write_bytes((configuration_source/'config.json').read_bytes())
 ET.ElementTree(root).write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')},eyelet=quality,parts=parts,forecast_s=forecast,duration_s=duration,child_limit_s=420,memory_GiB=4,SDK='/home/ubuntu/SOFA/v26.06.00',scope='NewfiniteEyeletANDactualthreefootSupporthull collisioncandidate;allhardwarecollisionsenabled,allparentmass/inertias inherited NOTcalibrated;noSphereProxy andnoobjectforcing. Nativephysicalresultsrequireindependentgoal/Guidepairaudits. Oldtime/meshFAILpreserved.');(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')],out/'process',420);tet=np.array(json.loads((src/'mesh.json').read_text())['tetrahedra']);det=lambda q:np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));qualities=[];counts=[]
 for i in range(3):
  rows=list(csv.DictReader((out/f'finger{i}.csv').open())) if (out/f'finger{i}.csv').exists() else [];counts.append(len(rows));q0=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);ref=det(q0);ratios=[float((det(np.fromstring(r['q_m'],sep=' ').reshape(-1,3))/ref).min()) for r in rows];qualities.append(dict(finite=bool(all(np.isfinite(r) for r in ratios)),minimum_saved_volume_ratio=min(ratios,default=None)))
 logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));ok=process['exit_code']==0 and '[ERROR]'not in logs and counts==[steps]*3 and all(x['finite'] and x['minimum_saved_volume_ratio']>0 for x in qualities);d=dict(status='VALID_BOUNDED_EXPLORATION_ONLY' if ok else 'FAIL_FINITE_HARDWARE_EXECUTION_OR_INVERSION',process=process,outputs=counts,qualities=qualities,duration_s=duration,single=False,physical_validation='NOT QUALIFIED',holding='NOT ASSESSED',scope=pre['scope']);(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--three',action='store_true');p.add_argument('--duration',type=float,choices=(.25,.6,1.2,2.),default=.25);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/unbraced_hold1001549';root=ET.parse(src/'scene.scn').getroot();c=json.loads((src/'config.json').read_text());ring,quality=eyelet(c,32);meta=[];sphere=root.find("Node[@name='object']/MechanicalObject");centre=np.fromstring(sphere.get('position'),sep=' ')[:3];R=.03;minimum=1.;steps=round(a.duration/.0025)
 if a.three:
  assert a.pilot;prior=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());assert prior['status'] in ('VALID_FINITE_HARDWARE_FIXED_PILOT_ONLY','VALID_BOUNDED_EXPLORATION_ONLY');forecast=prior['process']['runtime_s']*a.duration/prior.get('duration_s',.25)*(10 if prior.get('single',True) else 2);assert forecast<420
 else:assert a.duration==.25;forecast=30.
 for i,angle in enumerate((0,120,240)):
  parent=root.find(f"Node[@name='guides{i}']");anchors=parent.find("Node[@name='anchors']");aq=np.fromstring(anchors.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);owners=np.fromstring(anchors.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int)
  for j,side in enumerate((-1,1)):
   cable=parent.find(f"Node[@name='cable{j}']");proxy=cable.find('SphereCollisionModel');group=proxy.get('group');cable.remove(proxy);cq=np.fromstring(cable.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);body=np.fromstring(cable.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int)
   for k,x in enumerate(c['tendon']['guide_stations']):
    local=np.array([x,side*(width(c,x)/2+guide_outboard(c,x)),guide_normal(c,x)]);h=np.array([.001,0,0]);ex=np.array(world(c,local+h,angle))-world(c,local-h,angle);ex/=np.linalg.norm(ex);ey=np.array(world(c,local+[0,.001,0],angle))-world(c,local,angle);ey-=ex*(ex@ey);ey/=np.linalg.norm(ey);basis=np.stack([ex,ey,np.cross(ex,ey)],axis=1);vertices=ring.vertices*.001@basis.T+cq[k];feet=aq[owners==body[k]];assert len(feet)==3
    # Exact actual three mapped attachment centres; finite0.8mm manufacturing pads.
    # Hull terminal joins beneath eyelet outer rim;intended bond overlap explicit.
    cubes=np.array(list(__import__('itertools').product((-.0004,.0004),repeat=3)));points=np.concatenate([feet[:,None,:]+cubes[None],(cq[k]-.0012*basis[:,2])[None,None,:]+cubes[None]],axis=0).reshape(-1,3);bracket=trimesh.convex.convex_hull(points);assert bracket.is_watertight and bracket.volume>0
    for name,v,faces in [('eyelet',vertices,ring.faces),('support',bracket.vertices,bracket.faces)]:
     node=ET.SubElement(cable,'Node',name=f'{name}{k}');ET.SubElement(node,'MechanicalObject',name='surface',template='Vec3d',position=flat(v));ET.SubElement(node,'MeshTopology',position=flat(v),triangles=flat(faces));ET.SubElement(node,'RigidMapping',input='@../../frames',output='@surface',globalToLocalCoords='1',rigidIndexPerPoint=' '.join([str(body[k])]*len(v)))
     for kind in ('Triangle','Line','Point'):ET.SubElement(node,kind+'CollisionModel',group=group)
     tri=np.asarray(v)[faces];near=trimesh.triangles.closest_point(tri,np.repeat(centre[None],len(tri),axis=0));gap=float((np.linalg.norm(near-centre,axis=1)-R).min());minimum=min(minimum,gap);assert gap>=.0002,'InitialfinitehardwareObjectcollision'
     meta.append(dict(finger=i,cable=j,guide=k,part=name,rigid_body=int(body[k]),vertices=len(v),triangles=len(faces),initial_object_gap_mm=gap*1000,volume_mm3=float(trimesh.Trimesh(v,faces,process=False).volume)*1e9))
 # Bounded fixed-sphere singleFinger FIRST;not fullgrasp or unsupportedHolding.
 if not a.three:
  for n in list(root):
   if n.tag=='Node' and n.get('name') not in ('finger0','guides0','free0','object'):root.remove(n)
  ET.SubElement(root.find("Node[@name='object']"),'FixedProjectiveConstraint',indices='0')
 for n in root.iter():
  for key,value in list(n.attrib.items()):n.set(key,value.replace(str(src),str(out)))
 if a.three:return run_three(root,out,src,quality,meta,steps,a.duration,forecast)
 ET.ElementTree(root).write(out/'scene.scn');(out/'config.json').write_bytes((src/'config.json').read_bytes());(out/'mesh.json').write_bytes((src/'mesh.json').read_bytes());(out/'producer.py').write_bytes(Path(__file__).read_bytes());pre=dict(source_sha256=sha(Path(__file__)),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),geometry_dependencies={str(p.relative_to(BASE)):sha(p) for p in [BASE/'sofa/finite_guide_coupon.py',BASE/'sofa/mechanism_candidates.py']},eyelet=quality,parts=meta,binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')},child_limit_s=420,memory_GiB=4,scope='FiniteOD3/ID1.2/L2eyelets AND finiteactual3anchor-supporthulls;ALLhardwarecollisionsretained,notzero-radius/deletedGuide. Manufacturedaxisand0.8mmpads assumptions. Sameinheritedmass/inertia,NOTphysicalcalibration/strength. Intentionallybondedownfinger collisiongroup retained. FixedsphereONLY,notreaction/Holding/replay/timeconvergence.');(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','100','--hideProgressBar',str(out/'scene.scn')],out/'process',420)
 import csv
 rows=list(csv.DictReader((out/'finger0.csv').open())) if (out/'finger0.csv').exists() else [];q0=np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);tet=np.array(json.loads((out/'mesh.json').read_text())['tetrahedra']);det=lambda q:np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));reference=det(q0);ratios=[float((det(np.fromstring(r['q_m'],sep=' ').reshape(-1,3))/reference).min()) for r in rows];logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));valid=process['exit_code']==0 and '[ERROR]'not in logs and len(rows)==100 and all(np.isfinite(r) and r>0 for r in ratios);d=dict(status='VALID_FINITE_HARDWARE_FIXED_PILOT_ONLY' if valid else 'FAIL_FINITE_HARDWARE_PILOT',process=process,outputs=len(rows),minimum_saved_volume_ratio=min(ratios,default=None),minimum_initial_hardware_object_gap_mm=minimum*1000,physical_validation='NOT QUALIFIED',Holding='NOT TESTED',scope=pre['scope']);(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
