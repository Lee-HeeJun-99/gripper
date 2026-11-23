"""Independent linear recurrence/continuous reference vs actual Native coupon."""
import argparse,csv,json,sys
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.linalg import expm,lu_factor,lu_solve
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag
    if not a.worker:
        out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(guarded([sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'],out/'process',120)));return
    src=BASE/'results/b3_linear_gravity_coupon1162';root=ET.parse(src/'scene.scn').getroot();node=root.find('Node');q0=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ');N=len(q0);fixed=np.fromstring(node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int);free=np.ones(N,bool)
    for i in fixed:free[3*i:3*i+3]=False
    K0=np.zeros((N,N))
    for r in csv.DictReader((src/'rest.matrix.csv').open()):K0[int(r['i']),int(r['j'])]=float(r['K_N_per_m'])
    K=K0[np.ix_(free,free)];n=len(K);mass=node.find('UniformMass');m=float(mass.get('totalMass'))/(N//3);alpha=float(mass.get('rayleighMass'));beta=float(node.find('TetrahedronFEMForceField').get('rayleighStiffness'));M=m*np.eye(n);C=alpha*M+beta*K;f=np.tile(m*np.fromstring(root.get('gravity'),sep=' '),N//3)[free];dt=float(root.get('dt'));lu=lu_factor(M+dt*C+dt*dt*K)
    B=np.zeros((2*n+1,2*n+1));B[:n,n:2*n]=np.eye(n);B[n:2*n,:n]=-K/m;B[n:2*n,n:2*n]=-C/m;B[n:2*n,-1]=f/m;T=expm(dt*B);Th=expm(dt/2*B);semigroup=float(np.linalg.norm(T-Th@Th)/np.linalg.norm(T));cont=np.zeros(2*n+1);cont[-1]=1;x=np.zeros(n);v=np.zeros(n);trace=[]
    rows=list(csv.DictReader((src/'states.csv').open()))
    def error(u,w):
        den=max(np.linalg.norm(u),np.linalg.norm(w));return dict(absolute_L2=float(np.linalg.norm(u-w)),relative=float(np.linalg.norm(u-w)/den) if den else None)
    for r in rows:
        v=lu_solve(lu,M@v+dt*(f-K@x));x+=dt*v;cont=T@cont;actual=(np.fromstring(r['q'],sep=' ')-q0)[free];av=np.fromstring(r['v'],sep=' ')[free]
        trace.append(dict(time_s=float(r['time_s']),native_q_vs_discrete=error(actual,x),native_v_vs_discrete=error(av,v),discrete_q_vs_continuous=error(x,cont[:n])))
    maxima={k:max(t[k]['relative'] for t in trace) for k in ('native_q_vs_discrete','native_v_vs_discrete','discrete_q_vs_continuous')};d=dict(status='PASS_LINEAR_COUPON_DISCRETE_REFERENCE_ONLY' if max(maxima[k] for k in ('native_q_vs_discrete','native_v_vs_discrete'))<=.001 else 'FAIL_LINEAR_COUPON_DISCRETE_REFERENCE',maximum_relative_errors=maxima,exponential_semigroup_relative=semigroup,first=trace[0],last=trace[-1],relative_gate=.001,physical_validation='NOT QUALIFIED',B3_time_convergence='FAIL_PRESERVED',scope='Linear no-Guide/no-Cable/no-contact coupon ONLY. Native discretization agreement is not continuous-time accuracy or nonlinear grasp validation.',energy_work=None,input_hashes={str(f.relative_to(BASE)):sha(f) for f in (src/'scene.scn',src/'rest.matrix.csv',src/'states.csv',Path(__file__))});(out/'trace.json').write_text(json.dumps(trace,indent=2));(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
