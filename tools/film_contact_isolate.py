"""Read-only contact event diagnosis from completed actual SOFA coordinates.

Chord roots are estimates bracketed by saved states, not CCD certificates.
No time shifts, absolute floors or changed gates enter qualification.
"""
import argparse,csv,json,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_nonlinear_assess import read,compare

def clipped(g,area,kn=1e-5):
    polygon=[(np.array([0.,0.]),g[0]),(np.array([1.,0.]),g[1]),(np.array([0.,1.]),g[2])]
    vertices=[]
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if a[1]>0:vertices.append(a)
        if (a[1]>0)!=(b[1]>0):
            alpha=a[1]/(a[1]-b[1]);vertices.append((a[0]+alpha*(b[0]-a[0]),0.))
    total=force=0.
    for i in range(1,len(vertices)-1):
        a,b,c=vertices[0],vertices[i],vertices[i+1]
        u,v=b[0]-a[0],c[0]-a[0];weight=area*(u[0]*v[1]-u[1]*v[0])
        total+=weight;force+=kn*weight*(a[1]+b[1]+c[1])/3
    return total,force

def inspect(case,plane=.1):
    records=list(csv.DictReader((case/'journal.csv').open()))
    t=np.array([0.]+[float(r['time']) for r in records])
    x=np.array([np.fromstring(r['x'],sep=' ').reshape(-1,3) for r in records])
    rest=x[0].copy();rest[:,2]=0;x=np.concatenate([rest[None],x]);gap=x[:,:,2]-plane
    events=[];deaths=[];windows=[];opened=0. if np.any(gap[0]>0) else None
    for step in range(1,len(t)):
        for node in np.flatnonzero((gap[step-1]<=0)&(gap[step]>0)):
            alpha=-gap[step-1,node]/(gap[step,node]-gap[step-1,node])
            events.append(dict(node=int(node),bracket=[float(t[step-1]),float(t[step])],chord_time=float(t[step-1]+alpha*(t[step]-t[step-1]))))
        step_deaths=[]
        for node in np.flatnonzero((gap[step-1]>0)&(gap[step]<=0)):
            alpha=-gap[step-1,node]/(gap[step,node]-gap[step-1,node])
            event=dict(node=int(node),bracket=[float(t[step-1]),float(t[step])],chord_time=float(t[step-1]+alpha*(t[step]-t[step-1])))
            deaths.append(event);step_deaths.append(event)
        if not np.any(gap[step-1]>0) and np.any(gap[step]>0):
            opened=min(e['chord_time'] for e in events if e['bracket'][1]==t[step])
        if np.any(gap[step-1]>0) and not np.any(gap[step]>0):
            windows.append(dict(entry_chord_time=opened,exit_chord_time=max(e['chord_time'] for e in step_deaths)));opened=None
    if opened is not None:windows.append(dict(entry_chord_time=opened,exit_chord_time=None))
    nx=x.shape[1]//5;triangle_area=100*24/(2*(nx-1)*4)
    errors=[]
    for step,r in enumerate(records,1):
        area=force=0.
        for i in range(nx-1):
            for j in range(4):
                for nodes in ((5*i+j,5*(i+1)+j,5*i+j+1),(5*(i+1)+j+1,5*i+j+1,5*(i+1)+j)):
                    a,f=clipped(gap[step,list(nodes)],triangle_area);area+=a;force+=f
        errors.append([abs(area-float(r['contact_area'])),abs(force-float(r['normal_force']))])
    first=min(events,key=lambda e:e['chord_time']) if events else None
    # Gershgorin row-sum bound of the fully active CONTACT-ONLY triangle
    # tangent with uniform nodal mass. Not the coupled structural spectrum.
    tributary=np.zeros(x.shape[1])
    for i in range(nx-1):
        for j in range(4):
            for nodes in ((5*i+j,5*(i+1)+j,5*i+j+1),(5*(i+1)+j+1,5*i+j+1,5*(i+1)+j)):
                tributary[list(nodes)]+=triangle_area/3
    omega=float(np.sqrt(1e-5*max(tributary)/(1e-6/x.shape[1])))
    return dict(first_entry=first,first_exit=min(deaths,key=lambda e:e['chord_time']) if deaths else None,
                activation_crossings=len(events),deactivation_crossings=len(deaths),global_contact_windows=windows,active_nodes_end=int(sum(gap[-1]>0)),
                reference_area_reconstruction_max_abs=float(np.max(errors,axis=0)[0]),
                normal_force_reconstruction_max_abs=float(np.max(errors,axis=0)[1]),
                contact_only_omega_upper_bound=omega,omega_dt_upper_bound=omega*(t[1]-t[0]),
                entry_method='linear chord between stored states; interior birth/death not resolved')

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--control',type=str);p.add_argument('--fine-campaign',type=str);a=p.parse_args()
    if not a.tag.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    base=ROOT/'results/autonomous_film_20261116_hard_transient25'
    summary=json.loads((base/'summary.json').read_text());inputs={}
    cases={}
    for i in (1,2,4):
        path=base/str(i)/'journal.csv';inputs[str(path.relative_to(ROOT))]=sha(path)
        if len(read(path.parent)['time'])!=summary['rows'][str(i)]['steps']:raise RuntimeError('incomplete baseline')
        cases[i]=inspect(path.parent)
    controls={}
    if a.control:
        control=ROOT/'results'/('autonomous_film_'+a.control)
        cs=json.loads((control/'summary.json').read_text())
        if cs['process_status']!='PASS':raise RuntimeError('control incomplete')
        for i in (1,2,4):
            path=control/str(i)/'journal.csv';inputs[str(path.relative_to(ROOT))]=sha(path)
            controls[i]=inspect(path.parent,plane=100.)
        controls['full_time_status']=cs['time_status']
        controls['precontact_pairs']={}
        for i,j in ((1,2),(1,4),(2,4)):
            ds={k:read(control/str(k)) for k in (i,j)}
            selected={k:{key:v[d['time']<=1.3+1e-12] for key,v in d.items()} for k,d in ds.items()}
            controls['precontact_pairs'][f'{i}:{j}']=compare(selected[i],selected[j],.001)
    fine={}
    if a.fine_campaign:
        path=ROOT/'results'/('autonomous_film_'+a.fine_campaign)
        summary_fine=json.loads((path/'summary.json').read_text())
        if summary_fine['process_status']!='PASS':raise RuntimeError('fine campaign incomplete')
        if len(read(path/'1')['time'])!=summary_fine['expected_rows']:raise RuntimeError('partial fine rows')
        inputs[str((path/'1/journal.csv').relative_to(ROOT))]=sha(path/'1/journal.csv');fine=inspect(path/'1')
    report=dict(source='actual SOFA; independent clipped-triangle observer reconstruction',commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                script_sha256=sha(__file__),inputs=inputs,baseline=cases,control=controls,
                fine=fine,existing_full_time_gate=summary['time_status'],qualification='No new global qualification; chord event estimates and spectral bounds are diagnostics only')
    write_json(out/'summary.json',report);print(json.dumps(report,indent=2))

if __name__=='__main__':main()
