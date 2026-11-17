"""Exact frozen-FEM modal impulse response versus BE and midpoint.

This is NOT an actual nonlinear SOFA trajectory. It isolates temporal phase
resolution of the modal spectrum measured at an actual event.
"""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args()
    source=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((source/'summary.json').read_text())
    if meta['status']!='PASS' or meta['negative_modes']:raise ValueError('completed positive frozen spectrum required;negative modes cannot be discarded')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
    rows=list(csv.DictReader((source/'modes.csv').open()));lam=np.asarray([float(r['eigenvalue']) for r in rows]);amplitude=np.sqrt(2*np.asarray([float(r['jump_metric_energy']) for r in rows]));damping=2.
    times=np.append(np.arange(1,10)*.0025,.023)
    beta=np.sqrt(damping*damping/4-lam+0j);zero=beta==0
    def exact(t):
        ratio=np.empty_like(beta);ratio[zero]=t;ratio[~zero]=np.sinh(beta[~zero]*t)/beta[~zero]
        q=amplitude*np.exp(-damping*t/2)*ratio;v=amplitude*np.exp(-damping*t/2)*(np.cosh(beta*t)-damping/2*ratio)
        if np.max(np.abs(q.imag))+np.max(np.abs(v.imag))>1e-12:raise ValueError('unexpected complex state')
        return q.real,v.real
    reference=[exact(t) for t in times];metrics={};journal=[]
    for method in ('BE','midpoint'):
        for step in (.0025,.00125,.000625):
            q=np.zeros_like(lam);v=amplitude.copy();time=0.;observed=[]
            for target in times:
                while time<target:
                    h=min(step,target-time)
                    if method=='BE':
                        vn=(v-h*lam*q)/(1+damping*h+h*h*lam);qn=q+h*vn
                    else:
                        vn=((1-damping*h/2-h*h*lam/4)*v-h*lam*q)/(1+damping*h/2+h*h*lam/4);qn=q+h/2*(v+vn)
                    q,v=qn,vn;time+=h
                observed.append((q.copy(),v.copy()));journal.append([method,step,target,.5*np.dot(lam*q,q),.5*np.dot(v,v)])
            result={}
            for key,k in (('mass_norm_displacement',0),('mass_norm_velocity',1)):
                absolute=max(float(np.linalg.norm(x[k]-y[k])) for x,y in zip(observed,reference));scale=max(float(np.linalg.norm(y[k])) for y in reference)
                result[key]=dict(absolute=absolute,reference_scale=scale,relative=absolute/scale)
            for name,energy in (('elastic',lambda state:.5*np.dot(lam*state[0],state[0])),('kinetic',lambda state:.5*np.dot(state[1],state[1]))):
                absolute=max(abs(float(energy(x)-energy(y))) for x,y in zip(observed,reference));scale=max(float(energy(y)) for y in reference);result[name]=dict(absolute=absolute,reference_scale=scale,relative=absolute/scale)
            metrics[method+'_'+str(step)]=result
    with (out/'response.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['method','dt','elapsed_time','quadratic_elastic_energy','kinetic_energy']);writer.writerows(journal)
    write_json(out/'summary.json',dict(status='PASS',scope='completed independent exact frozen-linear FEM temporal diagnostic;NOT actual nonlinear SOFA convergence PASS',source_case=a.case,source_hashes={file:sha(source/file) for file in ('summary.json','modes.csv')},metrics=metrics,reference='closed-form damped oscillators for complete mass-normalized spectrum;no modes truncated',damping=damping,physical_scope='jump-only perturbation about frozen actual impact state;no evolving contact,actuation or geometry',sign_note='modal amplitude magnitudes suffice for squared mass-norm differences and diagonal quadratic energies;not reconstructed nodal directions'))
    print(json.dumps({k:{m:round(100*v['relative'],5) for m,v in value.items()} for k,value in metrics.items()}))
if __name__=='__main__':main()
