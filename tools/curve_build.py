import shutil
from curve_common import ROOT,OUT,BUILD,PREFIX,PLUGIN,sources,sha,write_json,parent_identity
from closure_validation_suite import logged
def main():
    OUT.mkdir(parents=True,exist_ok=True);out=OUT/('build_'+BUILD.name);out.mkdir(exist_ok=False);before=sources();parent=parent_identity();write_json(out/'before.json',dict(sources=before,inherited=parent))
    for name in before:
        target=out/'source_snapshot'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
    commands=[('configure',['cmake','-S','models/curved_contact','-B',BUILD,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX)]),('build',['cmake','--build',BUILD,'--target','ReGripCurvedContact','test_curved_contact','-j2']),('unit',[BUILD/'test_curved_contact']),('ldd',['ldd',PLUGIN])]
    for name,cmd in commands:
        result=logged(cmd,out/name,180)
        if result['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,result=result));raise RuntimeError(name+' FAIL')
    if before!=sources():raise RuntimeError('sources changed during compile')
    manifest=dict(sources=before,binary=sha(PLUGIN),generated=sha(BUILD/'CurvedGenerated.inc'),inherited_build=parent['material_point']);write_json(BUILD/'build_manifest.json',manifest);write_json(out/'summary.json',dict(status='PASS',**manifest));print('curved clean build and SOFA API PASS')
if __name__=='__main__':main()
