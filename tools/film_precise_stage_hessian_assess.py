"""Recover implied mechanical stage Hessians from saved Newton blocks;no rerun."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,json,re,shutil
import numpy as np
from scipy.sparse import coo_matrix
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261119_precise_newton_diagnostic1726';sm=json.loads((src/'summary.json').read_text());linear=ROOT/'results/autonomous_film_20261119_precise_linear_response1707';lm=json.loads((linear/'summary.json').read_text());matrix=linear/'matrix/process/stdout.log'
 for f,d in sm['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('saved actual Newton evidence changed')
 if sha(matrix)!=lm['raw_hashes']['matrix/process/stdout.log']:raise ValueError('archived public projected mass dump changed')
 command=json.loads((linear/'matrix/process/command.json').read_text());mass=ROOT/'results/autonomous_film_20261119_precise_tendon_gauss1715/public_mass.txt'
 if sha(command[1])!=sha(mass):raise ValueError('public mass input differs from precise tendon fixture')
 header=src/'sources/models/film_c2_startup/Gauss4.h'
 if sha(header)!=sm['source_hashes']['models/film_c2_startup/Gauss4.h']:raise ValueError('actual assembled tableau source changed')
 text=re.search(r'double a\[4\]\[4\]=\{(.*?)\};',header.read_text(),re.S).group(1);A=np.array([float(x) for x in re.findall(r'[-+]?\d*\.\d+(?:[eE][-+]?\d+)?',text)]).reshape(4,4);inverse=np.linalg.inv(A);dump=np.fromstring(matrix.read_text(),sep=' ');n=int(dump[0]);M=np.diag(dump[1:1+n]);h=float(sm['last_trial']['h']);rows=np.genfromtxt(src/'failure_on/trials.csv.matrix.csv',delimiter=',',names=True);J=coo_matrix((rows['value'],(rows['row'].astype(int),rows['col'].astype(int))),shape=(4*n,4*n)).toarray();B=np.empty((4,4,n,n))
 for i in range(4):
  for k in range(4):B[i,k]=(J[i*n:(i+1)*n,k*n:(k+1)*n]-(M if i==k else 0)-2*h*A[i,k]*M)/(h*h)
 K=[];estimates=[]
 for j in range(4):
  candidates=[sum(inverse[j,i]*B[i,k] for i in range(4))/A[j,k] for k in range(4)];chosen=int(np.argmax(abs(A[j])));H=candidates[chosen];K.append(H);eigen=np.linalg.eigvalsh((H+H.T)/2);estimates.append(dict(stage=j,chosen_column=chosen,minimum_symmetric_eigenvalue_N_mm=float(eigen[0]),maximum_symmetric_eigenvalue_N_mm=float(eigen[-1]),estimated_symmetric_condition=float(abs(eigen[-1]/eigen[0])),asymmetry_Frobenius_N_mm=float(np.linalg.norm(H-H.T)),cross_column_disagreement_Frobenius_N_mm=max(float(np.linalg.norm(x-H)) for x in candidates)))
 rebuilt=np.empty_like(J)
 for i in range(4):
  for k in range(4):rebuilt[i*n:(i+1)*n,k*n:(k+1)*n]=(M if i==k else 0)+2*h*A[i,k]*M+h*h*sum(A[i,j]*A[j,k]*K[j] for j in range(4))
 error=float(np.linalg.norm(rebuilt-J)/np.linalg.norm(J));out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');r=dict(status='RECONSTRUCTED_DIAGNOSTIC' if error<=1e-12 else 'FAIL',scope='algebraic mechanical Hessian estimates implied by observed failed-trial stage matrix;NOT fresh force/Hessian API/FD or physics qualification',source_Newton_summary_sha256=sha(src/'summary.json'),source_mass_dump_sha256=sha(matrix),public_mass_sha256=sha(mass),actual_tableau_sha256=sha(header),h_s=h,relative_stage_matrix_reconstruction_error=error,stage_estimates=estimates,derivation='B_ik=(J_ik-delta_ik*M-2*h*a_ik*M)/h^2;sum_i(A^-1)_ji*B_ik=a_jk*K_j',warning='Subtraction/inversion introduce rounding;cross-column discrepancy is not a rigorous error bound. Symmetrization is diagnostic only,NEVER fed to solver. Do not confuse mechanical K conditioning with dynamic stage J conditioning.');write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
