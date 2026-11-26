"""Independent saved-state complex-step virtual-work and kinematic audit."""
import json,sys,copy
from pathlib import Path
import numpy as np
from baseline_registry import ROOT,REPO,sha,ref,dump
sys.path.insert(0,str(ROOT.parent/'stage2_load_transfer/scripts'))
from finger_structure import E_RAIL,E_PET,width

def inspect(row,d):
    n=d['n'];h=row['L_m']/n;s=(np.arange(n)+.5)*h
    if row['body']=='rail':EA=2*E_RAIL*.003*.0002;EI=2*E_RAIL*.003*.0002**3/12
    else:EA=E_PET*width(s)*.0003;EI=E_PET*width(s)*.0003**3/12
    th=np.array(d['theta_rad']);e=np.array(d['strain']);r=np.array(d['r_m']);F=row['force_N']
    def potential(t,eps):
        a=(t[1:]+t[:-1])/2
        return np.sum(h*(EA*eps**2+EI*(np.diff(t)/h)**2)/2-h*F*(1+eps)*np.sin(a))
    gradients=[]
    for i in range(1,n+1):
        t=th.astype(complex);t[i]+=1e-25j
        gradients.append(abs(potential(t,e).imag/1e-25))
    axial=[]
    for i in range(n):
        eps=e.astype(complex);eps[i]+=1e-25j
        axial.append(abs(potential(th,eps).imag/1e-25/h))
    a=(th[1:]+th[:-1])/2
    delta=h*(1+e)[:,None]*np.column_stack((np.cos(a),np.sin(a)))
    kin=float(np.max(abs(np.diff(r,axis=0)-delta)))
    stored=float(np.sum(h*(EA*e**2+EI*(np.diff(th)/h)**2)/2))
    err=abs(stored-d['stored_energy_J'])
    passed=max(gradients)<1e-10 and max(axial)<1e-10 and kin<1e-14 and err<1e-16 and np.max(abs(r[0]))==0 and th[0]==0 and d['solver_success']
    return dict(n=n,theta_stationarity_Nm=max(gradients),axial_stationarity_N=max(axial),kinematic_error_m=kin,stored_energy_error_J=err,passed=bool(passed))

def main():
    out=ROOT/'validation/finger'/sys.argv[1];source=out/'summary.json';doc=json.loads(source.read_text())
    inputs=json.loads((out/'inputs.json').read_text())
    hashes=all(sha(REPO/r['path'])==r['SHA256'] for r in inputs['inputs'])
    rows=[dict(body=row['body'],force_N=row['force_N'],**inspect(row,d)) for row in doc['rows'] for d in row['refinements']]
    bad=copy.deepcopy(doc['rows'][-1]['refinements'][-1]);bad['theta_rad'][-1]+=.01
    rejected=not inspect(doc['rows'][-1],bad)['passed']
    passed=hashes and rejected and all(r['passed'] for r in rows) and sha(out/'producer.py')==sha(ROOT/'scripts/extensible_rod_reference.py')
    result=dict(status='PASS' if passed else 'FAIL',scope='ACTUAL SAVED FINITE ROD STATES ONLY',input_hashes_match=hashes,perturbed_state_rejected=rejected,states=rows,source=ref(source),verifier=ref(Path(__file__)))
    dump(out/'verification.json',result);print(json.dumps(result,indent=2));raise SystemExit(0 if passed else 2)
if __name__=='__main__':main()
