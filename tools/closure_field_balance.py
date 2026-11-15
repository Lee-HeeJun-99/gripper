"""Live field-by-field wrench accounting at13.98s; not restored history guessing."""
import json,xml.etree.ElementTree as ET
from closure_frame_common import ROOT,OUT,BUILD,PLUGIN,SDK,write_json,sha
from closure_validation_suite import logged
from run_trial import execute_process
def main():
    out=OUT/'field_balance';out.mkdir(exist_ok=False);build=BUILD/'field_balance';records={}
    for name,cmd in [('configure',['cmake','-S','diagnostics/closure','-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(ROOT/'.runtime/closure_sdk')]),('build',['cmake','--build',str(build),'--target','closure_balance','-j2'])]:
        records[name]=logged(cmd,out/name,180)
        if records[name]['exit_code']:write_json(out/'summary.json',records);return
    tree=ET.parse(OUT/'trials/wrenches_Tzplus/scene.scn');body=tree.getroot().find('Node')
    for element in list(body):
        if element.tag=='IntegratedRecorder':body.remove(element);continue
        if 'filename' in element.attrib:element.set('filename',str(out/element.get('filename').rsplit('/',1)[-1]))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True);cmd=[str(build/'closure_balance'),str(SDK),str(out/'scene.scn'),str(PLUGIN)];write_json(out/'command.json',cmd);p=execute_process(cmd,out,480);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();fields=[json.loads(s[13:]) for s in log.splitlines() if s.startswith('FIELD_WRENCH ')];write_json(out/'summary.json',dict(process=p,fields=fields,binary_sha256=sha(build/'closure_balance'),plugin_sha256=sha(PLUGIN),scope='same actual27960-step physical history; observer removed only for I/O; per-field resultant about current objectCOM',execution='PASS' if p['exit_code']==0 and '[ERROR]' not in log and fields else 'FAIL'));print(fields)
if __name__=='__main__':main()
