"""Actual accepted surface strain and journal synchronization, not fracture prediction."""
import argparse,csv,json,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);source=ROOT/'results'/('autonomous_film_'+a.case)/'1';tree=ET.parse(source/'scene.scn');node=tree.find("Node[@name='assembly']/Node[@name='actual']");rest=np.fromstring(node.find('MechanicalObject').get('rest_position'),sep=' ').reshape(-1,3);tri=np.fromstring(node.find('TriangleSetTopologyContainer').get('triangles'),sep=' ',dtype=int).reshape(-1,3);j=list(csv.DictReader((source/'journal.csv').open()));c=list(csv.DictReader((source/'contact.csv').open()));maximum=0;states=[]
 if len(j)!=len(c):raise RuntimeError('journal length')
 for x,y in zip(j,c):
  if abs(float(x['time'])-float(y['time']))>1e-12:raise RuntimeError('journal time')
  maximum=max(maximum,float(np.max(abs(np.fromstring(x['x'],sep=' ')-np.fromstring(y['positions'],sep=' ')))))
 for t in (.25,.5,1):
  row=min(c,key=lambda r:abs(float(r['time'])-t));q=np.fromstring(row['positions'],sep=' ').reshape(-1,3);parts={}
  for label,offset,end in (('skin',0,105),('left_rail',105,168),('right_rail',168,231)):
   strain=[];ratios=[]
   for ids in tri:
    if not offset<=ids[0]<end:continue
    r=rest[ids];v=q[ids];B=np.column_stack((r[1,:2]-r[0,:2],r[2,:2]-r[0,:2]));F=np.column_stack((v[1]-v[0],v[2]-v[0]))@np.linalg.inv(B);C=F.T@F;strain.extend(np.linalg.eigvalsh(.5*(C-np.eye(2))).tolist());ratios.append(float(np.sqrt(np.linalg.det(C))))
   parts[label]=dict(minimum_principal_Green_strain=min(strain),maximum_principal_Green_strain=max(strain),minimum_area_ratio=min(ratios),maximum_area_ratio=max(ratios))
  states.append(dict(time=float(row['time']),parts=parts,maximum_skin_z=float(max(q[:105,2])),center_tip_z=float(q[102,2])))
 write_json(out/'summary.json',dict(status='PASS' if maximum<1e-10 else 'FAIL',scope='actual geometry/journal computation only;not damage,mechanical interference or grasp approval',inputs={str((source/f).relative_to(ROOT)):sha(source/f) for f in ('journal.csv','contact.csv','scene.scn')},maximum_accepted_journal_coordinate_difference_mm=maximum,states=states,self_collision='NOT RUN',material_failure_threshold=None));print(json.dumps(dict(journal_coordinate_error=maximum,states=states)))
if __name__=='__main__':main()
