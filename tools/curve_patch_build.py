"""Freeze a separate immutable element-refined component;never overwrite v1."""
import json
import shutil
from curve_common import ROOT, OUT, BUILD, PREFIX, identity, sha, write_json
from closure_validation_suite import logged

PATCH_BUILD=ROOT/'build/autonomous_20261116_patch_refinement_a01/v1'
PATCH_PLUGIN=PATCH_BUILD/'libReGripPatchRefinedContact.so'


def main():
    out=OUT/'patch_refinement/build_v1';out.mkdir(parents=True,exist_ok=False)
    if PATCH_BUILD.exists():raise ValueError('immutable patch build exists')
    runtime=identity();paths=list((ROOT/'models/patch_refined_contact').glob('*'))+[BUILD/'CurvedGenerated.inc']
    hashes={str(p.relative_to(ROOT)):sha(p)for p in paths if p.is_file()}
    write_json(out/'sources.json',hashes)
    for p in paths:
        if p.is_file():
            target=out/'sources'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    for name,command in [('configure',['cmake','-S','models/patch_refined_contact','-B',PATCH_BUILD,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX),'-DFROZEN_CURVE_BUILD='+str(BUILD)]),('build',['cmake','--build',PATCH_BUILD,'-j1']),('ldd',['ldd',PATCH_PLUGIN])]:
        process=logged(command,out/name,180)
        if process['exit_code']:
            write_json(out/'summary.json',dict(status='FAIL',stage=name,process=process));return
    manifest=dict(sources=hashes,binary=sha(PATCH_PLUGIN),generated=sha(PATCH_BUILD/'PatchGenerated.inc'),parent=runtime,scope='immutable per-element grid resolution only;force/return law unchanged;NOT dynamics qualification')
    write_json(PATCH_BUILD/'manifest.json',manifest);write_json(out/'summary.json',dict(status='PASS',manifest=manifest));print('independent patch build PASS')


if __name__=='__main__':main()
