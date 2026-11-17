"""Sole custom coupled sphere ODE;NOT Native correction or certified grasp."""
import argparse,csv,json,math,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--mode',choices=('impact','c2','touch','release'),default='impact');p.add_argument('--steps',type=int,default=20);p.add_argument('--duration',type=float,default=.001);p.add_argument('--reuse');p.add_argument('--profile');p.add_argument('--body-mass',type=float,default=.0001);p.add_argument('--body-force-z',type=float,default=0);p.add_argument('--strict-newton',action='store_true');p.add_argument('--no-cache',action='store_true');p.add_argument('--adaptive',action='store_true');p.add_argument('--value-energy',action='store_true');p.add_argument('--reuse-coarse',action='store_true');p.add_argument('--frozen-grid');p.add_argument('--grid-factor',type=int,choices=(1,2,4),default=1);p.add_argument('--midpoint-contact',action='store_true');a=p.parse_args()
    if not 1<=a.steps<=1600 or not 0<a.duration<=1 or not 0<a.body_mass<=1 or not abs(a.body_force_z)<=.1:raise ValueError('bounded coupled budget1s/1600steps/positive research mass/finite bounded force')
    if a.adaptive and (a.mode!='impact' or a.duration>.001 or a.steps>4 or a.body_mass!=.0001 or a.body_force_z!=0 or a.strict_newton or a.no_cache or not a.profile):raise ValueError('adaptive pilot requires measured actual21 profile,<=1ms/4macros,unchanged impact fixture')
    if (a.value_energy or a.reuse_coarse) and not a.adaptive:raise ValueError('energy/coarse estimator optimizations require explicit adaptive owner')
    if a.frozen_grid and (a.adaptive or a.mode!='impact' or a.steps!=1 or a.body_mass!=.0001 or a.body_force_z!=0 or a.strict_newton or a.no_cache):raise ValueError('frozen pilot:one fresh original impact fixture,not a state replay')
    if a.midpoint_contact and (a.adaptive or a.frozen_grid):raise ValueError('midpoint-contact contrast first requires independent uniform-step verification')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models/film_coupled_contact',archive/'models/film_coupled_contact')
    extended=bool(a.adaptive or a.frozen_grid)
    if extended:
        shutil.copytree(ROOT/'models/film_coupled_adaptive',archive/'models/film_coupled_adaptive');shutil.copytree(ROOT/'models/film_value_energy',archive/'models/film_value_energy')
    for d in ('film_impact','film_shell','film_rail_tendon','film_native_contact','film_sphere_contact'):
        target=archive/'models'/d;target.mkdir()
        for f in (ROOT/'models'/d).glob('*.h'):shutil.copy2(f,target/f.name)
    identity=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},sdk=str(SDK),actual_solver='CoupledSphereODE sole shared midpoint/event/accepted closure',contact_law='frictionless perfectly inelastic event;constrained midpoint plus separate unilateral velocity impulse',mode=a.mode,steps=a.steps,duration=a.duration,body_mass=a.body_mass,inertia_per_mass=25.6,body_radius=8,buffer_radius=8.01,rayleigh_mass=2.,material_status='research assumptions;not PET/TPU/actuator measurements',scope='actual single guided film/free isotropic sphere dynamics;NOT3finger/grasp/time/energy qualification')
    identity.update(adaptive=a.adaptive,frozen_grid=a.frozen_grid,value_energy=a.value_energy,reuse_coarse=a.reuse_coarse,state_file='coupled.macro_states.csv' if extended else 'coupled.states.csv')
    identity.update(midpoint_contact=a.midpoint_contact,regular_contact_jacobian_time='midpoint' if a.midpoint_contact else 'endpoint')
    module='film_coupled_adaptive' if extended else 'film_coupled_contact';library='libReGripCoupledAdaptive.so' if extended else 'libReGripCoupledSphere.so'
    if a.adaptive:identity.update(actual_solver='AdaptiveCoupledSphereODE query-only forecast + exact base accepted owner',adaptive_tolerance=1e-4,controller_norm='fixed physical macro-horizon scale;old global .1% gate unchanged',controller_max_trials=384,controller_max_depth=12)
    stages={};build=ROOT/'build'/('coupled_sofa_'+a.tag)
    if a.reuse:
        prior=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((prior/'identity.json').read_text());compiled=lambda d:{k:v for k,v in d.items() if k.endswith(('.h','.cpp','/CMakeLists.txt'))}
        if compiled(old['sources'])!=compiled(identity['sources']):raise ValueError('coupled compiled source drift')
        build=ROOT/'build'/('coupled_sofa_'+a.reuse);binary=build/library
        if sha(binary)!=old['binary_sha256']:raise ValueError('coupled binary drift')
        stages['build']=dict(exit_code=0,reused=a.reuse)
    else:
        build.mkdir(exist_ok=False);stages['configure']=guarded(['cmake','-S',archive/'models'/module,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);stages['build']=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if stages['configure']['exit_code']==0 else dict(exit_code=-1)
    result=dict(status='FAIL',stages=stages,scope=identity['scope'])
    if stages['build']['exit_code']==0:
        binary=build/library;identity['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
        identity['generated_source_hashes']={str(f.relative_to(build)):sha(f) for f in build.rglob('*') if f.is_file() and ('value_models' in f.parts or f.name=='generated_value_manifest.tsv')}
        if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('Installed SDK ABI mismatch')
        limit=120
        ticks=None;denominator=None
        if a.frozen_grid:
            prior=ROOT/'results'/('autonomous_film_'+a.frozen_grid);meta=json.loads((prior/'identity.json').read_text());data=json.loads((prior/'summary.json').read_text())
            if data['status']!='PASS' or not meta.get('adaptive') or meta['steps']!=1 or meta['duration']!=a.duration or meta['mode']!=a.mode or meta['body_mass']!=a.body_mass:raise ValueError('completed matching single-macro adaptive grid required')
            for key,value in meta['sources'].items():
                if key.endswith('.h') and (key.startswith(('models/film_shell/','models/film_rail_tendon/','models/film_native_contact/','models/film_sphere_contact/','models/film_impact/')) or key=='models/film_coupled_contact/CoupledSphere.h') and identity['sources'].get(key)!=value:raise ValueError('frozen grid physical kernel source drift:'+key)
            source_states=list(csv.DictReader((prior/'coupled.states.csv').open()));times=np.array([float(s['time']) for s in source_states]);intervals=np.diff(np.r_[0.,times]);levels=np.rint(np.log2(a.duration/intervals)).astype(int)
            if np.any(levels<0) or np.any(levels>20) or np.max(abs(intervals-np.ldexp(a.duration,-levels)))>64*np.finfo(float).eps*a.duration:raise ValueError('source is not a complete declared dyadic grid')
            denominator=2**int(max(levels));raw=times/a.duration*denominator;ticks=np.rint(raw).astype(int)
            if np.any(abs(raw-ticks)>64*np.finfo(float).eps*np.maximum(1,abs(raw))) or np.any(np.diff(np.r_[0,ticks])<=0) or ticks[-1]!=denominator:raise ValueError('source time ticks unresolved')
            count=len(ticks)*a.grid_factor
            if count>1600:raise ValueError('frozen accepted step budget1600')
            ref=ROOT/'results'/('autonomous_film_'+meta['profile']);reference=json.loads((ref/'summary.json').read_text());commit_cost=data['process']['runtime_s']-reference['run']['runtime_s']
            if commit_cost<=0:raise ValueError('no positive measured commit cost estimate')
            estimate=2*commit_cost*a.grid_factor
            identity.update(actual_solver='FrozenCoupledGridODE physical h/h2/h4;NOT output-only refinement',grid_factor=a.grid_factor,comparison_state_file='coupled.states.csv',comparison_steps=count,source_grid_state_sha256=sha(prior/'coupled.states.csv'),source_grid_identity_sha256=sha(prior/'identity.json'),grid_denominator=denominator,source_clock_roundoff_s=float(np.max(abs(times-a.duration*ticks/denominator))),predicted_runtime_s=estimate,cost_model='twofold measured SOFA accepted-commit cost after subtracting independent identical controller profile;all480s limits unchanged',work_file='coupled.work.csv')
            if estimate>480:write_json(out/'identity.json',identity);write_json(out/'summary.json',dict(status='BLOCKED',scope='frozen grid cost policy;not OS exhaustion',predicted_runtime_s=estimate));print(json.dumps(dict(status='BLOCKED')));return
            limit=480
        if a.adaptive:
            prior=ROOT/'results'/('autonomous_film_'+a.profile);meta=json.loads((prior/'identity.json').read_text());data=json.loads((prior/'summary.json').read_text())
            if data['status']!='PASS' or data.get('nx')!=21 or data.get('controller_norm')!='fixed physical macro-horizon scale with time budget':raise ValueError('complete matching actual21 adaptive reference required')
            if data.get('value_energy',False)!=a.value_energy or data.get('reuse_coarse',False)!=a.reuse_coarse:raise ValueError('adaptive cost profile backend differs')
            for key,value in meta['sources'].items():
                if key.endswith('.h') and identity['sources'].get(key)!=value:raise ValueError('adaptive reference mechanical/controller header drift:'+key)
            estimate=1.6*data['run']['runtime_s']*a.steps
            identity.update(predicted_runtime_s=estimate,profile=a.profile,profile_note='independent identical actual21 controller plus60% accepted-commit allowance per macro;not physics approval')
            if estimate>480:write_json(out/'identity.json',identity);write_json(out/'summary.json',dict(status='BLOCKED',scope='adaptive profile cost policy;not OS exhaustion',predicted_runtime_s=estimate));print(json.dumps(dict(status='BLOCKED')));return
            limit=480
        if a.steps>64 or a.duration>.1:
            if not a.profile:raise ValueError('extended coupled test needs measured same-binary profile')
            prior=ROOT/'results'/('autonomous_film_'+a.profile);meta=json.loads((prior/'identity.json').read_text());data=json.loads((prior/'summary.json').read_text())
            if meta['binary_sha256']!=identity['binary_sha256'] or data['status']!='PASS':raise ValueError('invalid cost profile')
            estimate=2*data['process']['runtime_s']*a.steps/meta['steps']
            if estimate>480:
                write_json(out/'identity.json',identity);write_json(out/'summary.json',dict(status='BLOCKED',scope='prelaunch runtime policy,not OS exhaustion or physics failure',physics_process_started=False,profile=a.profile,predicted_runtime_s=estimate,policy_limit_s=480));raise ValueError('profiled cost exceeds480s;reduce interval/optimize first')
            identity['predicted_runtime_s']=estimate;limit=480
        origin=ROOT/'results/autonomous_film_20261117_c2_bounded_short401';old=json.loads((origin/'identity.json').read_text());tree=ET.parse(origin/'1/scene.scn');scene=tree.getroot();scene.set('dt',str(a.duration/a.steps))
        for element in scene.iter():
            for k,value in list(element.attrib.items()):
                if str(origin/'1') in value:element.set(k,value.replace(str(origin/'1'),str(out)))
        for element in list(scene):
            if element.tag in ('ReGripBDFSolver','NewtonRaphsonSolver','ReGripMatrixLinearSystem','EigenSparseLU','FilmNativeCoupledCorrection','FilmNativeObserver','FreeMotionAnimationLoop','GenericConstraintSolver','BlockGaussSeidelConstraintSolver','LinearSolverConstraintCorrection','DefaultPipeline','CollisionPipeline','BruteForceBroadPhase','BVHNarrowPhase','DefaultContactManager','CollisionResponse','LocalMinDistance','MinProximityIntersection') or (element.tag=='Node' and element.get('name')=='fixed') or (element.tag=='RequiredPlugin' and 'libReGripFilmNativeObserver.so' in element.get('pluginName','')):scene.remove(element)
        for parent in scene.iter():
            for element in list(parent):
                if element.tag.endswith('CollisionModel') or element.tag=='GenericConstraintCorrection':parent.remove(element)
        ET.SubElement(scene,'DefaultAnimationLoop');scene.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
        for plugin in scene.findall('RequiredPlugin'):
            path=ROOT.__class__(plugin.get('pluginName',''));key={'libReGripFilmShell.so':'core_sha256','libReGripFilmRailTendon.so':'assembly_sha256'}.get(path.name)
            if key:
                if sha(path)!=old[key]:raise ValueError('preserved FF/core binary drift')
                identity[path.name]=dict(path=str(path),sha256=old[key])
        initial=np.zeros(231*3);initial[3*102+2]=-3 if a.mode=='impact' else 0;scene.find("MechanicalObject[@name='dofs']").set('velocity',' '.join(map(str,initial)))
        field=scene.find("Node[@name='assembly']/FilmRailTendon");field.set('maximumTension','.001' if a.mode=='c2' else '0');field.set('filename',str(out/'film.csv'));field.set('displacementFilename',str(out/'displacement.csv'))
        center='75 12 -8.2' if a.mode=='c2' else '100 12 -8.011' if a.mode=='impact' else '100 12 -8.01';velocity='0 0 -.1 0 0 0' if a.mode=='release' else '0 0 0 0 0 0'
        obj=ET.SubElement(scene,'Node',name='free_object');ET.SubElement(obj,'MechanicalObject',name='body',template='Rigid3d',position=center+' 0 0 0 1',velocity=velocity);ET.SubElement(obj,'UniformMass',template='Rigid3d',vertexMass=f'{a.body_mass} 1 25.6 0 0 0 25.6 0 0 0 25.6')
        solver=ET.SubElement(scene,'FrozenCoupledGridODE' if a.frozen_grid else 'AdaptiveCoupledSphereODE' if a.adaptive else 'CoupledSphereODE',name='ode',root='@dofs',body='@free_object/body',field='@assembly/filmField',radius='8.01',rayleighMass='2',strictNewton=str(int(a.strict_newton)),reuseAcceptedEvaluation=str(int(not a.no_cache)),externalForce='0 0 '+str(a.body_force_z),maxSteps=str(1600 if extended else a.steps),filename=str(out/'coupled'))
        solver.set('midpointContact',str(int(a.midpoint_contact)))
        if a.adaptive:solver.set('maxMacroSteps',str(a.steps));solver.set('adaptiveTolerance','0.0001');solver.set('valueEnergyEstimator',str(int(a.value_energy)));solver.set('reuseCoarseTrial',str(int(a.reuse_coarse)))
        if a.frozen_grid:solver.set('gridTicks',' '.join(map(str,ticks)));solver.set('tickDenominator',str(denominator));solver.set('gridDuration',str(a.duration));solver.set('gridFactor',str(a.grid_factor))
        tree.write(out/'scene.scn');identity.update(initial_body_center=center,initial_body_velocity=velocity,body_force_z=a.body_force_z,strict_newton=a.strict_newton,accepted_cache=not a.no_cache,control=field.attrib)
        write_json(out/'identity.json',identity);process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',limit);result['process']=process
        log=(out/'process/stdout.log').read_text()+(out/'process/stderr.log').read_text()
        if process['exit_code']==0 and '[ERROR]' not in log:
            rows=list(csv.DictReader((out/identity['state_file']).open()));events=list(csv.DictReader((out/'coupled.events.csv').open()));finite=len(rows)==a.steps and all(math.isfinite(float(v)) for row in rows for k,v in row.items() if k not in ('body_center','body_quaternion','body_velocity','body_omega','local_displacement','local_velocity')) and all(np.all(np.isfinite(np.fromstring(row[k],sep=' '))) for row in rows for k in ('body_center','body_quaternion','body_velocity','body_omega','local_displacement','local_velocity'))
            if extended:
                inner=list(csv.DictReader((out/'coupled.states.csv').open()));result['accepted_internal_steps']=len(inner);result['minimum_internal_gap']=min([float(s['minimum_gap']) for s in inner],default=None);finite=finite and bool(inner) and result['minimum_internal_gap']>=-1e-10
            if finite and abs(float(rows[-1]['time'])-a.duration)<1e-12:
                minimum=min(float(r['minimum_gap']) for r in rows);result.update(status='PASS' if minimum>=-1e-10 else 'FAIL',minimum_gap=minimum,event_rows=len(events),event_times=sorted(set(float(r['time']) for r in events)),maximum_body_displacement=max(float(np.linalg.norm(np.fromstring(r['body_center'],sep=' ')-np.fromstring(center,sep=' '))) for r in rows),maximum_position_residual=max(float(r['position_residual']) for r in rows),physical_qualification='NOT QUALIFIED:limited execution/clearance only;fulltime/energy/friction/grasp absent')
    write_json(out/'identity.json',identity);write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],minimum_gap=result.get('minimum_gap'),events=result.get('event_times'))))
if __name__=='__main__':main()
