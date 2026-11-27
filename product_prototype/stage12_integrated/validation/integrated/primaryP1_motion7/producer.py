"""Actual primary rotor and full constant-length cable BReps at prescribed poses."""
import argparse,json,math,sys,shutil,itertools
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,cut,common,volume,bounds,overlap,export,solid_count
from build_stage1 import fuse
from primary_module_design import route,Ry,tr
from OCP.gp import gp_Ax2,gp_Pnt,gp_Dir
from OCP.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCP.BRepCheck import BRepCheck_Analyzer

def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--tag',required=True);a=p.parse_args();assert not (ROOT/'runtime/STOP').exists()
 out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports'/a.candidate/'summary.json';d=json.loads(src.read_text());refs=d['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());s={n:read(REPO/r['path']) for n,r in refs.items()}
 deps=[src,ROOT/'scripts/primary_module_design.py',S1/'scripts/incremental_stage1.py',S1/'scripts/build_stage1.py',ROOT/'scripts/baseline_registry.py']
 dump(out/'inputs.json',dict(producer=ref(out/'producer.py'),candidate=ref(src),parts=refs,dependencies=[ref(x) for x in deps],predeclared=dict(intersection_mm3_max=1e-8,relative_volume_max=1e-6),poses_deg=[0,5,10,15,20,25,30,35,40,45,50,55,60],scope='Actual rigid component transforms and full wrap/free-span/6mm factory tail. Flexible rails/skin NOT transformed/certified, no equilibrium, no CCD.'))
 g0=route(0);C=np.array([0.,0,20.]);rows=[];hits=[];rhits=[];comparisons=0
 rotor=[n for n in s if n.startswith(('F0_STOCK_HUB','F0_SET_SCREW','F0_SPOOL','F0_DRUM'))]
 shaft_region=cyl(2,(0,-8.8,20),10,(0,1,0));shaft=__import__('OCP.BRepAlgoAPI',fromlist=['BRepAlgoAPI_Common']).BRepAlgoAPI_Common(s['F0_MICRO_MOTOR'],shaft_region).Shape();motorfixed=cut(s['F0_MICRO_MOTOR'],shaft_region)
 for deg in range(0,61,5):
  assert not (ROOT/'runtime/STOP').exists();g=route(deg);eta=(g0['free']-g['free'])/11.25;start=-math.pi/2-eta;span=g['phi']-start;rr=Ry(eta)
  ax=gp_Ax2(gp_Pnt(*C),gp_Dir(0,-1,0),gp_Dir(math.cos(start),0,math.sin(start)))
  arc=BRepPrimAPI_MakeTorus(ax,11.25,.25,span).Shape();dv=g['E']-g['Q'];lead=cyl(.25,tuple(g['Q']),float(np.linalg.norm(dv)),tuple(dv/np.linalg.norm(dv)))
  tail=tr(cyl(.25,(-6,0,8.75),6,(1,0,0)),rr,C-rr@C);wire=fuse(fuse(arc,lead),tail);vol=volume(wire)
  posed={};rpart={}
  for n,x in s.items():
   if n.endswith(('SKIN','RAIL_L','RAIL_R')) or n=='F0_TENDON_WIRE':continue
   if n in rotor:x=tr(x,rr,C-rr@C);rpart[n]=x
   elif n.startswith(('F0_SWIVEL_LOWER','F0_SWIVEL_UPPER','F0_SWIVEL_BOLT','F0_SWIVEL_NUT','F0_TIP_FACTORY_NIPPLE')):
    rt=Ry(g['b']-g0['b']);x=tr(x,rt,g['P']-rt@g0['P'])
   elif 'TERMINAL' in n or n.startswith(('F0_SWIVEL_AXLE','F0_SWIVEL_SLEEVE','F0_SWIVEL_SPACER')):x=tr(x,g['r'],g['shift'])
   elif n=='F0_MICRO_MOTOR':x=motorfixed
   posed[n]=x
  rpart['ACTUAL_D_SHAFT']=tr(shaft,rr,C-rr@C)
  local=[];rlo=[]
  for n,x in posed.items():
   if overlap(bounds(wire),bounds(x)):
    comparisons+=1;v=common(wire,x)
    if v>1e-8:local.append(dict(pose_deg=deg,part=n,common_mm3=v))
  for n,x in rpart.items():
   for m,y in posed.items():
    if m in rotor:continue
    if overlap(bounds(x),bounds(y)):
     comparisons+=1;v=common(x,y)
     if v>1e-8:rlo.append(dict(pose_deg=deg,rotor=n,fixed=m,common_mm3=v))
  hits+=local;rhits+=rlo
  if deg in (0,30,60):
   export(wire,out/('WIRE_'+str(deg)))
  expected=math.pi*.25**2*(g0['free']+6)
  rows.append(dict(angle_deg=deg,rotor_angle_rad=eta,wrap_span_rad=span,wire_valid=bool(BRepCheck_Analyzer(wire).IsValid()),wire_solids=solid_count(wire),wire_volume_mm3=vol,expected_volume_mm3=expected,relative_volume_error=abs(vol/expected-1),wire_hits=local,rotor_hits=rlo))
 checks=dict(full_wire_single_valid=all(r['wire_valid'] and r['wire_solids']==1 for r in rows),constant_actual_cable_volume=all(r['relative_volume_error']<1e-6 for r in rows),single_layer=all(0<r['wrap_span_rad']<2*math.pi for r in rows),full_wire_clear=not hits,rotor_clear=not rhits)
 r=dict(status='PRIMARY_FULL_CABLE_RIGID_MOTION_SCREEN_PASS' if all(checks.values()) else 'PRIMARY_FULL_CABLE_MOTION_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),checks=checks,rows=rows,exact_comparisons=comparisons,wire_hits=hits,rotor_hits=rhits,split_actual_motor='Only output-shaft solid region at y>=-8.8 rotates with rotor; housing/pilot stationary. No artificial torque capacity or bearing reaction supplied.',limitations=['13prescribed rigid hardware poses, not continuous collision/actual equilibrium','Actual loaded flexible Rail/PET swept geometry remains unqualified','Factory-end pullout, pocket/cap strength, full cable threading and real supplier terminal assembly remain unqualified','No physical protection, strength, friction, global energy or release'],whole_system_release=False)
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],checks=checks,wire_hits=hits,rotor_hits=rhits)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
