from birth_common import ROOT,OUT,BUILD,PREFIX,PLUGIN,sources,write_json,sha
from closure_validation_suite import logged
def main():
    out=OUT/('build_'+BUILD.name);out.mkdir(parents=True,exist_ok=False);before=sources()
    for name,cmd in [('configure',['cmake','-S','models/contact_birth','-B',str(BUILD),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX)]),('build',['cmake','--build',str(BUILD),'--target','ReGripBirthContact','test_birth','-j2']),('unit',[BUILD/'test_birth']),('ldd',['ldd',PLUGIN])]:
        r=logged(cmd,out/name,180)
        if r['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,result=r));return
    if before!=sources():raise ValueError('source changed while building')
    m=dict(source_sha256=before,binary_sha256=sha(PLUGIN),generated_sha256=sha(BUILD/'BirthGenerated.inc'));write_json(BUILD/'build_manifest.json',m);write_json(out/'summary.json',dict(status='PASS',**m));print('birth build and units PASS')
if __name__=='__main__':main()
