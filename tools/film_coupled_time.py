"""All-pair .1% coupled time comparison at common physical coordinates."""
import argparse,csv,itertools,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def metric(x,y):
    difference=float(np.max(np.linalg.norm(x-y,axis=1))) if x.ndim==2 else float(np.max(np.abs(x-y)));scale=float(np.max(np.linalg.norm(y,axis=1))) if y.ndim==2 else float(np.max(np.abs(y)));relative=difference/scale if scale else 0. if difference==0 else None
    return dict(status='PASS' if relative is not None and relative<=.001 else 'FAIL',maximum_absolute_error=difference,reference_scale=scale,relative_error=relative)
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');cases=[]
    for name in a.cases:
        folder=ROOT/'results'/('autonomous_film_'+name);meta=json.loads((folder/'identity.json').read_text());summary=json.loads((folder/'summary.json').read_text())
        if summary['status']!='PASS':raise ValueError('incomplete actual coupled case')
        if cases:
            original=cases[0][1]
            for key in ('binary_sha256','mode','duration','body_mass','inertia_per_mass','rayleigh_mass','initial_body_center','initial_body_velocity'):
                if meta[key]!=original[key]:raise ValueError('physical/source binary mismatch:'+key)
            for key,default in (('body_force_z',0.),('strict_newton',False),('midpoint_contact',False)):
                if meta.get(key,default)!=original.get(key,default):raise ValueError('force/numerical accuracy input mismatch:'+key)
        states=list(csv.DictReader((folder/meta.get('comparison_state_file',meta.get('state_file','coupled.states.csv'))).open()));events=list(csv.DictReader((folder/'coupled.events.csv').open()));cases.append((name,meta,states,events))
    cases.sort(key=lambda c:c[1].get('comparison_steps',c[1]['steps']));pairs={}
    for left,right in itertools.combinations(cases,2):
        ls,rs=left[2],right[2];fine=np.array([float(r['time']) for r in rs]);indices=[int(np.argmin(abs(fine-float(s['time'])))) for s in ls]
        if any(abs(fine[k]-float(s['time']))>1e-12 for k,s in zip(indices,ls)):raise ValueError('no common physical output coordinates;do not interpolate nonsmooth events')
        rr=[rs[k] for k in indices];errors={}
        for key in ('U_shell','U_attachment','K_film','K_linear','K_rotation'):
            errors[key]=metric(np.array([float(s[key]) for s in ls]),np.array([float(s[key]) for s in rr]))
        for key in ('local_displacement','local_velocity','body_velocity','body_omega'):
            errors[key]=metric(np.array([np.fromstring(s[key],sep=' ') for s in ls]),np.array([np.fromstring(s[key],sep=' ') for s in rr]))
        center=np.fromstring(left[1]['initial_body_center'],sep=' ');errors['body_displacement']=metric(np.array([np.fromstring(s['body_center'],sep=' ')-center for s in ls]),np.array([np.fromstring(s['body_center'],sep=' ')-center for s in rr]))
        def atoms(rows):
            times=sorted(set(r['time'] for r in rows));return [dict(time=float(t),impulse=sum(float(r['impulse']) for r in rows if r['time']==t),impact_loss=next(float(r['impact_loss']) for r in rows if r['time']==t),pre_normal=min(float(r['normal_before']) for r in rows if r['time']==t)) for t in times]
        x,y=atoms(left[3]),atoms(right[3]);errors['event_count']=dict(status='PASS' if len(x)==len(y) else 'FAIL',coarse=len(x),fine=len(y))
        if x and len(x)==len(y):
            for key in ('time','impulse','impact_loss','pre_normal'):errors['event_'+key]=metric(np.array([r[key] for r in x]),np.array([r[key] for r in y]))
        pairs[left[0]+'__'+right[0]]=dict(status='PASS' if all(v['status']=='PASS' for v in errors.values()) else 'FAIL',errors=errors)
    status='PASS' if all(p['status']=='PASS' for p in pairs.values()) else 'FAIL'
    evidence={c[0]:dict(identity=c[1],compared_state_file=c[1].get('comparison_state_file',c[1].get('state_file','coupled.states.csv')),state_sha256=sha(ROOT/'results'/('autonomous_film_'+c[0])/c[1].get('comparison_state_file',c[1].get('state_file','coupled.states.csv')))) for c in cases}
    write_json(out/'summary.json',dict(status=status,scope='limited interval coupled all-pair time gate;NOT full contact cycle/energy/grasp',relative_gate=.001,pairs=pairs,cases=evidence,not_qualified=['full cycle','history/mesh','tendon-work/damping energy balance','friction','3finger grasp']))
    print(json.dumps(dict(status=status,pairs={k:{name:v.get('relative_error',v['status']) for name,v in record['errors'].items()} for k,record in pairs.items()})))
if __name__=='__main__':main()
