"""Actual AV downstream geometric inertia and conditional blocked-tendon energy.
No motor rotor/gearing inertia, material certificate, or installed limiter assumed.
"""
import json,math,shutil,sys
import numpy as np
from scipy.integrate import solve_ivp
from baseline_registry import ROOT,REPO,S1,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.gp import gp_Ax1,gp_Pnt,gp_Dir

def main():
 assert not (ROOT/'runtime/STOP').exists()
 out=ROOT/'validation/overload/batch6_drive_inertia3';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 cp=ROOT/'cad/exports/revAV_micro_interface1/summary.json';op=ROOT/'validation/transmission/batch6_operating1/summary.json';sp=ROOT/'models/standard_drive/batch6_sources1/reviewed.json'
 cd=json.loads(cp.read_text());od=json.loads(op.read_text());facts=json.loads(sp.read_text())
 rows=[p for p in cd['parts'] if p['part_ID'].startswith('F0_') and p['part_ID']!='F0_MICRO_MOTOR']
 deps=[ref(cp),ref(op),ref(sp),ref(out/'producer.py')]+[p[k] for p in rows for k in ('STEP','STL')]
 assert all(sha(REPO/r['path'])==r['SHA256'] for r in deps)
 dump(out/'inputs.json',dict(dependencies=deps,axis_point_mm=[110,0,20],axis_direction=[0,1,0],mesh_inertia_relative_limit=.001,density_scenarios_kg_m3=dict(spool=2700,hub=2700,screws=7850),density_status='Explicit typical scenarios only, NOT material minima/maxima or certificates',stiffness_scenarios_N_m=[1000,10000],speed_scenarios_rpm=[0,310],model='Blocked end linear tendon, constant drive torque persists until first turning point. Not assembled transient certification.'))
 parts=[]
 for row in rows:
  assert not (ROOT/'runtime/STOP').exists()
  g=GProp_GProps();BRepGProp.VolumeProperties_s(read(REPO/row['STEP']['path']),g)
  exact=g.MomentOfInertia(gp_Ax1(gp_Pnt(110,0,20),gp_Dir(0,1,0)))
  verts=[]
  for line in (REPO/row['STL']['path']).read_text().splitlines():
   t=line.split()
   if t and t[0]=='vertex':verts.append(list(map(float,t[1:])))
  v=np.array(verts).reshape(-1,3,3)-np.array([110,0,20]);vol=np.einsum('ij,ij->i',v[:,0],np.cross(v[:,1],v[:,2]))/6
  # Exact tetrahedron monomial integration: int x_i^2=V/10*(sum a_i^2+sum pair products).
  moment=0.
  for d in (0,2):
   z=v[:,:,d];moment+=float(np.sum(vol*(np.sum(z*z,axis=1)+z[:,0]*z[:,1]+z[:,0]*z[:,2]+z[:,1]*z[:,2])/10))
  err=abs(moment/exact-1)
  rho=2700 if row['part_ID'].endswith(('SPOOL','STOCK_HUB')) else 7850
  parts.append(dict(part_ID=row['part_ID'],STEP=row['STEP'],STL=row['STL'],volume_mm3=g.Mass(),axis_geometric_inertia_mm5=exact,mesh_axis_inertia_mm5=moment,mesh_relative_error=err,scenario_density_kg_m3=rho,scenario_mass_kg=g.Mass()*1e-9*rho,scenario_axis_inertia_kg_m2=exact*1e-15*rho))
 J=sum(p['scenario_axis_inertia_kg_m2'] for p in parts);r=cd['wire_center_radius_mm']*.001
 tau=facts['motor']['extrapolated_stall_torque_kgcm']*.0980665;F=tau/r
 cases=[]
 for k in (1000.,10000.):
  for rpm in (0.,float(facts['motor']['no_load_rpm'])):
   w=rpm*2*math.pi/60;T0=max(x['conditional_tension_N'] for x in od['rows']);exact=F+math.sqrt((T0-F)**2+k*J*w*w);wn=r*math.sqrt(k/J);numeric=[]
   for n in (100,200):
    def rhs(t,y):return [y[1],(F-k*y[0])*r*r/J]
    def turn(t,y):return y[1]
    turn.direction=-1;turn.terminal=True
    sol=solve_ivp(rhs,[0,2*math.pi/wn],[T0/k,r*w],events=turn,max_step=2*math.pi/wn/n,rtol=1e-11,atol=1e-13)
    assert sol.success and len(sol.t_events[0])==1
    x,v=sol.y_events[0][0];W=F*(x-T0/k);E=.5*k*x*x+.5*J*(v/r)**2-.5*T0*T0/k-.5*J*w*w-W
    numeric.append(dict(interval_divisor=n,peak_N=k*x,time_s=float(sol.t_events[0][0]),energy_residual_J=E,steps=len(sol.t)))
   assert max(abs(z['peak_N']/exact-1) for z in numeric)<.001
   assert max(abs(z['energy_residual_J']) for z in numeric)<1e-8
   cases.append(dict(stiffness_N_m=k,initial_speed_rpm=rpm,initial_tension_N=T0,constant_force_scenario_N=F,exact_peak_N=exact,peak_to_static_ratio=exact/F,initial_kinetic_J=.5*J*w*w,numerical=numeric,source_status='Extrapolated stall and no-load speed are deliberately independent stress scenarios; NOT a simultaneous motor operating point or guaranteed maximum'))
 # Negative control: geometry-to-SI unit error must fail independent mesh comparison.
 wrong_units_rejected=abs((parts[0]['mesh_axis_inertia_mm5']*1e-12)/(parts[0]['axis_geometric_inertia_mm5']*1e-15)-1)>.001
 assert wrong_units_rejected
 result=dict(status='ACTUAL_GEOMETRIC_INERTIA_ANALYZED_PROTECTION_UNQUALIFIED',producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),candidate=ref(cp),parts=parts,scenario_total_downstream_J_kg_m2=J,cases=cases,wrong_units_control_rejected=wrong_units_rejected,guaranteed_peak_N=None,actual_capacity_qualified=False,whole_system_release=False,adopted=False,limitations=['Seven actual downstream interface parts, one Finger only; motor rotor/gears, wire, anchors and coupled Finger excluded','Unqualified typical densities, rigid co-rotation and linear tendon scenarios; not a complete inertia bound','Constant extrapolated stall torque is a stress-test scenario, not actual speed-dependent drive law or guaranteed cap','No installed protection, delay/drag/fault thermal bounds or structural allowable; numerical energy balance is not global product energy'],decision='Smaller motor alone fails to establish a physical force cap. Keep protected-drive gate BLOCKED pending actual rated protection and complete energy/load bounds; no additional custom limiter CAD justified by these scenarios.')
 result['mesh_inertia_verification']='PASS' if all(p['mesh_relative_error']<=.001 for p in parts) else 'FAIL';result['mesh_inertia_errors']=[dict(part_ID=p['part_ID'],relative_error=p['mesh_relative_error']) for p in parts if p['mesh_relative_error']>.001];dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],J=J,parts=len(parts),peaks=[c['exact_peak_N'] for c in cases])))
if __name__=='__main__':main()
