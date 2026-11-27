"""Actual P1 gravity/free-swivel rotor/cable BReps at saved finite loaded terminal poses."""
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
 p=argparse.ArgumentParser();p.add_argument('--candidate',required=True);p.add_argument('--tag',required=True);p.add_argument('--states',required=True);a=p.parse_args();assert not (ROOT/'runtime/STOP').exists()
 out=ROOT/'validation/integrated'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 src=ROOT/'cad/exports'/a.candidate/'summary.json';d=json.loads(src.read_text());refs=d['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());s={n:read(REPO/r['path']) for n,r in refs.items()}
 deps=[src,ROOT/'scripts/primary_module_design.py',S1/'scripts/incremental_stage1.py',S1/'scripts/build_stage1.py',ROOT/'scripts/baseline_registry.py']
 dump(out/'inputs.json',dict(producer=ref(out/'producer.py'),candidate=ref(src),parts=refs,dependencies=[ref(x) for x in deps],predeclared=dict(intersection_mm3_max=1e-8,relative_volume_max=1e-6),source_states=ref(ROOT/'validation/finger'/a.states/'cases.json'),scope='Actual rigid component transforms and full wrap/free-span/6mm factory tail. Flexible rails/skin NOT transformed/certified, no equilibrium, no CCD.'))
 states_path=ROOT/'validation/finger'/a.states/'cases.json';states=[r for r in json.loads(states_path.read_text()) if r['n']==32];assert states
 g0=route(0);C=np.array([0.,0,20.]);rows=[];hits=[];rhits=[];comparisons=0
 rotor=[n for n in s if n.startswith(('F0_STOCK_HUB','F0_SET_SCREW','F0_SPOOL','F0_DRUM'))]
 shaft_region=cyl(2,(0,-8.8,20),10,(0,1,0));shaft=__import__('OCP.BRepAlgoAPI',fromlist=['BRepAlgoAPI_Common']).BRepAlgoAPI_Common(s['F0_MICRO_MOTOR'],shaft_region).Shape();motorfixed=cut(s['F0_MICRO_MOTOR'],shaft_region)
 for index,state in enumerate(states):
  assert not (ROOT/'runtime/STOP').exists();deg=state['T_N'];P=np.array([state['cable_port_m'][0]*1000,0,state['cable_port_m'][1]*1000]);u=(P-C)/np.linalg.norm(P-C);k=11.25/np.linalg.norm(P-C);normal=k*u+math.sqrt(1-k*k)*np.array([-u[2],0,u[0]]);Q=C+11.25*normal;t=(Q-P)/np.linalg.norm(Q-P);rt=Ry(state['rail_angles_rad'][-1]);anchor=np.array([state['rail_tip_m'][0]*1000,0,state['rail_tip_m'][1]*1000]);shift=anchor-rt@np.array([50.4,0,-84.]);g=dict(P=P,Q=Q,E=P+16*t,free=state['free_cable_m']*1000,phi=math.atan2(normal[2],normal[0]),b=math.atan2(t[0],t[2]),r=rt,shift=shift);g.update(Q=np.array([state['cable_tangent_m'][0]*1000,0,state['cable_tangent_m'][1]*1000]),t=np.array([state['cable_direction'][0],0,state['cable_direction'][1]]),b=state['swivel_beta_rad'],free=state['free_cable_m']*1000)
  g['E']=np.array([state['cable_end_m'][0]*1000,0,state['cable_end_m'][1]*1000]);g['phi']=math.atan2(g['Q'][2]-20,g['Q'][0]);eta=state['rotor_angle_rad'];start=math.pi/2-eta;span=start-g['phi'];rr=Ry(eta)
  ax=gp_Ax2(gp_Pnt(*C),gp_Dir(0,1,0),gp_Dir(math.cos(start),0,math.sin(start)))
  arc=BRepPrimAPI_MakeTorus(ax,11.25,.25,span).Shape();dv=g['E']-g['Q'];lead=cyl(.25,tuple(g['Q']),float(np.linalg.norm(dv)),tuple(dv/np.linalg.norm(dv)))
  tail=tr(cyl(.25,(-6,0,31.25),6,(1,0,0)),rr,C-rr@C);wire=fuse(fuse(arc,lead),tail);vol=volume(wire)
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
  if index in (0,1,2,3):
   export(wire,out/('WIRE_'+str(deg)))
  expected=math.pi*.25**2*(g0['free']+6)
  rows.append(dict(tendon_N=deg,static_state_status=state['status'],rotor_angle_rad=eta,wrap_span_rad=span,wire_valid=bool(BRepCheck_Analyzer(wire).IsValid()),wire_solids=solid_count(wire),wire_volume_mm3=vol,expected_volume_mm3=expected,relative_volume_error=abs(vol/expected-1),wire_hits=local,rotor_hits=rlo))
 checks=dict(full_wire_single_valid=all(r['wire_valid'] and r['wire_solids']==1 for r in rows),constant_actual_cable_volume=all(r['relative_volume_error']<1e-6 for r in rows),single_layer=all(0<r['wrap_span_rad']<2*math.pi for r in rows),full_wire_clear=not hits,rotor_clear=not rhits)
 r=dict(status='PRIMARY_LOADED_CABLE_ROTOR_POSE_SCREEN_PASS' if all(checks.values()) else 'PRIMARY_LOADED_CABLE_ROTOR_POSE_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),source_states=ref(states_path),inputs=ref(out/'inputs.json'),checks=checks,rows=rows,exact_comparisons=comparisons,wire_hits=hits,rotor_hits=rhits,split_actual_motor='Only output-shaft solid region at y>=-8.8 rotates with rotor; housing/pilot stationary. No artificial torque capacity or bearing reaction supplied.',limitations=['Four actual saved32element finite-state hardware poses; failed static states remain failed, no continuous CCD or acceptance by pose clearance','Actual loaded flexible Rail/PET swept geometry remains unqualified','Factory-end pullout, pocket/cap strength, full cable threading and real supplier terminal assembly remain unqualified','No physical protection, strength, friction, global energy or release'],whole_system_release=False)
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],checks=checks,wire_hits=hits,rotor_hits=rhits)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
