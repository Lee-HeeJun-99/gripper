"""Strict completed-window trajectory, endpoint, phase and momentum assessment.
Existing trajectory gate and additional endpoint check are reported separately.
"""
import argparse,csv,json,re,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_nonlinear_assess import read,compare

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);a=p.parse_args()
    for tag in [a.tag]+a.cases:
        if not tag.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    datasets={};inputs={};schemes={};residuals={};binaries=[]
    for name in a.cases:
        base=ROOT/'results'/('autonomous_film_'+name);summary=json.loads((base/'summary.json').read_text());identity=json.loads((base/'identity.json').read_text())
        if summary['process_status']!='PASS' or summary['newton_failed_steps']:raise RuntimeError('failed case '+name)
        datasets[name]=read(base/'1')
        if len(datasets[name]['time'])!=summary['expected_rows'] or abs(datasets[name]['time'][-1]-2)>1e-12:raise RuntimeError('incomplete physical interval')
        if identity.get('contact_stiffness_override') is not None:raise RuntimeError('stiffness controls cannot qualify original model')
        binaries.append(identity['compiled']['binary_sha256'])
        text=(base/'1/scene.scn').read_text();match=re.search(r'<ReGripBDFSolver ([^>]+)',text)
        schemes[name]={key:re.search(key+r'="([^"]+)"',match[1])[1] for key in ('order','theta','variableStep')}
        rows=list(csv.DictReader((base/'1/profile.csv').open()));times=np.array([float(r['time']) for r in rows]);h=np.diff(np.r_[0.,times]);r=np.array([float(v['momentum_residual_norm']) for v in rows]);relative=r/(h*(1e-6*times/10)/np.sqrt(5))
        expected_h=np.where(times<=1.3+1e-12,identity['dt'],identity['dt']/4)
        if max(abs(h-expected_h))>1e-12:raise RuntimeError('runtime grid does not match identity')
        residuals[name]=dict(maximum_absolute=float(max(r)),maximum_relative=float(max(relative)),status='PASS' if max(relative)<=.001 else 'FAIL')
        for path in (base/'summary.json',base/'identity.json',base/'1/journal.csv',base/'1/profile.csv',base/'1/scene.scn'):inputs[str(path.relative_to(ROOT))]=sha(path)
    if len(set(binaries))!=1 or any(value!=next(iter(schemes.values())) for value in schemes.values()):raise RuntimeError('different binaries or algorithms cannot form one convergence family')
    comparisons={};endpoint={}
    for lo,hi in ((0,1),(1,1.3),(1.3,1.5),(1.5,2),(0,2)):
        selected={name:{key:v[(data['time']>=lo-1e-12)&(data['time']<=hi+1e-12)] for key,v in data.items()} for name,data in datasets.items()}
        comparisons[f'{lo}:{hi}']={f'{i}:{j}':compare(selected[i],selected[j],.001) for n,i in enumerate(a.cases) for j in a.cases[n+1:]}
    endpoint={pair:{key:dict(relative=v['final_relative'],absolute=v['final_absolute'],status='PASS' if (v['final_relative'] is not None and v['final_relative']<=.001) or (v['final_relative'] is None and v['final_absolute']==0) else 'FAIL') for key,v in metrics.items()} for pair,metrics in comparisons['0:2'].items()}
    trajectories=all(v['trajectory_status']=='PASS' for phase in comparisons.values() for pair in phase.values() for v in pair.values())
    endpoints=all(v['status']=='PASS' for pair in endpoint.values() for v in pair.values())
    result=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),inputs=inputs,tool_sha256=sha(__file__),actual_schemes=schemes,comparisons=comparisons,endpoint_checks=endpoint,momentum=residuals,
        existing_phase_trajectory_gate='PASS' if trajectories else 'FAIL',additional_endpoint_gate='PASS' if endpoints else 'FAIL',
        combined_coupon_time_scope='PASS' if trajectories and endpoints and all(v['status']=='PASS' for v in residuals.values()) else 'FAIL',
        limitation='Only21x5 frictionless rectangular fixed-plane coupon,0–2s ramp/contact/release/recontact. No pressure,wire,rails,freeobject,friction,globalenergy or full grasp approval;original coarse-grid FAIL retained.')
    write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('inputs','comparisons')},indent=2))

if __name__=='__main__':main()
