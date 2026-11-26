"""Independent barycentric-gradient and degree2 tetra quadrature verification.
P2 test certifies polynomial representation only, never an equilibrium solve.
"""
import json,shutil,time,itertools
import numpy as np
from baseline_registry import ROOT,REPO,sha,ref,dump
E=70e9;nu=.33;mu=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu))

def density(g):
    e=(g+g.swapaxes(-1,-2))*.5
    return mu*np.sum(e*e,axis=(-1,-2))+.5*lam*np.trace(e,axis1=-1,axis2=-2)**2

def displacement(p,axis):
    x=p[...,axis];y=p[...,1-axis];z=p[...,2]+.0095
    u=np.empty_like(p);u[...,axis]=-x*z;u[...,1-axis]=nu*y*z
    u[...,2]=.5*x*x+.5*nu*z*z-.5*nu*y*y;return u

def verify(p,t,solved):
    alpha=(5+3*np.sqrt(5))/20;beta=(5-np.sqrt(5))/20
    Q=np.full((4,4),beta);np.fill_diagonal(Q,alpha)
    sums=np.zeros((2,3));actual=0.;affine_error=0.
    for start in range(0,len(t),4000):
        v=p[t[start:start+4000]];n=len(v)
        # Local origin avoids conditioning from global metre translations.
        matrix=np.concatenate((np.ones((n,4,1)),v-v[:,0,None]),axis=2)
        inv=np.linalg.inv(matrix);gN=inv[:,1:,:].transpose(0,2,1)
        vol=abs(np.linalg.det(matrix))/6
        us=solved[t[start:start+4000]]
        actual+=float(np.sum(vol*density(np.einsum('nia,nib->nab',us,gN))))
        # Independent exact affine strain control on actual tetrahedra.
        A=np.array([[.001,.0002,0],[.0002,-.0003,.0001],[0,.0001,.0005]])
        af=(v-v[:,0,None])@A.T
        ga=np.einsum('nia,nib->nab',af,gN)
        affine_error=max(affine_error,float(np.max(abs(ga-A))))
        for axis in (0,1):
            u1=displacement(v,axis)
            e1=density(np.einsum('nia,nib->nab',u1,gN))
            sums[axis,0]+=np.sum(vol*e1)
            qpos=np.einsum('qi,nia->nqa',Q,v);z=qpos[:,:,2]+.0095
            sums[axis,1]+=np.sum(vol*.5*E*np.mean(z*z,axis=1))
            pairs=list(itertools.combinations(range(4),2))
            p2=np.concatenate((v,np.stack([(v[:,i]+v[:,j])/2 for i,j in pairs],axis=1)),axis=1)
            u2=displacement(p2,axis)
            for qi,L in enumerate(Q):
                dN=np.concatenate(((4*L[None,:,None]-1)*gN,np.stack([4*(L[i]*gN[:,j]+L[j]*gN[:,i]) for i,j in pairs],axis=1)),axis=1)
                sums[axis,2]+=np.sum(vol*density(np.einsum('nia,nib->nab',u2,dN)))/4
    return actual,sums,affine_error

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/transmission/AK_palm_bending_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py');start=time.monotonic()
    source=ROOT/'validation/transmission/AK_palm_bending1/summary.json';d=json.loads(source.read_text());rows=[]
    assert sha(REPO/d['producer']['path'])==d['producer']['SHA256']
    for r in d['rows']:
        assert not (ROOT/'runtime/STOP').exists()
        assert sha(REPO/r['field']['path'])==r['field']['SHA256'] and sha(REPO/r['source']['path'])==r['source']['SHA256']
        with np.load(REPO/r['field']['path']) as a:p=a['points_m'];t=a['tetra'];u=a['displacement_m']
        actual,sums,affine_error=verify(p,t,u)
        errs=[]
        for axis,probe in enumerate(r['probes']):
            errs.extend([abs(sums[axis,0]/probe['P1_energy_J']-1),abs(sums[axis,1]/probe['continuum_energy_J']-1)])
        p2err=float(np.max(abs(sums[:,2]/sums[:,1]-1)))
        checks=dict(P1_continuum_independent_agreement=max(errs)<1e-8,P2_polynomial_representation=p2err<1e-8,
            actual_solution_energy=abs(actual/r['actual_saved_energy_J']-1)<1e-8,affine_gradient=affine_error<1e-10,
            corrupted_1percent_displacement_rejected=abs(actual*1.01**2/r['actual_saved_energy_J']-1)>1e-8)
        rows.append(dict(h_mm=r['h_mm'],actual_energy_J=actual,independent_energies_J=sums.tolist(),
            max_P1_continuum_relative_difference=max(errs),P2_relative_error=p2err,affine_gradient_error=affine_error,checks={k:bool(v) for k,v in checks.items()}))
    ok=all(all(r['checks'].values()) for r in rows)
    result=dict(status='INDEPENDENT_REPRESENTATION_VERIFICATION_PASS' if ok else 'FAIL',source=ref(source),producer=ref(out/'producer.py'),rows=rows,
        elapsed_s=time.monotonic()-start,whole_system_release=False,scope='Actual mesh/solution independent energy reconstruction plus polynomial representation controls, not product solve or strength')
    dump(out/'summary.json',result);print(json.dumps(result,indent=2));raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
