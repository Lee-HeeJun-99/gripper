"""Actual initialized mass matrix and BeamFEM energy API probe, not a full audit."""
import xml.etree.ElementTree as ET
from stabilization_common import OUT,SOFA,BUILD,write_json,sha
from trial_validation import read_states
from run_trial import execute_process

def main():
    out=OUT/'mass_energy_probe';out.mkdir(parents=True,exist_ok=False);source=OUT/'grasp/sphere_x_valid';tree=ET.parse(source/'scene.scn');body=tree.getroot().find('Node');obj=body.find('MechanicalObject');obj.set('rest_position',obj.get('position'))
    raw=read_states(source/'state.txt');hold=min(raw,key=lambda x:abs(x['time']-7));obj.set('position',' '.join(map(str,hold['X'])))
    body.find('IntegratedRecorder').set('filename',str(out/'state.txt'));body.find('ContactHistory').set('filename',str(out/'contact.csv'));tree.write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    command=[str(BUILD/'memory/mass_energy_probe'),str(SOFA),str(out/'scene.scn'),str(BUILD/'contact_v2/libReGripDistributed.so')]
    result=execute_process(command,out,20);write_json(out/'result.json',dict(command=command,source_scene_sha256=sha(source/'scene.scn'),source_state_sha256=sha(source/'state.txt'),**result));print(result)

if __name__=='__main__':main()
