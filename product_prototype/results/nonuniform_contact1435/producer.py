"""Exploratory grasp: earlier distal turning plus clearance-derived root spacing.
Not latest finite hardware integration; original ideal Native joint/cable model.
"""
import argparse,csv,json,math,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from contact_adaptation_profile import candidate
from native_bending_coupon import guarded
def flat(a):return ' '.join(format(float(x),'.17g') for x in np.asarray(a).ravel())

def build(root,c,m):
 local=np.array(m['local_positions_mm']);tet=np.array(m['tetrahedra']);centre=np.array(c['simulation']['sphere_center_mm']);radius=c['simulation']['sphere_radius_mm'];source_radius=c['palm']['mount_radius'];wire_local=[]
 for i,angle in enumerate((0,120,240)):
  width=np.array([math.sin(math.radians(angle)),-math.cos(math.radians(angle)),0]);routes=[]
  for j in range(2):
   n=root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']");points=np.fromstring(n.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)*1000;pull=np.fromstring(n.find('CableConstraint').get('pullPoint'),sep=' ')*1000;routes.append(np.column_stack([[0]+c['tendon']['guide_stations'],np.vstack([pull,points])@width,np.full(7,3.)]))
  wire_local.append(routes)
 def gate(rad,save=False):
  c['palm']['mount_radius']=rad;records=[]
  for i,angle in enumerate((0,120,240)):
   q=np.array([candidate(c,p,angle) for p in local]);f=root.find(f"Node[@name='finger{i}']");s=f.find("Node[@name='skinCollision']");ids=np.fromstring(s.find('SubsetMapping').get('indices'),sep=' ',dtype=int);faces=ids[np.fromstring(s.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3)];near=trimesh.triangles.closest_point(q[faces],np.repeat(centre[None],len(faces),axis=0));skin=float(np.linalg.norm(near-centre,axis=1).min()-radius);wires=[];guide=[];paths=[]
   for j in range(2):
    path=np.array([candidate(c,p,angle) for p in wire_local[i][j]]);paths.append(path);u=path[1:]-path[:-1];v=np.clip(np.sum((centre-path[:-1])*u,axis=1)/np.sum(u*u,axis=1),0,1);wires.append(float(np.linalg.norm(path[:-1]+v[:,None]*u-centre,axis=1).min()-radius-.25));r=float(root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']/SphereCollisionModel").get('radius'))*1000;guide.append(float(np.linalg.norm(path[1:]-centre,axis=1).min()-radius-r))
   determinant=np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));records.append(dict(finger=i,skin_gap_mm=skin,wire_gap_mm=min(wires),guide_gap_mm=min(guide),minimum_reference_determinant_mm3=float(determinant.min())))
   if save:
    q*=.001;pairs=np.fromstring(f.find('SubsetMultiMapping').get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);free=np.empty(((pairs[:,0]==0).sum(),3));anchors=np.empty((36,3))
    for k,(owner,index) in enumerate(pairs):
     if owner==0:free[index]=q[k]
     else:anchors[index]=q[k]
    f.find('MechanicalObject').set('position',flat(q));f.find('MeshTopology').set('position',flat(q));root.find(f"Node[@name='free{i}']/MechanicalObject").set('position',flat(free));g=root.find(f"Node[@name='guides{i}']");a=g.find("Node[@name='anchors']");a.find('MechanicalObject').set('position',flat(anchors));owners=np.fromstring(a.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);frames=np.fromstring(g.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);assert np.max(np.abs(frames[:,3:]-[0,0,0,1]))==0
    for k in range(len(frames)):frames[k,:3]=anchors[owners==k].mean(0)
    g.find('MechanicalObject').set('position',flat(frames))
    for name in ('skinCollision','railCollision'):
     n=f.find(f"Node[@name='{name}']");ids=np.fromstring(n.find('SubsetMapping').get('indices'),sep=' ',dtype=int);n.find('MechanicalObject').set('position',flat(q[ids]));n.find('MeshTopology').set('position',flat(q[ids]))
    for j,path in enumerate(paths):
     n=g.find(f"Node[@name='cable{j}']");n.find('MechanicalObject').set('position',flat(path[1:]*.001));n.find('CableConstraint').set('pullPoint',flat(path[0]*.001))
  return records
 # Deterministic placement solve for 0.30mm initial assembly allowance;
 # not a grasp-performance search. Original50mm overlap rejection preserved.
 original=gate(source_radius);lo=source_radius;hi=source_radius+10
 assert min(min(r['skin_gap_mm'],r['wire_gap_mm'],r['guide_gap_mm']) for r in gate(hi))>.3
 for _ in range(38):
  mid=(lo+hi)/2;g=gate(mid)
  if min(min(r['skin_gap_mm'],r['wire_gap_mm'],r['guide_gap_mm']) for r in g)>=.3:hi=mid
  else:lo=mid
 final=gate(hi,True);assert min(r['minimum_reference_determinant_mm3'] for r in final)>0
 return dict(original_radius_mm=source_radius,candidate_radius_mm=hi,initial_at_original_radius=original,final_initial_gate=final,placement_rule='Smallest root radius>=original with Skin/wireR.25/actualguide sphere initial sphere gap>=.30mm;deterministic bisection,NOT performance optimization',assumption='New stress-free manufactured phi=40deg*(2u-u²) over70–100mm,original root14deg;paired root-radius compensation required by original1388 penetration. Not isolated one-variable superiority. Original assigned masses/guide inertias retained ideal assumptions,not new measured density or hardware.')

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--native',action='store_true');p.add_argument('--duration',type=float,choices=[.25,.6,1.2,2.],default=.25);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_railback_grasp1001298';root=ET.parse(src/'scene.scn').getroot();c=json.loads((src/'config.json').read_text());m=json.loads((src/'mesh.json').read_text());geometry=build(root,c,m);(out/'geometry.json').write_text(json.dumps(geometry,indent=2));(out/'config.json').write_text(json.dumps(c,indent=2));(out/'mesh.json').write_bytes((src/'mesh.json').read_bytes());(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),geometry=geometry,duration_s=a.duration,force_N_per_cable=1.5,classification='EXPLORATORY100g,not finite-wire hardware or numerical validation',SDK='/home/ubuntu/SOFA/v26.06.00',binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')},memory_GiB=4,child_limit_s=420)
 if not a.native:
  (out/'preflight.json').write_text(json.dumps(pre,indent=2));(out/'summary.json').write_text(json.dumps(dict(status='PASS_INITIAL_GEOMETRY_ONLY',geometry=geometry,Native='NOT RUN'),indent=2));print(json.dumps(geometry));return
 if a.duration>.25:
  assert a.pilot;pr=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());pm=json.loads((BASE/'results'/a.pilot/'preflight.json').read_text());assert pr['status']=='VALID_BOUNDED_EXPLORATION_ONLY' and pm['geometry']==geometry;forecast=pr['process']['runtime_s']*a.duration/pr['duration_s']*(5 if pr['duration_s']==.25 else 2);assert forecast<420;pre.update(pilot=a.pilot,forecast_s=forecast)
 command=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(round(a.duration/.0025)),'--hideProgressBar',str(out/'scene.scn')];pre['command']=command;(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(command,out/'process',420);logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));quality=[];counts=[];tet=np.array(m['tetrahedra'])
 for i in range(3):
  rows=list(csv.DictReader((out/f'finger{i}.csv').open())) if (out/f'finger{i}.csv').exists() else [];counts.append(len(rows));q0=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);det0=np.linalg.det((q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1));minimum=1.;finite=True
  for row in rows:
   q=np.fromstring(row['q_m'],sep=' ').reshape(-1,3);finite&=bool(np.isfinite(q).all());minimum=min(minimum,float((np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1))/det0).min()))
  quality.append(dict(minimum_saved_volume_ratio=minimum,finite=finite))
 valid=process['exit_code']==0 and '[ERROR]'not in logs and counts==[round(a.duration/.0025)]*3 and all(r['finite'] and r['minimum_saved_volume_ratio']>0 for r in quality);result=dict(status='VALID_BOUNDED_EXPLORATION_ONLY' if valid else 'FAIL_EXECUTION_OR_INVERSION',duration_s=a.duration,process=process,outputs=counts,qualities=quality,holding='NOT ASSESSED',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
