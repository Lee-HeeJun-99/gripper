"""Rerun original full3finger history, original diagnostics binary frozen."""
import json,xml.etree.ElementTree as ET
from beam_common import ROOT,OUT,SDK,FRAME,sha,write_json
from run_trial import execute_process
def main():
    out=OUT/'inherited_live';out.mkdir(exist_ok=False);source=ROOT/'results/closure_20261115/threefinger/trials/wrenches_Tzplus/scene.scn';tree=ET.parse(source);body=tree.getroot().find('Node')
    for e in list(body):
        if e.tag=='IntegratedRecorder':body.remove(e);continue
        if 'filename' in e.attrib:e.set('filename',str(out/e.get('filename').rsplit('/',1)[-1]))
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True);binary=ROOT/'build/closure_20261115/field_balance/closure_balance';command=[str(binary),str(SDK),str(out/'scene.scn'),str(FRAME)];write_json(out/'command.json',command);p=execute_process(command,out,480);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();fields=[json.loads(s[13:]) for s in log.splitlines() if s.startswith('FIELD_WRENCH ')];write_json(out/'summary.json',dict(process=p,fields=fields,status='PASS' if p['exit_code']==0 and '[ERROR]' not in log and fields else 'FAIL',source_template_sha256=sha(source),driver_sha256=sha(binary),plugin_sha256=sha(FRAME),scope='new actual27960step replay of original fullBeam+layer+cable+contact+Tz, independent raw, not old numerical result reuse'));print(fields)
if __name__=='__main__':main()
