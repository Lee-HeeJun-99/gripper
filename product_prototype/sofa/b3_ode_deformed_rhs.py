"""Read-only previous-state ODE damping matrix/free-RHS hypotheses."""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--source',choices=['b3_ode_deformed_step1174','b3_ode_force_step1177'],default='b3_ode_deformed_step1174');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results'/a.source;root=ET.parse(src/'scene.scn').getroot();ph={r['phase']:r for r in csv.DictReader((src/'step.phases.csv').open())};before=ph['begin'];build=ph['build_end'];q=np.fromstring(before['body_q'],sep=' ').reshape(-1,3);frames=np.fromstring(before['guide_q'],sep=' ').reshape(-1,7);gv=np.fromstring(before['guide_v'],sep=' ').reshape(-1,6);pairs=np.fromstring(root.find("./Node[@name='finger0']/SubsetMultiMapping").get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);ng=len(frames);nf=int(pairs[pairs[:,0]==0,1].max())+1;N=6*ng+3*nf;G=np.zeros((q.size,N));convective=np.zeros_like(q)
    def skew(v):return np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    for i,(owner,j) in enumerate(pairs):
        if owner==0:G[3*i:3*i+3,6*ng+3*j:6*ng+3*j+3]=np.eye(3)
        else:
            b=j//3;r=q[i]-frames[b,:3];G[3*i:3*i+3,6*b:6*b+3]=np.eye(3);G[3*i:3*i+3,6*b+3:6*b+6]=-skew(r);convective[i]=np.cross(gv[b,3:],np.cross(gv[b,3:],r))
    K0=np.zeros((q.size,q.size));A=np.zeros((N,N));elastic=np.zeros_like(q)
    for r in csv.DictReader((src/'step.previous_K.csv').open()):K0[int(r['i']),int(r['j'])]=float(r['K_N_per_m'])
    for r in csv.DictReader((src/'step.A.csv').open()):A[int(r['i']),int(r['j'])]=float(r['A'])
    for r in csv.DictReader((src/'step.previous_elastic_force.csv').open()):elastic[int(r['node'])]=np.fromstring(r['force_N'],sep=' ')
    mf=float(root.find("./Node[@name='finger0']/UniformMass").get('totalMass'))/len(q);M=mf*(G.T@G);gravity=np.fromstring(root.get('gravity'),sep=' ');f=G.T@(elastic+mf*gravity).ravel();mp=BASE/'results/b3_rail_back_hold1129/guide_frames0.csv.mass.json'
    for i,r in enumerate(json.loads(mp.read_text())['elements']):M[6*i:6*i+6,6*i:6*i+6]+=r['matrix'];f[6*i:6*i+3]+=r['mass_kg']*gravity
    K=G.T@K0@G;dt=float(root.get('dt'));alpha=float(root.find('EulerImplicitSolver').get('rayleighMass'));beta=float(root.find('EulerImplicitSolver').get('rayleighStiffness'));predA=(1+dt*alpha)*M+(dt*dt+dt*beta)*K;free=np.ones(N,bool)
    for j in np.fromstring(root.find("./Node[@name='free0']/FixedProjectiveConstraint").get('indices'),sep=' ',dtype=int):free[6*ng+3*j:6*ng+3*j+3]=False
    previous=np.r_[gv.ravel(),np.fromstring(before['free_v'],sep=' ')];actual=np.r_[np.fromstring(build['guide_free_v'],sep=' '),np.fromstring(build['free_free_v'],sep=' ')];observedRHS=A@actual;ix=np.ix_(free,free)
    def error(x,y):return dict(absolute=float(np.linalg.norm(x-y)),relative=float(np.linalg.norm(x-y)/max(np.linalg.norm(x),np.linalg.norm(y))))
    hypotheses={}
    for name,extra in [('no_convective_term',np.zeros(N)),('mapped_centripetal',-mf*(G.T@convective.ravel()))]:
        rhs=M@previous+dt*(f+extra);pred=np.linalg.solve(A[ix],rhs[free]);hypotheses[name]=dict(free_RHS=error(observedRHS[free],rhs[free]),free_velocity=error(actual[free],pred))
    accepted=ph['accepted_end'];lam=np.fromstring(accepted['lambda'],sep=' ');J=np.zeros((len(lam),N))
    for r in csv.DictReader((src/'step.build_end.J.csv').open()):
        val=np.fromstring(r['values'],sep=' ');column=int(r['column']);start=6*column if r['state']=='guide' else 6*ng+3*column;J[int(r['row']),start:start+len(val)]=val
    observed_correction=np.r_[np.fromstring(accepted['guide_v'],sep=' '),np.fromstring(accepted['free_v'],sep=' ')]-actual;impulse=J.T@lam;predicted_correction=np.linalg.solve(A[ix],impulse[free]);correction=error(observed_correction[free],predicted_correction) if np.any(lam) else None
    journal=list(csv.DictReader((src/'finger0.csv').open()));jr=min(journal,key=lambda r:abs(float(r['time_s'])-float(accepted['time_s'])));command=float(jr['command_N'])
    d=dict(status='DEFORMED_ODE_CONTRACT_DIAGNOSTIC_ONLY',previous_time_s=float(before['time_s']),accepted_time_s=float(accepted['time_s']),matrix_error=error(A[ix],predA[ix]),hypotheses=hypotheses,lambda_Ns=lam.tolist(),command_N=command,command_impulse_error_Ns=float(abs(lam-command*dt).max()),impulse_velocity_correction=correction,relative_gate=.001,physical_validation='NOT QUALIFIED',time_convergence='FAIL_PRESERVED',energy_work=None,scope='Previous-state mapped M/K/gravity/elastic; isotropic Guide inertia. Explicit with/without mapped centripetal term hypotheses,not fitted correction or state mutation.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in (src/'step.phases.csv',src/'step.A.csv',src/'step.previous_K.csv',src/'step.previous_elastic_force.csv',src/'step.build_end.J.csv',src/'finger0.csv',mp,Path(__file__))});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))

if __name__=='__main__':main()
