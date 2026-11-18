"""Read-only qualification of actual Hold against SAME-IVP base reference."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--reference',required=True);a=p.parse_args();actual=ROOT/'results'/('autonomous_film_'+a.case);ref=ROOT/'results'/('autonomous_film_'+a.reference);m=json.loads((actual/'summary.json').read_text());r=json.loads((ref/'summary.json').read_text())
 if m['status']!='EXPERIMENTAL' or m['process']['exit_code'] or m['sofa_errors'] or r['status']!='PASS' or r['refinement']!=1:raise ValueError('completed actual and SAME macro-dt reference required')
 if m['input_checkpoint_sha256']!=r['input_checkpoint_sha256'] or m['actual_steps']!=r['macro_steps']:raise ValueError('same actual IVP/macro horizon required')
 for path,meta in ((actual,m),(ref,r)):
  for f,d in meta['raw_hashes'].items():
   if sha(path/f)!=d:raise ValueError('actual/reference raw changed')
 x=list(csv.DictReader((actual/'three.states.csv').open()));y=list(csv.DictReader((ref/'states.csv').open()));rows=list(csv.DictReader((actual/'three.rows.csv').open()));fields=[list(csv.DictReader((actual/f'film_{f}.csv').open())) for f in range(3)]
 if len(x)!=len(y) or len(x)!=m['actual_steps'] or len(rows)!=9*len(x) or any(len(f)!=len(x) for f in fields):raise ValueError('incomplete actual/reference')
 api={k:max(float(np.max(abs(np.fromstring(i[k],sep=' ')-np.fromstring(j[k],sep=' ')))) for i,j in zip(x,y)) for k in ('q','v')};clock=all(i['time']==j['time'] for i,j in zip(x,y));energy=force=control=0.;n=len(np.fromstring(x[0]['q'],sep=' '));tokens=(actual/'input.checkpoint').read_text().split();offset=5+2*n+4+693;Mb=np.array(tokens[offset:offset+36],float).reshape(6,6)
 for i,(aa,rr) in enumerate(zip(x,y)):
  fvec=np.array([float(row['force']) for row in rows[9*i+6:9*i+9]]);force=max(force,float(np.max(abs(fvec-np.fromstring(rr['force'],sep=' ')))));velocity=np.fromstring(aa['v'],sep=' ');K=sum(float(f[i]['K']) for f in fields)+.5*velocity[-6:]@Mb@velocity[-6:];energy=max(energy,abs(float(rr['U_skin'])+float(rr['U_rails'])-sum(float(f[i]['U_shell']) for f in fields)),abs(float(rr['U_attachment'])-sum(float(f[i]['U_attachment']) for f in fields)),abs(float(rr['K'])-K));target=float(rr['T_per_rail']) if 'T_per_rail' in rr else .0001;control=max(control,max(abs(float(f[i]['T_per_rail'])-target) for f in fields))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if max(api.values())<1e-12 and clock and energy<1e-12 and force<1e-12 and control==0 else 'FAIL',scope='actual C2 Hold/Unload-input/API/state consistency;NOT object holding/time/energy/mesh/grasp certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(actual/'summary.json'),reference_summary_sha256=sha(ref/'summary.json'),reference_max_abs=api,accumulated_clock_exact=clock,actual_energy_max_abs_Nmm=energy,normal_force_max_abs_N=force,actual_control_tension_error_N=control,api_gate=1e-12,physical_holding_load=None,root_work=None);write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
