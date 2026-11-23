"""Compare identical actual20ms windows;no interpolation or velocity resets."""
import argparse,csv,itertools,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def load(case,count=100):
 src=BASE/'results'/case;m=json.loads((src/'mesh.json').read_text());q0=np.array(m['q0']);lo=np.flatnonzero((q0[:,2]==.0002)&(q0[:,0]>0));hi=lo-1;rr=[]
 for i in (0,1):
  with (src/f'layer{i}.csv').open() as f:rr.append(list(itertools.islice(csv.DictReader(f),count)))
 q=np.array([[np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in rs] for rs in rr]);v=np.array([[np.fromstring(r['v'],sep=' ').reshape(-1,3) for r in rs] for rs in rr]);times=np.array([float(r['time_s']) for r in rr[0]]);Cq=q[1][:,hi]-q[0][:,lo]-[0,0,.000002];Cv=v[1][:,hi]-v[0][:,lo]
 with (src/'constraints.csv').open() as f:cr=list(itertools.islice(csv.DictReader(f),count))
 impulses=[np.fromstring(r['impulses_Ns'],sep=' ') for r in cr];stats=dict(case=case,outputs=len(rr[0]),actual_last_time_s=float(times[-1]),max_Cq_abs_m=float(abs(Cq).max()),max_Cv_abs_m_s=float(abs(Cv).max()),max_solver_error=max(float(r['error']) for r in cr),max_solver_iterations=max(int(r['iterations']) for r in cr),row_counts=sorted(set(len(x) for x in impulses)),iteration_limit_outputs=sum(int(r['iterations'])>=1000 for r in cr),numeric_solver_tolerance=1e-10,input_hashes={str((src/f).relative_to(BASE)):sha(src/f) for f in ('scene.scn','preflight.json','layer0.csv','layer1.csv','constraints.csv')})
 return stats,q,v,times,impulses
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);base,qb,vb,tb,ib=load('layer_refined_interface1266');clean,qc,vc,tc,ic=load('layer_clean_unscaled1273');dirty,qd,vd,td,id_=load('layer_constraint_scale1270');assert np.array_equal(tb,tc) and np.array_equal(tc,td) and len(tc)==100;purity=dict(q=float(abs(qc-qd).max()),v=float(abs(vc-vd).max()),impulses_Ns=max(float(abs(a-b).max()) for a,b in zip(ic,id_)));d=dict(status='SAME_WINDOW_TERMINATION_DIAGNOSTIC_ONLY',scaled=base,unscaled=clean,explicit_link_vs_auto_link_unscaled_purity=purity,position_residual_reduction_factor=base['max_Cq_abs_m']/clean['max_Cq_abs_m'],velocity_residual_reduction_factor=base['max_Cv_abs_m_s']/clean['max_Cv_abs_m_s'],changed_only_normalization_after_link_purity=True,numeric_tolerance_relaxed=False,physical_validation='NOT QUALIFIED',time_convergence='NOT TESTED_BY_THIS_CONTRAST',source_sha256=sha(Path(__file__)),scope='Same actual100acceptedoutputs20ms,no interpolation. Explicitlink matches oldauto unscaled100steps q/v/impulses. Existing mesh/time/grasp/energy and old FAILs unchanged. New scaleTolerance flag is stricter termination,not a new physical model.');(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in d.items() if k not in ('scaled','unscaled')}));print(json.dumps([{k:v for k,v in r.items() if k!='input_hashes'} for r in (base,clean)]))
if __name__=='__main__':main()
