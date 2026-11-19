"""Offline analysis of actual saved Newton matrix, correction and rejected trial."""
import argparse,csv,json,shutil
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu,LinearOperator,onenormest
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text())
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('archived diagnostic raw mismatch')
 v=np.genfromtxt(src/'failure_on/trials.csv.vectors.csv',delimiter=',',names=True);rows=np.genfromtxt(src/'failure_on/trials.csv.matrix.csv',delimiter=',',names=True);n=len(v);A=coo_matrix((rows['value'],(rows['row'].astype(int),rows['col'].astype(int))),shape=(n,n)).tocsc();lu=splu(A);inverse=LinearOperator((n,n),matvec=lu.solve,rmatvec=lambda x:lu.solve(x,trans='T'));condition=float(abs(A).sum(axis=0).max()*onenormest(inverse));last=m['last_trial'];alpha=float(last['alpha']);predicted=alpha*(A@v['delta']);actual=v['trial_residual']-v['residual'];i=int(np.argmax(abs(v['residual'])));out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 r=dict(status='ANALYZED',scope='offline actual rejected Newton trial;condition estimate is not a proof or convergence waiver',source_summary_sha256=sha(src/'summary.json'),tangent_dimension=n,tangent_nonzeros=A.nnz,estimated_condition_one_norm=condition,linear_residual_Ns=float(np.linalg.norm(A@v['delta']+v['residual'])),relative_linear_residual=float(np.linalg.norm(A@v['delta']+v['residual'])/np.linalg.norm(v['residual'])),actual_trial_change_Ns=float(np.linalg.norm(actual)),linear_predicted_trial_change_Ns=float(np.linalg.norm(predicted)),trial_linearization_discrepancy_Ns=float(np.linalg.norm(actual-predicted)),unchanged_components=int(np.count_nonzero(v['state']==v['trial'])),dominant_residual=dict(index=i,stage=i//649,reduced_DOF=i%649,partition='Skin' if i%649<295 else 'Rail',value_Ns=float(v['residual'][i])),tolerance_unchanged_Ns=1e-24,physical_state_correction='NONE',conclusion='Accurate linear solve does not produce the predicted residual decrease at this representable trial. Floating-point/force-value evaluation requires further isolation;not evidence to relax physical gates.')
 write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
