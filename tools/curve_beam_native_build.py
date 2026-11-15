"""Recompile unchanged validated beam with strict-FP native ISA;old build immutable."""
import json,shutil
from curve_common import ROOT,PREFIX,sha,write_json
from closure_validation_suite import logged
def main():
    out=ROOT/'results/autonomous_20261116_full_native_a01/beam_build';out.mkdir(parents=True,exist_ok=False);build=ROOT/'build/autonomous_20261116_full_native_a01/beam';old=json.loads((ROOT/'build/beam_20261115/v2/build_manifest.json').read_text());sources=old['compiled_source_sha256'];deps=old.get('dependency_sha256',{})
    for name,digest in {**sources,**deps}.items():
        if sha(ROOT/name)!=digest:raise ValueError('validated beam dependency changed: '+name)
        target=out/'source_snapshot'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
    flags='-O3 -DNDEBUG -march=native -ffp-contract=off';commands=[('configure',['cmake','-S','models/conservative_beam','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX),'-DCMAKE_CXX_FLAGS_RELEASE='+flags]),('build',['cmake','--build',build,'-j2']),('kernel',[build/'test_conservative_beam']),('equivalence',[build/'test_conservative_beam_equivalence']),('ldd',['ldd',build/'libReGripConservativeBeam.so'])]
    for name,cmd in commands:
        result=logged(cmd,out/name,180)
        if result['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,process=result));raise RuntimeError(name)
    for name,digest in {**sources,**deps}.items():
        if sha(ROOT/name)!=digest:raise ValueError('source changed while compiling')
    manifest=dict(plugin_sha256=sha(build/'libReGripConservativeBeam.so'),compiled_source_sha256=sources,dependency_sha256=deps,flags=flags,dense_reference_sha256=sha(build/'BeamReferenceV1.inc'),scope='same source/model/API,strict FP native ISA,actual61state and100dense-reference tests;not yet full SOFA path equivalence')
    write_json(build/'build_manifest.json',manifest);write_json(out/'summary.json',dict(status='PASS',**manifest));print('strict-FP native Beam API and dense reference PASS')
if __name__=='__main__':main()
