"""Independent spatial wire: arc-length force ODE, closed-form free catenary,
actual BRep offset distances, full force/moment/virtual work; no solver imports.
"""
import sys,json,shutil
import numpy as np
from scipy.integrate import solve_ivp
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN
from OCP.gp import gp_Pnt

def crossW(q,f):return np.r_[f,np.cross(q,f)]
def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');assert not(ROOT/'runtime/STOP').exists();src=ROOT/'validation/integrated'/sys.argv[2]/'summary.json';s=json.loads(src.read_text());state=json.loads((REPO/s['state']['path']).read_text());curves=json.loads((REPO/s['curves']['path']).read_text());parent=s['pose'];cad=json.loads((REPO/s['candidate']['path']).read_text());inp=json.loads((REPO/s['inputs']['path']).read_text());mass=json.loads((REPO/inp['mass']['path']).read_text());c=state['string'];Rm=np.array(parent['motor_R']);C=np.array(parent['motor_C_m']);axis=Rm[:,1];r=parent['actual_wire_center_radius_m'];mu=next(p['mass_kg'] for p in mass if p['mode']=='wire')/.12404617484274723;grav=np.array([0,0,-9.80665]);w=mu*grav;A=np.array(c['A_m']);B=np.array(c['B_m']);Q=np.array(c['Q_m']);E=np.array(c['E_m']);z=np.array(c['state']);hA=Rm@z[:3];l0=c['lead_length_m'];lw=c['contact_length_m'];l1=c['free_length_m'];Fe=np.array(c['Fe_N']);hB=hA-w*l0;hQ=-Fe+w*l1
 def integral(h,L):
  g=np.linalg.norm(w);e=w/g;hp=h@e;ht=h-hp*e;b=np.linalg.norm(ht)
  return ht/g*(np.arcsinh(hp/b)-np.arcsinh((hp-g*L)/b))+e/g*(np.hypot(b,hp)-np.hypot(b,hp-g*L))
 free_error=[]
 for start,h,L,key in [(A,hA,l0,'lead_curve_m'),(Q,hQ,l1,'free_curve_m')]:
  pp=np.array(curves[key]);exact=np.array([start+integral(h,t) for t in np.linspace(0,L,len(pp))]);free_error.append(float(np.max(abs(exact-pp))))
 def ode(t,y):
  q,h=y[:3],y[3:6];rad=q-C-axis*((q-C)@axis);er=rad/np.linalg.norm(rad);et=np.cross(er,axis);H=np.linalg.norm(h);lam=(h@et)**2/(H*r)-w@er;f=lam*er
  return np.r_[h/H,-w-f,q,f,np.cross(q,f)]
 sol=solve_ivp(ode,(0,lw),np.r_[B,hB,np.zeros(9)],rtol=2e-12,atol=2e-14,dense_output=True);y=sol.y[:,-1];qe=y[:3];he=y[3:6];reaction=y[9:12];moment=y[12:15]
 # Independent wire equilibrium from start/end and actual normal-reaction integration.
 WG=np.array(c['wire_gravity_wrench_N_Nm']);eta=z[6];ce,se=np.cos(eta),np.sin(eta);Ry=np.array([[ce,0,se],[0,1,0],[-se,0,ce]]);tail=C+Rm@Ry@np.array([-.003,0,.01125]);freeWG=WG-crossW(tail,mu*.006*grav);balance=-crossW(A,hA)+crossW(E,-Fe)+freeWG+np.r_[reaction,moment]
 hnorm=np.linalg.norm(hA);tangent=Rm@Ry@np.array([1.,0,0]);exit_angle=float(np.arccos(np.clip(tangent@hA/hnorm,-1,1)))
 # Exact 3D point-to-solid distance is a necessary sampled finite wire offset check.
 # Curves are expressed in world coordinates; unrotate SAME rotor into rest CAD.
 names=['F0_SPOOL','F0_DRUM_NIPPLE_CAP','F0_DRUM_FACTORY_NIPPLE'];shapes={n:read(REPO/cad['part_references'][n]['path']) for n in names};rows=[]
 pp=np.vstack([curves['lead_curve_m'],curves['wrap_curve_m'],curves['free_curve_m']]);rest=(Ry.T@Rm.T@(pp-C).T).T*1000+[0,0,20]
 for n,shape in shapes.items():
  assert sha(REPO/cad['part_references'][n]['path'])==cad['part_references'][n]['SHA256'];mind=1e9;inside=0;worst=None
  for j,q in enumerate(rest):
   v=BRepBuilderAPI_MakeVertex(gp_Pnt(*map(float,q))).Vertex();d=BRepExtrema_DistShapeShape(v,shape);d.Perform();assert d.IsDone();dist=d.Value();cl=BRepClass3d_SolidClassifier(shape,gp_Pnt(*map(float,q)),1e-8)
   inside+=int(cl.State()==TopAbs_IN)
   if dist<mind:mind=dist;worst=j
  rows.append(dict(part=n,samples=len(rest),minimum_center_distance_mm=mind,nominal_wire_radius_mm=.25,minimum_offset_margin_mm=mind-.25,inside_centers=inside,worst_index=worst))
 dump(out/'normal_reaction.json',dict(force_N=reaction.tolist(),moment_Nm=moment.tolist(),wrap_endpoint_m=qe.tolist(),wrap_end_tension_N=he.tolist(),ODE_success=sol.success))
 endpoint=float(np.max(abs(qe-Q)));force=float(np.max(abs(he-hQ)));checks=dict(closed_form_free=max(free_error)<1e-10,independent_wrap_endpoint=endpoint<1e-10,independent_wrap_force=force<1e-8,wire_force=np.linalg.norm(balance[:3])<1e-8,wire_moment=np.linalg.norm(balance[3:])<1e-10,sampled_offset_clearance=all(q['minimum_offset_margin_mm']>=-1e-6 and q['inside_centers']==0 for q in rows))
 # Separate finite-bending gate: point string permits exit-direction change;
 # no invented zero-radius bend certificate or tension-cap/source strength claim.
 result=dict(status='ACTUAL_P1_SPATIAL_STRING_INDEPENDENT_PASS' if all(checks.values()) else 'ACTUAL_P1_SPATIAL_STRING_INDEPENDENT_FAIL',candidate=s['candidate'],source=ref(src),state=s['state'],curves=s['curves'],verifier=ref(out/'verifier.py'),reaction=ref(out/'normal_reaction.json'),checks={k:bool(v) for k,v in checks.items()},closed_form_error_m=free_error,wrap_endpoint_error_m=endpoint,wrap_force_error_N=force,wire_equilibrium_N_Nm=balance.tolist(),BRep_checks=rows,exit_tangent_change_rad=exit_angle,exit_tangent_change_deg=float(np.degrees(exit_angle)),finite_bending_exit_qualified=False,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Independentarc-lengthODEandclosedformfree-spanverifyfrictionlessinextensiblestringonly.','BRepdistancesarenecessaryfinitepointsamplesofradiusoffset,notcontinuousswepttubeCCD/tolerances.','NominalR11.25seatmatchesnippleXZtangent; lateralhelixexitangle/finitewirebend/sourceplayanddiametertolerancesremainunqualified.','Nofull3Drod/new20elastic/globalenergy/strength/hardware/full3Finger/Stage3certificate.']);dump(out/'summary.json',result);print(json.dumps(result));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
