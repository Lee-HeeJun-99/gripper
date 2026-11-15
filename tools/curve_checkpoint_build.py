import shutil,json
from curve_common import ROOT,OUT,BUILD,FRAME,PREFIX,identity,sha,write_json
from closure_validation_suite import logged
CPBUILD=ROOT/'build/autonomous_20261116_checkpoint_a01/v4'
def main():
    ident=identity();out=ROOT/'results/autonomous_20261116_checkpoint_a01/build_v4';out.mkdir(parents=True,exist_ok=False);source=ROOT/'diagnostics/physics_checkpoint'
    for p in source.iterdir():
        if p.is_file():shutil.copy2(p,out/p.name)
    commands=[('configure',['cmake','-S',source,'-B',CPBUILD,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX),'-DFROZEN_CURVE_BUILD='+str(BUILD),'-DFROZEN_FRAME_BUILD='+str(FRAME.parent)]),('build',['cmake','--build',CPBUILD,'-j2']),('symbols_curve',['nm','-D','--defined-only','--demangle',CPBUILD/'libCurveCheckpointBridge.so']),('symbols_frame',['nm','-D','--defined-only','--demangle',CPBUILD/'libFrameCheckpointBridge.so']),('ldd',['ldd',CPBUILD/'physics_checkpoint'])]
    for name,command in commands:
        result=logged(command,out/name,180)
        if result['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,result=result));raise RuntimeError(name)
    for name in('symbols_curve','symbols_frame'):
        text=(out/name/'stdout.log').read_text()
        if any(token in text for token in('regrip_integrated::','CurvedMaterialContact','FrameLayerNetwork')):raise RuntimeError('project class symbol interposition would be unsafe')
    manifest=dict(identity=ident,sources={str(p.relative_to(ROOT)):sha(p)for p in source.iterdir()if p.is_file()},binaries={p.name:sha(p)for p in CPBUILD.iterdir()if p.suffix=='.so'or p.name=='physics_checkpoint'},generated={p.name:sha(p)for p in CPBUILD.glob('*ClassOnly.inc')},scope='hidden read/write bridges to frozen public PROJECT state;no engine private access or force-law changes;NOT yet validated restart')
    write_json(CPBUILD/'build_manifest.json',manifest);write_json(out/'summary.json',dict(status='PASS',**manifest));print('checkpoint driver build and symbol isolation PASS')
if __name__=='__main__':main()
