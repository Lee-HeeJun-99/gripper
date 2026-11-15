"""Record the actual compiler/runtime and resolved SDK links read-only."""
import subprocess,sys
from birth_common import ROOT,OUT,SDK,PLUGIN,write_json
from closure_validation_suite import logged
def main():
    out=OUT/'environment';out.mkdir(exist_ok=False)
    commands={'kernel':['uname','-sr'],'os':['lsb_release','-ds'],'compiler':['g++','--version'],'cmake':['cmake','--version'],'python':[sys.executable,'--version'],'ldd':['ldd',PLUGIN]}
    rows={name:logged(command,out/name,30)for name,command in commands.items()}
    links={str(p.relative_to(ROOT)):str(p.resolve())for p in(ROOT/'.runtime/closure_sdk/lib').glob('libSofa*.so.26.06.00')}
    write_json(out/'summary.json',dict(status='PASS' if all(r['exit_code']==0 for r in rows.values()) and all(str(SDK)in p for p in links.values())else'FAIL',commands=rows,resolved_sdk_links=links,scope='actual compiler/OS/dynamic links; no dependency reinstallation'))
if __name__=='__main__':main()
