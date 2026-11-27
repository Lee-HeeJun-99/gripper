"""Independent GRAVITY-LOADED free-station corner virtual work, physical cone and actual BRep.
Uses independent sinc rod kinematics; avoids differentiating a nonsmooth max SDF.
"""
import sys,json,shutil,copy,math
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
from verify_primary_finger_v5 import independent,sectors,LR,ANCHOR
from primary_module_design import tr,Ry
from incremental_stage1 import read,common,bounds,overlap
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_VERTEX,TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Cylinder

from primary_gravity_independent import gradient as gravity_gradient, potential as gravity_potential, positions as gravity_positions
from primary_gravity_catenary import Catenary
from primary_catenary_independent import inspect_string
from primary_gravity_swivel import FreeSwivel
from primary_gravity_independent import derivatives_free,potential_free,length_free
POINTS=[]
LP=.0862

def port_kinematics(v,n,s):
 data,P,tip=independent(v,n);r,a,e,U=data[0];p,b,ep,Up=data[1];h=LP/n;i=min(int(float(np.real(s))/h),n-1);u=(s-i*h)/h;d=b[i+1]-b[i];theta=b[i]+u*d
 step=-h*u*(1+ep[i])*np.sinc(d*u/(2*np.pi))*np.array([np.sin(b[i]+d*u/2),np.cos(b[i]+d*u/2)])
 side=p[i]+step+.00015*np.array([-np.cos(theta),np.sin(theta)])
 R=np.array([[np.cos(a[-1]),np.sin(a[-1])],[-np.sin(a[-1]),np.cos(a[-1])]])
 local=R.T@(side-r[-1])+[.0504,-.084]
 nr=np.array([-np.cos(a[-1]),np.sin(a[-1])]);np_=np.array([-np.cos(b[-1]),np.sin(b[-1])]);rt=r[-1]+(LP-LR)*np.array([-np.sin(a[-1]),-np.cos(a[-1])])
 interface=(p[-1]-.00015*np_-rt-.0001*nr)@nr
 return data,P,tip,local,interface

def inspect(row,cadcorner):
 v=np.array(row['state']);n=row['n'];s=row['corner_material_station_m'];data,P,tip,pc,gap=port_kinematics(v,n,s);grad=[];JP=[];JT=[];JC=[];JI=[]
 for i in range(len(v)):
  x=v.astype(complex);x[i]+=1e-25j;d,p,t,c,g=port_kinematics(x,n,s);grad.append(sum(a[3] for a in d).imag/1e-25);JP.append(p.imag/1e-25);JT.append(t.imag/1e-25);JC.append(c.imag/1e-25);JI.append(g.imag/1e-25)
 JP=np.array(JP).T;JT=np.array(JT).T;JC=np.array(JC).T;JI=np.array(JI)
 ds=port_kinematics(v,n,s+1e-25j)[3].imag/1e-25;f=np.array(row['corner_contact_force_local_N']);x=np.r_[v,row['swivel_beta_rad']];bodypoints=[p for p in POINTS if p['mode'] not in ('wire','rotor')];gu,_=derivatives_free(x,n,bodypoints,row.get('gravity_factor',1.));Fe=np.array(row['cable_exit_force_XZ_N']);de=.016*np.array([np.cos(x[-1]),-np.sin(x[-1])]);res=np.r_[np.array(grad)-row['interface_tip_force_N']*JI-row['normal_N']*JT[0]-JC.T@f-Fe@JP,-Fe@de]+gu
 scale=np.r_[np.full(n,LR),np.full(n,LR*1e-4),np.full(n,LP),np.full(n,LP*1e-4),.016]
 residual=float(np.linalg.norm(res/scale));normals=np.column_stack(((cadcorner['point_m']-cadcorner['circle_center_m'])/cadcorner['radius_m'],[0.,1.]));cone=np.linalg.solve(normals,f)
 corner_error=float(np.max(abs(pc-cadcorner['point_m'])));kin=max(np.max(abs(data[0][0]-row['rail_nodes_m'])),np.max(abs(data[1][0]-row['PET_nodes_m'])))
 import primary_terminal_corner as analytic
 p,J,ds0=analytic.corner(v,n,s);derivative_error=float(max(np.max(abs(J-JC)),np.max(abs(ds-ds0))))
 U=sum(a[3] for a in data);passed=bool(residual<1e-8 and corner_error<1e-12 and kin<1e-13 and abs(U-row['stored_energy_J'])<1e-13 and derivative_error<1e-9 and abs(ds@f)<1e-8 and min(cone)>=0 and row['normal_N']>=0 and row['interface_tip_force_N']>=0 and abs(gap)<1e-9 and abs(tip[0]-.03)<1e-9)
 return dict(n=n,T_N=row['T_N'],normal_N=row['normal_N'],independent_force_equivalent_N=residual,corner_error_m=corner_error,kinematic_error_m=float(kin),energy_error_J=float(abs(U-row['stored_energy_J'])),point_Jacobian_error_m=derivative_error,free_station_tangent_force_N=float(ds@f),independent_cone_coefficients_N=cone.tolist(),interface_gap_m=float(gap),object_gap_m=float(tip[0]-.03),passed=passed)

