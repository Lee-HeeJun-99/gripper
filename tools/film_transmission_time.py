"""All-pair SAME absolute endpoint transmission observable convergence."""
import argparse,csv,itertools,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
def relative(a,b):
 a=np.atleast_1d(a);b=np.atleast_1d(b);err=float(np.linalg.norm(a-b));den=float(np.linalg.norm(b));return dict(absolute_L2=err,relative_percent=100*err/den if den else (0 if err==0 else None),pass_0p1=bool(err==0 if den==0 else 100*err/den<=.1))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);a=p.parse_args();data=[];hashes={}
 for case in a.cases:
  src=ROOT/'results'/('autonomous_film_'+case);proof=json.loads((src/'summary.json').read_text())
  if proof['status']!='PASS' or not proof['common_endpoint']:raise ValueError('complete exact-common actual trajectories required')
  for f,d in proof['raw_hashes'].items():
   if sha(src/f)!=d:raise ValueError('actual data changed')
  state=list(csv.DictReader((src/'actual.csv').open()))[-1];field=list(csv.DictReader((src/'film_0.csv').open()))[-1];q=np.fromstring(state['q'],sep=' ');v=np.fromstring(state['v'],sep=' ');metrics={k:float(field[k]) for k in ('U_shell','U_attachment','K')};metrics['tendon_pull_mm']=200-float(field['cable_length']);metrics.update(shape(q));
  for part,offset,ny in (('skin',0,5),('left',105,3),('right',168,3)):
   metrics[part+'_q']=q.reshape(231,3)[offset:offset+21*ny].ravel();metrics[part+'_v']=v.reshape(231,3)[offset:offset+21*ny].ravel()
  data.append((case,proof,float(state['time']),metrics));hashes[case]=sha(src/'summary.json')
 if len({d[1].get('scheme','midpoint') for d in data})!=1:raise ValueError('dt convergence requires the SAME integration method;cross-method diagnostic is separate')
 pairs=[]
 for x,y in itertools.combinations(data,2):
  if x[2]!=y[2] or any(x[1][k]!=y[1][k] for k in ('bond_stiffness_N_mm','guide_offset_mm','control','public_mass_sha256','volume_mm3')):raise ValueError('same physical input and exact physical endpoint required')
  errors={k:relative(x[3][k],y[3][k]) for k in x[3]};pairs.append(dict(cases=[x[0],y[0]],metrics=errors,status='PASS' if all(e['pass_0p1'] for e in errors.values()) else 'FAIL'))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if all(p['status']=='PASS' for p in pairs) else 'FAIL',scope='actual nonlinear single-coupon SAME absolute endpoint all-pair time observables;NOT whole trajectory/contact/full energy certification',endpoint_time_s=data[0][2],time_gate_percent=.1,source_summary_hashes=hashes,pairs=pairs,unmeasured_full_cycle='NOT RUN;all intermediate epochs,contact,release/recovery remain unqualified');write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],pairs=[dict(cases=p['cases'],status=p['status'],maximum_percent=max(e['relative_percent'] for e in p['metrics'].values() if e['relative_percent'] is not None),failed=[k for k,e in p['metrics'].items() if not e['pass_0p1']]) for p in pairs])))
if __name__=='__main__':main()
