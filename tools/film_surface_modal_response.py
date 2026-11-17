"""Exact frozen-FEM modal impulse response versus BE and midpoint.

This is NOT an actual nonlinear SOFA trajectory. It isolates temporal phase
resolution of the modal spectrum measured at an actual event.
"""
import argparse,csv,json,shutil
import numpy as np
def rational_step(q,v,lam,damping,h,method):
    if method not in ('Gauss2','Radau2') or h<=0:raise ValueError('rational oscillator method/step')
    u1,u2,w1,w2=(.5,1/12,-.5,1/12) if method=='Gauss2' else (1/3,0.,-2/3,1/6)
    bq=(1-u2*h*h*lam)*q+(u1*h-u2*h*h*damping)*v
    bv=(-u1*h*lam+u2*h*h*damping*lam)*q+(1-u1*h*damping+u2*h*h*(damping*damping-lam))*v
    d00=1-w2*h*h*lam;d01=w1*h-w2*h*h*damping;d10=-w1*h*lam+w2*h*h*damping*lam;d11=1-w1*h*damping+w2*h*h*(damping*damping-lam);det=d00*d11-d01*d10
    if np.any(det==0):raise ValueError('singular rational oscillator step;no epsilon')
    return (d11*bq-d01*bv)/det,(-d10*bq+d00*bv)/det
def main():
    from curve_common import ROOT,sha,write_json
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--steps',nargs='+',type=float);p.add_argument('--duration',type=float);p.add_argument('--higher-order',action='store_true');a=p.parse_args()
    if a.duration is not None and not 0<a.duration<=.1:raise ValueError('bounded modal window')
    if a.steps and any(not 0<h<=.01 for h in a.steps):raise ValueError('positive bounded modal step')
    source=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((source/'summary.json').read_text())
    if meta['status']!='PASS' or meta['negative_modes']:raise ValueError('completed positive frozen spectrum required;negative modes cannot be discarded')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
    rows=list(csv.DictReader((source/'modes.csv').open()));lam=np.asarray([float(r['eigenvalue']) for r in rows]);amplitude=np.asarray([float(r['signed_amplitude']) for r in rows]) if all('signed_amplitude' in r for r in rows) else np.sqrt(2*np.asarray([float(r['jump_metric_energy']) for r in rows]));damping=2.
    gram=np.loadtxt(source/'nodal_gram.csv',delimiter=',') if (source/'nodal_gram.csv').exists() else None
    if gram is not None and (gram.shape!=(len(lam),len(lam)) or not np.all(np.isfinite(gram)) or not all('signed_amplitude' in r for r in rows)):raise ValueError('complete signed amplitudes/nodal Gram required')
    times=np.linspace(a.duration/16,a.duration,16) if a.duration is not None else np.append(np.arange(1,10)*.0025,.023)
    beta=np.sqrt(damping*damping/4-lam+0j);zero=beta==0
    def exact(t):
        ratio=np.empty_like(beta);ratio[zero]=t;ratio[~zero]=np.sinh(beta[~zero]*t)/beta[~zero]
        q=amplitude*np.exp(-damping*t/2)*ratio;v=amplitude*np.exp(-damping*t/2)*(np.cosh(beta*t)-damping/2*ratio)
        if np.max(np.abs(q.imag))+np.max(np.abs(v.imag))>1e-12:raise ValueError('unexpected complex state')
        return q.real,v.real
    reference=[exact(t) for t in times];metrics={};journal=[]
    for method in (('BE','midpoint','Gauss2','Radau2') if a.higher_order else ('BE','midpoint')):
        for step in (a.steps or (.0025,.00125,.000625)):
            q=np.zeros_like(lam);v=amplitude.copy();time=0.;observed=[]
            for target in times:
                while time<target:
                    h=min(step,target-time)
                    if method=='BE':
                        vn=(v-h*lam*q)/(1+damping*h+h*h*lam);qn=q+h*vn
                    elif method=='midpoint':
                        vn=((1-damping*h/2-h*h*lam/4)*v-h*lam*q)/(1+damping*h/2+h*h*lam/4);qn=q+h/2*(v+vn)
                    else:
                        # Rational matrix functions of A=[[0,1],[-lambda,-c]].
                        # Gauss2:Pade[2/2],RadauIIA2:Pade[1/2]. No modes cut.
                        qn,vn=rational_step(q,v,lam,damping,h,method)
                    q,v=qn,vn;time+=h
                observed.append((q.copy(),v.copy()));journal.append([method,step,target,.5*np.dot(lam*q,q),.5*np.dot(v,v)])
            result={}
            for key,k in (('mass_norm_displacement',0),('mass_norm_velocity',1)):
                absolute=max(float(np.linalg.norm(x[k]-y[k])) for x,y in zip(observed,reference));scale=max(float(np.linalg.norm(y[k])) for y in reference)
                result[key]=dict(absolute=absolute,reference_scale=scale,relative=absolute/scale)
            if gram is not None:
                def nodal_norm(x):
                    square=float(x@gram@x)
                    if square<0:raise ValueError('negative squared nodal norm;no epsilon fix')
                    return np.sqrt(square)
                for key,k in (('full_nodal_displacement',0),('full_nodal_velocity',1)):
                    absolute=max(float(nodal_norm(x[k]-y[k])) for x,y in zip(observed,reference));scale=max(float(nodal_norm(y[k])) for y in reference);result[key]=dict(absolute=absolute,reference_scale=scale,relative=absolute/scale)
            for name,energy in (('elastic',lambda state:.5*np.dot(lam*state[0],state[0])),('kinetic',lambda state:.5*np.dot(state[1],state[1]))):
                absolute=max(abs(float(energy(x)-energy(y))) for x,y in zip(observed,reference));scale=max(float(energy(y)) for y in reference);result[name]=dict(absolute=absolute,reference_scale=scale,relative=absolute/scale)
            metrics[method+'_'+str(step)]=result
    with (out/'response.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['method','dt','elapsed_time','quadratic_elastic_energy','kinetic_energy']);writer.writerows(journal)
    files=['summary.json','modes.csv']+(['nodal_gram.csv'] if gram is not None else [])
    write_json(out/'summary.json',dict(status='PASS',scope='completed independent exact frozen-linear FEM temporal diagnostic;NOT actual nonlinear SOFA convergence PASS',source_case=a.case,source_hashes={file:sha(source/file) for file in files},metrics=metrics,reference='closed-form damped oscillators for complete mass-normalized spectrum;no modes truncated',damping=damping,physical_scope='jump-only perturbation about frozen actual impact state;no evolving contact,actuation or geometry',sign_note='signed amplitudes and full-nodal Gram used when provided;otherwise magnitudes suffice only for diagonal mass-norm/energy metrics'))
    print(json.dumps({k:{m:round(100*v['relative'],5) for m,v in value.items()} for k,value in metrics.items()}))
if __name__=='__main__':main()
