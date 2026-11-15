import shutil
from research_common import ROOT,OUT,BUILD,PREFIX,PLUGIN,sources,sha,write_json,inherited_identity
from closure_validation_suite import logged
def main():
    OUT.mkdir(parents=True,exist_ok=True);out=OUT/('build_'+BUILD.name);out.mkdir(exist_ok=False);before=sources();parent=inherited_identity()
    write_json(out/'before.json',dict(sources=before,inherited=parent))
    for name in before:
        target=out/'source_snapshot'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,target)
    commands=[('configure',['cmake','-S','models/material_point_contact','-B',BUILD,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX)]),('build',['cmake','--build',BUILD,'--target','ReGripMaterialPointContact','test_material_point','-j2']),('unit',[BUILD/'test_material_point']),('ldd',['ldd',PLUGIN])]
    for name,cmd in commands:
        result=logged(cmd,out/name,180)
        if result['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,result=result));print(name,'FAIL');return
    if before!=sources():raise RuntimeError('source changed during build')
    manifest=dict(sources=before,binary=sha(PLUGIN),generated=sha(BUILD/'MaterialPointGenerated.inc'),inherited_build=parent['birth_build']);write_json(BUILD/'build_manifest.json',manifest);write_json(out/'summary.json',dict(status='PASS',**manifest));print('clean build/API/point commit PASS')
if __name__=='__main__':main()
