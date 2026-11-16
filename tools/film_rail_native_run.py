"""Experimental fixed-sphere native contact; not free-object grasp certification."""
import argparse,csv,json,subprocess,shutil,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
from film_guarded_process import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--coupled-order',type=int,choices=(1,2),default=1);p.add_argument('--coupled-profile');p.add_argument('--general-coupled',action='store_true');p.add_argument('--coupled-correction',action='store_true');p.add_argument('--momentum-journal',action='store_true');p.add_argument('--cylinder-segments',type=int,choices=[32,64,128,256],default=64);p.add_argument('--object-shape',choices=['sphere','cylinder-mesh'],default='sphere');p.add_argument('--guide-intervals',type=int,choices=[4,10],default=4);p.add_argument('--state-jacobians',action='store_true');p.add_argument('--reuse-lift',action='store_true');p.add_argument('--contact-rows',action='store_true');p.add_argument('--assembly-case');p.add_argument('--slow-profile');p.add_argument('--ramp-time',type=float,default=1.);p.add_argument('--release-begin',type=float,default=1.);p.add_argument('--release-end',type=float,default=2.);p.add_argument('--fresh-assembly',action='store_true');p.add_argument('--guide-offset',type=float,default=.2);p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,default=20);p.add_argument('--duration',type=float,default=.2);p.add_argument('--tension',type=float,default=.0001);p.add_argument('--free-motion',action='store_true');p.add_argument('--sphere',action='store_true');p.add_argument('--sphere-x',type=float,default=75);p.add_argument('--installed-sdk',action='store_true');p.add_argument('--reuse-installed',help='Exclusive installed-ABI build tag');a=p.parse_args()
    if a.general_coupled:a.coupled_correction=True
    if a.coupled_order==2 and (not a.general_coupled or a.steps>160 or a.duration>.2):raise ValueError("BDF2 accepted-stage prototype limited to160 steps/.2s until profiled")
    if not a.tag.replace('_','').isalnum() or not 0<a.steps<=800 or not 0<a.duration<=8 or not 0<=a.tension<=.001 or a.sphere and not a.free_motion:raise ValueError('bounded fixed-object experiment')
    if not 0<a.ramp_time<=a.release_begin<a.release_end<=12:raise ValueError('bounded schedule')
    if a.coupled_correction and ((not a.fresh_assembly and not a.assembly_case) or not a.free_motion or not a.sphere or (a.object_shape!='sphere' and not a.general_coupled) or a.steps>(800 if a.general_coupled else 160) or a.duration>(4 if a.general_coupled else .2)):raise ValueError('bounded source-compatible coupled fixed-object BE experiment')
    coupled_budget=None
    if a.general_coupled and (a.steps>160 or a.duration>.2):
        if a.coupled_profile not in ('20261117_general_coupled218','20261117_coupled_cylinder235'):raise ValueError('coupled extension needs actual measured profile')
        prof=ROOT/'results'/('autonomous_film_'+a.coupled_profile);s=json.loads((prof/'summary.json').read_text())
        if s['status']!='PASS':raise ValueError('incomplete coupled profile')
        margin=3
        if a.coupled_profile=='20261117_coupled_cylinder235':
            if (a.object_shape,a.sphere_x,a.guide_offset,a.guide_intervals,a.cylinder_segments,a.duration,a.ramp_time,a.release_begin,a.release_end)!=('cylinder-mesh',75,5,4,64,4,4,6,8):raise ValueError('full-contact profile only applies to this geometry/closing window')
            if a.tension==.0003:margin=2 # full same-physics window, not short onset extrapolation
            elif a.tension==.001 and a.steps<=400:margin=3 # bounded separate design-capacity probe;NOT same-physics convergence
            else:raise ValueError('unprofiled tension/step count for full-contact projection')
        elif a.steps>400:raise ValueError('more than400 coupled steps requires the full-contact profile')
        estimate=s['stages']['physics']['runtime_s']/s['rows']*a.steps*margin
        if estimate>480:raise ValueError('coupled projection exceeds480s')
        coupled_budget=dict(profile_sha256=sha(prof/'summary.json'),projected_seconds=estimate,active_fraction_margin=margin,hard_seconds=480)
    budget=None
    if a.steps>400 or a.duration>2:
        design_capacity=a.general_coupled and a.coupled_profile=='20261117_coupled_cylinder235' and a.tension==.001 and a.steps<=400
        if a.slow_profile!='20261116_route_slowarm164' or (a.tension not in (.0001,.0003) and not design_capacity) or a.guide_offset not in (2,5) or (a.ramp_time,a.release_begin,a.release_end)!=(4,6,8):raise ValueError('long prototype trial requires measured slow-route profile and bounded variant')
        profile_root=ROOT/'results'/('autonomous_film_'+a.slow_profile);profile=json.loads((profile_root/'summary.json').read_text())
        if profile['status']!='PASS':raise ValueError('incomplete profile')
        estimate=profile['stages']['physics']['runtime_s']/profile['rows']*a.steps*3
        if estimate>480:raise ValueError('projected contact trial exceeds480s')
        budget=dict(profile_sha256=sha(profile_root/'summary.json'),projected_seconds=estimate,contact_cost_margin=3,tension_variant=a.tension,guide_offset_variant=a.guide_offset,hard_seconds=480)
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
        if a.fresh_assembly:
            new_assembly=ROOT/'build'/('film_native_assembly_'+a.tag)
            for key,cmd in [('configure',['cmake','-S',ROOT/'models/film_rail_tendon','-B',new_assembly,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(prefix),'-DREGRIP_FILM_RAIL_NATIVE=ON','-DREGRIP_FILM_REUSE_LIFT='+('ON' if a.reuse_lift else 'OFF')]),('build',['cmake','--build',new_assembly,'-j2','--target','ReGripFilmRailTendon','test_film_rail_tendon_api'])]:
                stages['fresh_assembly_'+key]=logged(cmd,out/('fresh_assembly_'+key),180)
                if stages['fresh_assembly_'+key]['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stages=stages));return
            assembly=new_assembly/'libReGripFilmRailTendon.so'
        if a.assembly_case:
            if a.fresh_assembly or not a.assembly_case.replace('_','').isalnum():raise ValueError('exclusive assembly reuse')
            assembly=ROOT/'build'/('film_native_assembly_'+a.assembly_case)/'libReGripFilmRailTendon.so'
            archive=json.loads((ROOT/'results'/('autonomous_film_'+a.assembly_case)/'identity.json').read_text())
            if sha(assembly)!=archive['assembly_sha256']:raise ValueError('reused installed assembly drift')
            if a.coupled_correction and not archive.get('coupled_correction'):raise ValueError('coupled model requires a qualified source-compatible assembly campaign')
        stages['assembly_api']=logged([assembly.parent/'test_film_rail_tendon_api'],out/'assembly_api',30)
        if a.guide_intervals==10:stages['distributed_api']=logged([assembly.parent/'test_film_rail_tendon_api','distributed'],out/'distributed_api',30)
    stages['factor_api']=logged([core/'test_film_native_be'],out/'factor_api',30)
    if any(s['exit_code'] for s in stages.values()):write_json(out/'summary.json',dict(status='FAIL',scope='API/build gate failed before dynamics',stages=stages));return
    build=ROOT/'build'/('film_native_'+a.tag)
    for key,cmd in [('configure',['cmake','-S',ROOT/'models/film_native_contact','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(prefix),'-DREGRIP_FILM_COUPLED='+('ON' if a.coupled_correction else 'OFF')]),('build',['cmake','--build',build,'-j2'])]:
        stages[key]=logged(cmd,out/key,180)
        if stages[key]['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=key,stages=stages));return
    if a.coupled_correction:
        stages['coupled_unit']=logged([build/'test_film_coupled_plane'],out/'coupled_unit',30)
        if a.general_coupled:stages['coupled_multi_unit']=logged([build/'test_film_coupled_contacts'],out/'coupled_multi_unit',30)
        if stages['coupled_unit']['exit_code'] or (a.general_coupled and stages['coupled_multi_unit']['exit_code']):write_json(out/'summary.json',dict(status='FAIL',stage='coupled_unit',stages=stages));return
    scene=ET.parse(ROOT/'results/autonomous_film_20261116_rail_native95/1/scene.scn');root=scene.getroot();root.set('dt',str(a.duration/a.steps));root.insert(0,ET.Element('RequiredPlugin',pluginName=str(assembly)))
    for plugin in root.findall('RequiredPlugin'):
        if 'libReGripFilmShell.so' in plugin.get('pluginName',''):plugin.set('pluginName',str(core/'libReGripFilmShell.so'))
    ode=root.find('ReGripBDFSolver');ode.set('name','ode');ode.set('order','1');ode.set('theta','1');ode.set('nativeConstraintBE','1' if a.free_motion else '0');ode.set('profileFilename',str(case/'profile.csv'))
    root.find('EigenSparseLU').set('name','linear')
    field=root.find("Node[@name='assembly']/FilmRailTendon");field.set('filename',str(case/'journal.csv'));field.set('maximumTension',str(a.tension));field.set('guideOffset',str(a.guide_offset));
    if a.guide_intervals!=4:field.set('guideIntervals',str(a.guide_intervals))
    field.set('rampTime',str(a.ramp_time));field.set('releaseBegin',str(a.release_begin));field.set('releaseEnd',str(a.release_end))
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
        if a.sphere and a.object_shape=='sphere':ET.SubElement(fixed,'SphereCollisionModel',template='Vec3d',radius='8',group='2',simulated='0',moving='0')
        if a.sphere and a.object_shape=='cylinder-mesh':
            from film_object_geometry import cylinder_y
            points,faces=cylinder_y((a.sphere_x,12.,-8.2),segments=a.cylinder_segments);mesh=ET.SubElement(fixed,'Node',name='collision_mesh');join=lambda rows:' '.join(str(v) for row in rows for v in row)
            ET.SubElement(mesh,'MechanicalObject',name='world',template='Vec3d',position=join(points));ET.SubElement(mesh,'TriangleSetTopologyContainer',name='topology',nbPoints=str(len(points)),position=join(points),triangles=join(faces));ET.SubElement(mesh,'FixedProjectiveConstraint',indices=' '.join(map(str,range(len(points)))))
            for kind in ('TriangleCollisionModel','LineCollisionModel','PointCollisionModel'):ET.SubElement(mesh,kind,group='2',simulated='0',moving='0')
        observer=build/'libReGripFilmNativeObserver.so';ET.SubElement(root,'RequiredPlugin',pluginName=str(observer));ET.SubElement(root,'FilmNativeObserver',body='@assembly/actual/world',sphere='@fixed/objectDOFs',solver='@constraints',filename=str(case/'contact.csv'),radius='8')
    if a.object_shape=='cylinder-mesh':root.find('FilmNativeObserver').set('objectShape','cylinderY')
    if a.coupled_correction:
        field.set('name','filmField')
        for required in list(root.findall('RequiredPlugin')):
            if required.get('pluginName')==str(observer):root.remove(required)
        root.insert(0,ET.Element('RequiredPlugin',pluginName=str(observer)))
        attributes=dict(name='coupled',root='@dofs',body='@assembly/actual/world',solver='@constraints',field='@assembly/filmField',filename=str(case/'coupled.csv'),rayleighMass='2')
        if a.general_coupled:root.find('FilmNativeObserver').set('impulseSource','@coupled')
        if a.general_coupled and a.object_shape=='sphere':attributes.update(sphereDiagnostic='1')
        if not a.general_coupled:attributes.update(sphere='@fixed/objectDOFs',radius='8',contactDistance='.01')
        if a.general_coupled:attributes['integrationOrder']=str(a.coupled_order)
        root.insert(2,ET.Element('FilmNativeCoupledCorrection' if a.general_coupled else 'FilmSphereCoupledCorrection',**attributes))
    if a.momentum_journal:root.find('FilmNativeObserver').set('momentumFilename',str(case/'momentum.csv'))
    if a.state_jacobians:root.find('FilmNativeObserver').set('stateJacobianFilename',str(case/'state_jacobians.csv'))
    if a.contact_rows:root.find('FilmNativeObserver').set('rowFilename',str(case/'contact_rows.csv'))
    scene.write(case/'scene.scn')
    sdk=ROOT/'build/grasp_20261115/sofa_patched';write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=__import__('sys').argv,sdk=str(prefix),scene_sha256=sha(case/'scene.scn'),core_sha256=sha(core/'libReGripFilmShell.so'),assembly_sha256=sha(assembly),observer_sha256=sha(build/'libReGripFilmNativeObserver.so'),cylinder_segments=a.cylinder_segments if a.object_shape=='cylinder-mesh' else None,constraint_impulse_source='coupled.constraintImpulses' if a.general_coupled else 'native_solver',accepted_integrator=('uniform BDF2 after BE startup' if a.coupled_order==2 else 'BE'),native_predictor_integrator='BE',coupled_budget=coupled_budget,general_coupled=a.general_coupled,coupled_correction=a.coupled_correction,object_shape=a.object_shape,sphere_center=[a.sphere_x,12,-8.2],radius=8,cylinder_height=40 if a.object_shape=='cylinder-mesh' else None,budget=budget,assembly_source_case=a.assembly_case,core_source_case=a.reuse_installed,scope='fixed sphere native constraint;mu=0;not SDF compliance,not free-object grasp'))
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
    ok=all(s['exit_code']==0 for s in stages.values()) and len(rows)==a.steps and '[ERROR]' not in log and 'Unused Attribute' not in log and 'Newton-Raphson method failed to converge' not in log
    finite=all(__import__('math').isfinite(float(v)) for r in rows for k,v in r.items() if k!='x') and all(__import__('math').isfinite(float(v)) for r in rows for v in r['x'].split())
    ok=ok and finite
    write_json(out/'summary.json',dict(status='PASS' if ok else 'FAIL',scope='execution only;contact/convergence not approved',finite=finite,stages=stages,rows=len(rows),last={k:v for k,v in rows[-1].items() if k!='x'} if rows else None))

if __name__=='__main__':main()
