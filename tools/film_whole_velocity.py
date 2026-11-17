"""All accepted triangle candidate kinematics;proximity is NOT contact area."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_coupled_row_audit import closest
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'identity.json').read_text())
 if json.loads((src/'summary.json').read_text())['status']!='PASS' or not meta.get('combined_contact'):raise ValueError('completed actual combined owner required')
 tree=ET.parse(src/'scene.scn');topology=tree.find('.//TriangleSetTopologyContainer');rest=np.fromstring(topology.get('position'),sep=' ').reshape(-1,3);tri=np.fromstring(topology.get('triangles'),sep=' ',dtype=int).reshape(-1,3);states=list(csv.DictReader((src/'coupled.states.csv').open()));rows=list(csv.DictReader((src/'coupled.rows.csv').open()));records=[];allMinimum=float('inf');nonpositive=[];positive=[]
 for step,s in enumerate(states,1):
  world=rest+np.fromstring(s['local_displacement'],sep=' ').reshape(-1,3);v=np.fromstring(s['local_velocity'],sep=' ').reshape(-1,3);center=np.fromstring(s['body_center'],sep=' ');bodyV=np.fromstring(s['body_velocity'],sep=' ');omega=np.fromstring(s['body_omega'],sep=' ')
  for id,ids in enumerate(tri):
   vertices=world[ids]
   if np.cross(vertices[1]-vertices[0],vertices[2]-vertices[0]).dot(np.cross(vertices[1]-vertices[0],vertices[2]-vertices[0]))<=0:raise ValueError('degenerate accepted triangle;no denominator regularization')
   point,bary,n=closest(vertices,center);gap=np.linalg.norm(point-center)-meta['buffer_radius'];allMinimum=min(allMinimum,float(gap))
   if gap>1e-10:continue
   vn=float(n@(bary@v[ids]-bodyV-np.cross(omega,point-center)));owned=any(r['stage']=='1' and int(r['step'])==step and int(r['triangle'])==id and r['time']==s['time'] for r in rows);records.append(dict(time=float(s['time']),triangle=id,gap=float(gap),normal_velocity=vn,owned_at_endpoint=owned,barycentric=bary.tolist()))
   (nonpositive if gap<=0 else positive).append(vn)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');minimum=min(nonpositive) if nonpositive else None;status='PASS' if allMinimum>=-1e-10 and (minimum is None or minimum>=-1e-10) else 'FAIL';write_json(out/'summary.json',dict(status=status,scope='all accepted triangle kinematics;positive-gap approaching candidates are NOT yet impacting contacts;NOT swept/global certification',case=a.case,minimum_gap=allMinimum,minimum_nonpositive_gap_normal_velocity=minimum,minimum_positive_near_band_normal_velocity=min(positive) if positive else None,near_band_rows=len(records),nonpositive_gap_rows=len(nonpositive),positive_gap_rows=len(positive),records=records,not_inferred=['contact area','pressure','force closure','full CCD'],input_hashes={f:sha(src/f) for f in ('identity.json','scene.scn','coupled.states.csv','coupled.rows.csv')}));print(json.dumps(dict(status=status,minimum_gap=allMinimum,minimum_nonpositive_gap_normal_velocity=minimum,near_band_rows=len(records))))
if __name__=='__main__':main()
