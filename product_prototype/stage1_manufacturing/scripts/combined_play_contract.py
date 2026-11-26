"""Tolerance counterexample plus conservative whole-pulley containment.

Full torus contains every wrapped arc; native intersections are actual BRep.
Offset test is geometrical uncertainty, not a simulated hardware trajectory.
"""
import argparse,json,shutil,math
from incremental_stage1 import ROOT,read,common,sha
from OCP.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());g=idx['design_geometry'];out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False);rows=[]
 # Incoming envelopes give larger clearance than mean-only SKF values.
 # Inner max local5.0025 vs shaft4.982 ->.01025; outer min15.9885
 # vs housing max16.035 ->.02325; pair-axis .0075 =>.041 <.045.
 radial=(5.0025-4.982)/2+(16.035-15.9885)/2+(.010+.005)/2
 assert radial<.045
 axial=(5.03-4.88)+.005
 assert abs(axial-.155)<1e-10
 for n,x,z in [('F0_DRUM',80,20),('F0_IDLER',44,25)]:
  q=read(ROOT/idx['parts'][n]['path'])
  for dx,dy in [(0,0),(.028,.0225),(.045,.155),(-.045,-.155)]:
   tor=BRepPrimAPI_MakeTorus(gp_Ax2(gp_Pnt(x+dx,dy,z),gp_Dir(0,1,0)),11.25,.26).Shape();rows.append(dict(part=n,relative_axis_shift_XY_mm=[dx,dy],wire_D_mm=.52,actual_common_mm3=common(q,tor)))
 defined='broad_groove_floor_radius_mm' in g
 radial_margin=11.25-.045-.26-g.get('broad_groove_floor_radius_mm',10.98)
 axial_margin=g.get('broad_groove_flat_halfwidth_mm',.0)-(.155+.26)
 bend_margin=min(g.get('broad_groove_root_limits_mm',[21.94]))-42*.52
 ok=defined and all(abs(r['actual_common_mm3'])<1e-7 for r in rows) and min(radial_margin,axial_margin,bend_margin)>0
 result=dict(status='COMBINED_PULLEY_PLAY_CLEARANCE_PASS' if ok else 'COMBINED_PULLEY_PLAY_CLEARANCE_FAIL',case=a.case,checks=rows,shaft_radial_play_plus_axis_bound_mm=radial,used_radial_uncertainty_mm=.045,used_axial_uncertainty_mm=axial,analytic_all_direction_radial_margin_mm=radial_margin,analytic_axial_margin_mm=axial_margin,minimum_root_to_42d_margin_mm=bend_margin,scope='Full torus uncertainty bound, actual native intersections; broad flat floor contains entire maximum wire tube for every axis shift within declared radial/axial bounds by triangle inequality. Side corner lies outside certified flat width. This is NOT driven wire tracking, bearing load/life, force/friction or fatigue qualification; wire may seek another seating radius under load.',input_sha256=sha(src),stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],native_max_common=max(r['actual_common_mm3'] for r in rows),radial_margin=radial_margin,axial_margin=axial_margin,bend_margin=bend_margin)))
if __name__=='__main__':main()
