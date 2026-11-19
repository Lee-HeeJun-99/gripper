"""Independent signed-simplex volume moments; no density calibration or union sum."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from finite_guide_coupon import eyelet

def moments(vertices,faces):
    # Each oriented surface triangle closes a signed tetrahedron with the origin.
    t=np.asarray(vertices)[faces];vol=np.linalg.det(t)/6
    total=vol.sum()
    if total<=0:raise ValueError('nonpositive oriented volume')
    s=t.sum(axis=1);first=(vol[:,None]*s/4).sum(axis=0)
    second=(vol[:,None,None]*(np.einsum('ni,nj->nij',s,s)+np.einsum('nki,nkj->nij',t,t))/20).sum(axis=0)
    c=first/total;cov=second/total-np.outer(c,c)
    return total,c,np.trace(cov)*np.eye(3)-cov

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    cfg=json.loads((BASE/'results/b3_alarm_window485/config.json').read_text());records=[]
    meshes=[('box',trimesh.creation.box(extents=[2.,3.,4.]))]
    for n in (16,32,64):meshes.append((f'eyelet{n}',eyelet(cfg,n)[0]))
    # Include every actual proposed support, not an eyelet/support overlapping union.
    cad=BASE/'meshes/finite_eyelet_support_v11'
    for path in sorted(cad.glob('*support*.stl')):
        meshes.append((path.name,trimesh.load_mesh(path,process=True)))
    theta=.731;R=np.array([[np.cos(theta),-np.sin(theta),0],[np.sin(theta),np.cos(theta),0],[0,0,1]])
    for name,m in meshes:
        v,c,I=moments(m.vertices,m.faces);ref=m.mass_properties;norm=np.asarray(ref.inertia)/ref.mass
        vt,ct,It=moments(m.vertices@R.T+[7.,-3.,2.],m.faces)
        records.append(dict(part=name,volume_mm3=float(v),COM_mm=c.tolist(),normalized_inertia_mm2=I.tolist(),volume_reference_error_mm3=float(abs(v-ref.volume)),COM_reference_error_mm=float(np.max(abs(c-ref.center_mass))),inertia_reference_error_mm2=float(np.max(abs(I-norm))),objectivity_COM_error_mm=float(np.max(abs(ct-(R@c+[7.,-3.,2.])))),objectivity_inertia_error_mm2=float(np.max(abs(It-R@I@R.T)))))
    ro=cfg['tendon']['guide_outer_radius'];ri=cfg['tendon']['guide_hole_radius'];L=cfg['tendon'].get('guide_length_mm',2.)
    exact=np.diag([(ro*ro+ri*ri)/2,(ro*ro+ri*ri)/4+L*L/12,(ro*ro+ri*ri)/4+L*L/12])
    ring_errors=[dict(segments=n,normalized_inertia_error_mm2=float(np.max(abs(np.array(next(r for r in records if r['part']==f'eyelet{n}')['normalized_inertia_mm2'])-exact)))) for n in (16,32,64)]
    maxerr=max(max(r['COM_reference_error_mm'],r['inertia_reference_error_mm2'],r['objectivity_COM_error_mm'],r['objectivity_inertia_error_mm2']) for r in records)
    passed=maxerr<1e-9 and all(ring_errors[i+1]['normalized_inertia_error_mm2']<ring_errors[i]['normalized_inertia_error_mm2'] for i in range(2))
    result=dict(status='PASS_INDEPENDENT_GEOMETRIC_MOMENTS' if passed else 'FAIL',scope='Signed tetrahedral volume moments vs trimesh,analytic box/annulus and rigid objectivity. No physical density,join,union or B3 dynamics qualification.',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),source_sha256=sha(Path(__file__)),records=records,analytic_annulus_normalized_inertia_mm2=exact.tolist(),annulus_mesh_errors=ring_errors,maximum_crosscheck_error=maxerr,physical_density=None,physical_union_mass=None)
    (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
