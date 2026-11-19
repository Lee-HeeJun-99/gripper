"""Actual SOFA same-binary passive envelope observer ON/OFF purity test."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
 old=ROOT/'results/autonomous_film_20261119_plan_actual1743';identity=json.loads((old/'summary.json').read_text())
 for f,d in identity['source_hashes'].items():
  if sha(old/'sources'/f)!=d:raise ValueError('archived source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(old/'sources',out/'sources')
 for name in ('SphereEquilibrium.h','Potential.h','EnvelopeObserver.cpp'):
  dest=out/'sources/models/film_precise_static'/name;dest.parent.mkdir(exist_ok=True);shutil.copy2(ROOT/'models/film_precise_static'/name,dest)
 folder=out/'sources/models/film_precise_static';cmake=(out/'sources/models/film_solver_plan/CMakeLists.txt').read_text().replace('ReGripPrecisePlan','ReGripEnvelopeAudit').replace('Owner.cpp ../film_precise_attachment','EnvelopeObserver.cpp ../film_precise_attachment');(folder/'CMakeLists.txt').write_text(cmake)
 r=dict(status='FAIL',scope='actual SOFA passive accepted-state thickness envelope geometry;NO sphere dynamics/contact forces/wrapping/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},sdk=str(SDK),sdk_runner_sha256=sha(SDK/'bin/runSofa-26.06.00'),mount_world_z_offset_mm=.2,actual_solver='FilmEnvelopeObservedODE:same qualified1ms Gauss4 early/late plan',steps=40,dt_s=.000025,root_reaction_work=None)
 build=ROOT/'build'/('thickness_audit_'+a.tag);build.mkdir(exist_ok=False)
 r['configure']=guarded(['cmake','-S',folder,'-B',build,'-DCMAKE_BUILD_TYPE=Release','-DCMAKE_PREFIX_PATH='+str(SDK)],out/'configure',120)
 if r['configure']['exit_code']==0:
  r['compile']=guarded(['cmake','--build',build,'-j','1'],out/'compile',180)
  if r['compile']['exit_code']==0:
   binary=build/'libReGripEnvelopeAudit.so';r['binary_sha256']=sha(binary);r['build_relative']=str(build.relative_to(ROOT));deps=subprocess.check_output(['ldd',binary],text=True);(out/'ldd.txt').write_text(deps)
   if 'not found' in deps or any('libSofa.' in x and '=> /' in x and str(SDK) not in x for x in deps.splitlines()):raise ValueError('SDK ABI mismatch')
   for mode in ('off','on'):
    d=out/mode;d.mkdir();tree=ET.parse(old/'scene.scn');root=tree.getroot();owner=root.find('FilmPreciseSolverPlanODE');owner.tag='FilmEnvelopeObservedODE';owner.set('observe','1' if mode=='on' else '0');owner.set('filename',str(d/'actual.csv'))
    field=root.find('.//FilmPreciseTendon');field.set('filename',str(d/'film.csv'));field.set('displacementFilename',str(d/'displacement.csv'))
    for node in root.findall('RequiredPlugin'):
     if node.get('pluginName','').endswith('libReGripPrecisePlan.so'):node.set('pluginName',str(binary))
    tree.write(d/'scene.scn');r[mode]=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','40','--hideProgressBar',d/'scene.scn'],d/'process',480)
   if all(r[x]['exit_code']==0 for x in ('off','on')):
    fields=('actual.csv','actual.csv.gauss4.csv','film.csv','displacement.csv');r['byte_exact_on_off']={f:sha(out/'on'/f)==sha(out/'off'/f) for f in fields};r['byte_exact_old_reference']={f:sha(out/'off'/f)==sha(old/f) for f in fields}
    rows=list(csv.DictReader((out/'on/actual.csv.envelope.csv').open()));r['geometry_rows']=len(rows);r['minimum_envelope_gap_mm']=min(float(x['buffered_envelope_gap_mm']) for x in rows);r['status']='PASS' if all(r['byte_exact_on_off'].values()) and all(r['byte_exact_old_reference'].values()) and len(rows)==12800 and r['minimum_envelope_gap_mm']>=-1e-10 else 'FAIL'
 r['raw_hashes']={str(f.relative_to(out)):sha(f) for f in out.rglob('*.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes')}))
if __name__=='__main__':main()
