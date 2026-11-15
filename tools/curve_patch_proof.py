"""Reversible source proof:force/Jacobian/return/Commit bodies unchanged."""
import ast
import json
from curve_common import ROOT,OUT,BUILD,sha,write_json
from curve_patch_build import PATCH_BUILD


def reverse(generated, generator):
    calls=[]
    for node in ast.parse(generator).body:
        if isinstance(node,ast.Expr)and isinstance(node.value,ast.Call)and isinstance(node.value.func,ast.Name)and node.value.func.id=='once':
            calls.append(tuple(ast.literal_eval(arg)for arg in node.value.args))
    if len(calls)!=5:raise ValueError('expected five declared nonconstitutive transformations')
    result=generated.replace('ReGripPatchRefinedContact','ReGripCurvedContact').replace('PatchRefinedContact','CurvedMaterialContact')
    for old,new in reversed(calls):
        if result.count(new)!=1:raise ValueError('compiled source differs from declared transform')
        result=result.replace(new,old)
    return result


def main():
    target=OUT/'patch_refinement/source_proof_v1.json'
    if target.exists():raise ValueError('immutable proof exists')
    generator=ROOT/'models/patch_refined_contact/generate.py';actual=PATCH_BUILD/'PatchGenerated.inc';parent=BUILD/'CurvedGenerated.inc';restored=reverse(actual.read_text(),generator.read_text())
    passed=restored==parent.read_text()
    write_json(target,dict(status='PASS'if passed else'FAIL',generator_sha256=sha(generator),compiled_generated_sha256=sha(actual),parent_generated_sha256=sha(parent),full_source_restored_exactly=passed,scope='five declared grid-interface/init/signature/count transformations only;source proof is NOT an energy or dynamics certification'))
    if not passed:raise ValueError('constitutive source unexpectedly changed')
    print('complete constitutive source restoration EXACT')


if __name__=='__main__':main()
