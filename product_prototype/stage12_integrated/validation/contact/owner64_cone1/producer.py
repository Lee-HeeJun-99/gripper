"""Test, rather than assume, that signed QR row reduction preserves contact cones.

Local linearized certificate only. No nonlinear contact row or state is changed.
Acceptance is relative cone reconstruction error <=1e-8 for EVERY original row.
"""
import argparse,json,shutil
from pathlib import Path
import numpy as np
from scipy.linalg import qr
from scipy.optimize import nnls
from baseline_registry import ROOT,ref,dump
import contact_rank_diagnostic as ranks

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    source=ROOT/'validation/finger'/a.input/'summary.json';d=json.loads(source.read_text());candidate=ROOT/'cad/exports/revAD_funnel1/summary.json'
    if d['candidate']!=ref(candidate):raise ValueError('Candidate mismatch')
    profile=json.loads(candidate.read_text())['funnel_profile'];out=ROOT/'validation/contact'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py');rows=[]
    for row in d['rows']:
        A=ranks.inspect(row,d['PET_free_length_m'],profile,True);sv=np.linalg.svd(A,compute_uv=False)
        rank=int(np.count_nonzero(sv>np.finfo(float).eps*max(A.shape)*sv[0]));_,_,piv=qr(A.T,pivoting=True,mode='economic');selected=piv[:rank];B=A[selected].T;records=[]
        for i,normal in enumerate(A):
            signed=np.linalg.lstsq(B,normal,rcond=None)[0];positive,residual=nnls(B,normal,maxiter=10000)
            records.append(dict(row=i,nonnegative_reconstruction_residual=float(residual),signed_reconstruction_residual=float(np.linalg.norm(B@signed-normal)),minimum_signed_coefficient=float(signed.min()),nonnegative_coefficients=positive.tolist()))
        maximum=max(r['nonnegative_reconstruction_residual'] for r in records)
        rows.append(dict(n=row['n'],original_rows=len(A),selected_rows=selected.tolist(),rank=rank,maximum_nonnegative_residual=maximum,criterion=1e-8,
            status='LOCAL_CONE_EQUIVALENCE_PASS' if maximum<=1e-8 else 'REJECTED_QR_CONTACT_REDUCTION',records=records,state_changed=False))
    if not rows:raise ValueError('Empty cone audit')
    result=dict(status='SCREEN_COMPLETE_NOT_RELEASE',scope='LOCAL NORMAL CONE vs SIGNED QR BASIS; NO CONTACT REMOVED',rows=rows,source=ref(source),candidate=ref(candidate),producer=ref(out/'producer.py'),Jacobian_builder=ref(Path(ranks.__file__)),product_release=False,limitations=['A local cone certificate does not establish nonlinear feasible-set equivalence or permit physical contact deletion','No new equilibrium, flexible-Rail, friction or system release'])
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],rows=[{k:r[k] for k in ('n','original_rows','rank','maximum_nonnegative_residual','status')} for r in rows]),indent=2))
if __name__=='__main__':main()
