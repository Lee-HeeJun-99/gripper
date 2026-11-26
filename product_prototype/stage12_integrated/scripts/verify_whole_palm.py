"""Independent affine-tetrahedron energy reconstruction of saved full Palm states."""
import json, shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,sha

def energy(p,t,u):
    dx=p[t[:,1:]]-p[t[:,0,None]];du=u[t[:,1:]]-u[t[:,0,None]]
    g=np.linalg.solve(dx,du).transpose(0,2,1);e=(g+g.transpose(0,2,1))/2
    E=70e9;nu=.33;mu=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu))
    return float(np.sum(abs(np.linalg.det(dx))/6*(mu*np.einsum('ijk,ijk->i',e,e)+.5*lam*np.trace(e,axis1=1,axis2=2)**2)))

def main():
    out=ROOT/'validation/transmission/AK_whole_palm_verify1';out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');rows=[]
    for tag in ('AK_whole_palm_h8_3','AK_whole_palm_h6_1','AK_whole_palm_h4_1'):
        src=ROOT/'validation/transmission'/tag/'summary.json';d=json.loads(src.read_text());a=np.load(REPO/d['field']['path']);v=np.load(REPO/d['verification']['path'])
        hashes=all(sha(REPO/r['path'])==r['SHA256'] for r in (d['field'],d['producer'],d['STEP'],d['source'],d['verification']))
        en=energy(a['points_m'],a['tetra'],a['displacement_m']);err=abs(en/d['energy_J']-1)
        work=.5*float(a['applied_f']@a['full_u']);u=a['displacement_m'].copy();u[np.argmax(np.linalg.norm(u,axis=1)),2]+=1e-6
        bad=abs(energy(a['points_m'],a['tetra'],u)/work-1)>1e-8
        checks=dict(hashes=hashes,energy=err<1e-8,work=abs(en/work-1)<1e-8,force=np.linalg.norm(v['force_balance'])<1e-8,moment=np.linalg.norm(v['moment_balance'])<1e-10,residual=np.linalg.norm(v['residual_free'])/np.linalg.norm(v['force_free'])<1e-8,perturbation_rejected=bool(bad))
        rows.append(dict(source=ref(src),energy_J=en,relative_energy_error=err,checks={k:bool(x) for k,x in checks.items()}))
    ok=all(all(r['checks'].values()) for r in rows)
    dump(out/'summary.json',dict(status='PASS' if ok else 'FAIL',scope='Saved affine strain energy/work/balance and input integrity only; does not cure mesh quality or support assumptions',rows=rows,producer=ref(out/'producer.py'),whole_system_release=False))
    raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
