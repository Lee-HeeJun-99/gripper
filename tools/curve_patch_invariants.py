import json
import shutil
from curve_common import ROOT,OUT,BUILD,PREFIX,sha,write_json
from curve_patch_build import PATCH_BUILD
from closure_validation_suite import logged


def main():
    out=OUT/'patch_refinement_v2/invariants';out.mkdir(exist_ok=False)
    manifest=json.loads((PATCH_BUILD/'manifest.json').read_text())
    if manifest['generated']!=sha(PATCH_BUILD/'PatchGenerated.inc'):raise ValueError('frozen generated component mismatch')
    paths=list((ROOT/'diagnostics/patch_invariants').glob('*'))+[ROOT/'diagnostics/curved_contact/Invariants.cpp']
    write_json(out/'sources.json',{str(p.relative_to(ROOT)):sha(p)for p in paths if p.is_file()})
    for p in paths:
        if p.is_file():
            target=out/'sources'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    build=ROOT/'build/autonomous_20261116_patch_invariants_a01/v1'
    for name,cmd in [('configure',['cmake','-S','diagnostics/patch_invariants','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX),'-DPATCH_BUILD='+str(PATCH_BUILD),'-DFROZEN_CURVE_BUILD='+str(BUILD)]),('build',['cmake','--build',build,'-j1']),('unit',[build/'patch_invariants'])]:
        result=logged(cmd,out/name,180)
        if result['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,process=result));return
    write_json(out/'summary.json',dict(status='PASS',binary=sha(build/'patch_invariants'),generated_test=sha(build/'PatchInvariants.cpp'),scope='actual SDK90states with explicit element grid:objectivity,action-reaction,moment balance,Jacobian covariance and query/Commit;not whole-grasp certification'))
    print('explicit element-grid90state invariants PASS')


if __name__=='__main__':main()