def main():
 global POINTS
 POINTS=json.loads((ROOT/'validation/finger'/sys.argv[3]/'mass_points.json').read_text())
 source=ROOT/'validation/finger'/sys.argv[1];out=ROOT/'validation/finger'/sys.argv[2];assert not(ROOT/'runtime/STOP').exists();out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');rows=json.loads((source/'cases.json').read_text());candidate=ROOT/'cad/exports/primaryP1_fixture15/summary.json';cad=json.loads(candidate.read_text());parts={n:read(REPO/cad['part_references'][n]['path']) for n in ('F0_TERMINAL_FRONT','F0_TERMINAL_BACK')};front=parts['F0_TERMINAL_FRONT']
 vertices=[];it=TopExp_Explorer(front,TopAbs_VERTEX)
 while it.More():
  p=BRep_Tool.Pnt_s(TopoDS.Vertex_s(it.Current()));q=np.array([p.X(),p.Z()])*.001
  if abs(q[1]+.09)<1e-10 and .049<q[0]<.0499:vertices.append(q)
  it.Next()
 assert vertices;point=vertices[0];assert all(np.linalg.norm(p-point)<1e-10 for p in vertices)
 cylinders=[];it=TopExp_Explorer(front,TopAbs_FACE)
 while it.More():
  surf=BRepAdaptor_Surface(TopoDS.Face_s(it.Current()))
  if surf.GetType()==GeomAbs_Cylinder:
   c=surf.Cylinder();p=c.Location();r=c.Radius();centre=np.array([p.X(),p.Z()])*.001
   if r>80 and abs(np.linalg.norm(point-centre)-r*.001)<1e-10:cylinders.append((centre,r*.001))
  it.Next()
 assert cylinders;actual=dict(point_m=point,circle_center_m=cylinders[0][0],radius_m=cylinders[0][1]);audits=[inspect(row,actual) for row in rows];geometry=[];gaps=[]
 gravity_checks=[]
 for row in rows:
  v=np.array(row['state']);n=row['n'];x=np.r_[v,row['swivel_beta_rad']];factor=row.get('gravity_factor',1.);bp=[p for p in POINTS if p['mode'] not in ('wire','rotor')];u,g,pp,ports=FreeSwivel(bp).evaluate(x,n,factor,True);gi,gl=derivatives_free(x,n,bp,factor);pi=gravity_positions(v,n,bp,x[-1]);pe=max(np.max(abs(pi[i]-np.array(p['position_m'])[[0,2]])) for i,p in enumerate(pp));ge=float(np.max(abs(g-gi)));ue=float(abs(u-potential_free(x,n,bp,factor)));gravity_checks.append(dict(n=n,position_error_m=float(pe),potential_error_J=ue,gradient_error_J=ge,passed=bool(pe<1e-12 and ue<1e-12 and ge<1e-10)))
 string_audits=[inspect_string(row,POINTS) for row in rows]
 import primary_finger_equilibrium_v6 as continuous
 # Independently evaluate all inherited inequalities plus current feature/kink roots.
 for row in rows:
  assert not(ROOT/'runtime/STOP').exists();v=np.array(row['state']);n=row['n'];continuous.EXTRA_POINTS=sorted(set(row['extra_contact_stations_m']+continuous.feature_stations(v,n)));g,labels=continuous.constraints(v,n,row['object_inward_stop_m'],48);gaps.append(dict(n=n,minimum_gap_m=float(g.min()),worst=labels[int(g.argmin())],rows=len(g),passed=bool(g.min()>=-1e-9)))
  a=row['rail_angles_rad'][-1];R=Ry(a);end=np.array([row['rail_tip_m'][0]*1000,0,row['rail_tip_m'][1]*1000]);shift=end-R@np.array([50.4,0,-84]);hits=[];comparisons=0
  pet=sectors(row);rail=sectors(row,True);rb=[bounds(s) for s in rail]
  for i,s in enumerate(pet):
   for j,rs in enumerate(rail):
    if overlap(bounds(s),rb[j]):
     comparisons+=1;v=common(s,rs)
     if v>1e-8:hits.append(dict(segment=i,rail_segment=j,part='ACTUAL_RAIL_STRIP_ENVELOPE',common_mm3=v))
   local=tr(s,R.T,-R.T@shift)
   for name,part in parts.items():
    comparisons+=1;v=common(local,part)
    if v>1e-8:hits.append(dict(segment=i,part=name,common_mm3=v))
  geometry.append(dict(n=n,T_N=row['T_N'],hits=hits,comparisons=comparisons,passed=not hits))
 refinement=[]
 for row in rows[:-1]:
  fine=rows[-1];err=abs(row['normal_N']/fine['normal_N']-1);angle=abs(row['rail_angles_rad'][-1]/fine['rail_angles_rad'][-1]-1);refinement.append(dict(n=row['n'],fine_n=fine['n'],normal_relative=err,rail_tip_angle_relative=angle,tendon_relative=abs(row['T_N']/fine['T_N']-1),passed=bool(err<.01 and angle<.01 and abs(row['T_N']/fine['T_N']-1)<.01)))
 controls=[]
 for key in ['corner_material_station_m','normal_N','corner_contact_force_local_N','swivel_beta_rad','cable_exit_force_XZ_N']:
  bad=copy.deepcopy(rows[-1])
  if key in ('corner_contact_force_local_N','cable_exit_force_XZ_N'):bad[key][0]*=-1
  else:bad[key]+=.001
  controls.append(dict(perturbation=key,rejected=not inspect(bad,actual)['passed']))
 inp=json.loads((source/'inputs.json').read_text());hashes=[dict(reference=p,matched=sha(REPO/p['path'])==p['SHA256']) for p in inp['inputs']];assert all(p['matched'] for p in hashes)
 passed=all(a['passed'] for a in audits+geometry+gaps+refinement+gravity_checks+string_audits) and all(c['rejected'] for c in controls)
 actual={k:v.tolist() if hasattr(v,'tolist') else v for k,v in actual.items()}
 result=dict(status='ACTUAL_P1_CATENARY_GRAVITY_STATIC_BREP_PARTIAL_PASS' if passed else 'ACTUAL_P1_CATENARY_GRAVITY_AUDIT_FAIL',candidate=ref(candidate),source=ref(source/'summary.json'),cases=ref(source/'cases.json'),actual_STEP_corner=actual,audits=audits,actual_deformed_BRep=geometry,full_inequalities=gaps,mesh=refinement,negative_controls=controls,input_hashes=hashes,gravity_checks=gravity_checks,string_audits=string_audits,criteria_unchanged=True,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Gravity-loaded conditional planar finite-rod equilibrium at fixed spatial stop,typical moduli and rigid Root/Terminal grips only','Same-material normal interface remains a reduced contact model,not closest-point whole-surface friction','No finite friction,minimal strength,hardware,dt,full global energy or100g system approval'])
 dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if passed else 2)
if __name__=='__main__':main()
