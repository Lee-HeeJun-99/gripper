"""Distinct exact-slope boundary experiment. Never replaces old penalty raw."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
from film_nonlinear_assess import read,compare

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--nodes',type=int,choices=[11,21,41],default=21);p.add_argument('--steps',type=int,default=200);p.add_argument('--duration',type=float,default=20);p.add_argument('--time',action='store_true');p.add_argument('--newton-tolerance',type=float,default=1e-13);p.add_argument('--profile',action='store_true')
    p.add_argument('--plane',type=float,default=.1,help='Externally fixed stop z; moving it is a separate physical control')
    p.add_argument('--compact-membrane',action='store_true',help='Opt-in compile-time nine-DOF AD2;requires exact regression and wall-clock validation')
    p.add_argument('--tangent-probe',action='store_true',help='Public actual matrix and trial state, first two steps only')
    p.add_argument('--refresh-mapped-mass',action='store_true',help='Independent SDK linear-system adapter;refresh cached mapped mass MBK factor')
    p.add_argument('--endpoint-ramp',action='store_true',help='Query continuous ramp at actual end time, including variable steps')
    p.add_argument('--window',action='store_true',help='Explicit phase window at1.3s;fourfold dt refinement after epoch,not CCD')
    p.add_argument('--native-opt',action='store_true',help='Opt-in native film-only vectorization;no fast-math')
    p.add_argument('--cubic-slope',action='store_true',help='Independent cubic-exact derivative boundary;old mapping preserved')
    p.add_argument('--scheme',choices=['bdf2','trapezoid'],default='bdf2',help='Distinct integration experiment;explicit runtime XML')
    a=p.parse_args()
    if not a.tag.replace('_','').isalnum() or not 1<=a.steps<=2000 or not 0<a.duration<=20 or not __import__('math').isfinite(a.plane):raise ValueError('bounded campaign')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);build=ROOT/'build'/('film_shell_'+a.tag);sdk=ROOT/'build/grasp_20261115/sofa_patched'
    sources=list((ROOT/'models/film_shell').glob('*'))+list((ROOT/'tests').glob('test_film*.cpp'))+[ROOT/'tools/film_slope_run.py']
    hashes={str(s.relative_to(ROOT)):sha(s) for s in sources if s.is_file()}
    for s in sources:
        if s.is_file():dest=out/'sources'/s.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(s,dest)
    write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=hashes,boundary='EXPERIMENTAL hard root slope;not K=100 penalty benchmark',total_mass=1e-6,physical_parameters=dict(E=250,nu=0,width=24,length=100,thickness=.0610194155,plane=.1,kn=1e-5,tip_force=1e-6,ramp=10,rayleigh_mass=2),driver_sha256=sha(sdk/'bin/graph_probe')))
    stages={}
    identity_path=out/'identity.json'
    identity=json.loads(identity_path.read_text());identity['physical_parameters']['plane']=a.plane
    identity['command']=__import__('sys').argv
    identity['compact_membrane']=a.compact_membrane
    identity['native_opt']=a.native_opt
    identity['cubic_slope']=a.cubic_slope
    identity['scheme']=a.scheme
    clock_plugin=ROOT/'build/autonomous_20261116_event_clock_a01/v1/libReGripEventStepClock.so'
    if a.window:
        if a.duration!=2 or not a.refresh_mapped_mass:raise ValueError('window requires2s and refreshed mapped mass')
        benchmark=json.loads((ROOT/'results/autonomous_film_20261116_contact_6400_43/summary.json').read_text())
        estimate=benchmark['process']['runtime_s']/6400*(1.3+4*.7)/(a.duration/(a.steps*(4 if a.time else 1)))
        if benchmark['process_status']!='PASS' or estimate*1.05>480:raise ValueError('window run exceeds profiled480s budget')
        identity['window']=dict(epoch=1.3,divisor=4,projected_max_seconds=estimate,clock_plugin_sha256=sha(clock_plugin),kind='predeclared phase refinement;not contact event detection')
    write_json(identity_path,identity)
    commands=[('configure',['cmake','-S',ROOT/'models/film_shell','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(ROOT/'.runtime/closure_sdk')]),('build',['cmake','--build',build,'-j2'])]+[(name,[build/exe]) for name,exe in [('kernel','test_film_shell'),('api','test_film_shell_api'),('plane','test_film_plane'),('mapping','test_film_slope_mapping')]]
    for name,command in commands:
        if name=='configure':command.append('-DREGRIP_FILM_NATIVE_OPT='+('ON' if a.native_opt else 'OFF'))
        stages[name]=logged(command,out/name,180)
        if stages[name]['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage=name,stages=stages));return
    stages['compact']=logged([build/'test_film_compact'],out/'compact',180)
    if stages['compact']['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stage='compact',stages=stages));return
    stages['coefficients']=logged([build/'test_film_bdf_coefficients'],out/'coefficients',180)
    if stages['coefficients']['exit_code']:raise RuntimeError('BDF coefficient unit failure')
    stages['cubic_slope']=logged([build/'test_film_cubic_slope'],out/'cubic_slope',180)
    if stages['cubic_slope']['exit_code']:raise RuntimeError('cubic slope unit failure')
    if hashes!={str(s.relative_to(ROOT)):sha(s) for s in sources if s.is_file()}:raise RuntimeError('source changed during build')
    plugin=build/'libReGripFilmShell.so';write_json(out/'compiled.json',dict(binary_sha256=sha(plugin),sources=hashes))
    rows={}
    for multiple in ([1,2,4] if a.time else [1]):
        case=out/str(multiple);case.mkdir();steps=a.steps*multiple;dt=a.duration/steps;n=a.nodes*5;zero=' '.join(['0 0 0']*n);tip=' '.join(map(str,range(n-5,n)))
        profile=f' profileFilename="{case/"profile.csv"}"' if a.profile else ''
        scene=f'''<Node name="exact_slope" dt="{dt}" gravity="0 0 0"><RequiredPlugin pluginName="Sofa.Component.AnimationLoop Sofa.Component.StateContainer Sofa.Component.Mass Sofa.Component.ODESolver.Backward Sofa.Component.LinearSolver.Direct Sofa.Component.Constraint.Projective Sofa.Component.MechanicalLoad"/><DefaultAnimationLoop/><NewtonRaphsonSolver name="newton" maxNbIterationsNewton="30" maxNbIterationsLineSearch="12" absoluteResidualStoppingThreshold="{a.newton_tolerance}" relativeInitialStoppingThreshold="1e-7" relativeSuccessiveStoppingThreshold="0"/><ReGripBDFSolver order="2" theta="1" newtonSolver="@newton" rayleighMass="2" rayleighStiffness="0"{profile}/><EigenSparseLU template="CompressedRowSparseMatrixd"/><MechanicalObject name="dofs" template="Vec3d" position="{zero}"/><FixedProjectiveConstraint indices="0 1 2 3 4"/><PartialFixedProjectiveConstraint indices="5 6 7 8 9" fixedDirections="0 0 1"/><Node name="film"><MechanicalObject name="surface" template="Vec3d" position="{zero}"/><UniformMass totalMass=".000001"/><FilmShell nx="{a.nodes}" ny="5" length="100" width="24" young="250" poisson="0" thickness=".0610194155" displacementDofs="1" slopeMapped="1" slopeFixture="0" observedTipForce=".000001" plane=".1" contactStiffness=".00001" filename="{case/'journal.csv'}"/><LinearForceField points="{tip}" times="{-dt} {10-dt} {20-dt}" forces="0 0 0 0 0 .0000002 0 0 .0000002"/><FilmSlopeMapping input="@../dofs" output="@surface" ny="5" mapMasses="1"/></Node></Node>'''
        scene=scene.replace('plane=".1"',f'plane="{a.plane:.17g}"')
        scene=scene.replace('<FilmShell ',f'<FilmShell compactMembrane="{int(a.compact_membrane)}" ')
        if a.tangent_probe:scene=scene.replace('<ReGripBDFSolver ',f'<ReGripBDFSolver tangentProbeFilename="{case/"tangent"}" ')
        if a.refresh_mapped_mass:scene=scene.replace('<EigenSparseLU ', '<ReGripMatrixLinearSystem name="refreshedSystem"/><EigenSparseLU linearSystem="@refreshedSystem" ')
        if a.endpoint_ramp or a.window:
            scene=__import__('re').sub(r'<LinearForceField [^>]*/>','<FilmRampLoad ny="5" totalForce=".000001" rampTime="10"/>',scene)
        if a.window:
            if abs(1.3/dt-round(1.3/dt))>1e-8 or abs(.7/(dt/4)-round(.7/(dt/4)))>1e-8:raise ValueError('phase not on time lattice')
            steps=round(1.3/dt)+round(.7/(dt/4))
            scene=scene.replace('<DefaultAnimationLoop/>',f'<RequiredPlugin pluginName="{clock_plugin}"/><EventStepClockAnimationLoop filename="{case/"clock.csv"}" eventTimes="0 1.3" stepDivisors="1 4"/>')
            scene=scene.replace('<ReGripBDFSolver ', '<ReGripBDFSolver variableStep="1" ')
        if a.cubic_slope:
            if a.tangent_probe:raise ValueError('cubic mapped tangent diagnostic not yet generalized;do not use old diagonal-mass checker')
            scene=scene.replace('<FilmSlopeMapping ', '<FilmCubicSlopeMapping ').replace('<FilmShell ', '<FilmShell cubicSlopeMapped="1" ')
        if a.scheme=='trapezoid':scene=scene.replace('order="2" theta="1"','order="1" theta=".5"')
        if f'plane="{a.plane:.17g}"' not in scene:raise RuntimeError('plane option not applied to actual XML')
        (case/'scene.scn').write_text(scene);stages[str(multiple)]=logged([sdk/'bin/graph_probe',sdk,case/'scene.scn',str(steps),'0',plugin],case/'process',480)
        log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
        if stages[str(multiple)]['exit_code'] or '[ERROR]' in log or 'Unused Attribute' in log:continue
        records=list(csv.DictReader((case/'journal.csv').open()))
        if len(records)!=steps:continue
        last=records[-1];rows[multiple]=dict(steps=steps,dt=dt,tip_z=float(last['tip_z']),U=float(last['U']),contact_area=float(last['contact_area']),normal_force=float(last['normal_force']),relative_static_residual=float(last['free_force'])/(1e-6/5**.5),newton_failed_steps=log.count('Newton-Raphson method failed to converge'))
    pairs={f'{i}:{j}':compare(read(out/str(i)),read(out/str(j)),.001) for i,j in ((1,2),(1,4),(2,4)) if i in rows and j in rows}
    result=dict(scope='hard-slope boundary,not same finite penalty model',rows=rows,stages=stages,process_status='PASS' if len(rows)==(3 if a.time else 1) else 'FAIL',trajectory_comparisons=pairs,time_status='NOT RUN' if not a.time else ('PASS' if len(pairs)==3 and all(v['trajectory_status']=='PASS' for pair in pairs.values() for v in pair.values()) and not any(r['newton_failed_steps'] for r in rows.values()) else 'FAIL'),full_grasp='NOT RUN')
    write_json(out/'summary.json',result);print(json.dumps(dict(out=str(out),rows=rows,time_status=result['time_status'])))

if __name__=='__main__':main()
