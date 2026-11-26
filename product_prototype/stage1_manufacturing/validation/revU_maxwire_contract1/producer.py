"""Actual torus/straight-tangent maximum wire vs actual groove material."""
import argparse,json,shutil
from incremental_stage1 import ROOT,read,common,sha
from OCP.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 rows=[]
 for name,x,z in [('F0_DRUM',80,20),('F0_IDLER',44,25)]:
  s=read(ROOT/idx['parts'][name]['path'])
  for d in (.48,.50,.52):
   wire=BRepPrimAPI_MakeTorus(gp_Ax2(gp_Pnt(x,0,z),gp_Dir(0,1,0)),11.25,d/2).Shape()
   rows.append(dict(part=name,wire_D_mm=d,actual_groove_intersection_mm3=common(s,wire)))
 g=idx['design_geometry'];pr=g['groove_profile_radius_mm'];margin=pr-(.26+abs(11.28-11.25));root_min=2*(11.28-max(g.get('groove_profile_limits_mm',[pr,pr])));bend_margin=root_min-42*.52
 result=dict(status='MAX_WIRE_GROOVE_PASS' if all(abs(x['actual_groove_intersection_mm3'])<1e-7 for x in rows) and margin>0 and bend_margin>0 else 'MAX_WIRE_GROOVE_FAIL',case=a.case,checks=rows,profile_nominal_radial_margin_mm=margin,worst_profile_root_D_mm=root_min,manufacturer_42d_margin_mm=bend_margin,input_sha256=sha(src),scope='Actual BRep maximum-wire full torus and radial-distance inequality for outward-open tangent paths. Does not qualify friction/sliding or physical wire seating. Whole foreign-hardware motion separately required.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(result))
if __name__=='__main__':main()
