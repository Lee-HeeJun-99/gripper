"""Build/run a READ-ONLY accepted-stage power observer with an immutable core DLL.

Old sampled-work columns remain untouched;new work is never called heat.
"""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--reference-work',required=True);p.add_argument('--reuse');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'identity.json').read_text());ss=json.loads((src/'summary.json').read_text());ref=ROOT/'results'/('autonomous_film_'+a.reference_work);reference=json.loads((ref/'summary.json').read_text())
 if ss['status']!='PASS' or reference['status']!='PASS' or meta['steps'] not in (8,16,32,64) or meta['duration']!=.01 or not meta['actual_solver'].startswith('ThreeFilmDriven') or reference['raw_hashes']['three.rows.csv']!=sha(src/'three.rows.csv'):raise ValueError('qualified bounded10ms actual and identical-state full-AD work reference required')
 estimate=2*ss['process']['runtime_s']+30
 if estimate>480:raise ValueError('runtime forecast exceeds480s policy')
 for name,digest in meta['plugin_sha256'].items():
  if sha(name)!=digest:raise ValueError('immutable core/field plugin changed:'+name)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');shutil.copytree(ROOT/'diagnostics/film_three_finger/stage_power',archive/'diagnostics/film_three_finger/stage_power');shutil.copy2(ROOT/'diagnostics/film_three_finger/RoutedCablePower.h',archive/'diagnostics/film_three_finger/RoutedCablePower.h');sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()};build=ROOT/'build'/('stage_power_'+a.tag);build.mkdir(exist_ok=False)
 if a.reuse:
  prior=ROOT/'results'/('autonomous_film_'+a.reuse);old=json.loads((prior/'summary.json').read_text());build=ROOT/'build'/('stage_power_'+a.reuse)
  compiled=lambda d:{k:v for k,v in d.items() if k.endswith('.h') or k.startswith('diagnostics/film_three_finger/stage_power/') and (k.endswith('.cpp') or k.endswith('/CMakeLists.txt'))}
  if old['status']!='PASS' or compiled(old['sources'])!=compiled(sources) or old['sdk']!=str(SDK) or sha(build/'libReGripStagePower.so')!=old['binary_sha256']:raise ValueError('observer immutable compiled headers/source/CMake/binary/SDK mismatch;unlinked core CPP excluded')
  configure=compile=dict(exit_code=0,reused=a.reuse)
 else:configure=guarded(['cmake','-S',archive/'diagnostics/film_three_finger/stage_power','-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120);compile=guarded(['cmake','--build',build,'-j','1'],out/'compile',180) if configure['exit_code']==0 else None
 result=dict(status='FAIL',scope='actual accepted-stage observer passivity/work consistency;NOT full energy/time/grasp certification',case=a.case,reference_work=a.reference_work,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),core_source_commit=meta['source_commit'],core_identity_sha256=sha(src/'identity.json'),sources=sources,predicted_runtime_s=estimate,configure=configure,compile=compile)
 if compile and compile['exit_code']==0:
  binary=build/'libReGripStagePower.so';result['binary_sha256']=sha(binary);deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
  if 'not found' in deps or any('libSofa.' in line and '=> /' in line and str(SDK) not in line for line in deps.splitlines()):raise ValueError('observer SDK ABI mismatch')
  tree=ET.parse(src/'scene.scn');root=tree.getroot()
  for node in root.iter():
   for key,value in list(node.attrib.items()):
    if key in ('filename','displacementFilename','ownerCostFilename','costProfileFilename','publicMassFilename') and value.startswith(str(src)):
     node.set(key,str(out)+value[len(str(src)):])
  root.insert(0,ET.Element('RequiredPlugin',dict(name='stage_power_plugin',pluginName=str(binary))));ET.SubElement(root,'ThreeFilmStagePowerObserver',dict(name='stage_power',owner='@ode',field='@finger0/assembly/filmField',filename=str(out/'stage_work.csv')));tree.write(out/'scene.scn');result['scene_sha256']=sha(out/'scene.scn');result['sdk']=str(SDK);result['core_plugin_sha256']=meta['plugin_sha256']
  process=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(meta['steps']),'--hideProgressBar',out/'scene.scn'],out/'process',480);result['process']=process;errors=sum((out/'process'/name).read_text(errors='replace').count('[ERROR]') for name in ('stdout.log','stderr.log'));result['sofa_errors']=errors
  names=['three.states.csv','three.rows.csv','three.policy.csv']+['film_'+str(f)+'.csv' for f in range(3)]+['displacement_'+str(f)+'.csv' for f in range(3)]
  if process['exit_code']==0 and errors==0 and all((out/name).exists() for name in names) and (out/'stage_work.csv').exists():
   files={name:dict(before=sha(src/name),after=sha(out/name)) for name in names};rows=list(csv.DictReader((out/'stage_work.csv').open()));full={r['sample']:r for r in csv.DictReader((ref/'observed.csv').open())};inventory=list(csv.DictReader((ref/'inventory.csv').open()));rate_error=length_error=work_error=0.
   if len(rows)!=3*meta['steps']:raise ValueError('incomplete once-per-accepted-stage observer')
   for i,row in enumerate(rows):
    macro,k=divmod(i,3)
    if int(row['macro'])!=macro or int(row['stage'])!=k:raise ValueError('observer ownership/order differs')
    value=full['stage'+str(macro)+'_'+str(k)];rate_error=max(rate_error,abs(float(row['shortening_rate_mm_s'])-float(value['unit_tendon_power'])));length_error=max(length_error,abs(float(row['cable_length_mm'])-float(value['cable_length'])));work_error=max(work_error,abs(float(row['cumulative_macro_work_Nmm'])-float(inventory[macro]['tendon_work'])))
   result.update(status='PASS' if all(x['before']==x['after'] for x in files.values()) and rate_error<=1e-10 and length_error<=1e-12 and work_error<=1e-15 else 'FAIL',physical_csv_exact=files,rate_error_mm_s=rate_error,length_error_mm=length_error,work_error_Nmm=work_error,final_tendon_work_Nmm=float(rows[-1]['cumulative_macro_work_Nmm']),old_field_work_preserved=True,work_sign='-integral T*dL,positive shortening work;not cable stored energy',missing=['root reaction work','full contact/friction/pressure inventory','fullcycle/lift/grasp'])
 write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','rate_error_mm_s','work_error_Nmm','final_tendon_work_Nmm','process','sofa_errors') if k in result}))
if __name__=='__main__':main()
