"""Exact nominal support-surface containment for the wire tangent contract.
This independently replaces only chord-vs-own-drum/idler collision tests.
It does NOT delete hardware, change radius, or certify dynamic friction.
"""
import argparse,json,math,shutil
import numpy as np
from incremental_stage1 import ROOT,read,common,sha
from build_stage1 import box,cyl,cut,volume
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from wire_motion import path
def distance_to_line(c,a,b):
 d=b-a;t=np.clip(np.dot(c-a,d)/np.dot(d,d),0,1);return np.linalg.norm(c-(a+t*d))
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 containment=[]
 for name,x,z,r in [('F0_DRUM',80,20,8),('F0_IDLER',44,25,4.5)]:
  s=read(ROOT/idx['parts'][name]['path']);slab=BRepAlgoAPI_Common(s,box(x-20,-.25,z-20,40,.5,40)).Shape();excess=volume(cut(slab,cyl(r,(x,-1,z),2,(0,1,0))))
  containment.append(dict(part=name,wire_full_width_slab_mm=[-.25,.25],maximum_support_radius_mm=r,excess_mm3=excess))
 lines=[]
 for deg in range(0,61,2):
  g=path(deg)
  for name,c,r,u,v in [('drum_lead',[80,0,20],8,g['A'],g['B']),('idler_lead',[44,0,25],4.5,g['A'],g['B']),('idler_tip',[44,0,25],4.5,g['Q'],g['E'])]:
   d=distance_to_line(np.array(c),u,v);lines.append(dict(angle_deg=deg,name=name,centre_distance_mm=float(d),wire_radius_mm=.25,surface_clearance_mm=float(d-r-.25)))
 # Floating arithmetic only: exact construction has d=R+.25. Record actual
 # errors; no new physical penetration allowance is assigned.
 passed=all(c['excess_mm3']<1e-9 for c in containment) and all(abs(r['surface_clearance_mm'])<1e-12 for r in lines)
 C=np.array([[86,3.6,13.5],[88,3.6,13.5],[88.25,0,18],[88.25,0,20]])
 second_bound=max(np.linalg.norm(6*(C[2]-2*C[1]+C[0])),np.linalg.norm(6*(C[3]-2*C[2]+C[1])))
 result=dict(status='NOMINAL_SUPPORT_TANGENCY_PASS' if passed else 'FAIL',containment=containment,tangent_lines=lines,arc_chord_sagitta_max_mm=8.25*(1-math.cos(.04/2)),bezier_chord_bound_mm=second_bound/(8*64**2),tube_inflation_mm=.002,scope='Exact nominal CAD, full0.5mm wire width. Analytic arcs inner radii8 and4.5mm; straight tangent capsule distance. This is NOT tolerance, friction, fatigue or dynamic contact qualification.',source_sha256=sha(src),stage1_release=False)
 assert result['arc_chord_sagitta_max_mm']<.002 and result['bezier_chord_bound_mm']<.002
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],containment=containment)))
if __name__=='__main__':main()
