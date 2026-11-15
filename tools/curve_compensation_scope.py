"""Actual SOFA scope test: recover structural summation,never move object directly."""
import json
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import OUT, SDK, FRAME, BEAM, PLUGIN, sha, write_json
from curve_compensation import PLUGIN as COMPENSATION
from run_trial import execute_process
from trial_validation import read_states


def main():
    out=OUT/'scope_test_v1';out.mkdir(exist_ok=False);states={};processes={}
    for enabled in(False,True):
        name='compensated'if enabled else'ordinary';p=out/name;p.mkdir()
        root=ET.Element('Node',name='root',dt='.000125',gravity='0 0 0')
        plugins=['Sofa.Component.StateContainer','Sofa.Component.Mass','Sofa.Component.ODESolver.Backward','Sofa.Component.LinearSolver.Direct','Sofa.Component.Constraint.Projective']
        if enabled:plugins.append(str(COMPENSATION))
        for i,plugin in enumerate(plugins):ET.SubElement(root,'RequiredPlugin',name='p'+str(i),pluginName=plugin)
        ET.SubElement(root,'DefaultAnimationLoop');ET.SubElement(root,'EulerImplicitSolver',rayleighMass='0',rayleighStiffness='0')
        ET.SubElement(root,'EigenSparseLU',template='CompressedRowSparseMatrixd')
        body=ET.SubElement(root,'Node',name='Multilayer')
        ET.SubElement(body,'MechanicalObject',template='Rigid3d',name='rigid',position='0 0 0 0 0 0 1 100 0 0 0 0 0 1 200 0 0 0 0 0 1',velocity='0 0 0 0 0 0 2e-12 0 1e-15 0 0 0 2e-12 0 0 0 .001 0')
        ET.SubElement(body,'UniformMass',totalMass='3')
        if enabled:ET.SubElement(body,'CompensatedBeamTranslations',indices='1',objectIndex='2',nodesPerLayer='2',filename=str(p/'compensation.csv'))
        ET.SubElement(body,'FixedProjectiveConstraint',indices='0')
        ET.SubElement(body,'IntegratedRecorder',filename=str(p/'state.txt'),stride='20')
        ET.ElementTree(root).write(p/'scene.scn',encoding='utf-8',xml_declaration=True)
        command=list(map(str,[SDK/'bin/graph_probe',SDK,p/'scene.scn',5000,0,FRAME,BEAM,PLUGIN]));write_json(p/'command.json',command)
        processes[name]=execute_process(command,p,60)
        log=(p/'stdout.log').read_text()+(p/'stderr.log').read_text()
        if processes[name]['exit_code']or'[ERROR]'in log:write_json(out/'summary.json',dict(status='FAIL',stage=name,process=processes[name]));return
        states[name]=read_states(p/'state.txt')
    a,b=states['ordinary'],states['compensated'];x=np.array([r['X']for r in a]).reshape(-1,3,7);y=np.array([r['X']for r in b]).reshape(-1,3,7)
    object_error=float(abs(x[:,2]-y[:,2]).max());root_error=float(abs(x[:,0]-y[:,0]).max());rotation_error=float(abs(x[:,:,3:]-y[:,:,3:]).max())
    v_error=float(abs(np.array([r['V']for r in a])-np.array([r['V']for r in b])).max())
    expected=float(np.longdouble(100)+np.longdouble('2e-12')*np.longdouble('.000125')*5000)
    arithmetic_error=abs(y[-1,1,0]-expected);ordinary_error=abs(x[-1,1,0]-expected)
    passed=not any((object_error,root_error,rotation_error,v_error,arithmetic_error))and ordinary_error>0
    write_json(out/'summary.json',dict(status='PASS'if passed else'FAIL',processes=processes,compensation_binary_sha256=sha(COMPENSATION),object_max_difference=object_error,root_max_difference=root_error,all_rotation_max_difference=rotation_error,all_velocity_max_difference=v_error,structural_expected_x=expected,structural_arithmetic_error=arithmetic_error,ordinary_structural_error=ordinary_error,scope='actual5000step constant-velocity SOFA comparison;only structure X/Z summation changes;not coupled-grasp certification'))
    print(passed,arithmetic_error,ordinary_error,object_error,rotation_error)


if __name__=='__main__':main()
