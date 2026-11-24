"""Conditional static LP from measured response wrench columns,not grasp PASS.
Only complete nonzero multiplier triplets allow J reconstruction;missing rows
are NOT fabricated. No detector normal inference or synthetic contact point.
"""
import argparse,csv,json,subprocess,sys
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
from analyse import BASE,sha
from native_bending_coupon import guarded

def cone_lp(columns,weight,mu=.3):
 if not columns:return dict(status='NOT MEASURED_NO_COMPLETE_COLUMNS',minimum_normal_sum_N=None)
 rays=[]
 for G in columns:
  for angle in np.arange(8)*np.pi/4:rays.append(G[:,0]+mu*(np.cos(angle)*G[:,1]+np.sin(angle)*G[:,2]))
 A=np.array(rays).T;b=np.array([0,0,weight,0,0,0.]);r=linprog(np.ones(len(rays)),A_eq=A,b_eq=b,bounds=(0,None),method='highs')
 return dict(status='CONDITIONAL_STATIC_SUBSET_FEASIBLE' if r.success else 'CONDITIONAL_STATIC_SUBSET_LP_FAILED',solver_message=r.message,minimum_normal_sum_N=float(r.fun) if r.success else None,force_residual_N=float(abs((A@r.x-b)[:3]).max()) if r.success else None,moment_residual_Nm=float(abs((A@r.x-b)[3:]).max()) if r.success else None)

def assess(case,mass):
 src=BASE/'results'/case;objects=list(csv.DictReader((src/'object.csv').open()));times=[float(r['time_s']) for r in objects];chosen=[min(times,key=lambda t:abs(t-target)) for target in (1.1,1.4,1.8)];groups={t:{} for t in chosen};seen=set()
 with (src/'response_rows.csv').open() as f:
  for r in csv.DictReader(f):
   t=float(r['time_s']);models=r['model0']+r['model1']
   if t not in groups or '/object/'not in models or 'skinCollision'not in models:continue
   row=int(r['row_id']);key=(t,row);assert key not in seen;seen.add(key);offset=row-int(r['first_row']);group=(r['constraint_path'],offset//3);groups[t].setdefault(group,{})[offset%3]=(float(r['lambda_Ns']),np.fromstring(r['object_impulse_Ns_Nms'],sep=' '))
 records=[]
 for t in chosen:
  cols=[];rejected=0;budget=0.;allnormal=0.;orth=[]
  for g in groups[t].values():
   if 0 in g:allnormal+=g[0][0]/.0025
   if set(g)!={0,1,2} or any(g[i][0]==0 for i in range(3)):rejected+=1;continue
   G=np.column_stack([g[i][1]/g[i][0] for i in range(3)])
   error=float(abs(G[:3].T@G[:3]-np.eye(3)).max());orth.append(error)
   if error>1e-8:rejected+=1;continue
   cols.append(G);budget+=g[0][0]/.0025
  r=cone_lp(cols,mass*9.81);r.update(actual_time_s=t,total_skin_contact_groups=len(groups[t]),complete_reconstructed_groups=len(cols),rejected_or_zero_multiplier_groups=rejected,measured_normal_sum_all_groups_N=allnormal,measured_normal_sum_complete_groups_N=budget,max_reconstructed_basis_orthogonality_error=max(orth) if orth else None)
  records.append(r)
 return dict(case=case,mass_kg=mass,records=records,input_hashes={f:sha(src/f) for f in ('object.csv','response_rows.csv','scene.scn')})

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag
 if not a.worker:
  out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(guarded([sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'],out/'process',60)));return
 d=dict(status='HISTORICAL_RESPONSE_CONE_REFERENCE_ONLY',records=[assess('b3_alarm_window485',.05),assess('b3_mass100_explore1059',.1)],friction_assumption=.3,polygon='8-ray inscribed cone;linearized static frozen measured basis',scope='Incomplete active-contact subset only. Feasible LP proves only force/moment equilibrium in frozen subset model,not capacity,stability or newholding. Failed subset LP does not prove full-contact infeasibility. Actual Native time/mesh and solver-limit failures retained. Measured normal sum is not actuator capacity.',physical_validation='NOT QUALIFIED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
