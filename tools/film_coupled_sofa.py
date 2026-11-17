"""Sole custom coupled sphere ODE;NOT Native correction or certified grasp."""
import argparse,csv,json,math,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--mode',choices=('impact','c2','touch','release'),default='impact');p.add_argument('--steps',type=int,default=20);p.add_argument('--duration',type=float,default=.001);p.add_argument('--reuse');p.add_argument('--profile');p.add_argument('--body-mass',type=float,default=.0001);p.add_argument('--body-force-z',type=float,default=0);p.add_argument('--strict-newton',action='store_true');p.add_argument('--no-cache',action='store_true');a=p.parse_args()
    if not 1<=a.steps<=1600 or not 0<a.duration<=1 or not 0<a.body_mass<=1 or not abs(a.body_force_z)<=.1:raise ValueError('bounded coupled budget1s/1600steps/positive research mass/finite bounded force')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models/film_coupled_contact',archive/'models/film_coupled_contact')
    for d in ('film_impact','film_shell','film_rail_tendon','film_native_contact','film_sphere_contact'):
        target=archive/'models'/d;target.mkdir()
        for f in (ROOT/'models'/d).glob('*.h'):shutil.copy2(f,target/f.name)
    identity=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},sdk=str(SDK),actual_solver='CoupledSphereODE sole shared midpoint/event/accepted closure',contact_law='frictionless perfectly inelastic event;constrained midpoint plus separate unilateral velocity impulse',mode=a.mode,steps=a.steps,duration=a.duration,body_mass=a.body_mass,inertia_per_mass=25.6,body_radius=8,buffer_radius=8.01,rayleigh_mass=2.,material_status='research assumptions;not PET/TPU/actuator measurements',scope='actual single guided film/free isotropic sphere dynamics;NOT3finger/grasp/time/energy qualification')
    stages={};build=ROOT/'build'/('coupled_sofa_'+a.tag)
    if a.reuse:
        prior=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((prior/'identity.json').read_text());compiled=lambda d:{k:v for k,v in d.items() if k.endswith(('.h','.cpp','/CMakeLists.txt'))}
        if compiled(old['sources'])!=compiled(identity['sources']):raise ValueError('coupled compiled source drift')
        build=ROOT/'build'/('coupled_sofa_'+a.reuse);binary=build/'libReGripCoupledSphere.so'
        if sha(binary)!=old['binary_sha256']:raise ValueError('coupled binary drift')
        stages['build']=dict(exit_code=0,reused=a.reuse)
    else:
        build.mkdir(exist_ok=False);stages['configure']=guarded(['cmake','-S',archive/'models/film_coupled_contact','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);stages['build']=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if stages['configure']['exit_code']==0 else dict(exit_code=-1)
    result=dict(status='FAIL',stages=stages,scope=identity['scope'])
    if stages['build']['exit_code']==0:
        binary=build/'libReGripCoupledSphere.so';identity['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
        if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('Installed SDK ABI mismatch')
        limit=120
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
        ET.SubElement(scene,'CoupledSphereODE',name='ode',root='@dofs',body='@free_object/body',field='@assembly/filmField',radius='8.01',rayleighMass='2',strictNewton=str(int(a.strict_newton)),reuseAcceptedEvaluation=str(int(not a.no_cache)),externalForce='0 0 '+str(a.body_force_z),maxSteps=str(a.steps),filename=str(out/'coupled'));tree.write(out/'scene.scn');identity.update(initial_body_center=center,initial_body_velocity=velocity,body_force_z=a.body_force_z,strict_newton=a.strict_newton,accepted_cache=not a.no_cache,control=field.attrib)
        write_json(out/'identity.json',identity);process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',limit);result['process']=process
        log=(out/'process/stdout.log').read_text()+(out/'process/stderr.log').read_text()
        if process['exit_code']==0 and '[ERROR]' not in log:
            rows=list(csv.DictReader((out/'coupled.states.csv').open()));events=list(csv.DictReader((out/'coupled.events.csv').open()));finite=len(rows)==a.steps and all(math.isfinite(float(v)) for row in rows for k,v in row.items() if k not in ('body_center','body_quaternion','body_velocity','body_omega','local_displacement','local_velocity')) and all(np.all(np.isfinite(np.fromstring(row[k],sep=' '))) for row in rows for k in ('body_center','body_quaternion','body_velocity','body_omega','local_displacement','local_velocity'))
            if finite and abs(float(rows[-1]['time'])-a.duration)<1e-12:
                minimum=min(float(r['minimum_gap']) for r in rows);result.update(status='PASS' if minimum>=-1e-10 else 'FAIL',minimum_gap=minimum,event_rows=len(events),event_times=sorted(set(float(r['time']) for r in events)),maximum_body_displacement=max(float(np.linalg.norm(np.fromstring(r['body_center'],sep=' ')-np.fromstring(center,sep=' '))) for r in rows),maximum_position_residual=max(float(r['position_residual']) for r in rows),physical_qualification='NOT QUALIFIED:limited execution/clearance only;fulltime/energy/friction/grasp absent')
    write_json(out/'identity.json',identity);write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],minimum_gap=result.get('minimum_gap'),events=result.get('event_times'))))
if __name__=='__main__':main()
