"""Independent equilibrium/convergence checks; never changes physical thresholds."""
import json
from stabilization_common import OUT,write_json

def main():
    def metric(group,name):return json.loads((OUT/group/name/'metrics.json').read_text())
    cold={p.parent.name:json.loads(p.read_text()) for p in (OUT/'compensated_cold').glob('*/metrics.json')}
    follow={p.parent.name:json.loads(p.read_text()) for p in (OUT/'compensated_followup').glob('*/metrics.json')}
    base=cold['L8_base'];checks={}
    for name,r in {**cold,**{'follow_'+k:v for k,v in follow.items()}}.items():
        checks[name+'_equilibrium']=r['status']=='PASS' and r['relative_residual']<1e-3
    comparisons={}
    for name,r,tol in [('halfdt',cold['L8_halfdt'],.001),('mesh',cold['L8_mesh'],.01),('extended',cold['L8_extended'],.001),('repeat',follow.get('repeat'),1e-10),('quarterdt',follow.get('quarterdt'),.001)]:
        if r is None:continue
        a,b=base['tip_deflection_mm'],r['tip_deflection_mm'];comparisons[name]=dict(base=a,value=b,absolute_difference=abs(a-b),relative_tolerance=tol)
        checks[name+'_tip']=abs(a-b)<=1e-10+tol*abs(a)
    for layer in (2,4):
        name='L%d_regression'%layer
        # Same physical configuration, unmodified standard Euler audit regression.
        old=metric('regression','L%d'%layer) if (OUT/'regression'/('L%d'%layer)).exists() else None
        if old:
            a,b=old['tip_deflection_mm'],cold[name]['tip_deflection_mm'];comparisons[name]=dict(original=a,compensated=b,absolute_difference=abs(a-b))
            checks[name+'_tip']=abs(a-b)<1e-10+1e-6*abs(a)
    write_json(OUT/'compensated_checks.json',dict(checks=checks,comparisons=comparisons,all_pass=all(checks.values()),scope='cold-start structural Euler; no free objects; original force/velocity/rotation gates unchanged'))
    print(checks,comparisons)

if __name__=='__main__':main()
