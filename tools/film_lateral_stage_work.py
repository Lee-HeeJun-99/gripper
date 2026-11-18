"""Read-only actual Gauss-stage work,not legacy endpoint sampled work."""
import argparse,csv,json,shutil,subprocess,math
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text());provider=ROOT/'results/autonomous_film_20261118_lateral_api_build1356';proof=json.loads((provider/'summary.json').read_text())
 if m['status']!='PASS' or m.get('design')!='lateral' or m['amplitude_mm']!=6 or not m['stage_rows_exact'] or m['binary_sha256']!=proof['binary_sha256']:raise ValueError('qualified actual lateral6 Gauss stages required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual raw changed')
 for f,d in proof['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('compiled model source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/LateralStagePower.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_three_finger/LateralStagePower.cpp',cpp);stages=list(csv.DictReader((src/'actual.csv.stages.csv').open()));(out/'stages.txt').write_text(str(len(stages))+'\n'+'\n'.join(' '.join((x['macro'],x['time'],x['weight'],x['T'],x['q'],x['v'])) for x in stages)+'\n');compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'power'],out/'compile',120);run=guarded([out/'power',src/'public_mass.txt',out/'stages.txt',out/'power.csv'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='actual NO-OBJECT stage-work inventory ONLY;NOT contact/whole energy/time/grasp certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,sign='W_tendon=-integral T*dL/dt;positive mechanical work into film',quadrature='actual two Gauss stages,actual weights;not endpoint trapezoid',diagnostic_accumulation='long-double products/sums;force/Hessian NOT altered',root_reaction_work=None,whole_energy='BLOCKED',external_work='not present in this no-object coupon',legacy_sampled_work='EXCLUDED')
 if run and run['exit_code']==0:
  values=list(csv.DictReader((out/'power.csv').open()));fields=list(csv.DictReader((src/'film_0.csv').open()));states=list(csv.DictReader((src/'actual.csv').open()));records=[];Wt=D=0.
  if len(values)!=2*len(states) or len(fields)!=len(states):raise ValueError('actual complete stage/field counts differ')
  for i,(state,field) in enumerate(zip(states,fields)):
   if float(field['time'])!=float(state['time']):raise ValueError('actual energy epoch differs')
   pair=values[2*i:2*i+2];Wt+=math.fsum(float(x['weight_s'])*float(x['tendon_power_Nmm_s']) for x in pair);D+=math.fsum(float(x['weight_s'])*float(x['damping_power_Nmm_s']) for x in pair);E=math.fsum(float(field[k]) for k in ('U_shell','U_attachment','K'));records.append(dict(time_s=float(state['time']),tendon_work_Nmm=Wt,damping_work_Nmm=D,stored_plus_kinetic_Nmm=E,signed_discrete_defect_Nmm=E-Wt+D))
  with (out/'inventory.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
  r.update(status='PASS',endpoint=records[-1],maximum_absolute_signed_defect_Nmm=max(abs(x['signed_discrete_defect_Nmm']) for x in records),binary_sha256=sha(out/'power'),raw_hashes={n:sha(out/n) for n in ('power.csv','inventory.csv','stages.txt')},defect_note='unexplained discretization/measurement defect,NOT heat or full energy PASS')
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
