"""Bounded actual whole-surface midpoint-event prototype. Not grasp certification."""
import argparse,csv,json,math,shutil,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
SDK=Path('/home/ubuntu/SOFA/v26.06.00')
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--mode',choices=('impact','c2','touch','touch-cycle'),default='impact');p.add_argument('--steps',type=int,default=1);p.add_argument('--duration',type=float,default=.001);p.add_argument('--reuse');p.add_argument('--sustained-be',action='store_true');p.add_argument('--owner-ode',action='store_true');p.add_argument('--profile');p.add_argument('--midpoint-contact',action='store_true');p.add_argument('--restart-case');p.add_argument('--local-divisor',type=int,choices=(1,2,4,8,16),default=1);p.add_argument('--refine-at',type=float,default=.975);p.add_argument('--trace-owner',action='store_true');a=p.parse_args()
    if a.midpoint_contact and not a.sustained_be:raise ValueError('midpoint contact requires explicit sustained branch')
    runtime_limit=120;prediction=None
    if a.steps<1 or not 0<a.duration:raise ValueError('positive step count and duration required')
    actual_steps=a.steps
    if a.local_divisor!=1:
        if not a.owner_ode or a.restart_case or not 0<a.refine_at<a.duration:raise ValueError('local time grid requires fresh sole owner and internal refinement epoch')
        count=a.refine_at/(a.duration/a.steps);prefix=round(count)
        if abs(count-prefix)>1e-10:raise ValueError('refinement epoch must lie on base time grid')
        actual_steps=prefix+(a.steps-prefix)*a.local_divisor
        if actual_steps>1600:raise ValueError('actual owner step budget1600')
    if a.steps>20 or a.duration>.1:
        if not a.profile or not a.reuse or not a.owner_ode or a.mode!='c2' or a.steps>1600 or a.duration>1:raise ValueError('extended original C2 onset requires measured same-binary owner profile;bounded1s/1600steps')
        prior=ROOT/'results'/('autonomous_film_'+a.profile);measured=json.loads((prior/'summary.json').read_text());meta=json.loads((prior/'identity.json').read_text())
        if measured['status']!='PASS' or not meta.get('owner_ode'):raise ValueError('completed owner profile required')
        prediction=2*measured['process']['runtime_s']*actual_steps/meta.get('actual_steps',meta['steps'])
        if prediction>480:raise ValueError('profiled twofold-margin runtime exceeds480s policy')
        runtime_limit=480
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
    build=ROOT/'build'/('film_whole_surface_'+a.tag);build.mkdir(exist_ok=False);archive=out/'sources'
    shutil.copytree(ROOT/'models/film_impact',archive/'models/film_impact')
    for name in ('film_shell','film_rail_tendon','film_sphere_contact','film_native_contact'):
        target=archive/'models'/name;target.mkdir()
        for s in (ROOT/'models'/name).glob('*.h'):shutil.copy2(s,target/s.name)
    identity=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(s.relative_to(archive)):sha(s) for s in archive.rglob('*') if s.is_file()},sdk=str(SDK),mode=a.mode,steps=a.steps,duration=a.duration,sustained_be=a.sustained_be,owner_ode=a.owner_ode,contact_law='fixed sphere plastic impact;quadratic midpoint path;optional independent BE-position/velocity-impulse split')
    identity.update(profile=a.profile,predicted_seconds_with_margin=prediction,child_limit=runtime_limit,midpoint_contact=a.midpoint_contact,actual_steps=actual_steps,local_divisor=a.local_divisor,refine_at=a.refine_at if a.local_divisor!=1 else None,actual_solver='FilmSurfaceODESolver:midpoint+explicit impact+separate sustained law' if a.owner_ode else 'ReGripBDFSolver:BE followed by end-event owner correction',sustained_law='constrained midpoint plus unilateral velocity projection' if a.midpoint_contact else 'BE position plus unilateral velocity projection',impact_law='frictionless perfectly inelastic research assumption',material_status='research assumptions;not measured PET/TPU')
    stages={};write_json(out/'identity.json',identity)
    if a.reuse:
        old=ROOT/'results'/('autonomous_film_'+a.reuse);prior=json.loads((old/'identity.json').read_text())
        if prior['sources']!=identity['sources']:raise ValueError('compiled source drift')
        build=ROOT/'build'/('film_whole_surface_'+a.reuse)
        if sha(build/'libReGripImpactReference.so')!=prior['binary_sha256']:raise ValueError('binary drift')
        if a.profile and json.loads((ROOT/'results'/('autonomous_film_'+a.profile)/'identity.json').read_text())['binary_sha256']!=prior['binary_sha256']:raise ValueError('profile binary differs')
        stages['build']=dict(exit_code=0,reused=a.reuse)
    else:
        stages['configure']=guarded(['cmake','-S',archive/'models/film_impact','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120)
        stages['build']=guarded(['cmake','--build',build,'-j','1'],out/'build_process',180) if stages['configure']['exit_code']==0 else dict(exit_code=-1)
    result=dict(status='FAIL',stages=stages,scope='bounded actual whole-surface prototype;NOT full time/energy/grasp qualification')
    if stages['build']['exit_code']==0:
        binary=build/'libReGripImpactReference.so';identity['binary_sha256']=sha(binary)
        ldd=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(ldd)
        if 'not found' in ldd or any('libSofa.' in l and '=> /' in l and str(SDK) not in l for l in ldd.splitlines()):raise ValueError('SDK ABI mismatch')
        prior=ROOT/'results/autonomous_film_20261117_c2_bounded_short401';parent=json.loads((prior/'identity.json').read_text());tree=ET.parse(prior/'1/scene.scn');scene=tree.getroot();scene.set('dt',str(a.duration/a.steps))
        for e in list(scene):
            if e.tag in ('FilmNativeCoupledCorrection','FilmNativeObserver') or (e.tag=='RequiredPlugin' and 'libReGripFilmNativeObserver.so' in e.get('pluginName','')):scene.remove(e)
        for e in scene.iter():
            for key,value in list(e.attrib.items()):
                if str(prior/'1') in value:e.set(key,value.replace(str(prior/'1'),str(out)))
        for e in scene.findall('RequiredPlugin'):
            name=Path(e.get('pluginName','')).name
            if name in ('libReGripFilmShell.so','libReGripFilmRailTendon.so'):
                expected=parent['core_sha256' if name=='libReGripFilmShell.so' else 'assembly_sha256']
                if sha(Path(e.get('pluginName')))!=expected:raise ValueError('archived FF/core binary drift')
                identity[name]=dict(path=e.get('pluginName'),sha256=expected)
        scene.find('ReGripBDFSolver').set('nativeCoupledPredictor','0')
        field=scene.find("Node[@name='assembly']/FilmRailTendon")
        if a.mode=='impact':
            field.set('maximumTension','0');velocity=[0.]*(231*3);velocity[3*102+2]=-3;scene.find("MechanicalObject[@name='dofs']").set('velocity',' '.join(map(str,velocity)));scene.find("Node[@name='fixed']/MechanicalObject").set('position','100 12 -8.011')
        if a.mode in ('touch','touch-cycle'):
            if not a.sustained_be:raise ValueError('touch test requires the explicit sustained method')
            scene.find("Node[@name='fixed']/MechanicalObject").set('position','100 12 -8.01')
        if a.mode=='touch-cycle':
            field.set('rampTime','.02');field.set('releaseBegin','.04');field.set('releaseEnd','.06')
        field.set('filename',str(out/'film.csv'));field.set('displacementFilename',str(out/'displacement.csv'))
        center=scene.find("Node[@name='fixed']/MechanicalObject").get('position')
        start_time=0
        if a.restart_case:
            if a.mode!='c2' or not a.owner_ode:raise ValueError('replay requires actual C2 sole owner')
            original=ROOT/'results'/('autonomous_film_'+a.restart_case);oldmeta=json.loads((original/'identity.json').read_text())
            if oldmeta['mode']!='c2' or not oldmeta.get('owner_ode') or oldmeta.get('midpoint_contact',False)!=a.midpoint_contact:raise ValueError('replay mechanical/integration model differs')
            for key,value in identity['sources'].items():
                if key.startswith(('models/film_shell/','models/film_rail_tendon/')) and oldmeta['sources'].get(key)!=value:raise ValueError('replay underlying mechanical source differs')
            saved=list(csv.DictReader((original/'event.csv.states.csv').open()))[-1];start_time=float(saved['time'])
            root_dofs=scene.find("MechanicalObject[@name='dofs']");root_dofs.set('position',saved['local_displacement']);root_dofs.set('velocity',saved['local_velocity'])
            identity['accepted_replay']=dict(source=a.restart_case,source_status=json.loads((original/'summary.json').read_text())['status'],state_file_sha256=sha(original/'event.csv.states.csv'),physical_start_time=start_time,note='last committed state from explicit accepted owner journal;NOT full trajectory convergence',legacy_ff_cumulative_work='INVALID across replay origin:legacy FF previousLength/previousT reset;do not use this replay for cumulative work/energy certification')
        ET.SubElement(scene,'RequiredPlugin',pluginName=str(binary));ET.SubElement(scene,'FilmWholeSurfaceEventOwner',name='surfaceOwner',root='@dofs',field='@assembly/filmField',center=center,radius='8.01',sustainedBE=str(int(a.sustained_be)),midpointContact=str(int(a.midpoint_contact)),odeDriven=str(int(a.owner_ode)),replayStartTime=str(start_time),filename=str(out/'event.csv'))
        if a.trace_owner:scene.find('FilmWholeSurfaceEventOwner').set('solverTraceFilename',str(out/'solver_trace.log'))
        if a.owner_ode:
            for e in list(scene):
                if e.tag in ('ReGripBDFSolver','NewtonRaphsonSolver','ReGripMatrixLinearSystem','EigenSparseLU','FreeMotionAnimationLoop','BlockGaussSeidelConstraintSolver','LinearSolverConstraintCorrection','CollisionPipeline','BruteForceBroadPhase','BVHNarrowPhase','MinProximityIntersection','CollisionResponse'):scene.remove(e)
            ET.SubElement(scene,'FilmSurfaceODESolver',name='ode',rayleighMass='2')
            ET.SubElement(scene,'DefaultAnimationLoop')
        if a.local_divisor!=1:
            clock_sources=out/'clock_sources';shutil.copytree(ROOT/'models/event_step_clock',clock_sources);clock_build=out/'clock_build'
            configure=guarded(['cmake','-S',clock_sources,'-B',clock_build,'-DCMAKE_PREFIX_PATH='+str(SDK)],out/'clock_configure',120)
            compile_clock=guarded(['cmake','--build',clock_build,'-j','1'],out/'clock_compile',120) if configure['exit_code']==0 else dict(exit_code=-1)
            if compile_clock['exit_code']:raise ValueError('clock build failure;process logs preserved')
            clock_binary=clock_build/'libReGripEventStepClock.so';dependencies=subprocess.check_output(['ldd',clock_binary],text=True);(out/'clock_ldd.txt').write_text(dependencies)
            if 'not found' in dependencies or any('libSofa.' in l and '=> /' in l and str(SDK) not in l for l in dependencies.splitlines()):raise ValueError('clock SDK ABI mismatch')
            loop=scene.find('DefaultAnimationLoop');scene.insert(list(scene).index(loop),ET.Element('RequiredPlugin',pluginName=str(clock_binary)));loop.tag='EventStepClockAnimationLoop';loop.set('eventTimes','0 '+str(a.refine_at));loop.set('stepDivisors','1 '+str(a.local_divisor));loop.set('filename',str(out/'grid.csv'))
            identity['clock']=dict(binary_sha256=sha(clock_binary),source_hashes={f.name:sha(f) for f in clock_sources.iterdir() if f.is_file()},note='existing event clock rebuilt against Installed SDK;explicit nonuniform time-grid contrast,NOT uniform dt refinement')
        path=out/'scene.scn';tree.write(path)
        identity.update(assembly_parameters={k:v for k,v in field.attrib.items() if 'filename' not in k.lower()},scene_sha256=sha(path),boundary_note='preserved mapped quarter-root clamp;fixed R8 sphere;not free-object grasp')
        write_json(out/'identity.json',identity)
        process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(actual_steps),'--hideProgressBar',path],out/'process',runtime_limit);result['process']=process
        try:
            log=(out/'process/stdout.log').read_text()+(out/'process/stderr.log').read_text()
            if process['exit_code'] or '[ERROR]' in log:raise ValueError('actual engine/owner failure')
            rows=list(csv.DictReader((out/'event.csv.surface.csv').open()));states=list(csv.DictReader((out/'event.csv.states.csv').open()));actual=list(csv.DictReader((out/'film.csv').open()))
            if len(states)!=actual_steps or len(actual)!=actual_steps:raise ValueError('incomplete states')
            for s in states:
                for key,value in s.items():
                    numbers=value.split() if key in ('local_displacement','local_velocity') else [value]
                    if not numbers or not all(math.isfinite(float(v)) for v in numbers):raise ValueError('nonfinite/missing accepted '+key)
                if float(s['minimum_gap']) < -1e-10:raise ValueError('whole endpoint gap gate failed')
            if abs(float(states[-1]['time'])-start_time-a.duration)>1e-12:raise ValueError('wrong physical end time')
            if a.local_divisor!=1:
                base=a.duration/a.steps;prefix=round(a.refine_at/base)
                for i,s in enumerate(states):
                    expected=(i+1)*base if i<prefix else a.refine_at+(i+1-prefix)*base/a.local_divisor
                    if abs(float(s['time'])-expected)>1e-12:raise ValueError('actual event clock differs from declared time grid')
            matched=all(float(s['end_tension'])==float(r['T_per_rail']) for s,r in zip(states,actual))
            if not matched:raise ValueError('FF and owner shared end-time C2 mismatch')
            if a.mode=='impact' and not rows:raise ValueError('impact expected but not observed')
            result.update(status='PASS',rows=len(rows),minimum_gap=min(float(r['minimum_gap']) for r in states),control_end_exact=matched,events=rows)
        except (OSError,ValueError) as e:result['failure_reason']=str(e)
    write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('stages','events','process')}))
if __name__=='__main__':main()
