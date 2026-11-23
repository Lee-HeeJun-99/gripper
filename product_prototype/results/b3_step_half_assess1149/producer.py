"""Same-step previous-state A identity and actual Native impulse correction.
Independent algebra only;never changes states,forces,solver or prior verdicts.
"""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--source',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    src=BASE/'results'/a.source;meta=json.loads((src/'preflight.json').read_text());ref=BASE/'results'/meta['reference'];root=ET.parse(src/'scene.scn').getroot();phases=list(csv.DictReader((src/'step.phases.csv').open()));phase={r['phase']:r for r in phases};before=phase['begin'];build=phase['build_end'];after=phase['accepted_end']
    q=np.fromstring(before['body_q'],sep=' ').reshape(-1,3);frame=np.fromstring(before['guide_q'],sep=' ').reshape(-1,7);pairs=np.fromstring(root.find("./Node[@name='finger0']/SubsetMultiMapping").get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);nf=int(pairs[pairs[:,0]==0,1].max())+1;ng=len(frame);N=6*ng+3*nf;G=np.zeros((q.size,N))
    def skew(v):return np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    for i,(owner,j) in enumerate(pairs):
        if owner==0:G[3*i:3*i+3,6*ng+3*j:6*ng+3*j+3]=np.eye(3)
        else:
            b=j//3;G[3*i:3*i+3,6*b:6*b+3]=np.eye(3);G[3*i:3*i+3,6*b+3:6*b+6]=-skew(q[i]-frame[b,:3])
    K=np.zeros((q.size,q.size));A=np.zeros((N,N))
    for r in csv.DictReader((src/'step.previous_K.csv').open()):K[int(r['i']),int(r['j'])]=float(r['K_N_per_m'])
    for r in csv.DictReader((src/'step.A.csv').open()):A[int(r['i']),int(r['j'])]=float(r['A'])
    mass=root.find("./Node[@name='finger0']/UniformMass");mf=float(mass.get('totalMass'))/len(q);Mfilm=mf*(G.T@G);Mguide=np.zeros((N,N))
    for i,r in enumerate(json.loads((ref/'guide_frames0.csv.mass.json').read_text())['elements']):Mguide[6*i:6*i+6,6*i:6*i+6]=r['matrix']
    dt=float(root.get('dt'));alpha=float(mass.get('rayleighMass','0'));beta=float(root.find("./Node[@name='finger0']/TetrahedronFEMForceField").get('rayleighStiffness','0'));expected=(1+dt*alpha)*Mfilm+Mguide+(dt*dt+dt*beta)*(G.T@K@G)
    free=np.ones(N,dtype=bool)
    for j in np.fromstring(root.find("./Node[@name='free0']/FixedProjectiveConstraint").get('indices'),sep=' ',dtype=int):free[6*ng+3*j:6*ng+3*j+3]=False
    rotation=np.zeros(N,dtype=bool)
    for j in range(ng):rotation[6*j+3:6*j+6]=True
    blocks={}
    for name,r,c in [('TT',free&~rotation,free&~rotation),('TR',free&~rotation,free&rotation),('RT',free&rotation,free&~rotation),('RR',free&rotation,free&rotation)]:
        actual=A[np.ix_(r,c)];predicted=expected[np.ix_(r,c)];den=max(np.linalg.norm(actual),np.linalg.norm(predicted));err=float(np.linalg.norm(actual-predicted)/den) if den else None;blocks[name]=dict(relative_error=err,absolute_difference=float(np.linalg.norm(actual-predicted)),pass_gate=err is not None and err<=.001)
    lam=np.fromstring(after['lambda'],sep=' ');J=np.zeros((len(lam),N))
    for r in csv.DictReader((src/'step.build_end.J.csv').open()):
        val=np.fromstring(r['values'],sep=' ');col=int(r['column']);start=6*col if r['state']=='guide' else 6*ng+3*col;J[int(r['row']),start:start+len(val)]=val
    rhs=J.T@lam;dv=np.zeros(N);dv[free]=np.linalg.solve(A[np.ix_(free,free)],rhs[free])
    observed=np.r_[np.fromstring(after['guide_v'],sep=' ')-np.fromstring(build['guide_free_v'],sep=' '),np.fromstring(after['free_v'],sep=' ')-np.fromstring(build['free_free_v'],sep=' ')]
    groups={'guide_translation':np.array([i for j in range(ng) for i in range(6*j,6*j+3)]),'guide_rotation':np.array([i for j in range(ng) for i in range(6*j+3,6*j+6)]),'free_translation':np.flatnonzero(free&(np.arange(N)>=6*ng))};correction={}
    for name,ids in groups.items():
        den=max(np.linalg.norm(observed[ids]),np.linalg.norm(dv[ids]));err=float(np.linalg.norm(observed[ids]-dv[ids])/den) if den else None;correction[name]=dict(relative_error=err,absolute_difference=float(np.linalg.norm(observed[ids]-dv[ids])),observed_norm=float(np.linalg.norm(observed[ids])),predicted_norm=float(np.linalg.norm(dv[ids])),pass_gate=err is not None and err<=.001)
    journal=list(csv.DictReader((src/'finger0.csv').open()));jr=min(journal,key=lambda r:abs(float(r['time_s'])-float(after['time_s'])));command=float(jr['command_N']);impulse_error=float(abs(lam-command*dt).max())
    d=dict(status='PASS_SAMPLED_EFFECTIVE_MATRIX_ONLY' if all(v['pass_gate'] for v in blocks.values()) else 'FAIL_SAMPLED_EFFECTIVE_MATRIX',source_case=a.source,previous_accepted_time_s=float(before['time_s']),accepted_time_s=float(after['time_s']),matrix_blocks=blocks,impulse_correction=correction,impulse_correction_status='PASS_DISCRETE_CORRECTION_IDENTITY_ONLY' if all(v['pass_gate'] for v in correction.values()) else 'FAIL_DISCRETE_CORRECTION_IDENTITY',lambda_Ns=lam.tolist(),command_N=command,command_impulse_error_Ns=impulse_error,dt_s=dt,relative_gate=.001,physical_validation='NOT QUALIFIED',time_convergence='FAIL_PRESERVED',energy_work=None,input_hashes={str(f.relative_to(BASE)):sha(f) for f in (src/'step.phases.csv',src/'step.previous_K.csv',src/'step.A.csv',src/'step.build_end.J.csv',src/'finger0.csv',Path(__file__))})
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
