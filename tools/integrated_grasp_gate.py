"""Do not confuse contact with a freely supported, perturbed object grasp."""
import json
from integrated_common import OUT,write_json,provenance

def main():
    data=json.loads((OUT/'contact/summary.json').read_text());decisions={}
    for name,r in data['records'].items():
        if r['config']['object_fixed']:
            decisions[name]=dict(status='NOT RUN',grasp_qualified=False,reason='object is fixed: contact-response benchmark only')
        else:
            displacement=r.get('object_displacement_mm')
            decisions[name]=dict(status='FAIL' if displacement is not None and displacement>1e-3 else 'NOT RUN',
                grasp_qualified=False,object_displacement_mm=displacement,declared_hold_benchmark_limit_mm=.001,
                reason='single unqualified planar normal-contact experiment; no verified multi-direction support/load envelope')
    write_json(OUT/'grasp_gate.json',dict(provenance=provenance(),decisions=decisions,grasp_model_qualified=False,
        integrated_grasp_optimization_status='BLOCKED',
        required_before_optimization=['free object, no artificial holding constraint','3 independent disturbance directions and multiple magnitudes',
            'sustained contact and force/moment balance','transient/release/repeat/mesh/dt validation','object friction or explicitly validated geometric enclosure',
            'validated rotation/material range'],
        exclusions='No fixed-object contact trial, static FEM enumeration or tiny-load stationary object is a grasp success.'))
    print(decisions)

if __name__=='__main__':main()
