"""Actual latest contact/cable/layer/free-object unload-reload on patched SDK."""
import json,copy,xml.etree.ElementTree as ET
from closure_common import ROOT,OUT,BUILD,write_json,sha,identity
from run_trial import execute_process
def main():
    out=OUT/'sdk_memory';out.mkdir(parents=True,exist_ok=False);source=OUT/'trials/wrenches_Fxplus';sdk=ROOT/'build/grasp_20261115/sofa_patched';plugin=BUILD/'matched/libReGripClosure.so';scenes=[]
    for repeat in (1,2):
        directory=out/str(repeat);directory.mkdir();tree=ET.parse(source/'scene.scn');body=tree.getroot().find('Node')
        for child in list(body):
            if child.tag=='IntegratedRecorder':body.remove(child)
            elif child.tag=='ActiveIntervalContact':child.set('filename',str(directory/'contact.csv'));child.set('stride','60000')
        path=directory/'scene.scn';tree.write(path,encoding='utf-8',xml_declaration=True);scenes.append(path)
    binary=BUILD/'diagnostics_v2/closure_memory';command=[str(binary),str(sdk),*map(str,scenes),str(plugin)];write_json(out/'command.json',command);process=execute_process(command,out,480);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();measurements=[json.loads(s[4:]) for s in log.splitlines() if s.startswith('MEM ')];boundaries=[json.loads(s[9:]) for s in log.splitlines() if s.startswith('BOUNDARY ')];positive=[r for r in measurements if r['step']>=0];growth=[positive[i+2]['live_heap']-positive[i+1]['live_heap'] for i in (0,3)] if len(positive)==6 else []
    result=dict(status='PASS' if process['exit_code']==0 and '[ERROR]' not in log and len(growth)==2 and max(growth)<1024**2 and max(r['fds'] for r in boundaries)==min(r['fds'] for r in boundaries) else 'FAIL',process=process,measurements=measurements,boundaries=boundaries,live_growth_last60000=growth,plugin_sha256=sha(plugin),binary_sha256=sha(binary),scope='2x120000 latest structural/cable/pressure/adaptive-contact/free-body steps; full hold only first24s, later released; NOT hours or native triangle pipeline')
    result['artifacts']={str(p.relative_to(out)):sha(p) for p in out.rglob('*') if p.is_file()};write_json(out/'result.json',result);print(result['status'],growth)
if __name__=='__main__':main()
