"""Archive, compile and execute independent thickness-envelope branch tests."""
import argparse,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
 parent=ROOT/'results/autonomous_film_20261119_thickness_static1778';pm=json.loads((parent/'summary.json').read_text())
 for f,d in pm['source_hashes'].items():
  if sha(parent/'sources'/f)!=d:raise ValueError('immutable snapshot changed')
 shutil.copytree(parent/'sources',out/'sources');test=out/'sources/tests/test_film_thickness_envelope.cpp';test.parent.mkdir();shutil.copy2(ROOT/'tests/test_film_thickness_envelope.cpp',test);shutil.copy2(__file__,out/'runner.py')
 r=dict(status='FAIL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},scope='smooth closest-feature constant-radius derivatives,rigid objectivity,conservative extrusion inequality;NOT full thickness dynamics')
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',test,'-o',out/'reference'],out/'compile',120)
 if r['compile']['exit_code']==0:
  r['binary_sha256']=sha(out/'reference');r['process']=guarded([out/'reference'],out/'process',60)
  if r['process']['exit_code']==0:r['metrics']=json.loads((out/'process/stdout.log').read_text());r['status']=r['metrics']['status']
 write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
