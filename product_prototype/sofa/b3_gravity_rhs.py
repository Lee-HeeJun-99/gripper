"""Initial rest-state Native discrete gravity identity, not time convergence."""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    src=BASE/'results/b3_first_free_step1159';root=ET.parse(src/'scene.scn').getroot();ph={r['phase']:r for r in csv.DictReader((src/'step.phases.csv').open())};before=ph['begin'];build=ph['build_end'];assert float(before['time_s'])==0
    q=np.fromstring(before['body_q'],sep=' ').reshape(-1,3);frames=np.fromstring(before['guide_q'],sep=' ').reshape(-1,7);pairs=np.fromstring(root.find("./Node[@name='finger0']/SubsetMultiMapping").get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);ng=len(frames);nf=int(pairs[pairs[:,0]==0,1].max())+1;N=6*ng+3*nf;G=np.zeros((q.size,N))
    for key in ('guide_v','free_v'):assert not np.any(np.fromstring(before[key],sep=' '))
    def skew(v):return np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    for i,(owner,j) in enumerate(pairs):
        if owner==0:G[3*i:3*i+3,6*ng+3*j:6*ng+3*j+3]=np.eye(3)
        else:
            b=j//3;G[3*i:3*i+3,6*b:6*b+3]=np.eye(3);G[3*i:3*i+3,6*b+3:6*b+6]=-skew(q[i]-frames[b,:3])
    A=np.zeros((N,N))
    for r in csv.DictReader((src/'step.A.csv').open()):A[int(r['i']),int(r['j'])]=float(r['A'])
    elastic=np.zeros_like(q)
    for r in csv.DictReader((src/'step.previous_elastic_force.csv').open()):elastic[int(r['node'])]=np.fromstring(r['force_N'],sep=' ')
    gravity=np.fromstring(root.get('gravity'),sep=' ');mf=float(root.find("./Node[@name='finger0']/UniformMass").get('totalMass'))/len(q);rhs=G.T@(elastic+mf*gravity).ravel()
    masses=json.loads((BASE/'results/b3_rail_back_hold1129/guide_frames0.csv.mass.json').read_text())['elements']
    for i,m in enumerate(masses):rhs[6*i:6*i+3]+=m['mass_kg']*gravity
    free=np.ones(N,dtype=bool)
    for j in np.fromstring(root.find("./Node[@name='free0']/FixedProjectiveConstraint").get('indices'),sep=' ',dtype=int):free[6*ng+3*j:6*ng+3*j+3]=False
    dt=float(root.get('dt'));observed=np.r_[np.fromstring(build['guide_free_v'],sep=' '),np.fromstring(build['free_free_v'],sep=' ')];predicted=np.zeros(N);predicted[free]=np.linalg.solve(A[np.ix_(free,free)],dt*rhs[free]);blocks={}
    for name,ids in [('guide_translation',np.array([6*i+j for i in range(ng) for j in range(3)])),('guide_rotation',np.array([6*i+j for i in range(ng) for j in range(3,6)])),('free_translation',np.flatnonzero(free&(np.arange(N)>=6*ng)))]:
        den=max(np.linalg.norm(predicted[ids]),np.linalg.norm(observed[ids]));err=float(np.linalg.norm(predicted[ids]-observed[ids])/den) if den else None;blocks[name]=dict(relative_error=err,absolute_difference=float(np.linalg.norm(predicted[ids]-observed[ids])),pass_gate=err is not None and err<=.001)
    residual=A@observed-dt*rhs;scale=max(np.linalg.norm((A@observed)[free]),np.linalg.norm((dt*rhs)[free]));d=dict(status='PASS_FIRST_STEP_GRAVITY_DISCRETE_IDENTITY_ONLY' if all(x['pass_gate'] for x in blocks.values()) else 'FAIL_FIRST_STEP_GRAVITY_DISCRETE_IDENTITY',blocks=blocks,free_rhs_relative_residual=float(np.linalg.norm(residual[free])/scale),initial_elastic_force_norm_N=float(np.linalg.norm(elastic)),dt_s=dt,previous_time_s=0,relative_gate=.001,physical_validation='NOT QUALIFIED',time_convergence='FAIL_PRESERVED',scope='Independent mapped gravitational force/moment plus measured Native initial elastic force. Zero initial velocity, no gyro. Not a deformed RHS or continuous dynamics certificate.',energy_work=None,input_hashes={str(f.relative_to(BASE)):sha(f) for f in (src/'scene.scn',src/'step.A.csv',src/'step.phases.csv',src/'step.previous_elastic_force.csv',Path(__file__))})
    (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))

if __name__=='__main__':main()
