"""Read-only scale robustness of prior Python Skin geometry references."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for case in ('dispatch_finite_holding1586','chamfer_eyelet_holding1594'):
  src=BASE/'results'/case;root=ET.parse(src/'scene.scn').getroot();obj=read(src/'object.csv');times=np.array([float(r['time_s']) for r in obj]);chosen=sorted({int(np.argmin(abs(times-t))) for t in (.0025,.1,.375,1.6,2.)});points=[]
  for i in range(3):
   rows=read(src/f'finger{i}.csv');node=root.find(f"Node[@name='finger{i}']/Node[@name='skinCollision']");ids=np.fromstring(node.find('SubsetMapping').get('indices'),sep=' ',dtype=int);faces=np.fromstring(node.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3)
   for k in chosen:
    q=np.fromstring(rows[k]['q_m'],sep=' ').reshape(-1,3);c=np.fromstring(obj[k]['rigid_q'],sep=' ')[:3];tri=q[ids][faces];m=trimesh.triangles.closest_point(tri,np.repeat(c[None],len(tri),axis=0));mm=trimesh.triangles.closest_point((tri-c)*1000,np.zeros((len(tri),3)))*.001;dm=float(np.linalg.norm(m-c,axis=1).min());dmm=float(np.linalg.norm(mm,axis=1).min());points.append(dict(time_s=float(times[k]),finger=i,metre_reference_gap_mm=(dm-.03)*1000,normalized_mm_reference_gap_mm=(dmm-.03)*1000,closest_distance_difference_m=abs(dm-dmm)))
  records.append(dict(case=case,sampled_finger_states=len(points),maximum_closest_distance_scale_difference_m=max(p['closest_distance_difference_m'] for p in points),records=points,input_hashes={f:sha(src/f) for f in ('scene.scn','object.csv','finger0.csv','finger1.csv','finger2.csv')}))
 d=dict(status='SAMPLED_PYTHON_GEOMETRY_REFERENCE_SCALE_AUDIT_ONLY',records=records,scope='Actual savedSkinstates sampled at5times;unscaledtrimesh vs translated/mmnormalizedreference,samegeometry. NOTalltime/sweptCCD,Nativeintersectoraccuracy orupdatedhistoricalverdict. Finiteeyeletskinnytriangle unitissue doesNOTautomatically implySkinreference orNativeC++bug.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({**d,'records':[{k:v for k,v in r.items() if k!='records'} for r in records]},indent=2))
if __name__=='__main__':main()
