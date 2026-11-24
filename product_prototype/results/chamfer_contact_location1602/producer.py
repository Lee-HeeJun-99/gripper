"""Read-only finite-eyelet detector coordinates in actual previous rigid frames."""
import argparse,csv,json,re,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();frames={};rings={};records=[]
 for i in range(3):
  parent=root.find(f"Node[@name='guides{i}']");initial=np.fromstring(parent.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);rows=read(src/f'guide_frames{i}.csv');accepted=[np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in rows];frames[i]={float(r['time_s']):(initial if k==0 else accepted[k-1]) for k,r in enumerate(rows)}
  for j in range(2):
   cable=parent.find(f"Node[@name='cable{j}']")
   for node in cable.findall('Node'):
    if not node.get('name','').startswith('eyelet'):continue
    v=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);owner=int(node.find('RigidMapping').get('rigidIndexPerPoint').split()[0]);q=initial[owner];local=Rotation.from_quat(q[3:]).inv().apply(v-q[:3]);n=len(v)//4;axis=local[2*n:].mean(0)-local[:2*n].mean(0);axis/=np.linalg.norm(axis);rings[i,j,node.get('name')]=(owner,local.mean(0),axis)
 active=set()
 for r in read(src/'response_rows.csv'):
  if float(r['lambda_Ns'])!=0 and '/guides'in r['model0'] and '/guides'in r['model1']:active.add((float(r['time_s']),*sorted((r['model0'],r['model1']))))
 for r in read(src/'detector.csv'):
  t=float(r['accepted_time_s']);names=(r['model0'],r['model1']);key=(t,*sorted(names))
  if key not in active:continue
  for k,name in enumerate(names):
   m=re.match(r'/guides(\d+)/cable(\d+)/(eyelet\d+)/',name)
   if not m:continue
   i,j=int(m[1]),int(m[2]);owner,c,axis=rings[i,j,m[3]];q=frames[i][t][owner];point=np.fromstring(r[f'detected_point{k}'],sep=' ');delta=Rotation.from_quat(q[3:]).inv().apply(point-q[:3])-c;axial=float(delta@axis);radial=float(np.linalg.norm(delta-axial*axis));records.append(dict(time_s=t,model=name,axial_mm=axial*1000,radial_mm=radial*1000))
 assert records
 d=dict(status='READ_ONLY_CONTACT_LOCATION_INVENTORY',case=a.case,points=len(records),axial_abs_min_max_mm=[min(abs(r['axial_mm']) for r in records),max(abs(r['axial_mm']) for r in records)],radial_min_max_mm=[min(r['radial_mm'] for r in records),max(r['radial_mm'] for r in records)],outer_rim_fraction=sum(abs(r['axial_mm'])>=.8 and r['radial_mm']>=1.3 for r in records)/len(records),scope='Actual detector points for model pairs having nonzero response at same accepted time;not row-to-point bijection, pressure, area or current-state geometry. Coordinates use previous accepted rigid poses; stage discrepancy must not be hidden.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ('scene.scn','detector.csv','response_rows.csv','guide_frames0.csv','guide_frames1.csv','guide_frames2.csv')});(out/'points.json').write_text(json.dumps(records));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
