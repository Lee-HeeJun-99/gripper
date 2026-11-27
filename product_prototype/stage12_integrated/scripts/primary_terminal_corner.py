"""P1 finite lip corner contact with free material station and physical normal cone.
Specialized static active-contact candidate; ALL original inequalities and actual
BRep must independently pass. No constraint deletion or release promotion.
"""
import json,sys,shutil
import numpy as np
from scipy.optimize import root,nnls
from baseline_registry import ROOT,REPO,ref,dump
import primary_finger_equilibrium_v5 as model
import primary_finger_tangent_v5 as tangent
FC=np.array([-.03363880995252074,-.095]);FR=.08350880995252075
CORNER=np.array([FC[0]+np.sqrt(FR*FR-.005**2),-.090])

def corner(v,n,s):
 r,p,R,dR,jr,P,JP,tip,Jtip,t=tangent.terminal(v,n)
 ps,Jp,_,_=tangent.point(p,s,.00015);J=np.zeros((2,4*n));J[:,2*n:]=Jp
 local=R.T@(ps-r[3][-1])+[.0504,-.084];JL=R.T@(J-jr);JL[:,n-1]+=dR.T@(ps-r[3][-1])
 a,e,h,_,_=p;i=min(int(s/h),n-1);u=(s-i*h)/h;angle=(1-u)*a[i]+u*a[i+1];d=(a[i+1]-a[i])/h
 ds=R.T@((1+e[i])*np.array([-np.sin(angle),-np.cos(angle)])+.00015*d*np.array([np.sin(angle),np.cos(angle)]))
 return local,JL,ds

def solve(old,T):
 n=old['n'];v=np.array(old['state']);model.EXTRA_POINTS=old['extra_contact_stations_m'];tangent.EXTRA_POINTS=model.EXTRA_POINTS.copy();delta=old['object_inward_stop_m']
 # Physical interface at free PET tip and spatial object-stop constraint.
 labels=model.constraints(v,n,delta)[1];ids=[labels.index(('interface',model.LP)),len(labels)-1]
 J=tangent.constraints_jac(v,n,delta);gradient=tangent.gradient(v,n,T,model.E_RAIL,model.E_PET,model.width)
 s=.0821595;p,Jc,ds=corner(v,n,s);weights=1/np.r_[np.full(n,model.L),np.full(n,model.ES*model.L),np.full(n,model.LP),np.full(n,model.ES*model.LP)]
 norms=np.column_stack(((CORNER-FC)/FR,[0.,1.]));A=np.vstack((J[ids],norms.T@Jc));lam=nnls((A*weights).T,gradient*weights,maxiter=10000)[0];f=norms@lam[2:]
 def equations(z):
  x=z[:4*n];l=z[4*n:4*n+2];f=z[4*n+2:4*n+4];s=z[-1]*model.LP
  pc,jc,ds=corner(x,n,s);j=tangent.constraints_jac(x,n,delta);g=model.constraints(x,n,delta)[0]
  residual=tangent.gradient(x,n,T,model.E_RAIL,model.E_PET,model.width)-j[ids].T@l-jc.T@f
  return np.r_[residual/1e-4,g[ids]/1e-3,(pc-CORNER)/1e-3,np.dot(ds,f)]
 sol=root(equations,np.r_[v,lam[:2],f,s/model.LP],tol=1e-10)
 x=sol.x[:4*n];l=sol.x[4*n:4*n+2];f=sol.x[4*n+2:4*n+4];s=sol.x[-1]*model.LP
 pc,jc,ds=corner(x,n,s);j=tangent.constraints_jac(x,n,delta);grad=tangent.gradient(x,n,T,model.E_RAIL,model.E_PET,model.width);res=float(np.linalg.norm((grad-j[ids].T@l-jc.T@f)*weights));cone=np.linalg.solve(norms,f)
 features=model.feature_stations(x,n);model.EXTRA_POINTS=sorted(set(model.EXTRA_POINTS+features+[s]));g,labels=model.constraints(x,n,delta,24)
 r,p,tr,tp,er,ep,R,P,tip,t,free=model.state(x,n);U,_=model.energy(x,n,T);artificial=bool(max(abs(x[:n]))>1.399 or max(abs(x[2*n:3*n]))>1.399 or max(abs(np.r_[er,ep]))>.00999)
 valid=bool(sol.success and res<1e-8 and g.min()>=-1e-9 and min(l)>=0 and min(cone)>=0 and not artificial and 0<s<model.LP and abs(pc-CORNER).max()<1e-12)
 return dict(n=n,T_N=T,state=x.tolist(),rail_free_length_m=model.L,object_inward_stop_m=delta,rail_nodes_m=r.tolist(),PET_nodes_m=p.tolist(),rail_angles_rad=tr.tolist(),PET_angles_rad=tp.tolist(),rail_strain=er.tolist(),PET_strain=ep.tolist(),rail_tip_m=r[-1].tolist(),terminal_tip_m=tip.tolist(),cable_port_m=P.tolist(),cable_direction=t.tolist(),free_cable_m=free,stored_energy_J=U,normal_N=float(l[1]),interface_tip_force_N=float(l[0]),corner_material_station_m=s,corner_local_m=CORNER.tolist(),corner_contact_point_local_m=pc.tolist(),corner_contact_force_local_N=f.tolist(),corner_face_normals=norms.T.tolist(),corner_cone_nonnegative_coefficients_N=cone.tolist(),corner_tangent_force_N=float(ds@f),KKT_force_equivalent_N=res,minimum_dense_gap_m=float(g.min()),dense_witness=labels[int(g.argmin())],extra_contact_stations_m=model.EXTRA_POINTS.copy(),optimizer_success=bool(sol.success),optimizer_message=str(sol.message),root_equation_residual=float(np.linalg.norm(equations(sol.x))),artificial_bound_active=artificial,status='CONDITIONAL_CORNER_EQUILIBRIUM' if valid else 'FAIL',scope='Free material station contact at actual circle/upper-plane corner; tip material-pair interface and fixed X stop. Active-set candidate only; independent complete inequalities/BRep/mesh/force/cone checks mandatory.')

