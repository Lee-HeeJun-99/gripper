"""Native PlaneForceField oscillator:separates ODE from collision/static-DOF graph.
No new solver or replacement output. Translation-only exact symmetry reduction.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def add(parent,tag,**attrs):return ET.SubElement(parent,tag,{k:str(v) for k,v in attrs.items()})
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--modes',nargs='+',choices=('euler','bdf1','bdf2','newmark'),default=['euler','bdf1','bdf2']);p.add_argument('--reuse-build');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'sofa/native_penalty_probe';build=BASE/'cad'/('build_'+a.tag)
 configure=compiled=None;records=[]
 if a.reuse_build:
  previous_case=BASE/'results'/a.reuse_build;previous=json.loads((previous_case/'summary.json').read_text());build=BASE.parent/previous['build'];binary=build/'libReGripPenaltyProbe.so'
  if sha(binary)!=previous['binary_sha256']:raise ValueError('probe binary mismatch')
  for n in ('Observer.cpp','CMakeLists.txt'):(out/n).write_bytes((previous_case/n).read_bytes())
 else:
  for n in ('Observer.cpp','CMakeLists.txt'):(out/n).write_bytes((source/n).read_bytes())
  configure=guarded(['cmake','-S',source,'-B',build,'-DCMAKE_PREFIX_PATH=/home/ubuntu/SOFA/v26.06.00','-DCMAKE_BUILD_TYPE=Release'],out/'configure',480);compiled=guarded(['cmake','--build',build,'--parallel','1'],out/'compile',480) if configure['exit_code']==0 else None;binary=build/'libReGripPenaltyProbe.so'
 if a.reuse_build or (compiled and compiled['exit_code']==0):
  for mode in a.modes:
   for dt in (.00025,.000125,.0000625):
    d=out/(mode+'_'+format(dt,'.7f'));d.mkdir();root=ET.Element('Node',name='root',dt=str(dt),gravity='0 0 0')
    for plugin in ('AnimationLoop','ODESolver.Backward','LinearSolver.Direct','Mass','StateContainer','MechanicalLoad'):add(root,'RequiredPlugin',pluginName='Sofa.Component.'+plugin)
    add(root,'RequiredPlugin',pluginName=binary);add(root,'DefaultAnimationLoop');add(root,'EigenSparseLU',name='linear',template='CompressedRowSparseMatrixMat3x3d')
    if mode=='euler':add(root,'EulerImplicitSolver',rayleighMass=0,rayleighStiffness=0)
    elif mode=='newmark':add(root,'NewmarkImplicitSolver',gamma='.5',beta='.25',rayleighMass=0,rayleighStiffness=0,vdamping=0)
    else:
     add(root,'NewtonRaphsonSolver',name='newton',maxNbIterationsNewton=50,relativeSuccessiveStoppingThreshold='1e-12',relativeInitialStoppingThreshold='1e-12',absoluteResidualStoppingThreshold='1e-14',maxNbIterationsLineSearch=20,updateStateWhenDiverged=0);add(root,'BDFOdeSolver',name='ode',order=int(mode[-1]),newtonSolver='@newton',rayleighMass=0,rayleighStiffness=0)
    add(root,'MechanicalObject',name='point',template='Vec3d',position='0 0 .001215',velocity='0 0 -.01');add(root,'UniformMass',totalMass='.001');add(root,'PlaneForceField',normal='0 0 1',d='.0012',stiffness='100',damping='0',bilateral='0');add(root,'NativePenaltyJournal',point='@point',filename=d/'probe.csv');ET.ElementTree(root).write(d/'scene.scn');proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(round(.02/dt)),'--hideProgressBar',d/'scene.scn'],d/'process',480);logs=''.join((d/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));count=len(list(csv.DictReader((d/'probe.csv.point.csv').open()))) if (d/'probe.csv.point.csv').exists() else None;records.append(dict(mode=mode,dt_s=dt,process=proc,sofa_errors=logs.count('[ERROR]'),scene_sha256=sha(d/'scene.scn'),actual_frames=count))
    if proc['exit_code']!=0 or '[ERROR]' in logs:break
 result=dict(status='NATIVE_SURROGATE_RUN_COMPLETED_NOT_PHYSICALLY_QUALIFIED' if len(records)==len(a.modes)*3 and all(r['process']['exit_code']==0 and not r['sofa_errors'] and r['actual_frames']==round(.02/r['dt_s']) for r in records) else 'FAIL_NATIVE_SURROGATE',scope='Native PlaneForceField Vec3 oscillator only,not collision detector/rigid/guide/B3/cable/contact production model. Same100N/m unilateral elastic law in exact translational plane symmetry reduction;stiffness research assumption,not measured hardware. Numerical solve remains stock Native.',producer_sha256=sha(Path(__file__)),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),configure=configure,compile=compiled,build=str(build.relative_to(BASE.parent)),binary_sha256=sha(binary) if binary.exists() else None,records=records,mass_kg=.001,stiffness_N_per_m=100.,initial_vz_m_s=-.01,initial_buffered_gap_m=.000015,SDK='/home/ubuntu/SOFA/v26.06.00')
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
