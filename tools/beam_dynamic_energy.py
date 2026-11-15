"""Derived implicit-Euler energy terms, not a fitted numerical dissipation."""
import json,xml.etree.ElementTree as ET
from beam_common import ROOT,OUT,BUILD,PREFIX,SDK,FRAME,PLUGIN,sha,write_json
from closure_validation_suite import logged
from run_trial import execute_process
def main():
    out=OUT/'dynamic_energy';out.mkdir(exist_ok=False);build=BUILD/'energy_diagnostics'
    for name,cmd in [('configure',['cmake','-S','diagnostics/conservative_beam','-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX)]),('build',['cmake','--build',str(build),'--target','beam_dynamic_energy','-j2'])]:
        r=logged(cmd,out/name,180)
        if r['exit_code']:write_json(out/'summary.json',dict(status='BLOCKED',build_result=r));return
    results={}
    for dt in (.001,.0005,.00025):
        d=out/str(dt).replace('.','p');d.mkdir();tree=ET.parse(OUT/'single/force11/scene.scn');tree.getroot().set('dt',str(dt));body=tree.getroot().find('Node');body.remove(body.find('IntegratedRecorder'));tree.write(d/'scene.scn',encoding='utf-8',xml_declaration=True);cmd=[str(build/'beam_dynamic_energy'),str(SDK),str(d/'scene.scn'),str(FRAME),str(PLUGIN),str(round(3/dt)),str(d/'energy.csv')];write_json(d/'command.json',cmd);p=execute_process(cmd,d,240);log=(d/'stdout.log').read_text()+(d/'stderr.log').read_text();rows=[json.loads(s[15:]) for s in log.splitlines() if s.startswith('DYNAMIC_ENERGY ')];result=dict(status='PASS' if p['exit_code']==0 and '[ERROR]' not in log and rows and abs(rows[0]['normalized_residual'])<1e-4 else 'FAIL',process=p,energy=rows,scope='isotropic mass, conservative rod, constant external wrench,alpha2/beta.1; D_implicit derived linear formula, nonlinear leftover separately reported, not fitted as dissipation');results[str(dt)]=result;write_json(d/'result.json',result);write_json(out/'summary.json',results);print(dt,result['status'],rows,flush=True)
if __name__=='__main__':main()
