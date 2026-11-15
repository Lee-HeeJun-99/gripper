"""Expose existing matched SDK headers/exports, never overwrite old binaries."""
import os,subprocess
from closure_common import ROOT,OUT,BUILD,write_json,sha
from run_trial import execute_process
def main():
    out=OUT/'sdk_setup';out.mkdir(parents=True,exist_ok=False);old=ROOT/'build/grasp_20261115/sofa_patched';prefix=ROOT/'.runtime/closure_sdk';prefix.mkdir(exist_ok=False)
    command=['cmake','--install',str(old),'--prefix',str(prefix),'--component','headers'];write_json(out/'command.json',command);p=execute_process(command,out,120)
    if p['exit_code']!=0:write_json(out/'result.json',dict(status='FAIL',process=p));return
    lib=prefix/'lib';lib.mkdir(exist_ok=True)
    # All symlinks refer to the SAME matched-source SDK, not ABI substitutes.
    for source in (old/'lib').glob('*.so*'):
        if source.is_file():(lib/source.name).symlink_to(source.resolve())
    build=BUILD/'matched';commands=[['cmake','-S',str(ROOT/'models/closure'),'-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(prefix)],['cmake','--build',str(build),'-j2'],[str(build/'test_closure')]];records=[]
    for i,command in enumerate(commands):
        directory=out/str(i);directory.mkdir();write_json(directory/'command.json',command);process=execute_process(command,directory,120);records.append(dict(command=command,process=process))
        if process['exit_code']!=0:break
    result=dict(status='PASS' if len(records)==3 and all(r['process']['exit_code']==0 for r in records) else 'FAIL',records=records,scope='headers/export install only; original SDK libraries remain byte-identical')
    if result['status']=='PASS':
        linked=subprocess.run(['ldd',str(build/'libReGripClosure.so')],capture_output=True,text=True,timeout=10);(out/'ldd.log').write_text(linked.stdout+linked.stderr);result['installed_sofa_linked']='/home/ubuntu/SOFA' in linked.stdout
        if result['installed_sofa_linked']:result['status']='FAIL'
        result['binary_sha256']=sha(build/'libReGripClosure.so')
    write_json(out/'result.json',result);print(result['status'])
if __name__=='__main__':main()
