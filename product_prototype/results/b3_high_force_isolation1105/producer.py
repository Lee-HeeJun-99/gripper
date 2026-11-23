"""Single actual Film,original2.5N input,NO external/other-finger contacts."""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results/b3_mass100_force25_1101';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);tree=ET.parse(src/'scene.scn');root=tree.getroot()
 removed=['object','floor','finger1','finger2','free1','free2','guides1','guides2']
 for n in list(root):
  if (n.tag=='Node' and n.get('name') in removed) or n.tag in ('NativeResponseRows','NativeDetectionPairs','NativeContactRows'):root.remove(n)
 for n in root.iter():
  for k,v in list(n.attrib.items()):
   if str(src) in v:n.set(k,v.replace(str(src),str(out)))
 for name in ('config.json','mesh.json'):shutil.copy2(src/name,out/name)
 tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());pre=dict(scope='Actual full single Film/Rails/Guide/Cable Native system,not empty scene. Same2.5N input and originalRoot/material/mesh/dt/solver. Remove object/support and two otherfingers to test whether inversion can occur without those contacts. Persistence rulesout their necessity;absence wouldnot uniquely separate their contributions.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),SDK='/home/ubuntu/SOFA/v26.06.00',removed_nodes=removed,steps=240,dt_s=.0025,estimated_runtime_s=173.734*240/243/3,estimate_basis='partial1101 per-step cost scaled by active finger count;not guaranteed',child_limit_s=120,memory_GiB=4,binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')})
 (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','240','--hideProgressBar',out/'scene.scn'],out/'process',120);path=out/'finger0.csv';rows=list(csv.DictReader(path.open())) if path.exists() else [];quality=None
 if rows:
  mesh=json.loads((src/'mesh.json').read_text());tet=np.array(mesh['tetrahedra']);q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);rest=np.fromstring(root.find("./Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);d0=np.linalg.det((rest[tet[:,1:]]-rest[tet[:,0,None]]).transpose(0,2,1));d=np.linalg.det((q[:,tet[:,1:]]-q[:,tet[:,0,None]]).transpose(0,1,3,2));bad=np.flatnonzero(np.any(d<=0,axis=1));quality=dict(first_inversion_time_s=float(rows[bad[0]]['time_s']) if len(bad) else None,minimum_determinant_ratio=float((d/d0).min()),inverted_element_samples=int((d<=0).sum()))
 logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'));complete=proc['exit_code']==0 and '[ERROR]' not in logs and len(rows)==240
 d=dict(status='ISOLATED_INVERSION_OBSERVED' if quality and quality['inverted_element_samples'] else 'NO_INVERSION_OBSERVED_ISOLATED_SCOPE_ONLY' if complete else 'FAIL_ISOLATION_EXECUTION',process=proc,outputs=len(rows),quality=quality,physical_validation='NOT QUALIFIED',holding='NOT RUN_NO_OBJECT',input_hashes={str(f.relative_to(BASE)):sha(f) for f in [src/'scene.scn',out/'scene.scn',Path(__file__)]})
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
