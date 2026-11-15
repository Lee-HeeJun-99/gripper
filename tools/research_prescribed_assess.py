import json
from research_common import ROOT,OUT,write_json
def main():
    folder=OUT/'prescribed_clean'
    if not(folder/'summary.json').exists():folder=OUT/'prescribed'
    records=json.loads((folder/'summary.json').read_text());result={};comparisons={}
    for model in('old','new'):
        zero=records[model+'_200_0.005']['metrics'];rotated=records[model+'_objective']['metrics'];err=abs(zero['query_return_D']-rotated['query_return_D'])/abs(zero['query_return_D'])
        result[model]=dict(objectivity_status='PASS'if err<1e-12 else'FAIL',objectivity_relative_error=err,maximum_absolute_commit_energy_jump=max(r['metrics']['absolute_commit_energy_jump']for n,r in records.items()if n.startswith(model)),minimum_return_loss=min(r['metrics']['query_return_D']for n,r in records.items()if n.startswith(model)))
        for steps in(200,400):
            hs=(.01,.005,.0025,.00125)
            for a,b in zip(hs,hs[1:]):
                x=records[f'{model}_{steps}_{a}']['metrics']['query_return_D'];y=records[f'{model}_{steps}_{b}']['metrics']['query_return_D'];error=abs(x-y)/abs(y);comparisons[f'{model}_{steps}_{a}_{b}']=dict(status='PASS'if error<=.01 else'FAIL',relative_difference=error,absolute_difference=abs(x-y),limit=.01)
    points=[r['metrics']for n,r in records.items()if n.startswith('new')];exact=max(abs(r['query_return_D']-r['actual_point_commit_D'])for r in points);jump=max(r['absolute_commit_energy_jump']for r in points)
    summary=dict(origin='independent prescribed geometry through SOFA ForceField API; NOT ODE or grasp',models=result,history_comparisons=comparisons,new_actual_query_commit_D_difference=exact,new_commit_energy_jump_bound=jump,new_consistency_status='PASS'if exact<1e-14 and jump<1e-14 else'FAIL',scope='observed representation-energy jump mechanism and frozen-path objectivity; not unique proof of every dynamic mesh error or global energy closure',source=str(folder.relative_to(ROOT)))
    write_json(OUT/'prescribed_assessment.json',summary);write_json(ROOT/'reports/autonomous_evidence/prescribed_assessment.json',summary);print(summary)
if __name__=='__main__':main()
