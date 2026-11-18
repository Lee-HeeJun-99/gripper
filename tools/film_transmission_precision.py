"""Generated extended-precision FORCE oracle only,NOT a production solver."""
import argparse,csv,json,re,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_transmission_onset_exact1203';meta=json.loads((src/'summary.json').read_text())
 if meta['status']!='PASS':raise ValueError('complete actual onset case required')
 for file,digest in meta['raw_hashes'].items():
  if sha(src/file)!=digest:raise ValueError('actual raw changed')
 rows=list(csv.DictReader((src/'actual.csv').open()));out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(ROOT/'models',archive/'models',ignore=shutil.ignore_patterns('*.so','__pycache__'));cpp=archive/'diagnostics/film_three_finger/TransmissionPrecision.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/TransmissionPrecision.cpp',cpp);generated={}
 for file in ('film_shell/AD.h','film_shell/MembraneAD.h','film_shell/Kernel.h','film_shell/PlaneContact.h','film_shell/PassiveProfile.h','film_rail_tendon/Kernel.h'):
  text=(archive/'models'/file).read_text();text=re.sub(r'\bdouble\b','long double',text);text=re.sub(r'\bregrip_film_rail\b','regrip_film_rail_ext',text);text=re.sub(r'\bregrip_film\b','regrip_film_ext',text)
  if file=='film_rail_tendon/Kernel.h':
   marker=' std::vector<Point>rest()const{'
   if text.count(marker)!=1:raise ValueError('exact geometry-freeze transformation anchor differs')
   text=text.replace(marker,' std::vector<Point>frozenRest;\n std::vector<Point>rest()const{if(!frozenRest.empty())return frozenRest;')
  target=archive/'extended'/file;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text);generated[file]=sha(target)
 samples=[('rest_noT','0',' '.join(['0']*693)),('rest_loaded',rows[-1]['T_end'],' '.join(['0']*693)),('actual_onset',rows[-1]['T_end'],rows[-1]['q'])];(out/'samples.txt').write_text(str(len(samples))+'\n'+'\n'.join(T+' '+q for _,T,q in samples)+'\n');binary=out/'probe';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120);run=guarded([binary,out/'samples.txt',src/'public_mass.txt',out/'precision.csv'],out/'process',120) if compile['exit_code']==0 else None
 result=dict(status='FAIL',scope='same actual double inputs,generated extended-precision projected FORCE oracle;NOT high precision trajectory/time certification',actual_summary_sha256=sha(src/'summary.json'),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),compile=compile,process=run,sample_names=[s[0] for s in samples],generated_source_hashes=generated,sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},binary_sha256=sha(binary) if binary.exists() else None,physical_model='Original geometry frozen exactly;all original input/state doubles lifted without invented digits. Separate generated oracle,production/SDK untouched.')
 if run and run['exit_code']==0:result.update(status='EXPERIMENTAL',measurements=list(csv.DictReader((out/'precision.csv').open())),interpretation='Force precision differences alone neither prove nor exclude accumulation in the extremely small skin displacement. No relative time failure is waived.')
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','process','raw_hashes')}))
if __name__=='__main__':main()