def main():
 out=ROOT/'validation/finger'/sys.argv[1];assert not(ROOT/'runtime/STOP').exists();out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');source=ROOT/'validation/finger/primaryP1_operating4/cases.json';old=json.loads(source.read_text());ns=list(map(int,sys.argv[2:])) or [8,16,32]
 deps=[__file__,ROOT/'scripts/primary_finger_equilibrium_v5.py',ROOT/'scripts/primary_finger_tangent_v5.py',ROOT/'scripts/rod_point_jacobian.py',ROOT.parent/'stage2_load_transfer/scripts/finger_structure.py',source,ROOT/'cad/exports/primaryP1_open9/summary.json']
 from pathlib import Path
 dump(out/'inputs.json',dict(inputs=[ref(Path(p)) for p in deps],candidate=ref(Path(deps[-1])),corner_local_m=CORNER.tolist(),criteria=dict(force_N_max=1e-8,gap_m_min=-1e-9,overlap_mm3_max=1e-8,mesh_relative_max=.01),assumptions='Same actual P1 finite strip reduction, typical moduli,rigid grips,frictionless planar symmetry,20mm fixed spatial stop; no system qualification'))
 rows=[]
 for n in ns:
  assert not(ROOT/'runtime/STOP').exists();r=solve(next(r for r in old if r['n']==n and r['T_N']==1),1.);rows.append(r);dump(out/'cases.json',rows);print(json.dumps({k:r[k] for k in ['n','status','normal_N','KKT_force_equivalent_N','minimum_dense_gap_m','corner_cone_nonnegative_coefficients_N']}),flush=True)
 dump(out/'summary.json',dict(status='ACTUAL_P1_FREE_STATION_CORNER_CANDIDATES_NOT_RELEASE',candidate=ref(Path(deps[-1])),task_id='goal_primary_terminal_feature_contact',inputs=ref(out/'inputs.json'),cases=ref(out/'cases.json'),rows=len(rows),whole_system_release=False,newly_qualified_system_gate_ids=[]))
if __name__=='__main__':main()
