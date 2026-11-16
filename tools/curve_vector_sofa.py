"""Actual matching-SDK fixed-patch isolation benchmark,NOT grasp validation."""
import argparse
import csv
import json
import re
import shutil
import subprocess
from closure_validation_suite import logged
from curve_common import ROOT,sha,write_json


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--tag',required=True)
    parser.add_argument('--steps',type=int,default=100)
    parser.add_argument('--dt',type=float,default=.01)
    parser.add_argument('--initial-vy',type=float,default=0.)
    parser.add_argument('--solver',choices=['euler','newmark'],default='euler')
    parser.add_argument('--directed',action='store_true')
    parser.add_argument('--compression-every',type=int,default=0)
    parser.add_argument('--snapshot-tolerance',type=float,default=1e-9)
    parser.add_argument('--normalized',action='store_true')
    parser.add_argument('--outward',action='store_true')
    parser.add_argument('--load',choices=['constant','reverse'],default='constant')
    args=parser.parse_args()
    if args.normalized and not args.compression_every:raise ValueError('normalized representation requires explicit compression')
    if args.outward and not args.normalized:raise ValueError('outward prefilter requires normalized representation')
    import math
    if not args.tag.replace('_','').isalnum() or not 1<=args.steps<=1024 or not 0<args.dt<=.01 or not math.isfinite(args.initial_vy) or abs(args.initial_vy)>.01 or not 0<=args.compression_every<=1024 or not 0<args.snapshot_tolerance<=1e-4:
        raise ValueError('fresh simple tag and bounded reference steps1..1024')
    out=ROOT/'results'/('vector_history_sdk_'+args.tag)
    build=ROOT/'build'/('vector_history_sdk_'+args.tag)
    out.mkdir(exist_ok=False)
    if build.exists():raise ValueError('refuse existing build')
    sdk=ROOT/'build/grasp_20261115/sofa_patched'
    paths=[p for p in (ROOT/'models/yield_front_history').glob('*') if p.is_file()]
    paths += [ROOT/'tests/test_vector_patch.cpp',ROOT/'tools/curve_vector_sofa.py',ROOT/'tools/run_trial.py']
    before={str(p.relative_to(ROOT)):sha(p)for p in paths}
    write_json(out/'identity.json',dict(source_sha256=before,source_commit=subprocess.check_output(
        ['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sdk=str(sdk),driver_sha256=sha(sdk/'bin/graph_probe'),
        scope='fixed normal/tangential patch displacement benchmark;not3Dcontact or grasp'))
    for p in paths:
        target=out/'sources'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    stages={}
    commands=[('configure',['cmake','-S',ROOT/'models/yield_front_history','-B',build,
                 '-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(ROOT/'.runtime/closure_sdk')]),
              ('build',['cmake','--build',build,'-j2']),('api',[build/'test_vector_patch']),
              ('ldd',['ldd',build/'libReGripVectorPatchReference.so'])]
    if args.compression_every:commands.insert(3,('api_compressed',[build/'test_vector_patch','compressed']))
    if args.normalized:commands.insert(3,('api_normalized',[build/'test_vector_patch','normalized']))
    if args.outward:commands.insert(3,('api_outward',[build/'test_vector_patch','outward']))
    for name,cmd in commands:
        stages[name]=logged(cmd,out/name,180)
        if stages[name]['exit_code']:
            write_json(out/'summary.json',dict(status='FAIL',stage=name,stages=stages));return
    if before!={str(p.relative_to(ROOT)):sha(p)for p in paths}:raise ValueError('source changed while compiling')
    libraries={}
    for line in (out/'ldd/stdout.log').read_text().splitlines():
        if 'not found' in line:raise ValueError('unresolved runtime library')
        match=re.search(r'(libSofa\S+)\s+=>\s+(\S+)',line)
        if match:
            path=__import__('pathlib').Path(match[2]).resolve()
            if not path.is_relative_to(sdk.resolve()):raise ValueError('mixed SOFA runtime '+str(path))
            libraries[match[1]]=dict(path=str(path),sha256=sha(path))
    if not libraries:raise ValueError('no resolved SOFA dependencies')
    write_json(out/'runtime.json',libraries)
    plugin=build/'libReGripVectorPatchReference.so'
    write_json(out/'compiled.json',dict(binary_sha256=sha(plugin),api_binary_sha256=sha(build/'test_vector_patch'),sources=before))
    case=out/'dynamic';case.mkdir()
    ode='<EulerImplicitSolver rayleighMass="0" rayleighStiffness="0"/>'if args.solver=='euler'else'<NewmarkImplicitSolver rayleighMass="0" rayleighStiffness="0" gamma="0.5" beta="0.25"/>'
    load='<ConstantForceField template="Vec3d" indices="0" forces="0.000002 0.000001 0"/>'if args.load=='constant'else'<LinearForceField template="Vec3d" points="0" times="0 0.1 0.11 0.5" forces="0.000002 0.000001 0 0.000002 0.000001 0 -0.00002 -0.00002 0 -0.00002 -0.00002 0"/>'
    scene=f'''<?xml version="1.0"?>
<Node name="VectorPatchIsolation" dt="{args.dt:.17g}" gravity="0 0 0">
 <RequiredPlugin pluginName="Sofa.Component.AnimationLoop Sofa.Component.StateContainer Sofa.Component.Mass Sofa.Component.ODESolver.Backward Sofa.Component.LinearSolver.Direct Sofa.Component.MechanicalLoad"/>
 <DefaultAnimationLoop/>
 {ode}
 <SparseLDLSolver/>
 <MechanicalObject template="Vec3d" position="0 0 0" velocity="0 {args.initial_vy:.17g} 0"/>
 <UniformMass totalMass="0.001"/>
 {load}
 <VectorPatchBenchmark halfLength="0.3192" stiffness="0.001" capacity="0.000003" velocityDirectedTangent="{int(args.directed)}" normalizedRepresentation="{int(args.normalized)}" outwardCertificates="{int(args.outward)}" compressionEvery="{args.compression_every}" snapshotTolerance="{args.snapshot_tolerance:.17g}" filename="{case/'journal.csv'}"/>
</Node>
'''
    (case/'scene.scn').write_text(scene)
    required={}
    import xml.etree.ElementTree as ET
    for name in ET.fromstring(scene).find('RequiredPlugin').attrib['pluginName'].split():
        path=(sdk/'lib'/('lib'+name+'.so')).resolve()
        if not path.is_file()or not path.is_relative_to(sdk.resolve()):raise ValueError('missing/mixed RequiredPlugin '+name)
        required[name]=dict(path=str(path),sha256=sha(path))
    write_json(out/'required_runtime.json',required)
    cmd=[sdk/'bin/graph_probe',sdk,case/'scene.scn',str(args.steps),'0',plugin]
    stages['dynamic']=logged(cmd,case/'process',480)
    logs=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
    result=dict(status='FAIL',stages=stages,scope='actual SDK fixed-patch benchmark ONLY',
                grasp='NOT RUN',global_energy='BLOCKED',steps_requested=args.steps,dt=args.dt,initial_vy=args.initial_vy,solver=args.solver,
                velocity_directed_tangent=args.directed,
                compression_every=args.compression_every,snapshot_tolerance=args.snapshot_tolerance,
                normalized_representation=args.normalized,
                outward_certificates=args.outward,
                load_schedule=args.load,
                nonsmooth_tangent=('explicit velocity-sided generalized derivative'if args.directed else'explicit elastic generalized derivative')+' at zero increment/equal positive capacity;not unique classical tangent')
    try:
        if stages['dynamic']['exit_code'] or '[ERROR]' in logs or 'Unused Attribute' in logs or f'{args.steps} iterations done' not in logs:
            raise ValueError('SOFA error/incomplete/unregistered Data')
        with (case/'journal.csv').open()as stream:rows=list(csv.DictReader(stream))
        if len(rows)!=args.steps or [int(r['commit'])for r in rows]!=list(range(1,args.steps+1)):
            raise ValueError('actual once-per-step Commit count')
        if any(not math.isfinite(float(v))for r in rows for v in r.values()):raise ValueError('NaN/Inf journal')
        if args.load=='constant'and(float(rows[-1]['x'])<=0 or float(rows[-1]['y'])<=0):raise ValueError('no actual state change')
        if args.load=='reverse'and args.steps*args.dt>=.5 and not(float(rows[-1]['vx'])<0 and float(rows[-1]['vy'])<0):raise ValueError('actual scheduled force did not reverse velocity')
        max_residual=max(abs(float(r['energy_residual']))for r in rows)
        if max_residual>1e-23:raise ValueError('local endpoint energy identity fails')
        if any(float(r['loss'])<0 for r in rows):raise ValueError('negative plastic loss')
        result.update(status='PASS',actual_commits=len(rows),last=rows[-1],max_material_energy_residual=max_residual)
    except (ValueError,OSError)as error:result['failure_reason']=str(error)
    write_json(out/'summary.json',result)
    print(json.dumps(result))


if __name__=='__main__':main()
