"""Independent actual-shape/profile, outlet and local-fit design contracts."""
import argparse,json,math,shutil
import numpy as np
from incremental_stage1 import ROOT,read,common,sha,bounds
from build_stage1 import box,cyl,cut,volume
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.GeomAbs import GeomAbs_Cylinder
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir,gp_Ax1,gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
import wire_motion as wm
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False);wm.setup(idx)
 s={n:read(ROOT/v['path']) for n,v in idx['parts'].items() if n.startswith('F0_')};profile=[]
 for name,x,z in [('F0_DRUM',80,20),('F0_IDLER',44,25)]:
  slab=BRepAlgoAPI_Common(s[name],box(x-20,-.25,z-20,40,.5,40)).Shape()
  tor=BRepPrimAPI_MakeTorus(gp_Ax2(gp_Pnt(x,0,z),gp_Dir(0,1,0)),11.28,.28).Shape()
  core=cut(cyl(11.28,(x,-.25,z),.5,(0,1,0)),tor)
  excess=volume(cut(slab,core));wire=BRepPrimAPI_MakeTorus(gp_Ax2(gp_Pnt(x,0,z),gp_Dir(0,1,0)),11.25,.25).Shape()
  profile.append(dict(part=name,actual_material_outside_ideal_U_floor_mm3=excess,full_nominal_wire_torus_intersection_mm3=common(s[name],wire)))
 lines=[];free0=wm.path(0)['free'];wrap=[]
 for deg in range(0,61,2):
  g=wm.path(deg);eta=(free0-g['free'])/11.25;theta=g['phi']+math.pi/2+eta;wrap.append(theta)
  for c,r,u,v in [(np.array([80,0,20]),11.25,g['A'],g['B']),(np.array([44,0,25]),11.25,g['A'],g['B']),(np.array([44,0,25]),11.25,g['Q'],g['E'])]:
   d=v-u;t=np.clip(np.dot(c-u,d)/np.dot(d,d),0,1);lines.append(float(np.linalg.norm(c-(u+t*d))-r))
 # New factory outlet coincides with coil start. For0<=theta<=pi, actual
 # tube Xmin>=80+(11.25-.25)*sin(theta)>=80, while nipple Xmax80.
 # Forpi<=theta<=maxwrap, tube Zmin remains above entire nipple envelope.
 maxwrap=max(wrap);upper_arc_zmin=8.75+11.25*(1-math.cos(maxwrap))-.25*abs(math.cos(maxwrap))
 ni=bounds(s['F0_DRUM_FACTORY_NIPPLE']);joint=dict(outlet_plane_X_mm=ni[3],expected_X_mm=80,max_wrap_deg=math.degrees(maxwrap),wire_after_halfturn_Z_lower_mm=upper_arc_zmin,nipple_Zmax_mm=ni[5],after_halfturn_clearance_mm=upper_arc_zmin-ni[5],tip_outlet_clearance_radius_mm=.4-.25,minimum_terminal_diameter_mm=2.2,wire_exit_diameter_mm=.8)
 anti=[]
 for name,q in s.items():
  if not name.startswith('F0_SWIVEL_NUT_'):continue
  b=bounds(q);c=[(b[j]+b[j+3])/2 for j in range(3)];tr=gp_Trsf();tr.SetRotation(gp_Ax1(gp_Pnt(*c),gp_Dir(0,1,0)),math.pi/6);turned=BRepBuilderAPI_Transform(q,tr,True).Shape()
  anti.append(dict(nut=name,nominal_body_intersection_mm3=common(q,s['F0_SWIVEL_UPPER']),attempted30deg_rotation_block_mm3=common(turned,s['F0_SWIVEL_UPPER'])))
 radii={}
 for name in ('F0_PEDESTAL_L','F0_PEDESTAL_R'):
  vals=[];it=TopExp_Explorer(s[name],TopAbs_FACE)
  while it.More():
   ad=BRepAdaptor_Surface(TopoDS.Face_s(it.Current()))
   if ad.GetType()==GeomAbs_Cylinder:vals.append(ad.Cylinder().Radius())
   it.Next()
  radii[name]=sorted(set(round(v,6) for v in vals))
 fit=dict(SKF_P6_diameter_series=2,inner_mean_mm=[4.993,5.000],inner_single_plane_variation_mm=.005,inner_local_diameter_bound_mm=[4.9905,5.0025],shaft_f6_mm=[4.982,4.990],local_diametral_clearance_mm=[.0005,.0205],outer_sealed_single_plane_variation_mm=.009,outer_local_diameter_bound_mm=[15.9885,16.0045],housing_custom_limits_mm=[16.010,16.021],housing_local_diametral_clearance_mm=[.0055,.0325],scope='Bounds of single diameters, NOT a guarantee of inscribed/circumscribed envelope or creep/life. Require incoming GO plug4.990, outer ring gauge16.006 and paired seat/journal max-material envelope inspection before hardware use; NOT MEASURED.',source='https://cdn.skfmediahub.skf.com/api/public/0901d1968094ddb3/pdf_preview_medium/0901d1968094ddb3_pdf_preview_medium.pdf',source_table='SKF radial P6 table3 p39; diameter series2; sealed outer ring variation9um, inner variation5um',actual_CAD_cylinder_radii_mm=radii)
 passed=all(abs(p['actual_material_outside_ideal_U_floor_mm3'])<1e-7 and abs(p['full_nominal_wire_torus_intersection_mm3'])<1e-7 for p in profile) and max(abs(v) for v in lines)<1e-12 and abs(ni[3]-80)<1e-6 and joint['after_halfturn_clearance_mm']>0 and all(r['attempted30deg_rotation_block_mm3']>1e-4 and abs(r['nominal_body_intersection_mm3'])<1e-7 for r in anti) and all(8.008 in r for r in radii.values())
 result=dict(status='BEND_OUTLET_LOCAL_FIT_DESIGN_PASS' if passed else 'FAIL',support_profile=profile,maximum_tangent_float_error_mm=max(abs(v) for v in lines),nominal_wire_profile_containment='.25+abs(11.25-11.28)=.28; outward-open U floor bounds every planar tangent capsule by radial-distance inequality',factory_join=joint,captive_nuts=anti,fit=fit,recommended_pulley_condition=dict(root_D_mm=22,maximum_wire_D_mm=.52,recommendation_ratio=42,required_D_mm=21.84,margin_mm=.16,source='https://www.carlstahl-technocables.com/gb/en/products/pulleys/',fatigue_test='NOT MEASURED'),source_sha256=sha(src),stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],profile=profile,fit_radii=radii,antirotation=len(anti),max_wrap_deg=joint['max_wrap_deg'])))
if __name__=='__main__':main()
