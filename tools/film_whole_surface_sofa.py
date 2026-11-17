"""Bounded actual whole-surface midpoint-event prototype. Not grasp certification."""
import argparse,csv,json,math,shutil,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
SDK=Path('/home/ubuntu/SOFA/v26.06.00')
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--mode',choices=('impact','c2','touch','touch-cycle'),default='impact');p.add_argument('--steps',type=int,default=1);p.add_argument('--duration',type=float,default=.001);p.add_argument('--reuse');p.add_argument('--sustained-be',action='store_true');p.add_argument('--owner-ode',action='store_true');a=p.parse_args()
    if a.steps<1 or a.steps>20 or not 0<a.duration<=.1:raise ValueError('new owner first requires bounded20step/.1s profile')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
    build=ROOT/'build'/('film_whole_surface_'+a.tag);build.mkdir(exist_ok=False);archive=out/'sources'
    shutil.copytree(ROOT/'models/film_impact',archive/'models/film_impact')
    for name in ('film_shell','film_rail_tendon','film_sphere_contact','film_native_contact'):
        target=archive/'models'/name;target.mkdir()
        for s in (ROOT/'models'/name).glob('*.h'):shutil.copy2(s,target/s.name)
    identity=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources={str(s.relative_to(archive)):sha(s) for s in archive.rglob('*') if s.is_file()},sdk=str(SDK),mode=a.mode,steps=a.steps,duration=a.duration,sustained_be=a.sustained_be,owner_ode=a.owner_ode,contact_law='fixed sphere plastic impact;quadratic midpoint path;optional independent BE-position/velocity-impulse split')
    stages={};write_json(out/'identity.json',identity)
    if a.reuse:
        old=ROOT/'results'/('autonomous_film_'+a.reuse);prior=json.loads((old/'identity.json').read_text())
        if prior['sources']!=identity['sources']:raise ValueError('compiled source drift')
        build=ROOT/'build'/('film_whole_surface_'+a.reuse)
        if sha(build/'libReGripImpactReference.so')!=prior['binary_sha256']:raise ValueError('binary drift')
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
        ET.SubElement(scene,'RequiredPlugin',pluginName=str(binary));ET.SubElement(scene,'FilmWholeSurfaceEventOwner',name='surfaceOwner',root='@dofs',field='@assembly/filmField',center=center,radius='8.01',sustainedBE=str(int(a.sustained_be)),odeDriven=str(int(a.owner_ode)),filename=str(out/'event.csv'))
        if a.owner_ode:
            for e in list(scene):
                if e.tag in ('ReGripBDFSolver','NewtonRaphsonSolver','ReGripMatrixLinearSystem','EigenSparseLU','FreeMotionAnimationLoop','BlockGaussSeidelConstraintSolver','LinearSolverConstraintCorrection','CollisionPipeline','BruteForceBroadPhase','BVHNarrowPhase','MinProximityIntersection','CollisionResponse'):scene.remove(e)
            ET.SubElement(scene,'FilmSurfaceODESolver',name='ode',rayleighMass='2')
            ET.SubElement(scene,'DefaultAnimationLoop')
        path=out/'scene.scn';tree.write(path);write_json(out/'identity.json',identity)
        process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',path],out/'process',120);result['process']=process
        try:
            log=(out/'process/stdout.log').read_text()+(out/'process/stderr.log').read_text()
            if process['exit_code'] or '[ERROR]' in log:raise ValueError('actual engine/owner failure')
            rows=list(csv.DictReader((out/'event.csv.surface.csv').open()));states=list(csv.DictReader((out/'event.csv.states.csv').open()));actual=list(csv.DictReader((out/'film.csv').open()))
            if len(states)!=a.steps or len(actual)!=a.steps:raise ValueError('incomplete states')
            for s in states:
                for key,value in s.items():
                    numbers=value.split() if key in ('local_displacement','local_velocity') else [value]
                    if not numbers or not all(math.isfinite(float(v)) for v in numbers):raise ValueError('nonfinite/missing accepted '+key)
                if float(s['minimum_gap']) < -1e-10:raise ValueError('whole endpoint gap gate failed')
            if abs(float(states[-1]['time'])-a.duration)>1e-12:raise ValueError('wrong physical end time')
            matched=all(float(s['end_tension'])==float(r['T_per_rail']) for s,r in zip(states,actual))
            if not matched:raise ValueError('FF and owner shared end-time C2 mismatch')
            if a.mode=='impact' and not rows:raise ValueError('impact expected but not observed')
            result.update(status='PASS',rows=len(rows),minimum_gap=min(float(r['minimum_gap']) for r in states),control_end_exact=matched,events=rows)
        except (OSError,ValueError) as e:result['failure_reason']=str(e)
    write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('stages','events','process')}))
if __name__=='__main__':main()
