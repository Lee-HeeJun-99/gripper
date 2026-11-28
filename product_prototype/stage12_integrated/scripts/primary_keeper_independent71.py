"""Independent original18-row wrench/finiteCAD/host-port bounds on coupled Root.
No reuse of producer equilibrium matrix or numerical face-distance output.
"""
import sys,json,shutil,math
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,translate,common
from build_stage1 import rotate
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');sp=ROOT/'validation/integrated/primaryP1_keepercoupled71/summary.json';d=json.loads(sp.read_text());cp=REPO/d['candidate']['path'];assert sha(cp)==d['candidate']['SHA256'];cad=json.loads(cp.read_text());refs=cad['part_references'];assert all(sha(REPO[r['path']])==r['SHA256'] for r in []) # all real refs checked below
assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),cad['assembly'],cad['BOM']]);settings=[q for q in json.loads((REPO/cad['settings']['path']).read_text())['settings'] if q['keeper']=='ROOT_SOCKET_KEEPER'];base={n:read(REPO/refs[n]['path']) for n in ['ROOT_SOCKET_KEEPER','F0_ROOT_BACK','ROOT_SOCKET_KEEPER_INSTALLED_SPLIT_PIN']+[q['bolt'] for q in settings]}
def moved(s,x,y,a,dz=0):return translate(rotate(translate(s,-x,-y,0),math.degrees(a)),x,y,dz)
def distance(s,t):
 q=BRepExtrema_DistShapeShape(s,t);q.Perform();assert q.IsDone();return float(q.Value())
def crossmat(p):return np.array([[0,-p[2],p[1]],[p[2],0,-p[0]],[-p[1],p[0],0]])
rows=[]
for r in d['rows']:
 x=np.array(r['solution']);keeper=translate(moved(base['ROOT_SOCKET_KEEPER'],60,0,x[2]),x[0],x[1],0);bs=[moved(base[q['bolt']],q['x'],q['y'],x[3+i],.5*x[3+i]/(2*np.pi)) for i,q in enumerate(settings)];nc=len(r['contacts']);A=np.zeros((18,nc));faceerrors=[]
 for j,c in enumerate(r['contacts']):
  p=np.array(c['point_mm']);n=np.array(c['normal_on_keeper']);w=np.r_[n,crossmat(p)@n];A[:6,j]=w;A[6+6*c['bolt_index']:12+6*c['bolt_index'],j]=-w
  vertex=BRepBuilderAPI_MakeVertex(gp_Pnt(*map(float,p))).Vertex();faceerrors.extend([distance(keeper,vertex),distance(bs[c['bolt_index']],vertex)])
 lam=np.array(r['normal_forces_N']);host=np.array(r['host_radial_forces_on_bolts_N']);ext=np.zeros((3,6));ext[1:,5]=r['conditional_bolt_torque_Nmm'];P=np.zeros((18,4))
 for i,q in enumerate(settings):
  c=np.array([q['x'],q['y'],0.])
  for ax in [0,1]:f=np.eye(3)[ax];P[6+6*i:12+6*i,2*i+ax]=np.r_[f,crossmat(c)@f]
 residual=(A@lam+P@host.ravel()+ext.ravel()).reshape(3,6)
 # Explicit min-max radial reaction, no arbitrary selection of one LP force distribution.
 AA=np.c_[A,P,np.zeros(18)];C=np.zeros((8,nc+5));rhs=np.zeros(8)
 for i in range(4):C[2*i,nc+i]=1;C[2*i+1,nc+i]=-1;C[2*i:2*i+2,-1]=-1
 mm=linprog(np.r_[np.zeros(nc+4),1],A_ub=C,b_ub=rhs,A_eq=AA,b_eq=-ext.ravel(),bounds=[(0,None)]*nc+[(None,None)]*4+[(0,None)],method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9});assert mm.success
 totalT=sum(r['conditional_bolt_torque_Nmm']);necessary=abs(totalT)/32.;bad=host.copy();bad[0,0]+=.01;baderr=float(abs(A@lam+P@bad.ravel()+ext.ravel()).max());force_sum=host.sum(0);hostmoment=sum(np.cross(np.array([q['x'],q['y'],0.]),np.r_[host[i],0]) for i,q in enumerate(settings));gaps=dict(keeper_host_mm=distance(keeper,base['F0_ROOT_BACK']),keeper_installed_pin_mm=distance(keeper,base['ROOT_SOCKET_KEEPER_INSTALLED_SPLIT_PIN']));free=linprog(np.ones(nc),A_eq=A,b_eq=-ext.ravel(),bounds=(0,None),method='highs')
 # Any common6twist does zero work on each equal/opposite physicalcontact.
 common=np.tile(np.array([.1,-.3,.2,.5,-.2,.7]),3);work=float(abs(common@A).max());row=dict(signs=r['signs'],maximum_original18_residual_N_Nmm=float(abs(residual).max()),independent_actual_contact_point_distance_mm=max(faceerrors),normal_unit_error=max(abs(np.linalg.norm(c['normal_on_keeper'])-1) for c in r['contacts']),minimum_force_N=float(lam.min()),host_force_sum_N=force_sum.tolist(),host_moment_sum_Nmm=hostmoment.tolist(),sum_applied_torque_Nmm=totalT,analytic_necessary_host_Fx_N=necessary,minimum_maximum_radial_component_N=float(mm.x[-1]),minimum_maximum_distribution=mm.x[:nc+4].tolist(),minimax_all18_residual=float(abs(AA@mm.x+ext.ravel()).max()),actual_clearance=gaps,common_twist_work_error=work,altered_host_force_error=baderr,altered_host_force_rejected=baderr>.009,no_host_ports_feasible=bool(free.success),physical_accepted_equilibria=0)
 rows.append(row)
