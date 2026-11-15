import json
import shutil
from curve_common import ROOT,OUT,BUILD,PREFIX,sha,write_json
from curve_patch_build import PATCH_BUILD,PATCH_PLUGIN
from closure_validation_suite import logged


def main():
    out=OUT/'patch_refinement/api_v1';out.mkdir(parents=True,exist_ok=False)
    m=json.loads((PATCH_BUILD/'manifest.json').read_text())
    if m['binary']!=sha(PATCH_PLUGIN)or m['generated']!=sha(PATCH_BUILD/'PatchGenerated.inc'):raise ValueError('frozen refined plugin differs')
    paths=list((ROOT/'diagnostics/patch_refined_contact').glob('*'))+[ROOT/'tests/test_curved_contact.cpp']
    write_json(out/'source_hashes.json',{str(p.relative_to(ROOT)):sha(p)for p in paths if p.is_file()})
    for p in paths:
        if p.is_file():
            target=out/'sources'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    build=ROOT/'build/autonomous_20261116_patch_refinement_api_a01/v1'
    for name,command in [('configure',['cmake','-S','diagnostics/patch_refined_contact','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX),'-DFROZEN_CURVE_BUILD='+str(BUILD),'-DPATCH_BUILD='+str(PATCH_BUILD)]),('build',['cmake','--build',build,'-j1']),('unit',[build/'patch_api'])]:
        process=logged(command,out/name,180)
        if process['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,process=process));return
    write_json(out/'summary.json',dict(status='PASS',binary=sha(build/'patch_api'),generated_test=sha(build/'TestPatch.cpp'),plugin_manifest=m,scope='actual SDK API tests with explicit refined element grid;not dynamics convergence'))
    print('refined actual API PASS')


if __name__=='__main__':main()
