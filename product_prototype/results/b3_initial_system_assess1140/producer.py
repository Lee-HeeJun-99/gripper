"""Compare Native first-step A to declared mass + mapped Native rest K.
Not a new solver;only algebraic assembly identity. No force/trajectory update.
"""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    src=BASE/'results/b3_rail_back_hold1129';system=BASE/'results/b3_rail_back_rest_system1139';root=ET.parse(src/'scene.scn').getroot();q=np.fromstring(root.find("./Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
    pairs=np.fromstring(root.find("./Node[@name='finger0']/SubsetMultiMapping").get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);nf=int(pairs[pairs[:,0]==0,1].max())+1;frame=np.fromstring(root.find("./Node[@name='guides0']/MechanicalObject").get('position'),sep=' ').reshape(-1,7);ng=len(frame);N=3*nf+6*ng;G=np.zeros((q.size,N))
    def skew(v):return np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    for i,(owner,j) in enumerate(pairs):
        if owner==0:G[3*i:3*i+3,3*j:3*j+3]=np.eye(3)
        else:
            k=j//3;col=3*nf+6*k;G[3*i:3*i+3,col:col+3]=np.eye(3);G[3*i:3*i+3,col+3:col+6]=-skew(q[i]-frame[k,:3])
    K=np.zeros((q.size,q.size));A=np.zeros((N,N))
    for r in csv.DictReader((system/'rest.matrix.csv').open()):K[int(r['i']),int(r['j'])]=float(r['K_N_per_m'])
    for r in csv.DictReader((system/'assembled.csv').open()):A[int(r['i']),int(r['j'])]=float(r['A'])
    filmMass=root.find("./Node[@name='finger0']/UniformMass");mf=float(filmMass.get('totalMass'))/len(q);Mf=mf*(G.T@G);Mg=np.zeros((N,N))
    for i,r in enumerate(json.loads((src/'guide_frames0.csv.mass.json').read_text())['elements']):Mg[3*nf+6*i:3*nf+6*i+6,3*nf+6*i:3*nf+6*i+6]=r['matrix']
    dt=float(root.get('dt'));alpha=float(filmMass.get('rayleighMass','0'));beta=float(root.find("./Node[@name='finger0']/TetrahedronFEMForceField").get('rayleighStiffness','0'))
    expected=(1+dt*alpha)*Mf+Mg+(dt*dt+dt*beta)*(G.T@K@G)
    order=np.r_[np.arange(3*nf,N),np.arange(3*nf)];expected=expected[np.ix_(order,order)]
    free=np.ones(N,dtype=bool);fixed=np.fromstring(root.find("./Node[@name='free0']/FixedProjectiveConstraint").get('indices'),sep=' ',dtype=int)
    for k in fixed:free[6*ng+3*k:6*ng+3*k+3]=False
    rotation=np.zeros(N,dtype=bool)
    for k in range(ng):rotation[6*k+3:6*k+6]=True
    comparisons={}
    for name,r,c in [('TT',free&~rotation,free&~rotation),('TR',free&~rotation,free&rotation),('RT',free&rotation,free&~rotation),('RR',free&rotation,free&rotation)]:
        actual=A[np.ix_(r,c)];ref=expected[np.ix_(r,c)];den=max(np.linalg.norm(actual),np.linalg.norm(ref));error=float(np.linalg.norm(actual-ref)/den) if den else None;comparisons[name]=dict(relative_error=error,absolute_Frobenius_difference=float(np.linalg.norm(actual-ref)),status='PASS_INITIAL_BLOCK_ONLY' if error is not None and error<=.001 else 'FAIL_INITIAL_BLOCK')
    d=dict(status='PASS_FIRST_EFFECTIVE_SYSTEM_IDENTITY_ONLY' if all(r['status'].startswith('PASS') for r in comparisons.values()) else 'FAIL_FIRST_EFFECTIVE_SYSTEM_IDENTITY',sample='Firstfree-motionassemblyatrest,beforefirstCableimpulse',formula='A=(1+dt*alphaFilm)*G^T Mfilm G+Mguide+(dt²+dt*betaFilm)*G^T KnativeRest G;projectiveRootDOFs excluded',native_order='12Rigidframes first,then216freeVec3nodes;Rootrows72–143excluded',dt_s=dt,alphaFilm=alpha,betaFilm=beta,blocks=comparisons,relative_gate=.001,mass_isolation_verified=False,full_deformed_assembly_verified=False,physical_validation='NOT QUALIFIED',time_convergence='FAIL_PRESERVED',input_hashes={str(f.relative_to(BASE)):sha(f) for f in (src/'scene.scn',src/'guide_frames0.csv.mass.json',system/'rest.matrix.csv',system/'assembled.csv',Path(__file__))})
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
