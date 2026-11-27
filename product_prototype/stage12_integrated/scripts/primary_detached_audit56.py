"""Actual lower STEP edge incident normals and independent two-contact virtual work.
All original physical thresholds retained. One-dimensional strip extrema are not CCD.
"""
import sys,json,shutil,numpy as np
from scipy.optimize import minimize_scalar
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
import primary_terminal_corner_v2 as corner
import primary_finger_tangent_v5 as kin
from primary_support_feedback import body
from primary_gravity_swivel import ARM
from primary_gravity_pullback import G
from rod_point_jacobian import walls
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED,TopAbs_IN,TopAbs_OUT
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_detached56/summary.json';d=json.loads(src.read_text());r=json.loads((REPO/d['state']['path']).read_text());cp=REPO/d['candidate']['path'];cad=json.loads(cp.read_text());front=read(REPO/cad['part_references']['F0_TERMINAL_FRONT']['path']);vertex=BRepBuilderAPI_MakeVertex(gp_Pnt(50,0,-95)).Vertex();ex=TopExp_Explorer(front,TopAbs_FACE);normals=[]
while ex.More():
 f=TopoDS.Face_s(ex.Current());ex.Next();dist=BRepExtrema_DistShapeShape(vertex,f);dist.Perform()
 if dist.Value()>1e-7:continue
 ad=BRepAdaptor_Surface(f)
 if ad.GetType()!=GeomAbs_Plane:continue
 n=ad.Plane().Axis().Direction();vec=np.array([n.X(),n.Y(),n.Z()])*(-1 if f.Orientation()==TopAbs_REVERSED else 1);normals.append(vec.tolist())
probes=[]
for shift,state in [([-.001,0,-.001],TopAbs_IN),([.001,0,.001],TopAbs_OUT)]:
 p=np.array([50,0,-95])+shift;c=BRepClass3d_SolidClassifier(front,gp_Pnt(*map(float,p)),1e-9);probes.append(dict(point_mm=p.tolist(),expected_matches=c.State()==state))
assert any(np.linalg.norm(np.array(n)-[1,0,0])<1e-8 for n in normals) and any(np.linalg.norm(np.array(n)-[0,0,1])<1e-8 for n in normals)
base=json.loads((ROOT/'validation/integrated/primaryP1_operating56/inputs.json').read_text());points=json.loads((REPO/base['mass_points']['path']).read_text());seed=json.loads((REPO/base['seed']['path']).read_text())[0];m=corner.model;v=np.array(r['state']);n=r['n'];beta=r['swivel_beta_rad'];m.EXTRA_POINTS=sorted(set(seed['extra_contact_stations_m']+m.feature_stations(v,n)+[r['corner_material_station_m'],r['lower_corner_material_station_m']]));labels=m.constraints(v,n,seed['object_inward_stop_m'])[1];idx=labels.index(('interface',m.LP));fc=np.array(r['corner_force_N']);fc2=np.array(r['lower_corner_force_local_N']);Fe=np.array(r['string']['Fe_N'])[[0,2]];Fo=np.array([r['normal_N'],-r['object_downward_friction_N']]);z=np.r_[v,beta]
def phi(z,omit=False):
 vv=z[:-1];bb=z[-1];Ug,_,ports,_=body(points,vv,n,bb,np.array([0.,-G]));U=m.energy(vv,n,0)[0];ep=ports['P']+ARM*np.array([np.sin(bb),np.cos(bb)]);g=m.constraints(vv,n,seed['object_inward_stop_m'])[0][idx];pc=corner.corner(vv,n,r['corner_material_station_m'])[0];pc2=corner.corner(vv,n,r['lower_corner_material_station_m'])[0];return U+Ug-Fe@ep-Fo@ports['tip']-r['interface_tip_force_N']*g-fc@pc-(0 if omit else fc2@pc2)
