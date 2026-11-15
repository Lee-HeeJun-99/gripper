import json
from curve_common import OUT,write_json
from history_assess import comparison
from birth_assess import same_physics,observables
def main():
    cases={};checks={}
    for p in(OUT/'grasp').glob('*/metrics.json'):
        r=json.loads(p.read_text())
        if not r['config']['profile_only']:cases[p.parent.name]=r
    for a,b in(('n11','n21'),('n21','n41')):
        name=a+'_'+b
        if a not in cases or b not in cases:checks[name]=dict(status='NOT RUN');continue
        x,y=cases[a],cases[b];same_physics(x,y)
        if x['identity']['curved']!=y['identity']['curved']:raise ValueError('compiled models differ')
        if not(x.get('bounded_hold_pass')and y.get('bounded_hold_pass')):checks[name]=dict(status='FAIL',reason='underlying physical gate',cases=[a,b]);continue
        r=comparison(x,y,.01);r['observables']={};oa,ob=observables(OUT/'grasp'/a),observables(OUT/'grasp'/b)
        for k in oa:
            rel=abs(oa[k]-ob[k])/abs(ob[k])if ob[k]else(0 if oa[k]==0 else None);r['observables'][k]=dict(absolute=abs(oa[k]-ob[k]),relative=rel)
        d=r['observables']['friction_dissipation']['relative'];r['loss_status']='PASS'if d is not None and d<=.01 else'FAIL';checks[name]=r
    result=dict(status='FAIL'if any(r['status']=='FAIL'or r.get('loss_status')=='FAIL'for r in checks.values())else'EXPERIMENTAL',comparisons=checks,cases={n:{k:r.get(k)for k in('status','bounded_hold_pass','hold_displacement_mm','hold_rotation_increment_rad','global_force_residual','global_moment_residual','process','failure_reason')}for n,r in cases.items()},scope='new director-Hermite component,normal/tangent fixed material midpoint quadrature;1percent unchanged;no global grasp or energy qualification',grasp_optimization='BLOCKED')
    write_json(OUT/'assessment.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
