"""Static material-owned contact exchange. No derivative of moving minima.
Same rigid-rail/PET fixture and energy as prior study; different verified
constraint representation. Initial stored q is a starting guess, not correction.
"""
import argparse,json,math,shutil,ast
from pathlib import Path
import numpy as np
from scipy.optimize import minimize,brentq
from baseline_registry import ROOT,ref,dump
import finite_pet_coupon as geometric
import rod_point_jacobian as rod
def solve(old,L,profile,exchanges=4,checkpoint=None):
    q=np.array(old['state_angles_rad']);n=len(q);h=L/n;theta=math.radians(old['fixture_angle_deg']);R=.088/theta
    c,s=math.cos(theta),math.sin(theta);M=np.array([[c,s],[-s,c]]);shift=np.array([.0504-R*(1-c),-.007-R*s])-M@np.array([.0504,-.095])
    fc=np.array([profile['center_X_mm'],profile['center_Z_mm']])*.001;fr=profile['radius_mm']*.001
    EI=507000*6894.757293168*(.024-.012*(.007+(np.arange(n)+.5)*h)/.100)*.0003**3/12;scale=float(EI.mean()*theta**2/.088)
    points={ast.literal_eval(k):list(v) for k,v in old['material_contact_points'].items()} if 'material_contact_points' in old else {(i,side):sorted(set([0.,1.,*((np.polynomial.legendre.leggauss(3)[0]+1)/2).tolist()])) for i in range(n) for side in (-1,1)}
    if set(points)!={(i,side) for i in range(n) for side in (-1,1)} or any(not all(0<=t<=1 for t in ts) for ts in points.values()):raise ValueError('Invalid stored material coordinates')
    def geometry(v):
        a=np.r_[0.,v];d=np.diff(a);step=h*np.sinc(d/(2*np.pi))*np.exp(1j*(a[1:]+a[:-1])/2);return a,np.r_[1j*.00025,1j*.00025+np.cumsum(step)]
    def point(a,u,i,t,side,local=True):
        delta=a[i+1]-a[i];p=u[i]+h*t*np.sinc(delta*t/(2*np.pi))*np.exp(1j*(a[i]+delta*t/2));phi=a[i]+delta*t
        world=np.array([.0504-p.imag,-.007-p.real])+side*.00015*np.array([-math.cos(phi),math.sin(phi)])
        return M.T@(world-shift) if local else world
    def distances(p):
        def rectangle(lo,hi):
            lo,hi=np.array(lo),np.array(hi);d=np.abs(p-(lo+hi)/2)-(hi-lo)/2
            return np.linalg.norm(np.maximum(d,0))+min(float(d.max()),0.)
        return np.array([rectangle([.040,-.095],[.049,-.084]),rectangle([.040,-.100],[.050,-.095]),max(rectangle([.04898,-.095],[.04990,-.090]),np.linalg.norm(p-fc)-fr)])
    def energy(v):return float(np.sum(EI*np.diff(np.r_[0.,v])**2/(2*h))/scale)
    def gradient(v):
        d=np.diff(np.r_[0.,v]);g=EI*d/h;g[:-1]-=EI[1:]*d[1:]/h;return g/scale
    def constraints(v):
        a,u=geometry(v);g=[]
        for (i,side),ts in points.items():
            for t in ts:
                g.extend(distances(point(a,u,i,t,side))/1e-4)
                if side==-1 and not (i==0 and t==0):
                    p=point(a,u,i,t,0,False);g.append((R-.00025-np.linalg.norm(p-[.0504-R,-.007]))/1e-4)
        return np.array(g)
    def constraint_derivatives(v,values=False):
        prepared=rod.prepare(v,L);rows=[];g=[]
        for (i,side),ts in points.items():
            for t in ts:
                p,J=rod.point(prepared,i,t,side,M,shift);value,N=rod.walls(p,fc,fr);rows.extend(N@J/1e-4);g.extend(value/1e-4)
                if side==-1 and not (i==0 and t==0):
                    p,J=rod.point(prepared,i,t,0,M,shift,False);d=p-np.array([.0504-R,-.007]);radius=np.linalg.norm(d)
                    rows.append(-(d/radius)@J/1e-4);g.append((R-.00025-radius)/1e-4)
        return np.array(g) if values else np.array(rows)
    history=[]
    accepted_iterations=0
    def save_guess(v,force=False):
        nonlocal accepted_iterations
        accepted_iterations+=1
        if checkpoint is not None and (force or accepted_iterations%10==0):
            checkpoint(old,v,points,history,accepted_iterations)
    for exchange in range(exchanges):
        identity=float(np.max(abs(constraint_derivatives(q,True)-constraints(q))))
        if identity>1e-9:raise ValueError('Analytic Jacobian module changed physical constraint values')
        solution=minimize(energy,q,jac=gradient,method='SLSQP',constraints=[dict(type='ineq',fun=constraints,jac=constraint_derivatives)],callback=save_guess,options=dict(ftol=1e-12,maxiter=300));q=solution.x;a,u=geometry(q);added=0
        minimum_witness=math.inf
        for (i,side),ts in points.items():
            splits=[0.,1.];delta=a[i+1]-a[i]
            if abs(delta)>1e-12:
                lo,hi=sorted((a[i]-theta,a[i+1]-theta))
                for k in range(math.floor(2*lo/math.pi)-1,math.ceil(2*hi/math.pi)+2):
                    t=(k*math.pi/2-(a[i]-theta))/delta
                    if 0<t<1:splits.append(t)
            splits=sorted(splits);candidates=list(splits)
            for axis,levels in [(0,(.040,.04898,.049,.0499,.050)),(1,(-.100,-.095,-.090,-.084))]:
                for level in levels:
                    fn=lambda t:point(a,u,i,t,side)[axis]-level
                    for left,right in zip(splits[:-1],splits[1:]):
                        if fn(left)*fn(right)<0:candidates.append(brentq(fn,left,right,xtol=1e-13))
            # Exact extrema of both circle distances generate material-owned
            # witnesses. This addresses the measured1.74nm missed radial gap,
            # rather than relaxing its1nm criterion or scanning sample counts.
            def radial_derivative(t):
                phi=a[i]+delta*t;p=point(a,u,i,t,0,False)
                return float((p-np.array([.0504-R,-.007]))@(h*np.array([-math.sin(phi),-math.cos(phi)])))
            def lip_derivative(t):
                phi=a[i]+delta*t-theta;p=point(a,u,i,t,side)
                return float((p-fc)@((h-side*.00015*delta)*np.array([-math.sin(phi),-math.cos(phi)])))
            circle_splits=list(splits)
            for derivative in (radial_derivative,lip_derivative):
                for left,right in zip(splits[:-1],splits[1:]):
                    if derivative(left)*derivative(right)<0:
                        t=brentq(derivative,left,right,xtol=1e-13);candidates.append(t)
                        if derivative==lip_derivative:circle_splits.append(t)
            circle_splits=sorted(circle_splits);fn=lambda t:np.linalg.norm(point(a,u,i,t,side)-fc)-fr
            for left,right in zip(circle_splits[:-1],circle_splits[1:]):
                if fn(left)*fn(right)<0:candidates.append(brentq(fn,left,right,xtol=1e-13))
            # Boundary roots alone have g=0 even when the intervening arc passes
            # through solid material. A witness in EACH feature interval is
            # required (measured actual-BRep overlap0.0883mm3 in owner2).
            ordered=sorted(set(candidates));candidates +=[(l+r)/2 for l,r in zip(ordered[:-1],ordered[1:])]
            # Add actual feature material coordinates, not a denser uniform scan.
            for t in candidates:
                wall=float(distances(point(a,u,i,t,side)).min());rad=R-.00025-np.linalg.norm(point(a,u,i,t,0,False)-[.0504-R,-.007]);minimum_witness=min(minimum_witness,wall,rad)
                if min(wall,rad)<=1e-9 and min(abs(t-oldt) for oldt in ts)>1e-7:ts.append(t);added+=1
            ts.sort()
        history.append(dict(exchange=exchange,solver_success=bool(solution.success),message=solution.message,energy_J=energy(q)*scale,added_material_features=added,minimum_feature_interval_witness_m=minimum_witness,minimum_fixed_point_constraint=float(constraints(q).min()),jacobian_model_value_identity_max=identity,optimizer_iterations=int(solution.nit),points=sum(len(v) for v in points.values())))
        save_guess(q,True)
        if not added:break
    p=point(*geometry(q),n-1,1.,0,False);arc=R*math.atan2(-p[1]-.007,p[0]-(.0504-R))
    gap=float(geometric.continuous_gap(q,n,R).min())
    return dict(n=n,fixture_angle_deg=old['fixture_angle_deg'],state_angles_rad=q.tolist(),energy_J=energy(q)*scale,axial_migration_m=arc-L,
        continuous_min_gap_m=gap,solver_success=bool(solution.success),status='PASS' if solution.success and gap>=-1e-9 and minimum_witness>=-1e-9 and constraints(q).min()>=-1e-5 else 'FAIL',
        material_contact_points={str(k):v for k,v in points.items()},history=history,
        old_state_difference_rad=float(np.linalg.norm(q-np.array(old['state_angles_rad']))),warning='Sample/material-owner solve only; exact BRep, physical force certificate and1% migration audit REQUIRED')
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--seed',default='finite_pet_AD6');p.add_argument('--seed-file');p.add_argument('--meshes',nargs='+',type=int,default=[16,32]);p.add_argument('--exchanges',type=int,default=4);a=p.parse_args()
    if not 1<=a.exchanges<=12:p.error('1..12exchanges per bounded child; no indefinite optimizer loop')
    out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/a.seed_file if a.seed_file else ROOT/'validation/finger'/a.seed/'summary.json'
    if not source.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Static seed must remain within integrated package')
    d=json.loads(source.read_text());candidate=ROOT/'cad/exports/revAD_funnel1/summary.json';profile=json.loads(candidate.read_text())['funnel_profile'];L=d['PET_free_length_m'];geometric.L=L
    if d['candidate']!=ref(candidate):raise ValueError('Different candidate cannot be used as a static optimizer seed')
    rows=[]
    checkpoints=[]
    def checkpoint(old,v,points,history,iteration):
        directory=out/'optimizer_checkpoints';directory.mkdir(exist_ok=True)
        path=directory/f'n{old["n"]}_{iteration:08d}.json'
        if path.exists():raise RuntimeError('Never overwrite a saved optimizer guess')
        row=dict(n=old['n'],fixture_angle_deg=old['fixture_angle_deg'],state_angles_rad=v.tolist(),material_contact_points={str(k):list(ts) for k,ts in points.items()},status='OPTIMIZER_GUESS_NOT_PHYSICAL_PASS')
        dump(path,dict(rows=[row],PET_free_length_m=L,candidate=ref(candidate),source=ref(source),scope='STATIC NLP INITIAL GUESS ONLY; MAY BE INFEASIBLE; NOT NATIVE DYNAMIC CHECKPOINT',history=history))
        checkpoints.append(ref(path))
    for old in d['rows']:
        if old['n'] not in a.meshes:continue
        rows.append(solve(old,L,profile,a.exchanges,checkpoint));dump(out/'partial_states.json',dict(rows=rows,complete=False))
    result=dict(status='PASS' if rows and all(r['status']=='PASS' for r in rows) else 'FAIL',scope='MATERIAL-OWNED CONSTRAINT EXCHANGE / FRICTIONLESS RIGID-RAIL COUPON ONLY',rows=rows,PET_free_length_m=L,source=ref(source),candidate=ref(candidate),producer=ref(out/'producer.py'),geometry_implementation=ref(Path(geometric.__file__)),analytical_Jacobian=ref(Path(rod.__file__)),whole_system_release=False,seed_scope='STATIC OPTIMIZER INITIAL GUESS AND FIXED MATERIAL WITNESSES ONLY; NOT NATIVE STATE RESTORE OR DYNAMIC CHUNK EQUIVALENCE')
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],rows=[{k:r[k] for k in ('n','status','axial_migration_m','continuous_min_gap_m','old_state_difference_rad')} for r in rows]),indent=2))
    dump(out/'LOCAL_OPTIMIZER_CHECKPOINTS.json',dict(scope='LOCAL ONLY STATIC INITIAL GUESSES; NO PHYSICAL VERDICT',checkpoints=checkpoints))
if __name__=='__main__':main()
