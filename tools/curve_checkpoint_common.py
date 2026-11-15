import json,xml.etree.ElementTree as ET
from pathlib import Path
from curve_common import ROOT,OUT,SDK,FRAME,BEAM,PLUGIN,identity,sha,write_json
from curve_checkpoint_build import CPBUILD
from run_trial import execute_process
from birth_monitor import Monitor
CPROOT=ROOT/'results/autonomous_20261116_checkpoint_a01'
def fingerprint(ident):
    beam=ident['inherited']['inherited']['beam'];return dict(curve=ident['curved'],beam_sha256=beam['plugin_sha256'],frame_sha256=beam['frame_sha256'],sdk_driver_sha256=beam['sdk_driver_sha256'])
def guard():
    current=identity();m=json.loads((CPBUILD/'build_manifest.json').read_text())
    if fingerprint(current)!=fingerprint(m['identity']):raise ValueError('checkpoint runtime identity changed')
    for n,h in m['sources'].items():
        if sha(ROOT/n)!=h:raise ValueError('checkpoint source changed: '+n)
    for n,h in {**m['binaries'],**m['generated']}.items():
        if sha(CPBUILD/n)!=h:raise ValueError('checkpoint compiled artifact changed: '+n)
    return current,m
def physics_hash(tree):
    duplicate=ET.fromstring(ET.tostring(tree.getroot()))
    for element in duplicate.iter():
        if'filename'in element.attrib:
            if element.tag not in('FrameLayerNetwork','CurvedMaterialContact','IntegratedRecorder'):raise ValueError('unknown physical filename scope')
            element.attrib.pop('filename')
    import hashlib
    return hashlib.sha256(ET.tostring(duplicate)).hexdigest()
def validate_scope(tree):
    allowed={'Node','RequiredPlugin','DefaultAnimationLoop','EulerImplicitSolver','EigenSparseLU','MechanicalObject','MeshTopology','DiagonalMass','ConservativeBeam','FixedProjectiveConstraint','PartialFixedProjectiveConstraint','FrameLayerNetwork','RoutedCable','CurvedMaterialContact','SpatialLoad','IntegratedRecorder'}
    unknown={e.tag for e in tree.getroot().iter()}-allowed
    if unknown:raise ValueError('uncheckpointed component state: '+repr(unknown))
    if len(list(tree.getroot().iter('Node')))!=2:raise ValueError('checkpoint scope is one rigid mechanical body node')
    ode=tree.getroot().find('EulerImplicitSolver')
    if ode is None or any(ode.get(k,'false')not in('0','false')for k in('firstOrder','trapezoidalScheme','solveConstraint'))or float(ode.get('vdamping','0'))!=0:raise ValueError('unsupported time integration state')
def chunk(directory,source,steps,input_checkpoint=None,dt=None,wall=480):
    ident,build=guard();directory=Path(directory);directory.mkdir(parents=True,exist_ok=False);tree=ET.parse(source/'scene.scn')
    if dt is not None:tree.getroot().set('dt',str(dt))
    validate_scope(tree)
    digest=physics_hash(tree);meta=None
    if input_checkpoint is not None:
        meta=json.loads(Path(str(input_checkpoint)+'.meta.json').read_text())
        if meta['physics_sha256']!=digest or meta['checkpoint_sha256']!=sha(input_checkpoint)or meta['runtime']!=fingerprint(ident)or meta.get('code_build')!=build['binaries']or meta.get('jacobian_sha256')!=sha(Path(str(input_checkpoint)+'.J')):raise ValueError('checkpoint/config/hash mismatch')
    for element in tree.getroot().iter():
        if'filename'in element.attrib:element.set('filename',str(directory/element.get('filename').rsplit('/',1)[-1]))
    tree.write(directory/'scene.scn',encoding='utf-8',xml_declaration=True);output=directory/'physical.cp';command=list(map(str,[CPBUILD/'physics_checkpoint',SDK,directory/'scene.scn',steps,input_checkpoint or'-',output,FRAME,BEAM,PLUGIN,directory/'chunk_summary.json']));write_json(directory/'command.json',command);write_json(directory/'identity.json',dict(runtime=ident,checkpoint_build=build));write_json(directory/'request.json',dict(local_steps=steps,dt=float(tree.getroot().get('dt')),wall=wall,source_scene_sha256=sha(source/'scene.scn'),physics_sha256=digest,input_checkpoint_sha256=sha(input_checkpoint)if input_checkpoint else None,scope='same physical state/history restored;startup init frame of restored chunks excluded from merged trajectory'))
    monitor=Monitor(directory);monitor.thread.start()
    try:process=execute_process(command,directory,wall)
    finally:monitor.finish()
    log=(directory/'stdout.log').read_text()+(directory/'stderr.log').read_text()
    if process['exit_code']or'[ERROR]'in log:write_json(directory/'result.json',dict(status='FAIL',process=process));raise RuntimeError('checkpoint child failed')
    s=json.loads((directory/'chunk_summary.json').read_text());start=meta['summary']['global_steps']if meta else 0
    if s['local_steps']!=steps or s['global_steps']!=start+steps:raise ValueError('actual checkpoint step count')
    metadata=dict(physics_sha256=digest,checkpoint_sha256=sha(output),jacobian_sha256=sha(Path(str(output)+'.J')),code_build=build['binaries'],runtime=fingerprint(ident),summary=s,process=process);write_json(Path(str(output)+'.meta.json'),metadata);write_json(directory/'result.json',dict(status='EXPERIMENTAL',**metadata));return output,metadata
def merge_states(parts,target):
    with target.open('x')as out:
        for index,path in enumerate(parts):
            block=-1
            with(path/'state.txt').open()as stream:
                for line in stream:
                    if line.startswith('T='):block+=1
                    if index==0 or block>0:out.write(line)
def merge_csv(parts,name,target):
    with target.open('x')as out:
        for index,path in enumerate(parts):
            with(path/name).open()as stream:
                header=next(stream)
                if index==0:out.write(header)
                for line in stream:out.write(line)
