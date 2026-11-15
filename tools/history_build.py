from history_common import ROOT,OUT,BUILD,PREFIX,PLUGIN,sources,write_json,sha
from closure_validation_suite import logged
def main():
    out=OUT/('build_'+BUILD.name);out.mkdir(parents=True,exist_ok=False)
    for name,cmd in [('configure',['cmake','-S','models/contact_history','-B',str(BUILD),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX)]),('build',['cmake','--build',str(BUILD),'-j2']),('unit',[str(BUILD/'test_contact_history')]),('ldd',['ldd',str(PLUGIN)])]:
        r=logged(cmd,out/name,180)
        if r['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,result=r));return
    write_json(BUILD/'build_manifest.json',dict(source_sha256=sources(),binary_sha256=sha(PLUGIN)));write_json(out/'summary.json',dict(status='PASS',source_sha256=sources(),binary_sha256=sha(PLUGIN)));print('build and units PASS')
if __name__=='__main__':main()
