import json,csv,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,OUT,BUILD,SDK,FRAME,BEAM,PLUGIN,PREFIX,identity,sha,write_json
from closure_validation_suite import logged
from run_trial import execute_process
from trial_validation import read_states
def main():
    ident=identity();out=OUT/'transaction_journal_v3';out.mkdir(exist_ok=False);build=ROOT/'build/autonomous_20261116_curve_a01/transaction_v3'
    for p in(ROOT/'diagnostics/transaction_energy').iterdir():
        if p.is_file():shutil.copy2(p,out/p.name)
    for name,command in [('configure',['cmake','-S','diagnostics/transaction_energy','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX)]),('build',['cmake','--build',build,'-j2'])]:
        result=logged(command,out/name,180)
        if result['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,process=result));return
    tree=ET.parse(OUT/'grasp/n11/scene.scn')
    for element in tree.getroot().iter():
        if'filename'in element.attrib:element.set('filename',str(out/element.get('filename').rsplit('/',1)[-1]))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True);command=list(map(str,[build/'transaction_journal',SDK,out/'scene.scn',2000,out/'energy.csv',FRAME,BEAM,PLUGIN]));write_json(out/'command.json',command);write_json(out/'identity.json',ident);result=execute_process(command,out,240);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();markers=[json.loads(s[len('TRANSACTIONS '):])for s in log.splitlines()if s.startswith('TRANSACTIONS ')];passed=not result['exit_code']and'[ERROR]'not in log and bool(markers)
    errors={};rows=[]
    if passed:
        with(out/'energy.csv').open()as f:rows=list(csv.DictReader(f))
        passed=markers[-1]['begins']==markers[-1]['pre_commits']==markers[-1]['post_commits']==2000 and len(rows)==6000
        original=[r for r in read_states(OUT/'grasp/profile_n11/state.txt')if r['time']<=1+1e-8];actual=read_states(out/'state.txt')
        if len(original)!=len(actual):passed=False
        else:
            for k in('X','V','R'):errors[k]=float(np.max(np.abs(np.array([r[k]for r in original])-np.array([r[k]for r in actual]))))
            passed=passed and all(v<1e-12 for v in errors.values())
    write_json(out/'summary.json',dict(status='PASS'if passed else'FAIL',process=result,transactions=markers,raw_rows=len(rows),instrumentation_state_difference=errors,global_energy='BLOCKED',unknown_terms=['pressure parameter work','per-step friction','stored-energy closure'],scope='actual root top-down pre-child-commit and driver post-all-commit journal;Rayleigh/projection terms and independent kinetic-step residual,not exact stored-energy closure',binary_sha256=sha(build/'transaction_journal')));print(passed,markers,errors)
if __name__=='__main__':main()
