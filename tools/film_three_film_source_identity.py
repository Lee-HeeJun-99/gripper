"""Current compiled-model bytes vs actual1010 archived DLL;NOT physics gate."""
import argparse,json,shutil,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();case=ROOT/'results/autonomous_film_20261118_three_film_first_journal1010';m=json.loads((case/'summary.json').read_text());binary=ROOT/'build/three_film_first_journal_20261118_three_film_first_journal1010/libReGripThreeFilmEvent.so';compiled={k:v for k,v in m['sources'].items() if k.endswith(('.h','.cpp','/CMakeLists.txt'))};changed=[k for k,h in compiled.items() if sha(case/'sources'/k)!=h or sha(ROOT/k)!=h];plugins={n.get('pluginName'):sha(n.get('pluginName')) for n in ET.parse(case/'on/scene.scn').getroot().findall('RequiredPlugin') if n.get('pluginName','').startswith('/')};dependencies={}
 for line in (case/'ldd.txt').read_text().splitlines():
  if 'libSofa.' in line and '=> /' in line:
   path=line.split('=> ')[1].split()[0]
   if not path.startswith('/home/ubuntu/SOFA/v26.06.00/'):raise ValueError('mixed SDK dependency')
   dependencies[path]=sha(path)
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if m['status']=='PASS' and not changed and sha(binary)==m['binary_sha256'] else 'FAIL',scope='live compiled MODEL source/immutable DLL/public SDK identity only;NOT physics/time/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),checked_compiled_model_files=len(compiled),changed=changed,binary_sha256=sha(binary),plugins=plugins,sdk_dependencies=dependencies,actual_purity_summary_sha256=sha(case/'summary.json'),compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0],cmake=subprocess.check_output(['cmake','--version'],text=True).splitlines()[0]);write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','scope','checked_compiled_model_files','changed','compiler','cmake')}))
if __name__=='__main__':main()