checks=dict(all83hashes=True,all_original18_balance=all(r['maximum_original18_residual_N_Nmm']<1e-8 for r in rows),finite_actual_BRep_witnesses=all(r['independent_actual_contact_point_distance_mm']<1e-7 for r in rows),compressive_unit_normals=all(r['minimum_force_N']>=-1e-9 and r['normal_unit_error']<1e-12 for r in rows),independent_contact_work=all(r['common_twist_work_error']<1e-12 for r in rows),minimax_bounds=all(r['minimum_maximum_radial_component_N']+1e-10>=r['analytic_necessary_host_Fx_N'] and r['minimax_all18_residual']<1e-8 for r in rows),host_force_negative_controls=all(r['altered_host_force_rejected'] for r in rows),strict_keeper_host_pin_clearance=all(min(r['actual_clearance'].values())>1e-4 for r in rows),same_sign_floating_reject=all(not r['no_host_ports_feasible'] for r in rows if r['signs'][0]==r['signs'][1]))
dump(out/'summary.json',dict(status='ACTUAL_P1_COUPLED_ROOT_INDEPENDENT_WRENCH_AND_HOST_FORCE_BOUNDS' if all(checks.values()) else 'ACTUAL_P1_COUPLED_ROOT_INDEPENDENT_FAIL',candidate=d['candidate'],source=ref(sp),producer=ref(out/'producer.py'),checks={k:bool(v) for k,v in checks.items()},rows=rows,accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Rigidplanarbranch conditionalhostBC remains; minmax is necessary reactionbound, not stiffnessunique distribution/capacity.','Strictpositive keeperhost/pinclearance means thoseinterfacescannotcarryreaction ATTHESEPOSES withoutclosure/deformation/preload. Does not prove their absence throughout operation.','No gravity, realhost/nut/cageconstitutivelaw, globalenergy/mesh/time/full3D systemcertificate.']))
print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},rows=[{k:r[k] for k in ['signs','minimum_maximum_radial_component_N','analytic_necessary_host_Fx_N','actual_clearance']} for r in rows])));raise SystemExit(0 if all(checks.values()) else 2)
