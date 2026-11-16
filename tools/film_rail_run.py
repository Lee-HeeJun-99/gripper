"""Actual experimental film + separate flexible rails + routed-tendon dynamics.
Not tapered geometry, jamming, free-object contact or qualified grasp.
"""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
from film_guarded_process import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--ramp-time',type=float,default=1.);p.add_argument('--release-begin',type=float,default=1.);p.add_argument('--release-end',type=float,default=2.);p.add_argument('--root-guide-second-order',action='store_true');p.add_argument('--reuse-lift',action='store_true');p.add_argument('--direct-visitor',action='store_true');p.add_argument('--cost-profile',action='store_true');p.add_argument('--guide-offset',type=float,default=.2);p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,default=20);p.add_argument('--duration',type=float,default=.2);p.add_argument('--tension',type=float,default=.001);p.add_argument('--reuse',help='Immutable compiled assembly campaign;do not rerun its unit tests');p.add_argument('--scheme',choices=['trapezoid','bdf2'],default='trapezoid');p.add_argument('--tangent-probe',action='store_true');p.add_argument('--native-opt',action='store_true');p.add_argument('--critical-window',action='store_true',help='Predeclared dt=.0025 before1s,.00015625 after1s;not CCD/retry');p.add_argument('--profile-source',help='Completed same-binary profile to bound a critical window');p.add_argument('--coarsen-release',action='store_true',help='Explicit growth-by-two transitions after1.5s;new numerical experiment');a=p.parse_args()
    if not 0<a.ramp_time<=a.release_begin<a.release_end<=12:raise ValueError('bounded control schedule')
    if not a.tag.replace('_','').isalnum() or not 1<=a.steps<=6400 or not 0<a.duration<=8 or not 0<=a.tension<=.02:raise ValueError('bounded prototype run')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);build=ROOT/'build'/('film_rail_'+a.tag)
    sources=list((ROOT/'models/film_rail_tendon').glob('*'))+list((ROOT/'models/film_shell').glob('*.h'))+list((ROOT/'tests').glob('test_film_rail*.cpp'))+[ROOT/'tools/film_rail_run.py',ROOT/'tools/film_guarded_process.py']
    hashes={str(f.relative_to(ROOT)):sha(f) for f in sources if f.is_file()}
    for f in sources:
        if f.is_file():destination=out/'sources'/f.relative_to(ROOT);destination.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,destination)
    stages={}
    high_resolution_budget=None
    if a.reuse:
        if not a.reuse.replace('_','').isalnum():raise ValueError('reuse tag')
        previous=ROOT/'results'/('autonomous_film_'+a.reuse);previous_identity=json.loads((previous/'identity.json').read_text());previous_summary=json.loads((previous/'summary.json').read_text())
        if previous_summary['status']!='PASS':raise RuntimeError('cannot reuse failed physics build')
        build=ROOT/'build'/('film_rail_'+a.reuse)
        if sha(build/'libReGripFilmRailTendon.so')!=previous_identity['binary_sha256']:raise RuntimeError('assembly binary changed')
        for rel,digest in previous_identity['sources'].items():
            if rel.startswith('models/') and sha(previous/'sources'/rel)!=digest:raise RuntimeError('archived assembly model drift')
    if a.steps>1000:
        if not a.reuse or not previous_identity.get('native_opt') or a.tension!=.0001 or a.duration!=4:raise ValueError('high-resolution authorization limited to profiled low-load family')
        benchmark_root=ROOT/'results/autonomous_film_20261116_rail_native_benchmark96';benchmark=json.loads((benchmark_root/'summary.json').read_text());profile_root=ROOT/'results/autonomous_film_20261116_rail_low84';profile=json.loads((profile_root/'summary.json').read_text())
        if benchmark['status']!='PASS' or profile['status']!='PASS':raise ValueError('missing compiler/physics profile evidence')
        estimate=profile['stages']['physics']['runtime_s']/profile['rows']*a.steps*benchmark['median_native_over_base']
        if a.scheme=='bdf2':
            profile_root=ROOT/'results/autonomous_film_20261116_attachment_bdf136';profile=json.loads((profile_root/'summary.json').read_text())
            if profile['status']!='PASS':raise ValueError('BDF2 full-window profile required')
            estimate=profile['process']['runtime_s']/profile['rows']*a.steps*1.3
        if estimate*1.05>480:raise ValueError('high-resolution projection exceeds480s')
        high_resolution_budget=dict(profile_sha256=sha(profile_root/'summary.json'),compiler_qualification_sha256=sha(benchmark_root/'summary.json'),projected_seconds=estimate,hard_seconds=480)
    commands=[] if a.reuse else [('configure',['cmake','-S',ROOT/'models/film_rail_tendon','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(ROOT/'.runtime/closure_sdk')]),('build',['cmake','--build',build,'-j2']),('kernel',[build/'test_film_rail_tendon']),('api',[build/'test_film_rail_tendon_api']),('mappings',[build/'test_film_rail_mappings']),('ldd',['ldd',build/'libReGripFilmRailTendon.so'])]
    for name,cmd in commands:
        if name=='configure':cmd.append('-DREGRIP_FILM_REUSE_LIFT='+('ON' if a.reuse_lift else 'OFF'))
        if name=='configure':cmd.append('-DREGRIP_FILM_DIRECT_VISITOR='+('ON' if a.direct_visitor else 'OFF'))
        if name=='configure':cmd.append('-DREGRIP_FILM_RAIL_NATIVE='+('ON' if a.native_opt else 'OFF'))
        stages[name]=logged(cmd,out/name,180)
        if stages[name]['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,stages=stages));return
    if hashes!={str(f.relative_to(ROOT)):sha(f) for f in sources if f.is_file()}:raise RuntimeError('source drift during build')
    nx=21;layout=[(0,5,24.,.05,0.,0.),(5*nx,3,1.322329862910148,.1,0.,-.075),(8*nx,3,1.322329862910148,.1,24-1.322329862910148,-.075)]
    # Compute width from the same declared equal-volume constraint, not a fit.
    rail_w=(439.3397917746089/3-100*24*.05)/(2*100*.1)
    layout=[(0,5,24.,.05,0.,0.),(5*nx,3,rail_w,.1,0.,-.075),(8*nx,3,rail_w,.1,24-rail_w,-.075)]
    n=11*nx;zero=' '.join(['0 0 0']*n);rest=[];triangles=[];masses=[];fixed=[];redundant=[]
    volume=439.3397917746089/3
    for offset,ny,width,thickness,y,z in layout:
        fixed.extend(range(offset,offset+ny));redundant.extend(range(offset+ny,offset+2*ny))
        for i in range(nx):
            for j in range(ny):rest.extend([100*i/(nx-1),y+width*j/(ny-1),z]);masses.append(1e-6*(100*width*thickness/volume)/(nx*ny))
        for i in range(nx-1):
            for j in range(ny-1):triangles.extend([offset+i*ny+j,offset+(i+1)*ny+j,offset+i*ny+j+1,offset+(i+1)*ny+j+1,offset+i*ny+j+1,offset+(i+1)*ny+j])
    sdk=ROOT/'build/grasp_20261115/sofa_patched';engine=ROOT/'build/film_shell_20261116_trapezoid_reference69/libReGripFilmShell.so';plugin=build/'libReGripFilmRailTendon.so';dt=a.duration/a.steps
    steps=a.steps;window=None
    clock_plugin=ROOT/'build/autonomous_20261116_event_clock_a01/v1/libReGripEventStepClock.so'
    if a.critical_window:
        if not a.reuse or a.scheme!='bdf2' or not 1<a.duration<=2:raise ValueError('critical window restricted to bounded BDF2 assembly research')
        dt=.0025;steps=400+round((a.duration-1)/(.0025/16))
        if abs(1+(steps-400)*dt/16-a.duration)>1e-12:raise ValueError('critical time lattice')
        if a.coarsen_release:
            if a.duration!=2:raise ValueError('coarsened release requires2s')
            steps=4401
        profile_case=a.profile_source or a.reuse
        if not profile_case.replace('_','').isalnum():raise ValueError('profile tag')
        profile_root=ROOT/'results'/('autonomous_film_'+profile_case);profile=json.loads((profile_root/'summary.json').read_text());profile_identity=json.loads((profile_root/'identity.json').read_text())
        if profile['status']!='PASS' or profile_identity['binary_sha256']!=sha(plugin):raise ValueError('invalid profile binary/status')
        estimate=profile['stages']['physics']['runtime_s']/profile['rows']*steps
        if estimate*1.1>480:raise ValueError('critical window exceeds profiled480s budget')
        window=dict(epoch=1,base_dt=dt,divisor=16,steps=steps,projected_seconds=estimate,profile_source=profile_case,profile_sha256=sha(profile_root/'summary.json'),clock_sha256=sha(clock_plugin),coarsen_release=a.coarsen_release)
    engine_manifest=json.loads((ROOT/'results/autonomous_film_20261116_trapezoid_reference69/compiled.json').read_text())
    if sha(engine)!=engine_manifest['binary_sha256']:raise RuntimeError('integration plugin drift')
    case=out/'1';case.mkdir();join=lambda x:' '.join(map(str,x))
    scene=f'''<Node name="experimental_film_rail" dt="{dt:.17g}" gravity="0 0 0"><RequiredPlugin pluginName="{engine}"/><RequiredPlugin pluginName="Sofa.Component.AnimationLoop Sofa.Component.StateContainer Sofa.Component.Mass Sofa.Component.ODESolver.Backward Sofa.Component.LinearSolver.Direct Sofa.Component.Constraint.Projective Sofa.Component.Topology.Container.Dynamic"/><DefaultAnimationLoop/><NewtonRaphsonSolver name="newton" maxNbIterationsNewton="30" maxNbIterationsLineSearch="12" absoluteResidualStoppingThreshold="1e-15" relativeInitialStoppingThreshold="1e-7" relativeSuccessiveStoppingThreshold="0"/><ReGripBDFSolver order="1" theta=".5" newtonSolver="@newton" rayleighMass="2" rayleighStiffness="0" profileFilename="{case/'profile.csv'}"/><ReGripMatrixLinearSystem name="system"/><EigenSparseLU linearSystem="@system" template="CompressedRowSparseMatrixd"/><MechanicalObject name="dofs" template="Vec3d" position="{zero}"/><FixedProjectiveConstraint indices="{join(fixed)}"/><PartialFixedProjectiveConstraint indices="{join(redundant)}" fixedDirections="0 0 1"/><Node name="assembly"><MechanicalObject name="surface" template="Vec3d" position="{zero}"/><DiagonalMass vertexMass="{join(masses)}" topology="@actual/topology" geometryState="@actual/world"/><FilmRailTendon nx="21" maximumTension="{a.tension:.17g}" rampTime="1" releaseBegin="1" releaseEnd="2" bondStiffness=".001" guideOffset=".2" filename="{case/'journal.csv'}"/><FilmAssemblyRootMapping nx="21" input="@../dofs" output="@surface" mapMasses="1"/><Node name="actual"><MechanicalObject name="world" template="Vec3d" position="{join(rest)}" rest_position="{join(rest)}"/><TriangleSetTopologyContainer name="topology" nbPoints="{n}" position="{join(rest)}" triangles="{join(triangles)}"/><FilmAssemblyWorldMapping nx="21" input="@../surface" output="@world" mapMasses="0"/></Node></Node></Node>'''
    (case/'scene.scn').write_text(scene)
    scene=scene.replace('rampTime="1" releaseBegin="1" releaseEnd="2"',f'rampTime="{a.ramp_time:.17g}" releaseBegin="{a.release_begin:.17g}" releaseEnd="{a.release_end:.17g}"')
    scene=scene.replace('guideOffset=".2"',f'guideOffset="{a.guide_offset:.17g}"')
    if a.root_guide_second_order:scene=scene.replace('<FilmRailTendon ','<FilmRailTendon rootGuideSecondOrder="1" ')
    if a.cost_profile:scene=scene.replace('<FilmRailTendon ',f'<FilmRailTendon costProfileFilename="{case/"cost.csv"}" ')
    (case/'scene.scn').write_text(scene)
    if a.tangent_probe:scene=scene.replace('<ReGripBDFSolver ',f'<ReGripBDFSolver tangentProbeFilename="{case/"tangent"}" ');(case/'scene.scn').write_text(scene)
    if a.scheme=='bdf2':scene=scene.replace('order="1" theta=".5"','order="2" theta="1"');(case/'scene.scn').write_text(scene)
    if a.critical_window:
        epochs='0 1 1.5 1.5003125 2' if a.coarsen_release else '0 1';divisors='1 16 8 4 4' if a.coarsen_release else '1 16'
        scene=scene.replace('<DefaultAnimationLoop/>',f'<RequiredPlugin pluginName="{clock_plugin}"/><EventStepClockAnimationLoop filename="{case/"clock.csv"}" eventTimes="{epochs}" stepDivisors="{divisors}"/>').replace('<ReGripBDFSolver ','<ReGripBDFSolver variableStep="1" ')
        (case/'scene.scn').write_text(scene)
    write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=hashes,binary_sha256=sha(plugin),integration_binary_sha256=sha(engine),driver_sha256=sha(sdk/'bin/graph_probe'),scene_sha256=sha(case/'scene.scn'),
        reused_build=a.reuse,binary_source_identity=previous_identity if a.reuse else None,native_opt=previous_identity.get('native_opt',False) if a.reuse else a.native_opt,critical_window=window,high_resolution_budget=high_resolution_budget,
        geometry='rectangular equal-core-volume experimental single finger;not tapered concept_v2',core_volume_mm3=volume,total_model_mass=1e-6,layout=layout,material=dict(E=250,nu=0,measured=False),dt=dt,tension_per_rail=a.tension,bond_stiffness=.001,guide_offset=a.guide_offset,cost_profile=a.cost_profile,direct_visitor=a.direct_visitor,reuse_lift=a.reuse_lift,root_guide_second_order=a.root_guide_second_order,control_schedule=dict(ramp=a.ramp_time,release_begin=a.release_begin,release_end=a.release_end),
        force_model='five objective point attachments per rail;five eccentric actual-normal-offset guides;independent flexible strips',energy_scope='tendon generator is not cable stored energy;mechanical tendon work is separately approximated',command=__import__('sys').argv))
    stages['physics']=guarded([sdk/'bin/graph_probe',sdk,case/'scene.scn',str(steps),'0',plugin],case/'process',480)
    log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text();rows=list(csv.DictReader((case/'journal.csv').open())) if (case/'journal.csv').exists() else []
    finite=all(__import__('math').isfinite(float(v)) for r in rows for k,v in r.items() if k!='x') and all(__import__('math').isfinite(float(v)) for r in rows for v in r['x'].split())
    status='PASS' if stages['physics']['exit_code']==0 and len(rows)==steps and '[ERROR]' not in log and 'Unused Attribute' not in log and finite and 'Newton-Raphson method failed to converge' not in log else 'FAIL'
    write_json(out/'summary.json',dict(status=status,scope='experimental assembly execution only;NOT convergence/contact/grasp approval',stages=stages,rows=len(rows),expected_rows=steps,newton_failed_steps=log.count('Newton-Raphson method failed to converge'),finite=finite,last={k:v for k,v in rows[-1].items() if k!='x'} if rows else None,contact='NOT RUN',grasp='NOT RUN',coupled_energy='BLOCKED'))
    print(json.dumps(dict(status=status,rows=len(rows),last={k:v for k,v in rows[-1].items() if k!='x'} if rows else None)))

if __name__=='__main__':main()
