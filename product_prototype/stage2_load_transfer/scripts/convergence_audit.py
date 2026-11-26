"""Read immutable FE results, recompute comparisons; never promote capacity."""
import argparse,json
from pathlib import Path
from load_requirements import ROOT,sha
def get(tag):
    p=ROOT/'validation/shaft'/tag/'summary.json';return json.loads(p.read_text()),sha(p)
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/convergence'/a.tag;out.mkdir(parents=True,exist_ok=False)
    direct,dsha=get('shaft08amg');block,bsha=get('shaft08block');fine,fsha=get('shaft06block')
    c0,c0sha=get('cylinder05p2');c1,c1sha=get('cylinder035amg')
    method_error=abs(block['twist_rad']/direct['twist_rad']-1)
    refinement=abs(block['twist_rad']/fine['twist_rad']-1)
    reference_refine=abs(c0['twist_rad']/c1['twist_rad']-1)
    checks=dict(same_weak_form_compliance=method_error<1e-8,shaft_compliance_refinement=refinement<.01,
        cylinder_reference=c1['reference_relative_error']<.01,cylinder_refinement=reference_refine<.01,
        all_hashes_current=all(sha(ROOT/'validation/shaft'/tag/'field.npz')==x['field_SHA256'] for tag,x in [('shaft08amg',direct),('shaft08block',block),('shaft06block',fine),('cylinder05p2',c0),('cylinder035amg',c1)]))
    result=dict(status='PASS' if all(checks.values()) else 'FAIL',scope='STATIC LOCAL COUPON COMPLIANCE ONLY, NOT SHAFT CAPACITY OR SYSTEM CONVERGENCE',
        checks=checks,assembly_method_relative_error=method_error,shaft_compliance_refinement_relative=refinement,
        cylinder_refinement_relative=reference_refine,cylinder_reference_relative=c1['reference_relative_error'],
        shaft_torsional_compliance_rad_Nm=fine['twist_rad']/fine['input_torque_Nm'],
        stress_warning='Different quadrature sample positions change reported peaks. No stress singularity/contact/fatigue approval from this compliance test.',
        source_SHA256=sha(Path(__file__)),input_SHA256=dict(shaft08amg=dsha,shaft08block=bsha,shaft06block=fsha,cylinder05p2=c0sha,cylinder035amg=c1sha),
        command='python scripts/convergence_audit.py --tag '+a.tag)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
