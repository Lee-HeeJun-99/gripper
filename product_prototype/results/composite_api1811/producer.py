"""Installed public composite-acceleration route audit, no SDK writes/replay."""
import argparse,json,re,subprocess
from pathlib import Path
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);sdk=Path('/home/ubuntu/SOFA/v26.06.00')
    paths=[sdk/'include/Sofa.Core/sofa/core/Mapping.h',sdk/'include/Sofa.Core/sofa/core/Multi2Mapping.h',
        sdk/'include/Sofa.Component.Mapping.NonLinear/sofa/component/mapping/nonlinear/RigidMapping.h',
        sdk/'include/Sofa.Component.Mapping.NonLinear/sofa/component/mapping/nonlinear/RigidMapping.inl',
        sdk/'plugins/ArticulatedSystemPlugin/include/ArticulatedSystemPlugin/ArticulatedSystemMapping.h',
        sdk/'plugins/ArticulatedSystemPlugin/include/ArticulatedSystemPlugin/ArticulatedSystemMapping.inl',
        sdk/'include/Sofa.Component.Mass/sofa/component/mass/UniformMass.inl']
    records=[]
    for path in paths:
        text=path.read_text();lines=text.splitlines()
        relevant=[k for k,line in enumerate(lines) if any(s in line for s in ('computeAccFromMapping','compute_mapping_inertia','void UniformMass<DataTypes>::addForce'))]
        snippets=[]
        for k in relevant:snippets.append(dict(line=k+1,text='\n'.join(lines[max(0,k-2):min(len(lines),k+12)])))
        records.append(dict(path=str(path),sha256=sha(path),acceleration_callback_occurrences=text.count('computeAccFromMapping'),snippets=snippets))
    implementations=[r for r in records if Path(r['path']).name in ('RigidMapping.h','RigidMapping.inl','ArticulatedSystemMapping.h','ArticulatedSystemMapping.inl')]
    absent=all(r['acceleration_callback_occurrences']==0 for r in implementations)
    result=dict(status='BLOCKED_SUPPORTED_COMPOSITE_ACCELERATION_ROUTE' if absent else 'NEW_CALLBACK_REQUIRES_IMPLEMENTATION_REVIEW',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),records=records,
        source_sha256=sha(Path(__file__)),prior_native_evidence={case:sha(BASE/'results'/case/'summary.json') for case in ('open_parallel_convective1806','open_parallel_mapping_inertia1807','open_convective_reference1808')},
        native_run=False,scope='Public installed template source audit ONLY. Base Mapping/Multi2Mapping expose documented J*a+dJ*v callback with empty default body; selected derived header/inl do not override it. UniformMass addForce ignores x/v. Prior actual1806/07 confirms missing response for THIS graph. This does NOT claim all installed plugins/compiled code/configurations are unsupported. No field/flag/SDK/force/ODE modification or unchanged Native replay. P0 stays blocked until a concrete supported composite force path is identified; proceed independent mechanisms/performance analysis.')
    (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(dict(status=result['status'],selected_derived_callbacks_absent=absent,native_run=False),indent=2))

if __name__=='__main__':main()
