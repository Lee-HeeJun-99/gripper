"""Native functional exploration of conforming paired-QR mesh,not certification.
Strict reflection vGate1528 FAIL is preserved,not silently promoted or relaxed.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from native_bending_coupon import guarded
from mirror_conforming_mesh import generate,adapt
from conformal_cradle_grasp import continuation_cost
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--single',action='store_true');p.add_argument('--duration',type=float,choices=[.25,.6,.8,1.,1.2,2.],default=.25);p.add_argument('--pilot');p.add_argument('--cost-prefix');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/untapered_hold1001506';coupon=BASE/'results/centreline_paired1527';eligible=json.loads((coupon/'summary.json').read_text());assert eligible['status']=='VALID_CENTRELINE_MESH_COUPON_ONLY' and eligible['only_two_Cable_rows'];root=ET.parse(src/'scene.scn').getroot();c=json.loads((src/'config.json').read_text());old=json.loads((src/'mesh.json').read_text());m,quality=generate(c,True,True);assert m==json.loads((coupon/'mesh.json').read_text());records=adapt(root,c,old,m);skin=[];centre=np.fromstring(root.find("Node[@name='object']/MechanicalObject").get('position'),sep=' ')[:3];radius=float(root.find("Node[@name='object']/Node/SphereCollisionModel").get('radius'))
 for i in range(3):
  n=root.find(f"Node[@name='finger{i}']/Node[@name='skinCollision']");q=np.fromstring(n.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);faces=np.fromstring(n.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3);tri=q[faces];near=trimesh.triangles.closest_point(tri,np.repeat(centre[None],len(tri),axis=0));gap=float(np.linalg.norm(near-centre,axis=1).min()-radius);assert gap>=c['simulation']['contact_distance_mm']*.001;skin.append(gap)
 geometry=dict(mesh=quality,adaptation=records,initial_Skin_object_gap_m=skin,source_geometry_sha256=sha(src/'geometry.json'),scope='Sameuntaperedreference/material/totalmass/cables/Guides/foot/Root/T1.5/BC as1506. Extra centreline nodeschangeUniformMassnodalquadrature andmatchingcollisiontriangulation vs252nodecase;not isolatedtopology-onlyfullgraspcomparison. No duplicated material/newforcefield/SDK. Strictmirrorvelocity1.44e−12 FAIL1528preserved;positions4.13e−15 andhandednesssuppressed supportEXPLORATORY functionalpilot ONLY,not numericalqualification.')
 if a.single:
  for n in list(root):
   if n.tag=='Node' and n.get('name') not in ('finger0','guides0','free0','object'):root.remove(n)
  ET.SubElement(root.find("Node[@name='object']"),'FixedProjectiveConstraint',indices='0')
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');(out/'config.json').write_text(json.dumps(c,indent=2));(out/'mesh.json').write_text(json.dumps(m));(out/'geometry.json').write_text(json.dumps(geometry,indent=2));(out/'holding_protocol.json').write_bytes((src/'holding_protocol.json').read_bytes());(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'mesh_generator.py').write_bytes((BASE/'sofa/mirror_conforming_mesh.py').read_bytes());forecast=30.
 if a.duration>.25 or not a.single:
  assert a.pilot;pr=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());pm=json.loads((BASE/'results'/a.pilot/'preflight.json').read_text());assert pr['status']=='VALID_BOUNDED_EXPLORATION_ONLY' and pm['geometry']==geometry and pm['force_N_per_cable']==1.5;forecast=pr['process']['runtime_s']*a.duration/pr['duration_s']*(10 if pr['single'] and not a.single else 2)
  if a.cost_prefix:
   assert not a.single;forecast,cost=continuation_cost(a.pilot,a.cost_prefix,a.duration,geometry,1.5);(out/'cost_evidence.json').write_text(json.dumps(cost,indent=2))
  assert forecast<420
 binaries={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')};assert binaries==json.loads((src/'preflight.json').read_text())['binary_hashes'];command=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(round(a.duration/.0025)),'--hideProgressBar',str(out/'scene.scn')];pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),generator_sha256=sha(BASE/'sofa/mirror_conforming_mesh.py'),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),binary_hashes=binaries,geometry=geometry,force_N_per_cable=1.5,forecast_s=forecast,child_limit_s=420,memory_GiB=4,single_fixed_sphere=a.single,duration_s=a.duration,SDK='/home/ubuntu/SOFA/v26.06.00',fixed_object_total_reaction='NOT MEASURED whenfixed;projectedJacobianisnotreaction');(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(command,out/'process',420);logs=''.join((out/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));qualities=[];counts=[];tet=np.array(m['tetrahedra']);first=None
 for i in range(1 if a.single else 3):
  rows=list(csv.DictReader((out/f'finger{i}.csv').open())) if (out/f'finger{i}.csv').exists() else [];counts.append(len(rows));q0=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);det0=np.linalg.det((q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1));minimum=1.;finite=True
  for r in rows:
   q=np.fromstring(r['q_m'],sep=' ').reshape(-1,3);finite&=bool(np.isfinite(q).all());rat=np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1))/det0;minimum=min(minimum,float(rat.min()))
   if rat.min()<=0 and first is None:first=dict(finger=i,time_s=float(r['time_s']),tet=int(rat.argmin()))
  qualities.append(dict(finite=finite,minimum_saved_volume_ratio=minimum))
 ok=process['exit_code']==0 and '[ERROR]'not in logs and counts==[round(a.duration/.0025)]*len(counts) and all(r['finite'] and r['minimum_saved_volume_ratio']>0 for r in qualities);d=dict(status='VALID_BOUNDED_EXPLORATION_ONLY' if ok else 'FAIL_EXECUTION_OR_INVERSION',duration_s=a.duration,single=a.single,process=process,outputs=counts,qualities=qualities,first_inversion=first,holding='NOT ASSESSED',physical_validation='NOT QUALIFIED',mirror_API_velocity_gate='FAIL1528UNCHANGED',time_mesh_convergence='NOT QUALIFIED,oldFAILs preserved');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
