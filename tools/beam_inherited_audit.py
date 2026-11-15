"""Independent actual inherited Beam addForce and missing-geometric-couple audit."""
import json,xml.etree.ElementTree as ET
from beam_common import ROOT,OUT,BUILD,PREFIX,SDK,FRAME,sha,write_json
from closure_validation_suite import logged
from integrated_trial import Config,scene
from run_trial import execute_process
def main():
    out=OUT/'inherited_audit';out.mkdir(parents=True,exist_ok=False);build=BUILD/'diagnostics';results={}
    for name,cmd in [('configure',['cmake','-S','diagnostics/conservative_beam','-B',str(build),'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(PREFIX)]),('build',['cmake','--build',str(build),'--target','inherited_audit','-j2'])]:
        results[name]=logged(cmd,out/name,180)
        if results[name]['exit_code']:write_json(out/'summary.json',results);return
    scene(out,Config());tree=ET.parse(out/'scene.scn');body=tree.getroot().find('Node')
    for e in list(body):
        if e.tag not in ('MechanicalObject','MeshTopology','UniformMass','BeamFEMForceField','FixedProjectiveConstraint'):body.remove(e)
    tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True);cmd=[str(build/'inherited_audit'),str(SDK),str(out/'scene.scn'),str(FRAME)];write_json(out/'command.json',cmd);p=execute_process(cmd,out,90);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();rows=[json.loads(s[10:]) for s in log.splitlines() if s.startswith('INHERITED ')];write_json(out/'summary.json',dict(process=p,rows=rows,execution_status='PASS' if p['exit_code']==0 and '[ERROR]' not in log and len(rows)==6 else 'FAIL',source_sha256=sha(ROOT/'diagnostics/conservative_beam/InheritedAudit.cpp'),binary_sha256=sha(build/'inherited_audit'),scope='prescribed two parallel cantilevers, actual Beam addForce; rigid-space virtual work convention confirmed by RigidCoord::operator+=; no dynamics or reset-history inference'))
    print(rows)
if __name__=='__main__':main()
