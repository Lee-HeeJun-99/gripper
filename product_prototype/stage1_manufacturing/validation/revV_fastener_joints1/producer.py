"""Actual native cylindrical thread-envelope axial engagement inventory.

Nominal envelopes only, not helical thread contact, preload or strength.
Every nut must be assigned; unknown screw partner fails rather than vanishes.
"""
import argparse,json,math,shutil
import numpy as np
from incremental_stage1 import ROOT,read,bounds,sha
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder
def cylinders(s):
 rows=[];e=TopExp_Explorer(s,TopAbs_FACE)
 while e.More():
  face=TopoDS.Face_s(e.Current());ad=BRepAdaptor_Surface(face)
  if ad.GetType()==GeomAbs_Cylinder:
   c=ad.Cylinder();d=np.array([c.Axis().Direction().X(),c.Axis().Direction().Y(),c.Axis().Direction().Z()]);o=np.array([c.Location().X(),c.Location().Y(),c.Location().Z()]);bb=bounds(face);points=np.array([[x,y,z] for x in (bb[0],bb[3]) for y in (bb[1],bb[4]) for z in (bb[2],bb[5])]);ts=points@d
   rows.append(dict(r=c.Radius(),axis=d.tolist(),origin=o.tolist(),interval=[float(ts.min()),float(ts.max())],orientation=str(face.Orientation())))
  e.Next()
 return rows
def aligned(a,b):
 u=np.array(a['axis']);v=np.array(b['axis']);delta=np.array(b['origin'])-a['origin'];return abs(np.dot(u,v))>1-1e-8 and np.linalg.norm(delta-np.dot(delta,u)*u)<1e-5 and abs(a['r']-b['r'])<.02
def project_interval(b,axis):
 sign=float(np.dot(b['axis'],axis));return sorted(sign*t for t in b['interval'])
def overlap(a,b):return max(0.,min(a[1],b[1])-max(a[0],b[0]))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 parts={n:read(ROOT/v['path']) for n,v in idx['parts'].items() if n.startswith('F0_')};cs={n:cylinders(s) for n,s in parts.items()};nuts={n:v for n,v in cs.items() if 'NUT' in n};screws={n:v for n,v in cs.items() if any(k in n for k in ('BOLT','PLUG','AXLE')) and 'NUT' not in n and 'WASHER' not in n and 'SPACER' not in n};rows=[];used=set();unassigned=[]
 for n,faces in screws.items():
  outer=[c for c in faces if 'FORWARD' in c['orientation'] and c['r']>=.9]
  if not outer:unassigned.append(dict(part=n,reason='No external shank cylinder'));continue
  rmin=min(c['r'] for c in outer);bolt=max((c for c in outer if abs(c['r']-rmin)<1e-5),key=lambda c:c['interval'][1]-c['interval'][0]);matches=[]
  for nn,ff in nuts.items():
   if nn.startswith('F0_SHAFT_NUT'):continue
   for f in ff:
    if not aligned(bolt,f):continue
    t=project_interval(f,bolt['axis']);eng=overlap(bolt['interval'],t)
    if eng>1e-5:matches.append(dict(part=nn,kind='nut',nut_axial_extent_mm=t[1]-t[0],engagement_mm=eng,full_nut=eng>=t[1]-t[0]-1e-5));used.add(nn);break
  target=None
  for prefix,partner in [('F0_CAP_L_BOLT','F0_PEDESTAL_L'),('F0_CAP_R_BOLT','F0_PEDESTAL_R'),('F0_DRUM_CAP_BOLT','F0_DRUM'),('F0_DRUM_PIN_PLUG','F0_DRUM'),('F0_COUPLING_BOLT','F0_COUPLING_LOWER'),('F0_CASSETTE_ADAPTER_BOLT','F0_CASSETTE_BLANK_ADAPTER'),('F0_CASSETTE_BOLT','F0_ROOT_BACK'),('F0_MOTOR_BOLT','F0_MOTOR')]:
   if n.startswith(prefix):target=partner;break
  if target:
   candidates=[]
   for f in cs[target]:
    if aligned(bolt,f):
     t=project_interval(f,bolt['axis']);eng=overlap(bolt['interval'],t)
     if eng>1e-5:candidates.append(dict(part=target,kind='declared_tapped_body',actual_hole_axial_interval_mm=t,engagement_mm=eng))
   if candidates:matches.append(max(candidates,key=lambda m:m['engagement_mm']))
  if not matches:unassigned.append(dict(part=n,reason='No coaxial nut or declared tapped-hole overlap'))
  rows.append(dict(screw=n,nominal_shank_D_mm=2*bolt['r'],shank_axis=bolt['axis'],actual_shank_interval_mm=bolt['interval'],partners=matches))
 for side,zone in [('L',[-12.2,-8.5]),('R',[14,18.5])]:
  n='F0_SHAFT_NUT_'+side;ff=[c for c in cs[n] if abs(c['r']-2.5)<.02];assert ff,n;f=max(ff,key=lambda c:c['interval'][1]-c['interval'][0]);t=project_interval(f,[0,1,0]);eng=overlap(zone,t);used.add(n);rows.append(dict(screw='F0_SHAFT:M5x0.5_'+side,nominal_shank_D_mm=5,shank_axis=[0,1,0],actual_shank_interval_mm=zone,partners=[dict(part=n,kind='nut',nut_axial_extent_mm=t[1]-t[0],engagement_mm=eng,full_nut=eng>=t[1]-t[0]-1e-5)],thread_zone='Explicit drawing override; do not treat entire smooth journal as threaded'))
 missing=sorted(set(nuts)-used);incomplete=[r for r in rows if any(m.get('full_nut') is False for m in r['partners'])]
 result=dict(status='FASTENER_AXIAL_ENGAGEMENT_PASS' if not unassigned and not missing and not incomplete else 'FASTENER_AXIAL_ENGAGEMENT_FAIL',case=a.case,rows=rows,unassigned_screws=unassigned,unassigned_nuts=missing,incomplete_nut_engagement=incomplete,input_sha256=sha(src),scope='Actual native nominal cylindrical envelopes, full nut overlap and positive declared tapped-body overlap only. Nominal CAD does not model helices, partial-thread runout, actual6g/6H/preload/strength or prove all blind-hole bottom margins. M5 and custom axle thread zones require drawing overrides. No missing partner is silently accepted.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],screws=len(rows),unassigned=unassigned,missing_nuts=missing,incomplete=incomplete)))
if __name__=='__main__':main()
