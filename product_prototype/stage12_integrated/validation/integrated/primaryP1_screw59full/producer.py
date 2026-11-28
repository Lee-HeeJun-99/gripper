"""Actual new P1 retained M3 geometry: screw spin, torque and conditional rod bounds.
No physical thread/preload coefficient or actual connector law is certified.
"""
import sys,json,math,shutil
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_contacts59c';sd=json.loads((src/'summary.json').read_text());cp=REPO/sd['candidate']['path'];cad=json.loads(cp.read_text());L=json.loads((src/'load_ledger.json').read_text());patches=json.loads((src/'patches.json').read_text());ports=json.loads((src/'connector_ports.json').read_text());names=L['body_names'];external=np.array(L['external_wrench_N_Nm']).ravel();a=.5/(2*np.pi);E=200000.;nu=.3;G=E/(2*(1+nu));dc=3-1.226869*.5;Ac=np.pi*dc*dc/4;Jc=np.pi*dc**4/32;geometry=[]
for port in ports['ports']:
 if port['label'].startswith('through'):continue
 bolt,nut=port['part_IDs'];bb=bounds(read(REPO/cad['part_references'][bolt]['path']));nb=bounds(read(REPO/cad['part_references'][nut]['path']));head=-3 if bolt.startswith('F0_RF') else 29;lo=max(bb[2],nb[2]);hi=min(head,nb[5]);eng=hi-lo;free=head-hi
 assert eng>0 and free>0
 # Exact 1D rod integral for uniformly distributed thread axial/torque traction:
 # N/F=1 on free shank, linear0..1 over engagement. integral(N/F)^2 dz=free+eng/3.
 # Uniform traction and basic core are explicit conditional assumptions, not a thread-law certificate.
 c=(free+eng/3)/(E*Ac);ct=(free+eng/3)/(G*Jc);geometry.append(dict(label=port['label'],bolt=bolt,nut=nut,bolt_STEP=cad['part_references'][bolt],nut_STEP=cad['part_references'][nut],actual_headseat_z_mm=head,actual_nut_z_interval_mm=nb[2::3],actual_overlap_mm=eng,free_shank_mm=free,pitch_mm=.5,basic_minor_core_d_mm=dc,basic_core_area_mm2=Ac,conditional_E_MPa=E,conditional_G_MPa=G,conditional_axial_compliance_mm_N=c,conditional_torsional_compliance_rad_Nmm=ct,thread_load_distribution='Uniform along actual overlap; not solved flank pressure',source_minimum_qualified=False))
seats={q['port']:q['area_mm2'] for q in ports['actual_seats'] if 'NUT' not in q['part_ID']};results=[]
def col(ni,nj,p,f,couple=None):
 p=np.array(p)*.001;f=np.array(f);w=np.r_[f,np.cross(p,f)];w[3:]+=np.zeros(3) if couple is None else couple;z=np.zeros((5,6));z[names.index(ni)]+=w;z[names.index(nj)]-=w;return z.ravel()
for contact_mu,head_mu in [(0,0),(0,.02),(0,.03),(.1,0),(.1,.02),(.1,.03),(.1,.05)]:
 columns=[];meta=[]
 for patch in patches:
  n=np.array(patch['normal_on_i'],float);axes=[i for i in range(3) if i!=patch['axis']]
  for cell in patch['cells']:
   for axis,sgn in [(axes[0],1),(axes[0],-1),(axes[1],1),(axes[1],-1)] if contact_mu else [(axes[0],0)]:
    f=n.copy();f[axis]+=sgn*contact_mu;columns.append(col(patch['body_i'],patch['body_j'],cell['point_mm'],f));meta.append(dict(label=patch['label'],kind='normal_contact_ray',body_i=patch['body_i'],body_j=patch['body_j'],point_mm=cell['point_mm'],direction=f.tolist(),couple_Nm_per_N=[0,0,0]))
 port_indices=[]
 for port in ports['ports']:
  # Add physical equal/opposite screw torque on clamped upperbody/nut cage.
  # Thread friction=0, hence head torque=aF. Head friction cannot be omitted.
  screw=not port['label'].startswith('through');j=len(columns);port_indices.append((j,port,screw));columns.append(col(port['body_i'],port['body_j'],port['point_mm'],port['direction'],[0,0,a*.001] if screw else None));meta.append(dict(port,kind='screw_axial_plus_helix_torque' if screw else 'unresolved_M5_axial_port',couple_Nm_per_N=[0,0,a*.001] if screw else [0,0,0]))
 A=np.array(columns).T;H=np.zeros((30,6));H[-6:]=np.eye(6);B=np.c_[A,H];ub=[]
 for j,port,screw in port_indices:
  if not screw:continue
  # Actual seat outer-radius bound: the original head is r2.75mm.
  # |M|<=mu*rmax*F is a necessary bound for ANY nonnegative pressure,
  # not a uniform-pressure assumption or actual friction measurement.
  row=np.zeros(B.shape[1]);row[j]=a-head_mu*2.75;ub.append(row)
 scale=np.tile([1,1,1,100,100,100],5);r=linprog(np.r_[np.ones(A.shape[1]),np.zeros(6)],A_eq=scale[:,None]*B,b_eq=-scale*external,A_ub=np.array(ub),b_ub=np.zeros(len(ub)),bounds=[(0,None)]*A.shape[1]+[(None,None)]*6,method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9});q=dict(contact_mu_ASSUMED=contact_mu,head_mu_ASSUMED=head_mu,thread_mu_ASSUMED=0,feasible=bool(r.success),message=r.message,scope='Necessary torque-aware cut reactions ONLY; cages assumed at backlash limit, no fixed screw rotation or actual preload. Ultimatehost still unknown6resultant. FourM5 laws unresolved.')
 if r.success:
  residual=(B@r.x+external).reshape(5,6);loads=[]
  for j,port,screw in port_indices:
   if not screw:continue
   F=float(r.x[j]);g=next(q for q in geometry if q['label']==port['label']);loads.append(dict(label=port['label'],required_axial_N=F,required_head_and_cage_torque_Nmm=a*F,conditional_rod_extension_mm=g['conditional_axial_compliance_mm_N']*F,conditional_rod_twist_rad=g['conditional_torsional_compliance_rad_Nmm']*a*F,head_mean_normal_pressure_MPa=F/seats[port['label']],conditional_basic_core_axial_stress_MPa=F/Ac))
  q.update(force_residual_N=float(np.linalg.norm(residual[:,:3],axis=1).max()),moment_residual_Nm=float(np.linalg.norm(residual[:,3:],axis=1).max()),required_ports=loads,all_reactions=[dict(m,coefficient_N=float(v)) for m,v in zip(meta,r.x[:len(meta)]) if v>1e-12],required_unknown_host_wrench_N_Nm=r.x[-6:].tolist())
 results.append(q)
