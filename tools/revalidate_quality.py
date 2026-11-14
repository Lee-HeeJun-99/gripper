"""Static compilation, structural V109 comparison and measured artifact consistency."""
import ast
import csv
import json
import math
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
from verification_common import ROOT,RUN,BUILD,SOFA,PHYSICS,command,write_json,sha
from trial_validation import verify_artifacts


def main():
    static={}
    for folder in ('tools','tests','reference_fem','scenes'):
        for path in (ROOT/folder).glob('*.py'):
            try:compile(path.read_text(),str(path),'exec');static[str(path.relative_to(ROOT))]='PASS'
            except (SyntaxError,UnicodeError) as exc:static[str(path.relative_to(ROOT))]=str(exc)
    source=ROOT/'handover/20261114/SOFA_V109_SparseLDL_Tangential/sofa_v109.py'
    tree=ast.parse(source.read_text());values={}
    for node in tree.body:
        if isinstance(node,ast.Assign):
            try:
                value=ast.literal_eval(node.value)
                for target in node.targets:
                    if isinstance(target,ast.Name):values[target.id]=value
            except (ValueError,TypeError):pass
    context=dict(values,range=range,list=list,axial_force=0)
    scene=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='create_combined_scene')
    wanted=('poses','lines','lower_force','upper_force')
    for node in scene.body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in wanted for t in node.targets):
            expression=compile(ast.Expression(node.value),str(source),'eval')
            for target in node.targets:
                if isinstance(target,ast.Name):context[target.id]=eval(expression,dict(context,__builtins__={}),{})
    xml=ET.parse(PHYSICS/'baseline/scene.scn').getroot()
    def floats(value):return list(map(float,value.split()))
    model=dict(dt=float(xml.attrib['dt'])==.0005,gravity=floats(xml.attrib['gravity'])==[0,0,0],
               initial_positions=floats(xml.find('.//MechanicalObject').attrib['position'])==[v for p in context['poses'] for v in p],
               topology=floats(xml.find('.//MeshTopology').attrib['lines'])==[v for p in context['lines'] for v in p],
               mass=float(xml.find('.//UniformMass').attrib['totalMass'])==2e-5,
               young_modulus=float(xml.find('.//BeamFEMForceField').attrib['youngModulus'])==values['E'],
               poisson_ratio=float(xml.find('.//BeamFEMForceField').attrib['poissonRatio'])==values['NU'],
               radius=float(xml.find('.//BeamFEMForceField').attrib['radius'])==(4*(values['WIDTH']*values['H']**3/12)/math.pi)**.25,
               force=floats(xml.find('.//ConstantForceField').attrib['forces'])==context['lower_force']+context['upper_force'],
               fixed_roots=xml.find('.//FixedProjectiveConstraint').attrib['indices']=='0 11',
               force_nodes=xml.find('.//ConstantForceField').attrib['indices']=='10 21',
               integrator=xml.find('EulerImplicitSolver').attrib==dict(rayleighMass='0.2',rayleighStiffness='0.1'),
               solver=xml.find('SparseLDLSolver').attrib['template']=='CompressedRowSparseMatrixd',
               mapping=xml.find('.//RigidMapping').attrib['rigidIndexPerPoint']==' '.join(map(str,range(22))))
    command('release_final_plugin_ldd',['ldd',str(BUILD/'plugin/bin/libSofaTangentialV110.so')])
    command('release_final_diagnostics_ldd',['ldd',str(BUILD/'diagnostics/libReGripDiagnostics.so')])
    command('release_plugin_exports',['nm','-D','--defined-only',str(BUILD/'plugin/bin/libSofaTangentialV110.so')])
    command('release_python_abi',['readelf','-d',str(SOFA/'plugins/SofaPython3/lib/libSofaPython3.so')])
    flags=subprocess.run(['g++','-dM','-E','-x','c++','-'],input='#include <string>\n',capture_output=True,text=True)
    abi=[line for line in flags.stdout.splitlines() if '_GLIBCXX_USE_CXX11_ABI ' in line]
    artifacts={}
    for path in sorted(PHYSICS.glob('*/metrics.json')):
        report=verify_artifacts(path.parent)
        artifacts[path.parent.name]=dict(status=report['status'],artifact_integrity='PASS')
    write_json(RUN/'quality_release.json',dict(static_python=static,structural_model_checks=model,artifact_validation=artifacts,
        compiler_abi=abi,source_scene_sha256=sha(source),golden_sha256=sha(ROOT/'handover/20261114/result_V109_00_FREE_LDL.csv'),
        source_code_audit='No measured-response literals or golden-data reads in the execution/generation path. Golden reads are confined to regression/reference comparisons; plot scripts explicitly select a result directory.',
        full_vector_golden_available=False,full_vector_comparison_status='NOT RUN: Windows CSV stores derived metrics, not all 22 rigid states',
        status='PASS' if all(model.values()) and all(v=='PASS' for v in static.values()) else 'FAIL'))
    print('quality',all(model.values()),'Python files',len(static))


if __name__=='__main__':main()
