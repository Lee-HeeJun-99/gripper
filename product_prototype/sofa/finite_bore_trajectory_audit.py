"""Finite wire cylinder versus actual moving guide bore,geometric replay only."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def audit(case):
 src=BASE/'results'/case;root=ET.parse(src/'scene.scn').getroot();records=[]
 for i in range(3):
  parent=root.find(f"Node[@name='guides{i}']");initial=np.fromstring(parent.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);frames=read(src/f'guide_frames{i}.csv');film=read(src/f'finger{i}.csv');assert [r['time_s'] for r in frames]==[r['time_s'] for r in film]
  for j in range(2):
   cable=parent.find(f"Node[@name='cable{j}']");origin=np.fromstring(cable.find('CableConstraint').get('pullPoint'),sep=' ')
   for k in range(6):
    node=cable.find(f"Node[@name='eyelet{k}']");v=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);owner=int(node.find('RigidMapping').get('rigidIndexPerPoint').split()[0]);axis=v[len(v)//2:].mean(0)-v[:len(v)//2].mean(0);axis/=np.linalg.norm(axis);axislocal=Rotation.from_quat(initial[owner,3:]).inv().apply(axis);worst=1.;mincos=1.;first=None;inapplicable=0
    for fr,fl in zip(frames,film):
     rigid=np.fromstring(fr['rigid_q'],sep=' ').reshape(-1,7)[owner];ax=Rotation.from_quat(rigid[3:]).apply(axislocal);path=np.vstack([origin,np.fromstring(fl[f'guide{j}_q_m'],sep=' ').reshape(-1,3)]);segments=[path[k+1]-path[k]]
     if k<5:segments.append(path[k+2]-path[k+1])
     for segment in segments:
      length=np.linalg.norm(segment);cos=abs(float((segment/length)@ax));mincos=min(mincos,cos)
      if cos<1e-12 or length*cos<.001:inapplicable+=1;continue
      # Exact outer radial reach of a radius.25mm straight cylinder section
      # at a bore end1mm from centre;same unchamfered ID1.2 and length2mm.
      clearance=.0006-(.001*np.sqrt(max(0.,1-cos*cos))+.00025)/cos;worst=min(worst,clearance)
      if clearance<0 and first is None:first=float(fl['time_s'])
    records.append(dict(finger=i,cable=j,guide=k,minimum_radial_wire_bore_clearance_mm=worst*1000,minimum_abs_axis_cosine=mincos,first_proven_straight_tube_wall_intersection_s=first,inapplicable_short_or_perpendicular_halfsegments=inapplicable))
 return dict(case=case,minimum_clearance_mm=min(r['minimum_radial_wire_bore_clearance_mm'] for r in records),guides_with_proven_wall_intersection=sum(r['first_proven_straight_tube_wall_intersection_s'] is not None for r in records),records=records,input_hashes={f:sha(src/f) for f in ('scene.scn','finger0.csv','finger1.csv','finger2.csv','guide_frames0.csv','guide_frames1.csv','guide_frames2.csv')})
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[audit(x) for x in ('dispatch_finite_holding1586','chamfer_eyelet_holding1594')];d=dict(status='ACTUAL_TRAJECTORY_GEOMETRY_ONLY_NOT_FINITE_WIRE_DYNAMICS',records=records,wire_radius_mm=.25,bore_radius_mm=.6,bore_length_mm=2.,scope='ActualNativeguideposes/cablepath replay. Idealstraightsegments imply finitecylinder radialreach atboreends; only segmentslongenough toreachend classified. Negativeclearance iswallintersection forassumedsegment;realwirecouldbend,butbending/friction/radius/stress NOTsimulated. Cablekinks areNOTa validfinitebeam solution. NoGuidecollisiondisabled andnoNativegrasp rerun.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({**d,'records':[{k:v for k,v in r.items() if k!='records'} for r in records]},indent=2))
if __name__=='__main__':main()
