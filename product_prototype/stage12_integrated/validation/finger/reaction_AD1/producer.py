"""Independent stored-state normal-cone certificate, not q correction.
Physical surface normals and fixed material-coordinate point Jacobians avoid
finite-differencing a moving minimum/contact-owner. No negative contact force.
"""
import argparse,json,math,shutil
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar,nnls
from baseline_registry import ROOT,ref,dump
def certify(row,L,profile):
    q=np.array(row['state_angles_rad']);n=len(q);h=L/n;theta=math.radians(row['fixture_angle_deg']);R=.088/theta
    c,s=math.cos(theta),math.sin(theta);M=np.array([[c,s],[-s,c]])
    shift=np.array([.0504-R*(1-c),-.007-R*s])-M@np.array([.0504,-.095])
    fc=np.array([profile['center_X_mm'],profile['center_Z_mm']])*.001;fr=profile['radius_mm']*.001
    def material(v,i,t,side,local=True):
        a=np.r_[0.,v];delta=np.diff(a)
        factors=np.sinc(delta/(2*np.pi))*np.exp(1j*(a[1:]+a[:-1])/2)*h
        u=1j*.00025+factors[:i].sum()+h*t*np.sinc(delta[i]*t/(2*np.pi))*np.exp(1j*(a[i]+delta[i]*t/2))
        p=np.array([.0504-u.imag,-.007-u.real]);phi=a[i]+delta[i]*t
        p+=side*.00015*np.array([-math.cos(phi),math.sin(phi)])
        return M.T@(p-shift) if local else p
    def segment(p,a,b):
        a,b=np.array(a),np.array(b);t=np.clip((p-a)@(b-a)/((b-a)@(b-a)),0,1);return a+t*(b-a)
    surfaces=[('core_right',lambda p:segment(p,[.049,-.095],[.049,-.084]),np.array([1.,0.])),
      ('core_top',lambda p:segment(p,[.04,-.084],[.049,-.084]),np.array([0.,1.])),
      ('bottom_right',lambda p:segment(p,[.05,-.100],[.05,-.095]),np.array([1.,0.])),
      ('bottom_top',lambda p:segment(p,[.04,-.095],[.05,-.095]),np.array([0.,1.])),
      ('lip_top',lambda p:segment(p,[.04898,-.09],[fc[0]+math.sqrt(fr*fr-.005**2),-.09]),np.array([0.,1.]))]
    def circle(p):
        a=math.atan2(p[1]-fc[1],p[0]-fc[0]);a=np.clip(a,0,math.asin(.005/fr));return fc+fr*np.array([math.cos(a),math.sin(a)])
    surfaces.append(('lip_circle',circle,None));contacts=[]
    for i in range(n):
        for side in (-1,1):
            for name,project,normal in surfaces:
                def distance(t):
                    p=material(q,i,t,side);return float(np.sum((p-project(p))**2))
                solution=minimize_scalar(distance,bounds=(0,1),method='bounded',options={'xatol':1e-13})
                t=min((0.,float(solution.x),1.),key=distance);p=material(q,i,t,side);gap=math.sqrt(distance(t))
                if gap<=1e-9:
                    normal=(project(p)-fc)/fr if normal is None else normal
                    contacts.append((i,t,side,normal,name,gap,True))
        # Independent rail contact at centreline, radial normal toward rail centre.
        def gap(t):return R-.00025-np.linalg.norm(material(q,i,t,0,False)-np.array([.0504-R,-.007]))
        sol=minimize_scalar(gap,bounds=(0,1),method='bounded',options={'xatol':1e-13});t=min((0.,float(sol.x),1.),key=gap)
        if abs(gap(t))<=1e-9:
            p=material(q,i,t,0,False);normal=(np.array([.0504-R,-.007])-p);normal/=np.linalg.norm(normal)
            contacts.append((i,t,0,normal,'rail',abs(gap(t)),False))
    columns=[];eps=1e-6;kept=[]
    for i,t,side,normal,name,gap,local in contacts:
        column=np.array([normal@(material(q+np.eye(n)[j]*eps,i,t,side,local)-material(q-np.eye(n)[j]*eps,i,t,side,local))/(2*eps) for j in range(n)])
        if np.linalg.norm(column)>1e-12:columns.append(column);kept.append(dict(segment=i,material_fraction=t,side=side,surface=name,gap_m=gap,normal=normal.tolist()))
    width=.024-.012*(.007+(np.arange(n)+.5)*h)/.100;EI=507000*6894.757293168*width*.0003**3/12
    delta=np.diff(np.r_[0.,q]);grad=EI*delta/h;grad[:-1]-=EI[1:]*delta[1:]/h
    forces,res=nnls(np.array(columns).T,grad,maxiter=100*n) if columns else ([],np.linalg.norm(grad))
    scale=max(float(np.linalg.norm(grad)),1e-20);complementarity=max((abs(f*r['gap_m']) for f,r in zip(forces,kept)),default=0.)/max(float(row['energy_J']),1e-20)
    for f,r in zip(forces,kept):r['normal_force_N']=float(f)
    return dict(n=n,angle_deg=row['fixture_angle_deg'],force_equivalent_N=float(res/L),maximum_N=1e-8,
        complementarity_relative=complementarity,complementarity_maximum=1e-7,contacts=kept,
        status='PASS' if res/L<1e-8 and complementarity<1e-7 else 'FAIL',
        state_changed=False,warning='A nonnegative force certificate is not a unique physical contact-force prediction or actual flexible-rail solution')
def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--candidate',required=True);p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'validation/finger'/a.input/'summary.json';d=json.loads(source.read_text());candidate=ROOT/'cad/exports'/a.candidate/'summary.json';profile=json.loads(candidate.read_text())['funnel_profile']
    rows=[certify(r,d['PET_free_length_m'],profile) for r in d['rows'] if r['n'] in (16,32)]
    result=dict(status='PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL',scope='INDEPENDENT STORED-STATE FRICTIONLESS NORMAL-CONE CERTIFICATE ONLY',rows=rows,source=ref(source),candidate=ref(candidate),producer=ref(out/'producer.py'),product_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],rows=[{k:r[k] for k in ('n','angle_deg','status','force_equivalent_N','complementarity_relative')} for r in rows]),indent=2))
if __name__=='__main__':main()
