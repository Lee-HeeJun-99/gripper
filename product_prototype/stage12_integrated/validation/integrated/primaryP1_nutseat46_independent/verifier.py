"""Independent polygon/BRep audit of actual eight pockets and unchanged ground keys.
Includes conditional finite-height screw cone screening, never product capacity.
"""
import sys,json,shutil,math
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,volume,common,bounds,overlap,translate
from mechanisms_stage1 import hex_axis
from primary_nutseat46b import STATIONS
from validate_nutseat46b import rotate

def poly_area(v):
 return abs(sum(np.cross(v[i],v[(i+1)%len(v)]) for i in range(len(v))))/2 if len(v)>2 else 0.
def clipped_area(AF,a):
 v=[np.array([AF/math.sqrt(3)*math.cos(k*math.pi/3+a),AF/math.sqrt(3)*math.sin(k*math.pi/3+a)]) for k in range(6)]
 for k in range(6):
  n=np.array([math.cos(math.pi/6+k*math.pi/3),math.sin(math.pi/6+k*math.pi/3)]);w=[]
  for i,u in enumerate(v):
   q=v[(i+1)%len(v)];du=np.dot(n,u)-4.1;dq=np.dot(n,q)-4.1
   if du<=0:w.append(u)
   if (du<0<dq) or (dq<0<du):w.append(u+(q-u)*du/(du-dq))
  v=w
 return poly_area(v)
