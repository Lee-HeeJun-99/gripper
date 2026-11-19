"""Actual native tetra quality/inversion evidence,including NO-object isolation."""
import argparse,csv,json,hashlib,xml.etree.ElementTree as ET
import numpy as np
from mechanism_candidates import BASE
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);results={}
 for name in a.cases:
  src=BASE/'results'/name;m=json.loads((src/'summary.json').read_text());mesh=json.loads((src/'mesh.json').read_text());tet=np.array(mesh['tetrahedra']);tree=ET.parse(src/'scene.scn');records=[]
  if m['status']!='RUN_COMPLETED_NOT_QUALIFIED':raise ValueError('complete simulation horizon required')
  for f in range(m['fingers']):
   rows=list(csv.DictReader((src/f'finger{f}.csv').open()));q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);rest=np.fromstring(tree.find(f"./Node[@name='finger{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);d0=np.linalg.det((rest[tet[:,1:]]-rest[tet[:,0,None]]).transpose(0,2,1));d=np.linalg.det((q[:,tet[:,1:]]-q[:,tet[:,0,None]]).transpose(0,1,3,2));bad=np.flatnonzero(np.any(d<=0,axis=1));tip=np.array(mesh['local_positions_mm'])[:,0]==100
   records.append(dict(finger=f,minimum_determinant_ratio=float((d/d0).min()),inverted_element_samples=int((d<=0).sum()),first_inversion_time_s=float(rows[bad[0]]['time_s']) if len(bad) else None,peak_tip_displacement_mm=float(np.linalg.norm(q[:,tip].mean(axis=1)-rest[tip].mean(axis=0),axis=1).max()*1000),last_time_s=float(rows[-1]['time_s']),reference_state_error_first_frame_m=float(abs(q[0]-rest).max()),state_sha256=hashlib.sha256((src/f'finger{f}.csv').read_bytes()).hexdigest()))
  results[name]=dict(status='FAIL_INVERTED_TETRAHEDRA' if any(r['inverted_element_samples'] for r in records) else 'NO_INVERSION_OBSERVED_NOT_PHYSICS_PASS',records=records,summary_sha256=hashlib.sha256((src/'summary.json').read_bytes()).hexdigest())
 result=dict(status='FAIL' if any(r['status'].startswith('FAIL') for r in results.values()) else 'QUALITY_SCOPE_ONLY',scope='saved-state tetra orientation quality;does not identify locking,buckling,time step or contact as unique cause',cases=results);(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
