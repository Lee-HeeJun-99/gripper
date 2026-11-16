"""New active-contact path benchmark;never a full-grasp qualification."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--substeps',type=int,default=32,choices=[32,128,512]);a=p.parse_args()
 if not a.tag.replace('_','').isalnum():raise ValueError('unique tag')
 out=ROOT/'results'/('vector_history_sphere_event_'+a.tag);out.mkdir(exist_ok=False);build=ROOT/'build'/('vector_history_sphere_event_'+a.tag)
 sdk=ROOT/'build/grasp_20261115/sofa_patched';sources=list((ROOT/'models').rglob('*.h'))+[ROOT/'models/general_vector_history/SphereEventBenchmark.cpp',ROOT/'models/sphere_event_benchmark/CMakeLists.txt',ROOT/'tests/test_sphere_event_api.cpp',ROOT/'tools/sphere_event_run.py'];before={str(p.relative_to(ROOT)):sha(p)for p in sources}
 write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),sources=before,driver_sha256=sha(sdk/'bin/graph_probe'),scope='one-point fixed sphere chord Birth/Death;not CurvedContact/free-object/grasp'))
 for p in sources:
  q=out/'sources'/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 stages={}
 for name,cmd in [('configure',['cmake','-S',ROOT/'models/sphere_event_benchmark','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(ROOT/'.runtime/closure_sdk')]),('build',['cmake','--build',build,'-j2']),('api',[build/'test_sphere_event_api'])]:
  stages[name]=logged(cmd,out/name,180)
  if stages[name]['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stages=stages));return
 if before!={str(p.relative_to(ROOT)):sha(p)for p in sources}:raise ValueError('source mutation')
 plugin=build/'libReGripSphereEventBenchmark.so';write_json(out/'compiled.json',dict(binary_sha256=sha(plugin),sources=before))
 rows={}
 for steps in (20,40,80):
  case=out/str(steps);case.mkdir();dt=.02/steps
  scene=f'''<Node name="sphere_event_path" dt="{dt}" gravity="0 0 0"><RequiredPlugin pluginName="Sofa.Component.AnimationLoop Sofa.Component.StateContainer Sofa.Component.Mass Sofa.Component.ODESolver.Backward Sofa.Component.LinearSolver.Direct"/><DefaultAnimationLoop/><EulerImplicitSolver rayleighMass="0" rayleighStiffness="0"/><EigenSparseLU template="CompressedRowSparseMatrixd"/><MechanicalObject template="Vec3d" position="0 1.021 0" velocity=".2 -.2 .1"/><UniformMass totalMass=".001"/><SphereEventBenchmark substeps="{a.substeps}" filename="{case/'journal.csv'}"/></Node>'''
  (case/'scene.scn').write_text(scene)
  stages[str(steps)]=logged([sdk/'bin/graph_probe',sdk,case/'scene.scn',str(steps),'0',plugin],case/'process',480)
  text=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
  if stages[str(steps)]['exit_code']or '[ERROR]'in text or 'Unused Attribute'in text:continue
  r=list(csv.DictReader((case/'journal.csv').open()))
  if len(r)!=steps or [int(v['commits'])for v in r]!=list(range(1,steps+1)):continue
  rows[steps]=r
 comparisons=[]
 for c,f in ((20,40),(20,80),(40,80)):
  if c not in rows or f not in rows:continue
  fine={round(float(r['time']),12):r for r in rows[f]};p0=p1=0;relative=[]
  for r in rows[c]:
   other=fine[round(float(r['time']),12)];v0=float(r['plastic']);v1=float(other['plastic']);d0=v0-p0;d1=v1-p1
   relative.append(abs(d0-d1)/abs(d1)if d1 else (0 if not d0 else None));p0=v0;p1=v1
  comparisons.append(dict(steps=[c,f],max_phase_relative=max((x for x in relative if x is not None),default=0),undefined=any(x is None for x in relative),status='PASS'if all(x is not None and x<=.001 for x in relative)else'FAIL'))
 write_json(out/'summary.json',dict(process_status='PASS'if len(rows)==3 else'FAIL',time_status='PASS'if len(comparisons)==3 and all(x['status']=='PASS'for x in comparisons)else'FAIL',comparisons=comparisons,stages=stages,full_gripper='NOT RUN',energy='BLOCKED'))
 print(json.dumps(dict(out=str(out),completed=len(rows),comparisons=comparisons)))
if __name__=='__main__':main()
