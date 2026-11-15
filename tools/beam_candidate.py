"""Independent fresh SOFA validation of linear structural Pareto candidate only."""
import json
from beam_common import OUT,write_json,sha
from beam_multilayer import run
from integrated_trial import Config
def main():
    summary=json.loads((OUT/'structural_optuna/summary.json').read_text())
    if summary['status']!='PASS' or summary['complete']<24:raise ValueError('study incomplete')
    candidate=summary['pareto'][0];k=candidate['params']['k'];ids=tuple(candidate['connector_indices']);cases=[('candidate_free',Config(k=0,duration=12.)),('candidate_on',Config(k=k,connectors=ids,duration=12.)),('candidate_repeat',Config(k=k,connectors=ids,duration=12.)),('candidate_halfdt',Config(k=k,connectors=ids,duration=12.,dt=.00025)),('candidate_n21',Config(k=k,connectors=tuple(2*i for i in ids),duration=12.,nodes=21))];results={}
    write_json(OUT/'candidate_plan.json',dict(candidate=candidate,cases=[dict(name=n,config=vars(c)) for n,c in cases],scope='same physical loads/materials/100mm/two layers; positions exactly preserved on refined mesh; NOT grasp optimization',workers=1))
    for name,c in cases:results[name]=run(name,c)
    passed=all(r.get('status')=='PASS' and r.get('equilibrium_validated') for r in results.values());checks={};ratio=None
    if passed:
        on=results['candidate_on'];ratio=results['candidate_free']['tip_deflection_mm']/on['tip_deflection_mm'];checks['linear_stiffness_agreement']=abs(ratio/candidate['values'][0]-1)<.005;checks['linear_equilibrium_slip_agreement']=abs(on['max_interface_slip_mm']/candidate['values'][1]-1)<.005
        for name,tol in [('candidate_repeat',1e-6),('candidate_halfdt',.001),('candidate_n21',.01)]:checks[name]=all(abs(results[name][key]/on[key]-1)<tol for key in ('tip_deflection_mm','max_interface_slip_mm'))
    r=dict(status='PASS' if passed and all(checks.values()) else 'FAIL',actual_sofa_stiffness_ratio=ratio,checks=checks,source_study_sha256=sha(OUT/'structural_optuna/study.sqlite3'),metrics={n:{k:v for k,v in r.items() if k in ('status','tip_deflection_mm','max_interface_slip_mm','relative_residual','equilibrium_validated')} for n,r in results.items()},scope='one selected independent100mm linear-structure candidate; no object/contact/wire/vacuum/force-closure or fabricated optimum');write_json(OUT/'candidate_result.json',r);print(r)
if __name__=='__main__':main()