deriv=[];negative=[];errors=[]
for j in range(4):
 direction=np.cos(np.arange(len(z))*(.71+j*.19)+j);direction/=np.linalg.norm(direction)
 def fd(h,omit=False):return (phi(z-2*h*direction,omit)-8*phi(z-h*direction,omit)+8*phi(z+h*direction,omit)-phi(z+2*h*direction,omit))/(12*h)
 a,b=fd(2e-5),fd(1e-5);deriv.append(b);errors.append(abs(a-b));negative.append(fd(1e-5,True))
rail,pet,R,dR,jr,P,JP,tip,JT,_=kin.terminal(v,n);fcgeom=np.array([-.03363880995252074,-.095]);fr=.08350880995252075
knots=sorted(set(np.linspace(0,m.LP,n+1).tolist()+m.EXTRA_POINTS+[m.L]));knots=[s for s in knots if 0<=s<=m.LP];extrema=[]
def gap(s,side,j):
 ps=kin.point(pet,s,side*.00015)[0];local=R.T@(ps-rail[3][-1])+[.0504,-.084];return walls(local,fcgeom,fr)[0][j]
for side in [-1,1]:
 for j in range(3):
  for a,b in zip(knots,knots[1:]):
   if b<m.L:continue
   a=max(a,m.L)
   if b-a<1e-14:continue
   sol=minimize_scalar(lambda s:gap(s,side,j),bounds=(a,b),method='bounded',options=dict(xatol=1e-14));ss=min([(a,gap(a,side,j)),(b,gap(b,side,j)),(sol.x,sol.fun)],key=lambda q:q[1]);extrema.append(dict(side=side,wall=j,interval_m=[a,b],station_m=float(ss[0]),gap_m=float(ss[1])))
g,labels=m.constraints(v,n,seed['object_inward_stop_m'],192);minimum=min(float(g.min()),min(q['gap_m'] for q in extrema));cone=np.array(normals).T;from scipy.optimize import nnls
ff=np.array([fc2[0],0,fc2[1]]);coef,coneerr=nnls(cone,ff);pc2,jc2,ds2=corner.corner(v,n,r['lower_corner_material_station_m']);checks=dict(actual_STEP_incident_normals=True,actual_material_probes=all(p['expected_matches'] for p in probes),actual_normal_cone=coneerr<1e-10 and min(coef)>=0,independent_virtualwork=max(abs(np.array(deriv)))<1e-10,FD_refinement=max(errors)<1e-10,omitted_new_contact_rejected=max(abs(np.array(negative)))>1e-6,all_finite_feature_intervals_gap=minimum>=-1e-9,material_stationarity=abs(ds2@fc2)<1e-10,upper_inactive_exact_zero=abs(np.array(r['corner_force_N'])).max()==0,producer_checks=all(d['checks'].values()))
dump(out/'extrema.json',extrema);dump(out/'summary.json',dict(status='ACTUAL_PRODUCT_LOWER_CORNER_CAD_NORMAL_AND_INDEPENDENT_WORK_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_PRODUCT_LOWER_CORNER_INDEPENDENT_AUDIT_FAIL',candidate=d['candidate'],source=ref(src),producer=ref(out/'producer.py'),checks={k:bool(v) for k,v in checks.items()},actual_incident_outward_normals=normals,actual_material_probes=probes,lower_contact_force_local_N=fc2.tolist(),actual_incident_normal_cone_coefficients_N=coef.tolist(),normal_cone_residual_N=coneerr,independent_virtualwork_J=deriv,omitted_lower_contact_residual_J=negative,FD_refinement_error_J=max(errors),finite_feature_interval_count=len(extrema),extrema=ref(out/'extrema.json'),minimum_requeried_gap_m=minimum,material_stationarity_N=float(ds2@fc2),accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['ActualSTEPedgeconeandlocalPETstation validated,notfullwidthcontactpressure/surfaceCCD','Bounded scalar searchesoneachfeatureinterval plusdensechecksarefiniteaudits,notproofallnonconvexsurfaceevents','ReferenceRoot/Motorcuts,typicalmaterial/PETmesh/time/host/frictionlowerbound/protection/all22stillunqualified']))
print((out/'summary.json').read_text(),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