# Full screw generalized energy has a real free spin/advance mode.
# y=[relative axial displacement mm, head relative rotation rad].
k=1/geometry[0]['conditional_axial_compliance_mm_N'];b=np.array([1.,-a]);K=k*np.outer(b,b);v=np.array([a,1.]);free_mode=K@v
rp=(3-.6495190528*.5)/2;tanlambda=a/rp;mu_t_crit=tanlambda*math.cos(math.pi/6);uniformR=(2/3)*(2.75**3-1.5**3)/(2.75**2-1.5**2)
# Independent quadrature confirms derived rod compliance integral (not global energy).
z,w=np.polynomial.legendre.leggauss(12);quadrature=[]
for q in geometry:
 eng=q['actual_overlap_mm'];vint=q['free_shank_mm']+eng/2*sum(w*((z+1)/2)**2);quadrature.append(abs(vint/(E*Ac)-q['conditional_axial_compliance_mm_N']))
checks=dict(canonical77=len(cad['part_references'])==77 and all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values()),actual_six_positive_engagements=len(geometry)==6 and all(q['actual_overlap_mm']>0 for q in geometry),all_rod_integrals_verified=max(quadrature)<1e-15,free_screw_mode_retained=np.linalg.norm(free_mode)<1e-8,frictionless_free_head_rejected=all(not q['feasible'] for q in results if q['head_mu_ASSUMED']==0),insufficient_head_friction_rejected=all(not q['feasible'] for q in results if q['head_mu_ASSUMED']==.02),all_admitted_cut_balance=all(q['force_residual_N']<1e-8 and q['moment_residual_Nm']<1e-10 for q in results if q['feasible']))
dump(out/'actual_connectors.json',geometry);dump(out/'torque_cases.json',results);dump(out/'summary.json',dict(status='ACTUAL77_SCREW_SPIN_AND_GEOMETRIC_COMPLIANCE_BOUNDS_VERIFIED_NOT_CONNECTOR_CERTIFICATION' if all(checks.values()) else 'ACTUAL77_SCREW_BOUNDS_REJECTED',candidate=ref(cp),producer=ref(out/'producer.py'),source=ref(src/'summary.json'),checks={k:bool(v) for k,v in checks.items()},actual_connector_geometry=ref(out/'actual_connectors.json'),necessary_torque_cases=ref(out/'torque_cases.json'),screw_lead_mm_rad=a,source_backed_pitch_mm=.5,thread_source=ref(ROOT/'models/standard_drive/primary_captive_sources59/thread_reviewed.json'),head_friction_absolute_necessary_min=a/2.75,uniform_annular_pressure_mu_head_contrast=a/uniformR,thread_friction_selflock_threshold_basic_profile=mu_t_crit,screw_free_mode=dict(coordinates=['relative_axial_mm','relative_head_rotation_rad'],tangent_N_mm_mixed=K.tolist(),null_mode=v.tolist(),residual=float(np.linalg.norm(free_mode)),meaning='Free head can advance screw bypitch/(2pi) with zero conditionalaxialstrain. Captive nut DOESNOT eliminate boltspin; scalar axial spring alone invents rotationalrestraint.'),nut_backlash_induced_lead_mm=a*math.radians(2.650594711303711),physical_coefficients_measured=False,preload_implemented=False,full77compliant_contact_solved=False,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Conditional1D rod with basiccore and uniformengagement load;NOT actual3D threadedbolt/head/nut/flank/cage elastic response or source-minimum strength. Localquadrature identity NOTglobalstoredenergyclosure.','TwistDOF retained and torque-aware necessarycuts only. Head/threadfriction/preload/locking coefficients not known or qualified; assumedmu cases never actual capacities or accepted equilibria.','Cage firstcontact has no finitearea capacity; assumingbacklashlimit for necessarybounds not an implemented coupled pose. Requiredhost6resultant not realhost attachment.','All22originalgates,mesh1percent/time.1percent/globalenergy/final3Finger unchanged.']))
print((out/'summary.json').read_text());raise SystemExit(0 if all(checks.values()) else 2)
