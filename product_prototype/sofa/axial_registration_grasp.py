"""One approach-pose hypothesis:align material90mm with lower-hemisphere contact.
Original finger geometry,T1.5,material,object/support unchanged;not a pose sweep.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from mechanism_candidates import world
from native_bending_coupon import guarded
def flat(a):return ' '.join(format(float(x),'.17g') for x in np.asarray(a).ravel())
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--duration',type=float,choices=[.25,.6,1.2,2.],default=.25);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_railback_grasp1001298';root=ET.parse(src/'scene.scn').getroot();c=json.loads((src/'config.json').read_text());m=json.loads((src/'mesh.json').read_text());local=np.array(m['local_positions_mm']);station=c['tendon']['guide_stations'][-2];normal_z=.85;centre=np.array(c['simulation']['sphere_center_mm']);radius=c['simulation']['sphere_radius_mm'];old_point=np.array(world(c,[station,0,.1],0));shift_mm=float(centre[2]-normal_z*radius-old_point[2]);shift=np.array([0,0,shift_mm*.001]);records=[]
 for i in range(3):
  for parent_name in (f'finger{i}',f'guides{i}',f'free{i}'):
   for node in root.find(f"Node[@name='{parent_name}']").iter():
    if node.tag in ('MechanicalObject','MeshTopology') and node.get('position'):
     size=7 if node.tag=='MechanicalObject' and node.get('template','').startswith('Rigid') else 3;q=np.fromstring(node.get('position'),sep=' ').reshape(-1,size);q[:,:3]+=shift;node.set('position',flat(q))
    if node.tag=='CableConstraint':node.set('pullPoint',flat(np.fromstring(node.get('pullPoint'),sep=' ')+shift))
  f=root.find(f"Node[@name='finger{i}']");q=np.fromstring(f.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)*1000;s=f.find("Node[@name='skinCollision']");ids=np.fromstring(s.find('SubsetMapping').get('indices'),sep=' ',dtype=int);faces=ids[np.fromstring(s.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3)];near=trimesh.triangles.closest_point(q[faces],np.repeat(centre[None],len(faces),axis=0));skin=float(np.linalg.norm(near-centre,axis=1).min()-radius);wires=[];guides=[]
  for j in range(2):
   n=root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']");pts=np.fromstring(n.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)*1000;pull=np.fromstring(n.find('CableConstraint').get('pullPoint'),sep=' ')*1000;path=np.vstack([pull,pts]);delta=np.diff(path,axis=0);u=np.clip(np.sum((centre-path[:-1])*delta,axis=1)/np.sum(delta*delta,axis=1),0,1);wires.append(float(np.linalg.norm(path[:-1]+u[:,None]*delta-centre,axis=1).min()-radius-.25));r=float(n.find('SphereCollisionModel').get('radius'))*1000;guides.append(float(np.linalg.norm(pts-centre,axis=1).min()-radius-r))
  records.append(dict(finger=i,initial_skin_gap_mm=skin,initial_wire_gap_mm=min(wires),initial_guide_gap_mm=min(guides)))
 geometry=dict(shift_z_mm=shift_mm,registered_material_station_mm=station,design_target_normal_z=normal_z,rule='Move gripper initial approach pose only,so undeformed90mmSkin centre reaches sphere lower-hemisphere z(c)−.85R. .85 is a declared design direction inspired by old50g upwardnormals,not a new measured result. Object/support are not moved. One derived pose,no sweep.',records=records,root_radius_mm=c['palm']['mount_radius'],unchanged='Relativefingergeometry/mass/material/tendonpath/cableforce/Rootangle/friction/objectpose/supportprotocol;all three root/free/guide/collision reference positions and pullpoints translate equally. Fullhardware/gripper dynamics not certified.')
 (out/'geometry.json').write_text(json.dumps(geometry,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes())
 if min(min(r[k] for k in ('initial_skin_gap_mm','initial_wire_gap_mm','initial_guide_gap_mm')) for r in records)<c['simulation']['contact_distance_mm']:
  (out/'summary.json').write_text(json.dumps(dict(status='REJECT_INITIAL_GEOMETRY',geometry=geometry,Native='NOT RUN'),indent=2));print('REJECT_INITIAL_GEOMETRY');return
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');c['research_initial_root_translation_mm']=shift_mm;(out/'config.json').write_text(json.dumps(c,indent=2));(out/'mesh.json').write_bytes((src/'mesh.json').read_bytes());protocol=json.loads((BASE/'results/nonuniform_hold1001438/holding_protocol.json').read_text());(out/'holding_protocol.json').write_text(json.dumps(protocol,indent=2));forecast=30.
 if a.duration>.25:
  assert a.pilot;pr=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());assert pr['status']=='VALID_BOUNDED_EXPLORATION_ONLY';forecast=pr['process']['runtime_s']*a.duration/pr['duration_s']*(5 if pr['duration_s']==.25 else 2);assert forecast<420
 command=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(round(a.duration/.0025)),'--hideProgressBar',str(out/'scene.scn')];pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),baseline_sha256=sha(src/'scene.scn'),geometry=geometry,command=command,duration_s=a.duration,forecast_s=forecast,SDK='/home/ubuntu/SOFA/v26.06.00',binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')},memory_GiB=4,child_limit_s=420,force_N_per_cable=1.5,holding_protocol_sha256=sha(out/'holding_protocol.json'));(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(command,out/'process',420);logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));quality=[];counts=[];tet=np.array(m['tetrahedra']);first=None
 for i in range(3):
  rows=list(csv.DictReader((out/f'finger{i}.csv').open())) if (out/f'finger{i}.csv').exists() else [];counts.append(len(rows));q0=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);det0=np.linalg.det((q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1));minimum=1.;finite=True
  for row in rows:
   q=np.fromstring(row['q_m'],sep=' ').reshape(-1,3);finite&=bool(np.isfinite(q).all());ratio=np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1))/det0;minimum=min(minimum,float(ratio.min()))
   if ratio.min()<=0 and first is None:first=dict(finger=i,time_s=float(row['time_s']),tet=int(np.argmin(ratio)))
  quality.append(dict(minimum_saved_volume_ratio=minimum,finite=finite))
 valid=process['exit_code']==0 and '[ERROR]'not in logs and counts==[round(a.duration/.0025)]*3 and all(r['finite'] and r['minimum_saved_volume_ratio']>0 for r in quality);result=dict(status='VALID_BOUNDED_EXPLORATION_ONLY' if valid else 'FAIL_EXECUTION_OR_INVERSION',duration_s=a.duration,process=process,outputs=counts,qualities=quality,first_inversion=first,holding='NOT ASSESSED',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