def solve_thread(lo,hi,r,mu,nperturn=32):
 # A loaded nominal60degree flank at r. Right-hand helix uses z=k*theta.
 # Its normal is perpendicular to both radial-flank and helical tangent.
 # Three complete translational and rotational contact columns are retained.
 p=.8;k=p/(2*math.pi);s=1/math.sqrt(3);count=int(math.floor((hi-lo)/p*nperturn));theta=(np.arange(count)+.5)*2*math.pi/nperturn
 z=lo+k*theta;theta=theta[z<hi];z=z[z<hi];er=np.array([np.cos(theta),np.sin(theta),np.zeros(len(theta))]).T;et=np.array([-np.sin(theta),np.cos(theta),np.zeros(len(theta))]).T;ez=np.array([0.,0.,1.]);n=-s*er-k/r*et+ez;n/=np.linalg.norm(n,axis=1)[:,None]
 t1=et+k/r*ez;t1/=np.linalg.norm(t1,axis=1)[:,None];t2=np.cross(n,t1)
 positions=r*er;positions[:,2]=z-(lo+hi)/2;angles=np.arange(16)*2*math.pi/16
 f=n[:,None,:]+mu*(np.cos(angles)[None,:,None]*t1[:,None,:]+np.sin(angles)[None,:,None]*t2[:,None,:]);mom=np.cross(positions[:,None,:],f);A=np.concatenate([f,mom],axis=2).reshape(-1,6).T;target=np.array([0,0,1.,0,0,0]);res=linprog(np.ones(A.shape[1]),A_eq=A,b_eq=target,bounds=(0,None),method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
 # A free ideal screw displacement is a separating virtual-work direction
 # at mu=0. This directly bounds torque mismatch without assuming equilibrium.
 work=np.r_[np.zeros(3),[0,0,1.]];work[2]=k;normalwork=float(np.max(abs(np.concatenate([n,np.cross(positions,n)],axis=1)@work)))
 return dict(mu_assumed=mu,contact_points=len(theta),cone_rays=A.shape[1],feasible=bool(res.success),residual=None if not res.success else float(np.max(abs(A@res.x-target))),normal_force_sum_N=None if not res.success else float(sum(res.x)),thread_normal_screw_virtual_work_error=normalwork,mu_is_source_guaranteed=False)
def main():
 out=ROOT/'validation/integrated/primaryP1_nutseat46_independent';out.mkdir();shutil.copyfile(__file__,out/'verifier.py');cp=ROOT/'cad/exports/primaryP1_nutseat46b/summary.json';d=json.loads(cp.read_text());old=json.loads((ROOT/'cad/exports/primaryP1_benchattachment45/summary.json').read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values());parts={n:read(REPO/r['path']) for n,r in d['part_references'].items()};valid=json.loads((ROOT/'validation/integrated/primaryP1_nutseat46_validation2/summary.json').read_text());rows=[]
 for prefix,i,x,y,z0,z1,parent in STATIONS:
  assert not(ROOT/'runtime/STOP').exists()
  for AF,height in [(8.,4.7),(7.78,4.4)]:
   nut=parts[f'{prefix}_NUT_{i}'] if AF==8 else __import__('incremental_stage1').cut(hex_axis((x,y,z0),(0,0,1),AF,height),__import__('incremental_stage1').cyl(2.5,(x,y,z0-.01),height+.02))
   stop=next(r['zero_contact_angle_rad'] for r in valid['nut_yaw_stops'] if r['part']==f'{prefix}_NUT_{i}' and r['AF_mm']==AF and r['sign']==1)
   for sign in [-1,1]:
    a=sign*(stop+.001);actual=common(rotate(nut,x,y,a),parts[parent]);analytic=(math.sqrt(3)/2*AF*AF-clipped_area(AF,a))*height
    rows.append(dict(part=f'{prefix}_NUT_{i}',AF_mm=AF,angle_rad=a,BRep_mm3=actual,analytic_mm3=analytic,error_mm3=abs(actual-analytic)))
 unchanged=[n for n in old['part_references'] if old['part_references'][n]==d['part_references'][n]];changedvol=[]
 for row in d['changed']:
  n=row['part_ID'];v0=volume(read(REPO/old['part_references'][n]['path']));v1=volume(parts[n]);changedvol.append(dict(part_ID=n,old_mm3=v0,new_mm3=v1,added_mm3=v1-v0,physical_mass_kg=None,density_minimum_kg_m3=None))
 # Re-run complete moving-versus-fixed assembly near actual old key stops
 # with changed stand and plate;all pairs retained,not only key coupons.
 fixed={n for n in parts if n.startswith('BENCH_THROUGH_')}|{'EXTERNAL_BENCH_PLATE'};bb={n:bounds(parts[n]) for n in fixed};relative=[]
 modes=[('X-',lambda sh:translate(sh,-.099,0,0)),('X+',lambda sh:translate(sh,.099,0,0)),('Y-',lambda sh:translate(sh,0,-.099,0)),('Y+',lambda sh:translate(sh,0,.099,0))]
 angle=.001961087206957
 for sign in [-1,1]:modes.append((f'yaw{sign}',lambda sh,sign=sign:rotate(sh,20,-5,sign*(angle-1e-6))))
 for name,trans in modes:
  hits=[];pairs=0
  for n,s in parts.items():
   if n in fixed:continue
   sh=trans(s);b=bounds(sh)
   for m in fixed:
    if overlap(b,bb[m]):
     pairs+=1;v=common(sh,parts[m])
     if v>1e-8:hits.append(dict(moving=n,fixed=m,mm3=v))
  relative.append(dict(mode=name,moving_parts=103,fixed_parts=9,exact_pairs=pairs,hits=hits))
 # Installed bolt/nut finite-height flank mathematical contrast. Radius is
 # source-nominal pitch radius,not major diameter and not a claimed tolerance.
 # Actual8stacks have identical4.7mm nominal overlap but different positions.
 screw=[]
 for prefix,i,x,y,z0,z1,parent in STATIONS:
  r=(5-.649519052838329*.8)/2;k=.8/(2*math.pi);crit=k/r/math.sqrt(1+1/3)
  trials=[solve_thread(z0,z1,r,mu) for mu in [0.,.03,.06,.1]]
  screw.append(dict(bolt_ID=f'{prefix}_BOLT_{i}',nut_ID=f'{prefix}_NUT_{i}',actual_nut_interval_mm=[z0,z1],nominal_pitch_radius_mm=r,nominal_axial_thread_overlap_mm=z1-z0,effective_engagement_mm=None,pointwise_circular_cone_selflocking_threshold_mu=crit,friction_trials=trials,law_adopted_for_physical_product=False))
 # Core and class screening is explicitly conditional;current bolt is only
 # labelled A2. No arbitrary A2-70 property minimum is assigned to it.
 d2=5-.649519052838329*.8;d3=5-1.226869322027955*.8;As=math.pi/4*((d2+d3)/2)**2;Ac=math.pi*d3*d3/4
 screening=dict(nominal_pitch_diameter_mm=d2,nominal_core_diameter_mm=d3,nominal_core_area_mm2=Ac,nominal_tensile_stress_area_mm2=As,major_area_mm2=math.pi*25/4,nominal_core_stress_MPa_per_N=1/Ac,nominal_stress_area_MPa_per_N=1/As,conditional_class70_bolt_Rp02_MPa=450,conditional_class70_bolt_Rm_MPa=700,conditional_class70_bolt_02proof_N=As*450,current_bolt_class_guaranteed=False,current_bolt_minimum_capacity_N=None,actual_nut_catalog_class='A4-70',nut_class70_proof_stress_MPa=700,nut_nominal_assembly_proof_N=As*700,actual_nut_certificate=None,installed_stack_capacity_N=None,reason='Catalog nutclass is source-backed;boltpropertyclass notestablished. Nominal stressareabounds do not establish nutflankbearing/strip/coretolerance/fatigue/preload/assembly or supportcapacity.')
 checks=dict(independent_hex_contact_volume=max(r['error_mm3'] for r in rows)<1e-7,unchanged110partSTEP=len(unchanged)==110,positive_added_volume=all(r['added_mm3']>0 for r in changedvol),actual_full_assembly_key_travel=all(not r['hits'] for r in relative),finite_screw_rejects_zero_and_low_friction=all(not t['feasible'] for r in screw for t in r['friction_trials'] if t['mu_assumed']<=.03),finite_screw_conditional_friction_transfer=all(t['feasible'] and t['residual']<1e-8 for r in screw for t in r['friction_trials'] if t['mu_assumed']>=.06),screw_normal_virtual_work=all(t['thread_normal_screw_virtual_work_error']<1e-12 for r in screw for t in r['friction_trials']))
 result=dict(status='ACTUAL_P1_NUT_CONTACT_AND_CONDITIONAL_THREAD_AUDIT_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_NUT_CONTACT_THREAD_AUDIT_FAIL',candidate=ref(cp),verifier=ref(out/'verifier.py'),checks=checks,independent_polygon_BRep=rows,unchanged_old_part_STEP_count=len(unchanged),changed_volume=changedvol,actual_complete_assembly_relative_modes=relative,eight_installed_thread_scenarios=screw,source_nominal_core_and_class_screening=screening,accepted_physical_product_equilibria=0,physical_operating_sourcefield=None,system_mesh_pass=False,time_convergence_pass=False,global_energy_pass=False,whole_system_release=False,source_review=ref(ROOT/'models/standard_drive/primary_thread_sources46/reviewed.json'),limitations=['FiniteheighthelicoidCoulombcone is source-nominal mathematical contrast bound to actualeightstackcoordinates;not implementedflanks/fit/preload orvalidated physicalconnector','No sourceguaranteedthreadfrictionminimum available;mu.06/.1 are assumptions,notcapacity orvibrationlocking','Bolt propertyclass not inferred from A2;source-backed class70values remain conditional','110otherpartSTEP unchanged does not propagate supportFE/contact/mass approval;keys revalidated only geometrictravel','Ultimateexternalplateattachment,operating100gfriction/Fingerdeflection demand andall22gates remain open'])
 dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,polygon_error=max(r['error_mm3'] for r in rows),relative_hits=[r for r in relative if r['hits']],screw=screw[0],screening=screening)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
