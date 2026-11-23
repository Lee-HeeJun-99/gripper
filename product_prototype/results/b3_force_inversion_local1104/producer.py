"""Explicit incomplete-run quality inventory;never bypass completion guard."""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--localize',action='store_true');a=p.parse_args();src=BASE/'results/b3_mass100_force25_1101';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 if json.loads((src/'summary.json').read_text())['status']!='CANCELLED_COST_FORECAST_NOT_HOLDING_VERDICT':raise ValueError('explicit interrupted case required')
 mesh=json.loads((src/'mesh.json').read_text());tet=np.array(mesh['tetrahedra']);local=np.array(mesh['local_positions_mm']);tree=ET.parse(src/'scene.scn');records=[];hashes={}
 for f in range(3):
  path=src/f'finger{f}.csv';rows=list(csv.DictReader(path.open()));q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);rest=np.fromstring(tree.find(f"./Node[@name='finger{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);d0=np.linalg.det((rest[tet[:,1:]]-rest[tet[:,0,None]]).transpose(0,2,1));d=np.linalg.det((q[:,tet[:,1:]]-q[:,tet[:,0,None]]).transpose(0,1,3,2));bad=np.flatnonzero(np.any(d<=0,axis=1));records.append(dict(finger=f,partial_outputs=len(rows),minimum_determinant_ratio=float((d/d0).min()),inverted_element_samples=int((d<=0).sum()),first_inversion_time_s=float(rows[bad[0]]['time_s']) if len(bad) else None));hashes[str(path.relative_to(BASE))]=sha(path)
  if a.localize and len(bad):
   records[-1]['first_bad_sample_elements']=[dict(tetrahedron_id=int(j),node_ids=tet[j].tolist(),reference_material_centroid_mm=local[tet[j]].mean(axis=0).tolist(),region='RAIL_INCLUDING' if np.any(local[tet[j],2]<0) else 'SKIN',determinant_ratio=float(d[bad[0],j]/d0[j])) for j in np.flatnonzero(d[bad[0]]<=0)]
 d=dict(status='PARTIAL_INVERSION_OBSERVED' if any(r['inverted_element_samples'] for r in records) else 'NO_INVERSION_IN_PARTIAL_SAVED_STATES_ONLY',records=records,scope='Incomplete trial explicitly retained. No completed Holding/mesh/time/quality or physical PASS;no interpolated states and no result completion flag changed.',physical_validation='NOT QUALIFIED',input_hashes=hashes,producer_sha256=sha(Path(__file__)))
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
