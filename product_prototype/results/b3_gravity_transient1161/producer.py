"""Independent frozen linear forced transient, not a new SOFA solver.
Rest M/K/G, declared Rayleigh terms; analytic matrix exponential vs backward
Euler recurrence and actual saved zero-Cable Native states. No physics writes.
"""
import argparse,csv,json,subprocess,sys
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.linalg import expm,lu_factor,lu_solve,solve
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args();out=BASE/'results'/a.tag
    if Path(a.tag).name!=a.tag:raise ValueError('local case name required')
    if not a.worker:
        out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes())
        proc=guarded([sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker'],out/'process',120)
        print(json.dumps(proc));return
    src=BASE/'results/b3_first_free_step1159';root=ET.parse(src/'scene.scn').getroot();before=next(csv.DictReader((src/'step.phases.csv').open()));q=np.fromstring(before['body_q'],sep=' ').reshape(-1,3);frame=np.fromstring(before['guide_q'],sep=' ').reshape(-1,7);pairs=np.fromstring(root.find("./Node[@name='finger0']/SubsetMultiMapping").get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);ng=len(frame);nf=int(pairs[pairs[:,0]==0,1].max())+1;N=ng*6+nf*3;G=np.zeros((q.size,N))
    def skew(v):return np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    for i,(owner,j) in enumerate(pairs):
        if owner==0:G[3*i:3*i+3,6*ng+3*j:6*ng+3*j+3]=np.eye(3)
        else:
            b=j//3;G[3*i:3*i+3,6*b:6*b+3]=np.eye(3);G[3*i:3*i+3,6*b+3:6*b+6]=-skew(q[i]-frame[b,:3])
    K0=np.zeros((q.size,q.size))
    for r in csv.DictReader((src/'step.previous_K.csv').open()):K0[int(r['i']),int(r['j'])]=float(r['K_N_per_m'])
    mass=root.find("./Node[@name='finger0']/UniformMass");mf=float(mass.get('totalMass'))/len(q);Mf=mf*(G.T@G);Mg=np.zeros((N,N));gravity=np.fromstring(root.get('gravity'),sep=' ');f=G.T@np.tile(mf*gravity,len(q))
    mp=BASE/'results/b3_rail_back_hold1129/guide_frames0.csv.mass.json'
    for i,m in enumerate(json.loads(mp.read_text())['elements']):Mg[6*i:6*i+6,6*i:6*i+6]=m['matrix'];f[6*i:6*i+3]+=m['mass_kg']*gravity
    K=G.T@K0@G;C=float(mass.get('rayleighMass'))*Mf+float(root.find("./Node[@name='finger0']/TetrahedronFEMForceField").get('rayleighStiffness'))*K
    free=np.ones(N,dtype=bool)
    for j in np.fromstring(root.find("./Node[@name='free0']/FixedProjectiveConstraint").get('indices'),sep=' ',dtype=int):free[6*ng+3*j:6*ng+3*j+3]=False
    ix=np.ix_(free,free);M=(Mf+Mg)[ix];K=K[ix];C=C[ix];f=f[free];g=G[:,free];n=len(f)
    # One affine transition at half dt; original nonsymmetric matrices retained.
    B=np.zeros((2*n+1,2*n+1));B[:n,n:2*n]=np.eye(n);B[n:2*n,:n]=-solve(M,K,assume_a='pos');B[n:2*n,n:2*n]=-solve(M,C,assume_a='pos');B[n:2*n,-1]=solve(M,f,assume_a='pos');transition=expm(.00125*B)
    exact=np.zeros(2*n+1);exact[-1]=1;continuous={}
    for step in range(1,81):
        exact=transition@exact
        if step%2==0:continuous[step//2]=g@exact[:n]
    skin=np.array(json.loads((BASE/'results/b3_rail_back_hold1129/mesh.json').read_text())['local_positions_mm'])[:,2]==.1;trace=[];inputs=[src/'scene.scn',src/'step.previous_K.csv',src/'step.phases.csv',mp,Path(__file__)]
    for name,dt in [('b3_rail_back_zero1127',.0025),('b3_rail_back_zero_half1157',.00125)]:
        file=BASE/'results'/name/'finger0.csv';inputs.append(file);rows=list(csv.DictReader(file.open()));A=M+dt*C+dt*dt*K;lu=lu_factor(A);x=np.zeros(n);v=np.zeros(n)
        for step in range(1,round(.1/dt)+1):
            v=lu_solve(lu,M@v+dt*(f-K@x));x+=dt*v
            if abs(step*dt/.0025-round(step*dt/.0025))>1e-10:continue
            k=round(step*dt/.0025);actual=(np.fromstring(rows[step-1]['q_m'],sep=' ')-q.ravel()).reshape(-1,3)[skin].ravel();pred=(g@x).reshape(-1,3)[skin].ravel();cont=continuous[k].reshape(-1,3)[skin].ravel()
            def compare(u,w):
                den=max(np.linalg.norm(u),np.linalg.norm(w));return dict(absolute_L2_m=float(np.linalg.norm(u-w)),relative=float(np.linalg.norm(u-w)/den) if den else None)
            trace.append(dict(case=name,time_s=step*dt,native_vs_frozen_discrete=compare(actual,pred),frozen_discrete_vs_continuous=compare(pred,cont),native_vs_continuous=compare(actual,cont)))
    d=dict(status='FROZEN_LINEAR_TRANSIENT_DIAGNOSTIC_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),free_dofs=n,interval_s=[.0025,.1],first_outputs=[x for x in trace if x['time_s']==.0025],last_outputs=[x for x in trace if x['time_s']==.1],maximum_native_vs_frozen_discrete_relative=max(x['native_vs_frozen_discrete']['relative'] for x in trace),physical_validation='NOT QUALIFIED',time_convergence='FAIL_PRESERVED',scope='Rest-linearized mathematical reference, not nonlinear Native truth. Matrix exponential vs backward Euler, no fitted material/damping/load.',energy_work=None,input_hashes={str(f.relative_to(BASE)):sha(f) for f in inputs})
    (out/'trace.json').write_text(json.dumps(trace,indent=2));(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
