"""Experimental fixed-sphere native contact; not free-object grasp certification."""
import argparse,csv,json,subprocess,shutil,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
from film_guarded_process import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,default=20);p.add_argument('--duration',type=float,default=.2);p.add_argument('--tension',type=float,default=.0001);p.add_argument('--free-motion',action='store_true');p.add_argument('--sphere',action='store_true');p.add_argument('--sphere-x',type=float,default=75);p.add_argument('--installed-sdk',action='store_true');p.add_argument('--reuse-installed',help='Exclusive installed-ABI build tag');a=p.parse_args()
    if not a.tag.replace('_','').isalnum() or not 0<a.steps<=400 or not 0<a.duration<=2 or not 0<=a.tension<=.001 or a.sphere and not a.free_motion:raise ValueError('bounded fixed-object experiment')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);case=out/'1';case.mkdir()
    core=ROOT/'build/film_shell_20261116_native_be_core105';assembly=ROOT/'build/film_rail_20261116_rail_native95/libReGripFilmRailTendon.so'
    identity=json.loads((ROOT/'results/autonomous_film_20261116_rail_native95/identity.json').read_text())
    if sha(assembly)!=identity['binary_sha256']:raise RuntimeError('archived assembly binary drift')
    stages={};prefix=ROOT/'.runtime/closure_sdk'
    if a.installed_sdk:
        prefix=__import__('pathlib').Path('/home/ubuntu/SOFA/v26.06.00');abi_build=ROOT/'build'/('film_native_installed_'+(a.reuse_installed or a.tag));core=abi_build/'core';assembly=abi_build/'assembly/libReGripFilmRailTendon.so'
        if not a.reuse_installed:
            for name,src,targets in [('core','film_shell',['ReGripFilmShell','test_film_native_be']),('assembly','film_rail_tendon',['ReGripFilmRailTendon','test_film_rail_tendon_api'])]:
                for key,cmd in [('configure',['cmake','-S',ROOT/'models'/src,'-B',abi_build/name,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(prefix),'-DREGRIP_FILM_RAIL_NATIVE=ON','-DREGRIP_FILM_NATIVE_OPT=ON']),('build',['cmake','--build',abi_build/name,'-j2','--target',*targets])]:
                    stages[name+'_'+key]=logged(cmd,out/(name+'_'+key),180)
                    if stages[name+'_'+key]['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name+'_'+key,stages=stages));return
        else:
            archived=json.loads((ROOT/'results'/('autonomous_film_'+a.reuse_installed)/'identity.json').read_text())
            if sha(core/'libReGripFilmShell.so')!=archived['core_sha256'] or sha(assembly)!=archived['assembly_sha256']:raise RuntimeError('installed ABI archive drift')
        stages['assembly_api']=logged([assembly.parent/'test_film_rail_tendon_api'],out/'assembly_api',30)
    stages['factor_api']=logged([core/'test_film_native_be'],out/'factor_api',30)
    build=ROOT/'build'/('film_native_'+a.tag)
    for key,cmd in [('configure',['cmake','-S',ROOT/'models/film_native_contact','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(prefix)]),('build',['cmake','--build',build,'-j2'])]:
        stages[key]=logged(cmd,out/key,180)
        if stages[key]['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=key,stages=stages));return
    scene=ET.parse(ROOT/'results/autonomous_film_20261116_rail_native95/1/scene.scn');root=scene.getroot();root.set('dt',str(a.duration/a.steps));root.insert(0,ET.Element('RequiredPlugin',pluginName=str(assembly)))
    for plugin in root.findall('RequiredPlugin'):
        if 'libReGripFilmShell.so' in plugin.get('pluginName',''):plugin.set('pluginName',str(core/'libReGripFilmShell.so'))
    ode=root.find('ReGripBDFSolver');ode.set('name','ode');ode.set('order','1');ode.set('theta','1');ode.set('nativeConstraintBE','1' if a.free_motion else '0');ode.set('profileFilename',str(case/'profile.csv'))
    root.find('EigenSparseLU').set('name','linear')
    field=root.find("Node[@name='assembly']/FilmRailTendon");field.set('filename',str(case/'journal.csv'));field.set('maximumTension',str(a.tension))
    if not 50<=a.sphere_x<=100:raise ValueError('declared sphere position')
    fixed=ET.SubElement(root,'Node',name='fixed');ET.SubElement(fixed,'MechanicalObject',name='objectDOFs',template='Vec3d',position=f'{a.sphere_x} 12 -8.2');ET.SubElement(fixed,'FixedProjectiveConstraint',indices='0')
    if a.free_motion:
        root.remove(root.find('DefaultAnimationLoop'));ET.SubElement(root,'FreeMotionAnimationLoop')
        root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.Collision.Detection.Algorithm Sofa.Component.Collision.Detection.Intersection Sofa.Component.Collision.Geometry Sofa.Component.Collision.Response.Contact Sofa.Component.Constraint.Lagrangian.Solver Sofa.Component.Constraint.Lagrangian.Correction'))
        ET.SubElement(root,'BlockGaussSeidelConstraintSolver',name='constraints',tolerance='1e-10',maxIterations='1000',computeConstraintForces='1')
        ET.SubElement(root,'LinearSolverConstraintCorrection',linearSolver='@linear',ODESolver='@ode')
        ET.SubElement(root,'CollisionPipeline',depth='10');ET.SubElement(root,'BruteForceBroadPhase');ET.SubElement(root,'BVHNarrowPhase');ET.SubElement(root,'MinProximityIntersection',alarmDistance='.05',contactDistance='.01',useSurfaceNormals='1');ET.SubElement(root,'CollisionResponse',response='FrictionContactConstraint',responseParams='mu=0')
        actual=root.find("Node[@name='assembly']/Node[@name='actual']")
        for kind in ('TriangleCollisionModel','LineCollisionModel','PointCollisionModel'):ET.SubElement(actual,kind,group='1')
        if a.sphere:ET.SubElement(fixed,'SphereCollisionModel',template='Vec3d',radius='8',group='2',simulated='0',moving='0')
        observer=build/'libReGripFilmNativeObserver.so';ET.SubElement(root,'RequiredPlugin',pluginName=str(observer));ET.SubElement(root,'FilmNativeObserver',body='@assembly/actual/world',sphere='@fixed/objectDOFs',solver='@constraints',filename=str(case/'contact.csv'),radius='8')
    scene.write(case/'scene.scn')
    sdk=ROOT/'build/grasp_20261115/sofa_patched';write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=__import__('sys').argv,sdk=str(prefix),scene_sha256=sha(case/'scene.scn'),core_sha256=sha(core/'libReGripFilmShell.so'),assembly_sha256=sha(assembly),observer_sha256=sha(build/'libReGripFilmNativeObserver.so'),scope='fixed sphere native constraint;mu=0;not SDF compliance,not free-object grasp'))
    for component in ('film_shell','film_rail_tendon','film_native_contact'):
        shutil.copytree(ROOT/'models'/component,out/'sources'/component)
    shutil.copy2(__file__,out/'sources/film_rail_native_run.py')
    for name,binary in [('core',core/'libReGripFilmShell.so'),('assembly',assembly),('observer',build/'libReGripFilmNativeObserver.so')]:
        stages[name+'_ldd']=logged(['ldd',binary],out/(name+'_ldd'),30)
        paths=(out/(name+'_ldd')/'stdout.log').read_text()
        if a.installed_sdk and any(str(ROOT/d) in paths for d in ('.runtime/closure_sdk','build/grasp_20261115/sofa_patched')):raise RuntimeError('mixed SOFA ABI')
    cmd=[prefix/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',case/'scene.scn'] if a.installed_sdk else [sdk/'bin/graph_probe',sdk,case/'scene.scn',str(a.steps),'0',assembly]
    stages['physics']=guarded(cmd,case/'process',480)
    rows=list(csv.DictReader((case/'journal.csv').open())) if (case/'journal.csv').exists() else [];log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
    ok=all(s['exit_code']==0 for s in stages.values()) and len(rows)==a.steps and '[ERROR]' not in log and 'Unused Attribute' not in log
    write_json(out/'summary.json',dict(status='PASS' if ok else 'FAIL',scope='execution only;contact/convergence not approved',stages=stages,rows=len(rows),last={k:v for k,v in rows[-1].items() if k!='x'} if rows else None))

if __name__=='__main__':main()
