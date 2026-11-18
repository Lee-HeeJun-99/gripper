"""Actual bounded four-stage startup;reuse qualified Field and numerical kernel."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--steps',type=int,choices=(8,16,32),default=8);p.add_argument('--reuse-build');a=p.parse_args();api=ROOT/'results/autonomous_film_20261119_attachment_api1685';am=json.loads((api/'summary.json').read_text());ref=ROOT/'results'/({8:'autonomous_film_20261119_precise_gauss4_1681',16:'autonomous_film_20261119_precise_gauss4_half1682',32:'autonomous_film_20261119_precise_gauss4_quarter1683'}[a.steps]);rm=json.loads((ref/'summary.json').read_text());scene=ROOT/'results/autonomous_film_20261119_rail_aspect_actual_profile1657/rail0.1/scene.scn'
 if am['status']!='PASS' or not rm['FD_query_state_stages_EXACT']:raise ValueError('qualified Field and four-stage kernel required')
 for parent,meta in ((api,am),(ref,rm)):
  for f,d in meta['source_hashes'].items():
   if sha(parent/'sources'/f)!=d:raise ValueError('frozen source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(api/'sources',archive);folder=archive/'models/film_precise_attachment';shutil.copy2(ROOT/'models/film_precise_attachment/Owner.cpp',folder/'Owner.cpp');shutil.copytree(ROOT/'models/film_c2_startup',archive/'models/film_c2_startup')
 for name in ('Elements.h','Force.h'):
  if sha(folder/name)!=rm['source_hashes']['models/film_precise_attachment/'+name]:raise ValueError('actual/numerical force model mismatch')
 if sha(archive/'models/film_c2_startup/Gauss4.h')!=rm['source_hashes']['models/film_c2_startup/Gauss4.h']:raise ValueError('actual/numerical kernel mismatch')
 cmake=(folder/'CMakeLists.txt').read_text();cmake+='\nfind_package(Sofa.Simulation.Core REQUIRED)\nadd_library(ReGripPreciseStartup SHARED Owner.cpp Field.generated.cpp)\ntarget_compile_features(ReGripPreciseStartup PRIVATE cxx_std_17)\ntarget_compile_options(ReGripPreciseStartup PRIVATE -O2 -ffp-contract=off)\ntarget_link_libraries(ReGripPreciseStartup PRIVATE Eigen3::Eigen Sofa.Core Sofa.DefaultType Sofa.LinearAlgebra Sofa.Simulation.Core Sofa.Component.StateContainer)\n';(folder/'CMakeLists.txt').write_text(cmake)
 if a.reuse_build:
  old=ROOT/'results'/('autonomous_film_'+a.reuse_build);build=ROOT/'build'/('precise_startup_'+a.reuse_build)
  before={str(f.relative_to(old/'sources')):sha(f) for f in (old/'sources').rglob('*') if f.is_file()};after={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()}
  if before!=after or json.loads((old/'compile/result.json').read_text())['exit_code']!=0:raise ValueError('ALL compiled sources and completed build required')
  configure=dict(exit_code=0,reused_build=str(build));compile=dict(exit_code=0,ALL_sources_EXACT=True,binary_sha256=sha(build/'libReGripPreciseStartup.so'))
 else:
  build=ROOT/'build'/('precise_startup_'+a.tag);build.mkdir(exist_ok=False);configure=guarded(['cmake','-S',folder,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'--target','ReGripPreciseStartup','-j','1'],out/'compile',180) if configure['exit_code']==0 else None
 r=dict(status='FAIL',scope='actual SOFA 8/16/32-step200us free startup ONLY;NOT contact/full time/energy/wrapping/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},configure=configure,compile=compile,reference_summary_sha256=sha(ref/'summary.json'),API_summary_sha256=sha(api/'summary.json'),build_relative=str(build.relative_to(ROOT)),sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),dt_s=.0002/a.steps,steps=a.steps,duration_s=.0002,energy='NOT ASSESSED',work='NOT ASSESSED',contact='NONE',selected_design=None)
 if compile and compile['exit_code']==0:
  binary=build/'libReGripPreciseStartup.so';r['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in z and '=> /' in z and str(SDK) not in z for z in deps.splitlines()):raise ValueError('SDK ABI mismatch')
  tree=ET.parse(scene);root=tree.getroot();root.set('dt',format(.0002/a.steps,'.17g'));owner=root.find('FilmRailAspectODE');owner.tag='FilmPreciseStartupODE';owner.set('maxSteps',str(a.steps));owner.set('endTime','.0002');owner.set('filename',str(out/'actual.csv'));field=root.find('.//FilmAspectTendon');field.tag='FilmPreciseAttachmentTendon';field.set('filename',str(out/'film.csv'));field.set('displacementFilename',str(out/'displacement.csv'))
  for node in root.findall('RequiredPlugin'):
   if node.get('pluginName','').endswith('libReGripFilmRailAspect.so'):node.set('pluginName',str(binary))
  tree.write(out/'scene.scn');r['scene_sha256']=sha(out/'scene.scn');run=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(a.steps),'--hideProgressBar',out/'scene.scn'],out/'process',480);errors=sum((out/'process'/f).read_text(errors='replace').count('[ERROR]') for f in ('stdout.log','stderr.log'));r.update(process=run,sofa_errors=errors)
  if run['exit_code']==0 and not errors:
   actual=list(csv.DictReader((out/'actual.csv').open()));expected=next(csv.DictReader((ref/'plain.csv').open()));stages=list(csv.DictReader((out/'actual.csv.gauss4.csv').open()));truth=list(csv.DictReader((ref/'plain.csv.stages.csv').open()));delta={key:float(np.max(abs(np.fromstring(actual[-1][key],sep=' ')-np.fromstring(expected[key],sep=' ')))) for key in ('q','v')};stage_error={key:max(float(np.max(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')))) for x,y in zip(stages,truth)) for key in ('q','v','reduced_physical_force_N')};clock=max(abs(float(x['time'])-float(y['time'])) for x,y in zip(stages,truth));r.update(status='PASS' if len(actual)==a.steps and len(stages)==len(truth)==4*a.steps and max(delta.values())<=1e-12 and max(stage_error.values())<=1e-12 and clock<=1e-18 else 'FAIL',endpoint_max_abs=delta,ALL_four_stages_max_abs=stage_error,stage_clock_max_abs_s=clock,legacy_two_stage_observer='empty by design;actual32 stages in gauss4.csv',accepted_time=float(actual[-1]['time']))
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.scn')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','configure','process')}))
if __name__=='__main__':main()
