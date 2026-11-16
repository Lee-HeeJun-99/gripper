"""Bounded film ROM mechanics; not a grasp or laminated-jamming certificate."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,default=200);p.add_argument('--nodes',type=int,default=11,choices=[11,21,41]);p.add_argument('--solver',choices=['euler','static','bdf','regrip'],default='euler');p.add_argument('--plane',type=float);p.add_argument('--width',type=float,default=10);p.add_argument('--thickness',type=float,default=.2);p.add_argument('--load',type=float,default=1e-7);p.add_argument('--single',action='store_true');p.add_argument('--fixture',type=float,default=0);p.add_argument('--ramp',type=float,default=0);p.add_argument('--displacement',action='store_true');p.add_argument('--matrix-probe',action='store_true');p.add_argument('--duration',type=float,default=20);p.add_argument('--newton-tolerance',type=float,default=1e-10);p.add_argument('--theta',type=float,choices=[.5,1.],default=1.);p.add_argument('--endpoint-load',action='store_true');p.add_argument('--order',type=int,choices=[1,2],default=1);a=p.parse_args()
 if not(a.width>0 and a.thickness>0 and a.load>0):raise ValueError('positive film/load')
 if not a.tag.replace('_','').isalnum()or not 1<=a.steps<=2000:raise ValueError('bounded campaign')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);build=ROOT/'build'/('film_shell_'+a.tag);sdk=ROOT/'build/grasp_20261115/sofa_patched'
 sources=list((ROOT/'models/film_shell').glob('*'))+list((ROOT/'tests').glob('test_film*.cpp'))+list((ROOT/'diagnostics/film_shell').glob('*.cpp'))+[ROOT/'tools/film_shell_run.py']
 before={str(p.relative_to(ROOT)):sha(p)for p in sources};write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=before,driver=sha(sdk/'bin/graph_probe'),assumptions=dict(E=250,nu=0,thickness=a.thickness,length=100,width=a.width,total_mass=1e-6,tip_force=a.load,boundary=('one fixed row plus explicit slope fixture'if a.fixture>0 else'two fixed rows;mesh-dependent effective clamp'),slope_fixture=a.fixture,scope='single film,not laminate/grasp')))
 for p in sources:
  q=out/'sources'/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 stages={}
 for name,cmd in [('configure',['cmake','-S',ROOT/'models/film_shell','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(ROOT/'.runtime/closure_sdk')]),('build',['cmake','--build',build,'-j2']),('kernel',[build/'test_film_shell']),('api',[build/'test_film_shell_api']),('plane_unit',[build/'test_film_plane']),('static',[build/'film_static'])]:
  stages[name]=logged(cmd,out/name,180)
  if stages[name]['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stages=stages));return
 if before!={str(p.relative_to(ROOT)):sha(p)for p in sources}:raise RuntimeError('source mutation while compiling')
 plugin=build/'libReGripFilmShell.so';write_json(out/'compiled.json',dict(sources=before,binary_sha256=sha(plugin)))
 rows={}
 for multiple in ([1]if a.single else[1,2,4]):
  case=out/str(multiple);case.mkdir();steps=a.steps*multiple;dt=a.duration/steps;ny=5;nx=a.nodes
  position=' '.join(f'{100*i/(nx-1)} {a.width*j/(ny-1)} 0'for i in range(nx)for j in range(ny))
  if a.displacement:position=' '.join(['0 0 0']*(nx*ny))
  solver='<EulerImplicitSolver rayleighMass="2" rayleighStiffness="0"/>'if a.solver=='euler'else'<NewtonRaphsonSolver name="newton" maxNbIterationsNewton="30" maxNbIterationsLineSearch="12" absoluteResidualStoppingThreshold="1e-10" relativeInitialStoppingThreshold="1e-7" relativeSuccessiveStoppingThreshold="0"/><StaticSolver newtonSolver="@newton"/>'
  if a.solver in ('bdf','regrip'):solver=solver.replace('<StaticSolver newtonSolver="@newton"/>','<BDFOdeSolver order="1" newtonSolver="@newton" rayleighMass="2" rayleighStiffness="0"/>')
  contact=''if a.plane is None else f'plane="{a.plane}" contactStiffness=".00001"'
  scene=f'''<Node name="film_cantilever" dt="{dt}" gravity="0 0 0"><RequiredPlugin pluginName="Sofa.Component.AnimationLoop Sofa.Component.StateContainer Sofa.Component.Mass Sofa.Component.ODESolver.Backward Sofa.Component.LinearSolver.Direct Sofa.Component.Constraint.Projective Sofa.Component.MechanicalLoad"/><DefaultAnimationLoop/>{solver}<EigenSparseLU template="CompressedRowSparseMatrixd"/><MechanicalObject template="Vec3d" position="{position}"/><UniformMass totalMass=".000001"/><FilmShell nx="{nx}" ny="{ny}" length="100" width="{a.width}" young="250" poisson="0" thickness="{a.thickness}" observedTipForce="{a.load}" slopeFixture="{a.fixture}" displacementDofs="{int(a.displacement)}" matrixProbe="{int(a.matrix_probe)}" {contact} filename="{case/'journal.csv'}"/><FixedProjectiveConstraint indices="{' '.join(map(str,range((1 if a.fixture>0 else 2)*ny)))}"/><ConstantForceField indices="{' '.join(map(str,range((nx-1)*ny,nx*ny)))}" forces="{' '.join([f'0 0 {a.load/ny}']*ny)}"/></Node>'''
  if a.solver=='regrip':scene=scene.replace('<BDFOdeSolver order="1" ',f'<ReGripBDFSolver order="{a.order}" theta="{a.theta}" ')
  solver_tolerance='absoluteResidualStoppingThreshold="1e-10"'
  scene=scene.replace(solver_tolerance,f'absoluteResidualStoppingThreshold="{a.newton_tolerance}"')
  actual_solver={'euler':'EulerImplicitSolver','static':'StaticSolver','bdf':'BDFOdeSolver','regrip':'ReGripBDFSolver'}[a.solver]
  if f'<{actual_solver} ' not in scene:raise RuntimeError('requested/actual ODE solver mismatch')
  write_json(case/'actual_solver.json',dict(requested=a.solver,xml_component=actual_solver))
  if a.ramp>0:
   start=scene.index('<ConstantForceField');end=scene.index('/>',start)+2
   scene=scene[:start]+f'<LinearForceField points="{" ".join(map(str,range((nx-1)*ny,nx*ny)))}" times="0 {a.ramp} 20" forces="0 0 0 0 0 {a.load/ny} 0 0 {a.load/ny}"/>'+scene[end:]
  if a.endpoint_load and a.ramp>0:scene=scene.replace(f'times="0 {a.ramp} 20"',f'times="{-dt} {a.ramp-dt} {20-dt}"')
  write_json(case/'sampling.json',dict(theta=a.theta if a.solver=='regrip' else None,load_time='step end' if a.endpoint_load else 'step start',duration=a.duration,dt=dt))
  (case/'scene.scn').write_text(scene);stages[str(multiple)]=logged([sdk/'bin/graph_probe',sdk,case/'scene.scn',str(steps),'0',plugin],case/'process',480)
  log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
  if stages[str(multiple)]['exit_code']or '[ERROR]'in log or 'Unused Attribute'in log:continue
  records=list(csv.DictReader((case/'journal.csv').open()))
  if len(records)!=steps:continue
  rows[multiple]=dict(steps=steps,dt=dt,tip_z=float(records[-1]['tip_z']),speed=float(records[-1]['max_speed']),U=float(records[-1]['U']),relative_static_residual=float(records[-1]['free_force'])/(a.load/(ny**.5)),contact_area=float(records[-1]['contact_area']),normal_force=float(records[-1]['normal_force']))
 comparisons=[dict(pair=[c,f],relative=abs(rows[c]['tip_z']-rows[f]['tip_z'])/abs(rows[f]['tip_z']))for c,f in [(1,2),(1,4),(2,4)]if c in rows and f in rows]
 summary=dict(equilibrium_status='PASS'if len(rows)==(1 if a.single else 3) and all(v['relative_static_residual']<.001 for v in rows.values())else'FAIL',solver=a.solver,plane=a.plane,process_status='PASS'if len(rows)==(1 if a.single else 3) else'FAIL',time_status='NOT RUN (static solve)'if a.solver=='static'else('PASS'if len(comparisons)==3 and all(v['relative']<=.001 for v in comparisons)else'FAIL'),rows=rows,comparisons=comparisons,stages=stages,full_grasp='NOT RUN',jamming='NOT RUN')
 summary['endpoint_time_status']=summary['time_status']
 summary['endpoint_time_scope']='final tip only; not whole-trajectory convergence'
 failed={str(i):(out/str(i)/'process/stdout.log').read_text().count('Newton-Raphson method failed to converge') for i in rows}
 summary['newton_failed_steps']=failed
 if a.solver!='static':
  from film_nonlinear_assess import read,compare
  full={f'{c}:{f}':compare(read(out/str(c)),read(out/str(f)),.001) for c,f in ((1,2),(1,4),(2,4)) if c in rows and f in rows}
  summary['trajectory_comparisons']=full
  summary['time_status']='NOT RUN' if a.single else ('PASS' if len(full)==3 and not any(failed.values()) and all(m['trajectory_status']=='PASS' for pair in full.values() for m in pair.values()) else 'FAIL')
 write_json(out/'summary.json',summary);print(json.dumps(dict(out=str(out),rows=rows,comparisons=comparisons,status=summary['time_status'])))
if __name__=='__main__':main()
