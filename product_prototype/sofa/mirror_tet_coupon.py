"""Same physical single-finger reference;reflect ONLY tetra connectivity.
No object/support. Diagnostic,not a qualified collision-boundary/grasp remesh.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def flat(q):return ' '.join(format(float(x),'.17g') for x in np.asarray(q).ravel())
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reflect',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/untapered_hold1001506';root=ET.parse(src/'scene.scn').getroot();m=json.loads((src/'mesh.json').read_text());local=np.array(m['local_positions_mm']);lookup={tuple(p):i for i,p in enumerate(local)};permutation=np.array([lookup[(x,-y,z)] for x,y,z in local]);tet=np.array(m['tetrahedra'],dtype=int)
 for node in list(root):
  if node.tag=='Node' and node.get('name') not in ('finger0','guides0','free0'):root.remove(node)
  elif node.tag in ('NativeResponseRows','NativeContactRows'):root.remove(node)
 finger=root.find("Node[@name='finger0']");q0=np.fromstring(finger.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)
 if a.reflect:
  tet=permutation[tet];tet[:,[0,1]]=tet[:,[1,0]];m['tetrahedra']=tet.tolist();finger.find('MeshTopology').set('tetrahedra',flat(tet))
 det0=np.linalg.det((q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1));assert det0.min()>0;assert np.max(abs(q0[permutation]*[1,-1,1]-q0))<1e-12
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');(out/'mesh.json').write_text(json.dumps(m));(out/'config.json').write_bytes((src/'config.json').read_bytes());(out/'producer.py').write_bytes(Path(__file__).read_bytes());pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),reflected_connectivity=a.reflect,reference_volume_m3=float(det0.sum()/6),mirror_node_permutation=permutation.tolist(),SDK='/home/ubuntu/SOFA/v26.06.00',child_limit_s=120,memory_GiB=4,binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')},scope='No checkpointq/v loaded. Allmass/Guidefoot/Cable/geometry/material/solverdata unchanged;onlytetconnectivity reflectedwithpositiveorientation. RemainingGuidecollisions retained. Surfacecollisiontriangulation unchanged intentionally;not approved collision-boundary/graspmodel. Removedobject/support andtheirread-onlyobservers to isolate singlefinger.');(out/'preflight.json').write_text(json.dumps(pre,indent=2));command=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','240','--hideProgressBar',str(out/'scene.scn')];process=guarded(command,out/'process',120);logs=''.join((out/'process'/name).read_text(errors='replace') for name in ('stdout.log','stderr.log'));rows=list(csv.DictReader((out/'finger0.csv').open())) if (out/'finger0.csv').exists() else [];minimum=1.;finite=True
 for r in rows:
  q=np.fromstring(r['q_m'],sep=' ').reshape(-1,3);finite&=bool(np.isfinite(q).all());ratio=np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1))/det0;minimum=min(minimum,float(ratio.min()))
 constraints=list(csv.DictReader((out/'constraints.csv').open())) if (out/'constraints.csv').exists() else [];counts=sorted(set(len(np.fromstring(r['impulses_Ns'],sep=' ')) for r in constraints));ok=process['exit_code']==0 and '[ERROR]'not in logs and len(rows)==240 and minimum>0 and finite;d=dict(status='VALID_NOOBJECT_MIRROR_COUPON_ONLY' if ok else 'FAIL_MIRROR_COUPON',process=process,outputs=len(rows),minimum_saved_volume_ratio=minimum,finite=finite,observed_constraint_row_counts=counts,only_two_Cable_rows=counts==[2],holding='NOT TESTED',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
