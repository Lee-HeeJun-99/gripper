"""Necessary straight-leg bore feasibility from actual cable turn;no axis scan."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);ri=.6;half=1.;wire=.25;limit=float(np.arccos(wire/np.hypot(ri,half))-np.arctan2(half,ri));records=[]
 for case in ('dispatch_finite_holding1586','chamfer_eyelet_holding1594'):
  src=BASE/'results'/case;root=ET.parse(src/'scene.scn').getroot();groups=[]
  for i in range(3):
   rows=list(csv.DictReader((src/f'finger{i}.csv').open()))
   for j in range(2):
    origin=np.fromstring(root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']/CableConstraint").get('pullPoint'),sep=' ');paths=np.array([np.vstack([origin,np.fromstring(r[f'guide{j}_q_m'],sep=' ').reshape(-1,3)]) for r in rows]);segments=np.diff(paths,axis=1);directions=segments/np.linalg.norm(segments,axis=2)[:,:,None]
    for k in range(5):
     angle=np.arccos(np.clip(np.sum(directions[:,k]*directions[:,k+1],axis=1),-1,1));optimal=angle/2;clearance=ri-(half*np.sin(optimal)+wire)/np.cos(optimal);bad=np.flatnonzero(clearance<0);groups.append(dict(finger=i,cable=j,guide=k,maximum_actual_path_turn_deg=float(np.degrees(angle.max())),minimum_even_ideal_bisector_axis_clearance_mm=float(clearance.min()),first_necessary_straight_leg_failure_s=float(rows[bad[0]]['time_s']) if len(bad) else None))
  records.append(dict(case=case,guides_failing_even_ideal_swivel_axis=sum(g['first_necessary_straight_leg_failure_s']is not None for g in groups),groups=groups,input_hashes={f:sha(src/f) for f in ('scene.scn','finger0.csv','finger1.csv','finger2.csv')}))
 d=dict(status='NECESSARY_STRAIGHT_LEG_BORE_GEOMETRY_ONLY',maximum_single_leg_angle_deg=float(np.degrees(limit)),maximum_turn_for_straight_leg_feasibility_deg=float(np.degrees(2*limit)),records=records,scope='Analytic optimalbisector ofactualincoming/outgoingstraightlegs,ID1.2/L2/wireR.25. Anegativebound precludes bothstraightlegs passingunalteredcylindricalbore EVENwithidealaxis;doesNOTpreclude actualflexiblewire bendinginside or flaredguide. Terminalanchoronelegexcluded;staticgeometryreplayNOTNativewirephysics orhardwarequalification. No dimensions/state altered.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({**d,'records':[{k:v for k,v in r.items() if k!='groups'} for r in records]},indent=2))
if __name__=='__main__':main()
