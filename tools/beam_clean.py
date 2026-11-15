"""Fresh isolated build with captured warnings, dependencies and unit output."""
from beam_common import ROOT,OUT,BUILD,PREFIX,PLUGIN,sha,write_json,identity
from closure_validation_suite import logged
def main():
    out=OUT/'clean';out.mkdir(exist_ok=False);build=BUILD/'clean_final';identity();summary={}
    for name,cmd in [('configure',['cmake','-S','models/conservative_beam','-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX)]),('build',['cmake','--build',str(build),'-j2']),('unit',[str(build/'test_conservative_beam')]),('equivalence',[str(build/'test_conservative_beam_equivalence')]),('ldd',['ldd',str(build/'libReGripConservativeBeam.so')])]:
        summary[name]=logged(cmd,out/name,180)
        if summary[name]['exit_code']:break
    summary['status']='PASS' if all(v['exit_code']==0 for v in summary.values()) else 'FAIL';summary['source_identity']=identity();summary['clean_binary_sha256']=sha(build/'libReGripConservativeBeam.so');summary['frozen_binary_sha256']=sha(PLUGIN);summary['scope']='fresh build, no overwrite of frozen physics binaries; same source not necessarily bit-identical linker build-id';write_json(out/'summary.json',summary);print(summary['status'])
if __name__=='__main__':main()
