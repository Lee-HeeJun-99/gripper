"""Strict finite-horizon actual100us API proof;failed reference stays FAIL."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261118_routed_refined_actual1318';ref=ROOT/'results/autonomous_film_20261118_routed_unload_half1317';m=json.loads((src/'summary.json').read_text());r=json.loads((ref/'summary.json').read_text())
 if m['status']!='EXPERIMENTAL' or m['process']['exit_code'] or m['sofa_errors'] or r['status']!='FAIL' or r['refinement']!=2 or m['source_checkpoint_sha256']!=r['input_checkpoint_sha256']:raise ValueError('explicit actual half-step and preserved failed reference required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual physical evidence changed')
 physical=lambda meta:{k:v for k,v in meta['source_hashes'].items() if k.startswith('models/') and not k.startswith('models/film_routed_refined_resume/')}
 if physical(m)!=physical(r):raise ValueError('compiled physical kernels differ')
 old=(ref/'input.checkpoint').read_text().split();new=(src/'input.checkpoint').read_text().split()
 if new[:4]+new[5:]!=old[:4]+old[5:]:raise ValueError('physical input checkpoint changed')
 actual=list(csv.DictReader((src/'three.states.csv').open()));x=actual[1::2];y=list(csv.DictReader((ref/'states.csv').open()))[:len(x)];rows=list(csv.DictReader((src/'three.rows.csv').open()));fields=[list(csv.DictReader((src/f'film_{f}.csv').open())) for f in range(3)];offset=5+2*1953+4+693;Mb=np.array(new[offset:offset+36],float).reshape(6,6)
 if len(actual)!=16 or len(x)!=8 or len(y)!=8:raise ValueError('complete actual16micro/common8macro prefix required')
 api={k:max(float(np.max(abs(np.fromstring(i[k],sep=' ')-np.fromstring(j[k],sep=' ')))) for i,j in zip(x,y)) for k in ('q','v')};clock=all(i['time']==j['time'] for i,j in zip(x,y));force=energy=control=0.
 for index,(aa,rr) in enumerate(zip(x,y)):
  i=2*index+1;force=max(force,float(np.max(abs(np.array([float(z['force']) for z in rows[9*i+6:9*i+9]])-np.fromstring(rr['force'],sep=' ')))));v=np.fromstring(aa['v'],sep=' ');K=sum(float(f[i]['K']) for f in fields)+.5*v[-6:]@Mb@v[-6:];energy=max(energy,abs(K-float(rr['K'])),abs(sum(float(f[i]['U_shell']) for f in fields)-float(rr['U_skin'])-float(rr['U_rails'])),abs(sum(float(f[i]['U_attachment']) for f in fields)-float(rr['U_attachment'])));control=max(control,max(abs(float(f[i]['T_per_rail'])-float(rr['T_per_rail'])) for f in fields))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if max(api.values())<1e-12 and clock and force<1e-12 and energy<1e-12 and control==0 else 'FAIL',scope='actual100us21.2..22.8ms finite-horizon API consistency at8exact common endpoints ONLY;1317 longer27.6ms reference remains FAIL',actual_summary_sha256=sha(src/'summary.json'),reference_summary_sha256=sha(ref/'summary.json'),failed_reference_prefix_observed_sha256=sha(ref/'states.csv'),reference_max_abs=api,accumulated_clock_exact=clock,force_max_abs_N=force,energy_max_abs_Nmm=energy,control_max_abs_N=control,api_gate=1e-12,full_time_gate='FAIL remains',full_energy_gate='BLOCKED',holding_load=None);write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
