"""Actual SOFA one-step controlled event checks; not a gripper certificate."""
import json,csv,xml.etree.ElementTree as ET
from birth_common import ROOT,OUT,SDK,FRAME,BEAM,PLUGIN,identity,write_json,sha
from native_scene import PLUGINS
from run_trial import execute_process
def case(name,y,vy,vz,steps=1,expect_error=False,expected_extension=None):
    out=OUT/'events'/name;out.mkdir(parents=True,exist_ok=False);ident=identity();root=ET.Element('Node',name='BirthEventResearch',dt='1',gravity='0 0 0')
    for i,p in enumerate(PLUGINS):ET.SubElement(root,'RequiredPlugin',name='p'+str(i),pluginName='Sofa.Component.'+p)
    ET.SubElement(root,'DefaultAnimationLoop');ET.SubElement(root,'EulerImplicitSolver',rayleighMass='0',rayleighStiffness='0');ET.SubElement(root,'EigenSparseLU',template='CompressedRowSparseMatrixMat3x3d');body=ET.SubElement(root,'Node',name='Event')
    ET.SubElement(body,'MechanicalObject',name='dofs',template='Rigid3d',position=f'-.5 {y} 0 0 0 0 1 .5 {y} 0 0 0 0 1 0 0 0 0 0 0 1',velocity=f'0 {vy} {vz} 0 0 0 0 {vy} {vz} 0 0 0 0 0 0 0 0 0');ET.SubElement(body,'UniformMass',totalMass='3');ET.SubElement(body,'FixedProjectiveConstraint',indices='2')
    ET.SubElement(body,'BirthAwareContact',name='contact',segments='0 1',objectIndex='2',shape='2',radius='1',halfHeight='5',pointRadius='.02',lineStiffness='1',tangentLineStiffness='1',mu='100',historySpacing='.02',stride='1',filename=str(out/'contact.csv'),journalFilename=str(out/'journal.csv'));ET.SubElement(body,'IntegratedRecorder',filename=str(out/'state.txt'),stride='1');ET.ElementTree(root).write(out/'scene.scn',encoding='utf-8',xml_declaration=True)
    command=[str(SDK/'bin/graph_probe'),str(SDK),str(out/'scene.scn'),str(steps),'0',str(FRAME),str(BEAM),str(PLUGIN)];write_json(out/'command.json',command);write_json(out/'identity.json',ident);p=execute_process(command,out,60);log=(out/'stdout.log').read_text()+(out/'stderr.log').read_text();r=dict(status='FAIL',process=p,expected_rejection=expect_error,origin='actual SOFA one-step finite-mass contact event, dt1 is an independent event unit, not100mm baseline dt',config=dict(y=y,vy=vy,vz=vz,steps=steps,expected_extension=expected_extension))
    if expect_error:r.update(status='PASS' if '[ERROR]'in log and 'resolved birth/death' in log else 'FAIL',scope='PASS rejection classifier only, physical run intentionally invalid')
    elif p['exit_code']==0 and '[ERROR]'not in log and f'{steps} iterations done'in log:
        rows=list(csv.DictReader((out/'contact.csv').open()));last=rows[-1];r['last_contact']=last
        if expected_extension is not None:
            # Unit reference: first force-stage is separated, hence first
            # Euler step follows exactly the prescribed initial velocity.
            energy=.5*expected_extension**2;r.update(status='PASS' if abs(float(last['elastic_energy'])-energy)<1e-12 else 'FAIL',reference_tangent_energy=energy)
        else:r['status']='EXPERIMENTAL'
    r['artifacts']={p.name:sha(p) for p in out.iterdir() if p.is_file()};write_json(out/'metrics.json',r);print(name,r['status']);return r
def main():
    results={};results['birth']=case('birth',1.03,-.02,.02,expected_extension=.01);results['through']=case('through',2.,-4.,.02,expect_error=True);results['none']=case('none',1.03,0,.02,expected_extension=0);write_json(OUT/'events_summary.json',results)
if __name__=='__main__':main()
