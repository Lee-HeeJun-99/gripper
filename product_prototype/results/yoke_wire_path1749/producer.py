"""Actual new candidate cable paths versus finite nominal faceted bore geometry.
Straight segment consistency ONLY; no claimed finite-wire bending solution.
"""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);root=ET.parse(src/'scene.scn').getroot();records=[]
 for i in range(3):
  parent=root.find(f"Node[@name='guides{i}']");initial=np.fromstring(parent.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);frames=list(csv.DictReader((src/f'guide_frames{i}.csv').open()));film=list(csv.DictReader((src/f'finger{i}.csv').open()));assert [r['time_s'] for r in frames]==[r['time_s'] for r in film]
  for j in range(2):
   cable=parent.find(f"Node[@name='cable{j}']");origin=np.fromstring(cable.find('CableConstraint').get('pullPoint'),sep=' ')
   for k in range(6):
    node=cable.find(f"Node[@name='eyelet{k}']");v=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);n=len(v)//4;c=v.mean(0);vector=v[2*n:].mean(0)-v[:2*n].mean(0);length=np.linalg.norm(vector);axis=vector/length;inner=v[n:2*n]-c;inner-=np.outer(inner@axis,axis);ri=float(np.linalg.norm(inner,axis=1).min());inradius=ri*np.cos(np.pi/n);owner=int(node.find('RigidMapping').get('rigidIndexPerPoint').split()[0]);axlocal=Rotation.from_quat(initial[owner,3:]).inv().apply(axis);worst=1.;first=None;negative=0;inapplicable=0
    for fr,fl in zip(frames,film):
     q=np.fromstring(fr['rigid_q'],sep=' ').reshape(-1,7)[owner];ax=Rotation.from_quat(q[3:]).apply(axlocal);path=np.vstack([origin,np.fromstring(fl[f'guide{j}_q_m'],sep=' ').reshape(-1,3)]);segments=[path[k+1]-path[k]]
     if k<5:segments.append(path[k+2]-path[k+1])
     for seg in segments:
      L=np.linalg.norm(seg);assert L>0;cos=abs(float((seg/L)@ax))
      if cos==0 or L*cos<length/2:inapplicable+=1;continue
      circle_gap=ri-(length/2*np.sqrt(max(0.,1-cos*cos))+.00025)/cos
      # Negative ideal analytic-circle gap proves straight tube cannot fit;
      # positive inradius clearance is sufficient for actual faceted bore.
      conservative=inradius-(length/2*np.sqrt(max(0.,1-cos*cos))+.00025)/cos;worst=min(worst,conservative)
      if circle_gap<0:
       negative+=1
       if first is None:first=float(fr['time_s'])
    records.append(dict(finger=i,cable=j,guide=k,nominal_bore_radius_mm=ri*1000,faceted_inradius_mm=inradius*1000,length_mm=length*1000,minimum_conservative_straight_wire_gap_mm=worst*1000,proven_straight_tube_nonfit_samples=negative,first_proven_nonfit_s=first,inapplicable_segments=inapplicable))
 d=dict(status='STRAIGHT_FINITE_WIRE_PATH_FAIL_BENDING_REQUIRED' if any(r['proven_straight_tube_nonfit_samples'] for r in records) else 'STRAIGHT_PATH_SCREEN_ONLY_NOT_SLIDING_PASS',case=a.case,wire_radius_mm=.25,guides_with_proven_nonfit=sum(r['proven_straight_tube_nonfit_samples']>0 for r in records),records=records,scope='Actual current guide/path states,not old1586 replay; fixed origin model only. Negative analytic circular-bore clearance disproves a radius.25mm STRAIGHT tube segment at centre; a real flexible wire can bend. No new finite wire dynamics/contact/friction/strength/sliding qualification;positive geometric proxy does not solve1675. Full GRASP grade must not silently assume finite wire compatibility.',source_sha256=sha(Path(__file__)),input_hashes={f:sha(src/f) for f in ['scene.scn']+[f'finger{i}.csv' for i in range(3)]+[f'guide_frames{i}.csv' for i in range(3)]});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k!='records'},indent=2))
if __name__=='__main__':main()
