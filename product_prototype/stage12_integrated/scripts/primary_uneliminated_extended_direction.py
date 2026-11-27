"""Actual P1 rejected terminal equation: uneliminated 3-block direction with extended accumulator ONLY.
No repeat continuation or iterate, physical change, regularization or row removal.
"""
import sys,time,json,shutil
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
from baseline_registry import ROOT,REPO,ref,dump

def main():
 t=time.monotonic();assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_certified_centrality1/summary.json';s=json.loads(src.read_text());r=np.load(REPO/s['reduced']['path']);e=np.load(src.parent/'direction19.npz');H,F=r['H'],r['F'];sl,lam=e['s'],e['l'];n,m=H.shape[0],len(sl)
 K=sparse.bmat([[sparse.csc_matrix(H),None,sparse.csc_matrix(-F.T)],[sparse.csc_matrix(F),-sparse.eye(m),None],[None,sparse.diags(lam),sparse.diags(sl)]],format='csc');rhs=np.r_[-e['rd'],-e['rp'],-e['rc_corrector']];left=np.ones(len(rhs));right=left.copy();M=K.copy()
 for i in range(10):
  row=np.asarray(abs(M).max(axis=1).toarray()).ravel();rr=1/np.sqrt(np.maximum(row,1e-300));left*=rr;M=sparse.diags(rr)@M;col=np.asarray(abs(M).max(axis=0).toarray()).ravel();cc=1/np.sqrt(np.maximum(col,1e-300));right*=cc;M=M@sparse.diags(cc)
 lu=splu(M.tocsc(),permc_spec='COLAMD',diag_pivot_thresh=1.);sol=(right*lu.solve(left*rhs)).astype(np.longdouble)
 def residual(w):
  dz,ds,dl=w[:n].astype(np.longdouble),w[n:n+m].astype(np.longdouble),w[n+m:].astype(np.longdouble)
  return np.r_[-e['rd'].astype(np.longdouble)-H.astype(np.longdouble)@dz+F.T.astype(np.longdouble)@dl,-e['rp'].astype(np.longdouble)-F.astype(np.longdouble)@dz+ds,-e['rc_corrector'].astype(np.longdouble)-lam.astype(np.longdouble)*ds-sl.astype(np.longdouble)*dl]
 history=[]
 for i in range(12):
  rr=residual(sol);history.append(float(np.max(abs(rr))));trial=sol+right*lu.solve(left*np.asarray(rr,dtype=float))
  if np.max(abs(residual(trial)))>=np.max(abs(rr)):break
  sol=trial
 rr=residual(sol);err=[float(np.max(abs(v))) for v in [rr[:n],rr[n:n+m],rr[n+m:]]];np.savez_compressed(out/'direction.npz',dz=sol[:n],ds=sol[n:n+m],dl=sol[n+m:]);dump(out/'summary.json',dict(status='ACTUAL_P1_UNELIMINATED_DIRECTION_ONLY',candidate=s['candidate'],source=ref(src),terminal_equation=ref(src.parent/'direction19.npz'),reduced=s['reduced'],producer=ref(out/'producer.py'),output=ref(out/'direction.npz'),first_order_errors=err,direction_certified=bool(max(err)<1e-8),refinement_history=history,matrix_shape=list(K.shape),minimum_slack=float(sl.min()),minimum_dual=float(lam.min()),maximum_s_over_l=float(np.max(sl/lam)),minimum_s_over_l=float(np.min(sl/lam)),physical_regularization=0,actual_iterate_updates=0,actual_support_updates=0,accepted_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,elapsed_s=time.monotonic()-t));print(json.dumps(dict(errors=err,history=history)))
if __name__=='__main__':main()
