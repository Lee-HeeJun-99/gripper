"""Actual two-stage Gauss power quadrature;never midpoint interpolation."""
import argparse,csv,json,math,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);proof=json.loads((src/'summary.json').read_text())
 if proof['status']!='PASS' or proof.get('scheme')!='gauss' or proof['process']['exit_code']:raise ValueError('complete actual Gauss API case required')
 for name,digest in proof['raw_hashes'].items():
  if sha(src/name)!=digest:raise ValueError('actual raw changed')
 rows=list(csv.DictReader((src/'actual.csv.stages.csv').open()))
 if len(rows)!=2*proof['steps'] or any(int(r['macro'])!=i//2+1 or int(r['stage'])!=i%2 for i,r in enumerate(rows)):raise ValueError('missing/reordered actual stages')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/TransmissionGaussObserve.cpp';cpp.parent.mkdir(parents=True)
 for name in ('TransmissionGaussObserve.cpp','TransmissionObserve.cpp'):shutil.copy2(ROOT/'diagnostics/film_three_finger'/name,cpp.parent/name)
 binary=out/'observer';compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
 (out/'stages.txt').write_text(str(len(rows))+'\n'+'\n'.join(' '.join(r[k] for k in ('time','weight','T','q','v')) for r in rows)+'\n')
 run=guarded([binary,str(proof['bond_stiffness_N_mm']),str(proof['guide_offset_mm']),src/'public_mass.txt',out/'stages.txt',out/'work.csv'],out/'process',480) if compile['exit_code']==0 else None
 result=dict(status='FAIL',scope='actual Gauss stage power quadrature;NOT full physical energy certification',parent=a.case,parent_summary_sha256=sha(src/'summary.json'),actual_binary_sha256=proof['binary_sha256'],source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),compile=compile,process=run,binary_sha256=sha(binary) if binary.exists() else None,root_reaction_work=None,sources={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()})
 if run and run['exit_code']==0:
  observed=list(csv.DictReader((out/'work.csv').open()));field=list(csv.DictReader((src/'film_0.csv').open()))[-1];end={k:float(v) for k,v in observed[-1].items()};energy=sum(float(field[k]) for k in ('U_shell','U_attachment','K'));result.update(status='PASS' if len(observed)==len(rows) else 'FAIL',actual_stage_count=len(rows),stage_weight_duration_s=math.fsum(float(r['weight']) for r in rows),endpoint=end,stored_plus_kinetic_Nmm=energy,signed_defect_Nmm=energy-end['tendon_work_Nmm']+end['damping_work_Nmm'],defect_scope='signed discrete inventory,NOT Coulomb heat or completed whole energy')
 result['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.csv','.txt')};write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k not in ('sources','compile','process','raw_hashes')}))
if __name__=='__main__':main()
