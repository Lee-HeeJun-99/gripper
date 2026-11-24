"""Exploratory100g rail-back joint candidate;not CAD/physical qualification."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--duration',type=float,choices=[.25,1.2,2.],default=.25);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_mass100_explore1059';tree=ET.parse(src/'scene.scn');root=tree.getroot();local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);changes=[];flat=lambda v:' '.join(format(float(x),'.17g') for x in np.asarray(v).ravel())
 for finger in range(3):
  n=root.find(f"./Node[@name='finger{finger}']");q=np.fromstring(n.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);mapping=n.find('SubsetMultiMapping');pairs=np.fromstring(mapping.get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);target={}
  for old,(owner,k) in enumerate(pairs):
   if owner!=1:continue
   want=local[old].copy();assert want[2]==0;want[2]=-.5;match=np.flatnonzero(np.all(abs(local-want)<1e-12,axis=1));assert len(match)==1;new=int(match[0]);assert pairs[new,0]==0;target[new]=int(k)
  assert len(target)==36
  free=[];anchors=np.zeros((36,3));newpairs=[]
  for i in range(len(q)):
   if i in target:newpairs.append([1,target[i]]);anchors[target[i]]=q[i]
   else:newpairs.append([0,len(free)]);free.append(q[i])
  free_node=root.find(f"./Node[@name='free{finger}']");fixed=np.fromstring(free_node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int);assert np.all(np.array(free)[fixed]==q[fixed]);free_node.find('MechanicalObject').set('position',flat(free));mapping.set('indexPairs',' '.join(str(v) for pair in newpairs for v in pair));root.find(f"./Node[@name='guides{finger}']/Node[@name='anchors']/MechanicalObject").set('position',flat(anchors));areas=[float(np.linalg.norm(np.cross(anchors[3*i+1]-anchors[3*i],anchors[3*i+2]-anchors[3*i]))) for i in range(12)];assert min(areas)>0;changes.append(dict(finger=finger,mapped_nodes=36,min_twice_triangle_area_m2=min(areas)))
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)).replace('detection_pairs.csv','detector.csv'))
 tree.write(out/'scene.scn')
 for f in ('mesh.json','config.json'):(out/f).write_bytes((src/f).read_bytes())
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());pre0=json.loads((src/'preflight.json').read_text());bins={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')};assert bins=={r['path']:r['sha256'] for r in pre0['binary_hashes']};dt=float(root.get('dt'));steps=round(a.duration/dt);forecast=25.
 if a.duration>.25:
  if not a.pilot:raise ValueError('actual pilot required')
  pr=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());assert pr['status']=='VALID_BOUNDED_EXPLORATION_ONLY' and pr['duration_s']==.25;forecast=pr['process']['runtime_s']*(a.duration/.25)*5
  if forecast>420:raise ValueError('conservative5xcontact forecast exceeds420s')
 cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')];pre=dict(command=cmd,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),SDK=pre0['SDK'],binary_hashes=bins,changes=changes,dt_s=dt,duration_s=a.duration,expected_outputs=steps,estimated_runtime_s=forecast,child_limit_s=420,memory_GiB=4,hypothesis='Move same36 rank6joint nodes per finger fromSkin/Railinterface toRailback to change transmitted bending without increasing1.5N cable force. Existing single-finger1129 avoided inversion;not yet a loaded grasp validation.',classification='EXPLORATORY FUNCTIONAL CANDIDATE',hardware_joint='IDEAL_ASSUMPTION_NOT_CAD_QUALIFIED',physical_validation='NOT QUALIFIED');(out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',420);logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));qualities=[];counts=[];tet=np.array(json.loads((out/'mesh.json').read_text())['tetrahedra'])
 for i in range(3):
  f=out/f'finger{i}.csv';rows=list(csv.DictReader(f.open())) if f.exists() else [];counts.append(len(rows))
  if rows:
   q0=np.fromstring(root.find(f"./Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);ratio=np.linalg.det((q[:,tet[:,1:]]-q[:,tet[:,0,None]]).transpose(0,1,3,2))/np.linalg.det((q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1));bad=np.argwhere(ratio<=0);qualities.append(dict(minimum_saved_volume_ratio=float(ratio.min()),first_inversion_time_s=float(rows[bad[0,0]]['time_s']) if len(bad) else None,finite=bool(np.isfinite(q).all())))
 clean=proc['exit_code']==0 and '[ERROR]'not in logs and counts==[steps]*3 and len(qualities)==3 and all(q['finite'] and q['minimum_saved_volume_ratio']>0 for q in qualities);d=dict(status='VALID_BOUNDED_EXPLORATION_ONLY' if clean else 'FAIL_EXECUTION_OR_INVERSION',process=proc,duration_s=a.duration,outputs=counts,qualities=qualities,unused_attribute_warnings=logs.count('Unused Attribute'),holding='NOT ASSESSED',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
