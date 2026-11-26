"""Representation diagnostic on immutable actual AK whole-Palm tetrahedra.
No equilibrium solve and no removal of failed elements. Unit curvature is a
manufactured kinematic probe, not measured product deformation or capacity.
"""
import json,shutil,time
import numpy as np
from baseline_registry import ROOT,REPO,sha,ref,dump
TAGS=('AK_whole_palm_h8_3','AK_whole_palm_h6_1','AK_whole_palm_h4_1')
E=70e9; NU=.33

def field(p,axis):
    # Exact uniaxial bending with free Poisson contraction: eps_aa=-z,
    # eps_bb=eps_zz=nu*z and all shears zero; z centered on Palm midplane.
    a=p[:,axis];b=p[:,1-axis];z=p[:,2]+.0095
    u=np.empty_like(p);u[:,axis]=-a*z;u[:,1-axis]=NU*b*z
    u[:,2]=.5*(a*a+NU*(z*z-b*b));return u

def element_energy(p,t,u):
    dx=p[t[:,1:]]-p[t[:,0,None]];du=u[t[:,1:]]-u[t[:,0,None]]
    grad=np.linalg.solve(dx,du).transpose(0,2,1);eps=(grad+grad.transpose(0,2,1))/2
    v=abs(np.linalg.det(dx))/6;mu=E/(2*(1+NU));lam=E*NU/((1+NU)*(1-2*NU))
    total=v*(mu*np.sum(eps*eps,axis=(1,2))+.5*lam*np.trace(eps,axis1=1,axis2=2)**2)
    shear=v*2*mu*(eps[:,0,1]**2+eps[:,0,2]**2+eps[:,1,2]**2)
    return total,shear,v

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/transmission/AK_palm_bending1';out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py');start=time.monotonic();rows=[]
    criteria=dict(original_min_quality=.01,representation_relative_energy_limit=.01,verification_rtol=1e-8,
        scope='Diagnostic 1% representation screen; unchanged original quality criterion; not equilibrium/strength gate')
    dump(out/'inputs.json',dict(producer=ref(out/'producer.py'),criteria=criteria,sources=[ref(ROOT/'validation/transmission'/s/'summary.json') for s in TAGS]))
    for tag in TAGS:
        assert not (ROOT/'runtime/STOP').exists()
        src=ROOT/'validation/transmission'/tag/'summary.json';d=json.loads(src.read_text())
        for r in (d['field'],d['STEP'],d['source'],d['producer']):assert sha(REPO/r['path'])==r['SHA256']
        with np.load(REPO/d['field']['path']) as a:p=a['points_m'];t=a['tetra'];u=a['displacement_m']
        actual,_,v=element_energy(p,t,u);verts=p[t];cent=verts.mean(axis=1)
        edge2=sum(np.sum((verts[:,i]-verts[:,j])**2,axis=1) for i in range(4) for j in range(i))
        q=12*(3*v)**(2/3)/edge2;poor=q<.01
        z=verts[:,:,2]+.0095;exact=.5*E*v*((z.sum(axis=1))**2+(z*z).sum(axis=1))/20
        probes=[]
        for axis in (0,1):
            en,sh,_=element_energy(p,t,field(p,axis));ratio=float(en.sum()/exact.sum())
            probes.append(dict(axis='XY'[axis],P1_energy_J=float(en.sum()),continuum_energy_J=float(exact.sum()),
                relative_energy_error=ratio-1,shear_energy_J=float(sh.sum()),shear_energy_fraction=float(sh.sum()/en.sum()),
                poor_element_energy_fraction=float(en[poor].sum()/en.sum()),representation_1percent_pass=abs(ratio-1)<.01))
        worst=[]
        for i in np.argsort(q)[:20]:
            faces=[np.linalg.norm(np.cross(verts[i,j]-verts[i,k],verts[i,l]-verts[i,k]))/2 for j,k,l in ((0,1,2),(0,1,3),(0,2,3),(1,2,3))]
            mm=cent[i]*1000
            worst.append(dict(element=int(i),quality=float(q[i]),centroid_mm=mm.tolist(),vertices_mm=(verts[i]*1000).tolist(),
                minimum_altitude_mm=float(3*v[i]/max(faces)*1000),
                support_partition_radial_distance_mm=abs(float(np.hypot(*mm[:2]))-30),
                load_partition_radial_distance_mm=abs(float(np.hypot(mm[0]-127,mm[1]+1))-4)))
        rows.append(dict(source=ref(src),field=d['field'],h_mm=d['h_mm'],elements=len(t),nodes=len(p),minimum_quality=float(q.min()),
            poor_element_count=int(poor.sum()),poor_volume_fraction=float(v[poor].sum()/v.sum()),
            actual_solved_energy_J=float(actual.sum()),actual_saved_energy_J=d['energy_J'],
            poor_actual_energy_fraction=float(actual[poor].sum()/actual.sum()),worst_elements=worst,probes=probes))
    result=dict(status='ACTUAL_PALM_REPRESENTATION_DIAGNOSTIC_COMPLETE',rows=rows,producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),criteria=criteria,
        elapsed_s=time.monotonic()-start,whole_system_release=False,
        limitations=['Manufactured curvature is not actual solved motion or measured load','Interpolation energy mismatch does not establish unique cause or a bound on actual compliance',
        'No failed element is removed from any result','No new mesh, material fit, boundary support, strength or physical PASS','P2 representation requires a separate supported equilibrium solve before adoption'])
    dump(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k!='rows'}));print(json.dumps([dict(h_mm=r['h_mm'],poor_count=r['poor_element_count'],probes=r['probes']) for r in rows]))
if __name__=='__main__':main()
