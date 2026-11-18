"""Exact accepted physical epoch comparison;NO timestamp interpolation/rounding."""
import argparse,csv,itertools,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
from film_transmission_time import relative
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--time',type=float,required=True);p.add_argument('--cases',nargs=3,required=True);a=p.parse_args();cases=[];hashes={}
 for name in a.cases:
  src=ROOT/'results'/('autonomous_film_'+name);proof=json.loads((src/'summary.json').read_text())
  if proof['status']!='PASS':raise ValueError('complete actual API trajectory required')
  for file,digest in proof['raw_hashes'].items():
   if sha(src/file)!=digest:raise ValueError('actual raw changed')
  rows=list(csv.DictReader((src/'actual.csv').open()));fields=list(csv.DictReader((src/'film_0.csv').open()));indices=[i for i,r in enumerate(rows) if float(r['time'])==a.time]
  if len(indices)!=1:raise ValueError('exact accepted epoch absent;no interpolation or rounding allowed')
  index=indices[0];state=rows[index];field=fields[index]
  if float(field['time'])!=a.time:raise ValueError('field energy epoch differs')
  q=np.fromstring(state['q'],sep=' ');v=np.fromstring(state['v'],sep=' ');values={k:float(field[k]) for k in ('U_shell','U_attachment','K')};values.update(shape(q));values['q']=q;values['v']=v;cases.append((proof,state,values,index));hashes[name]=sha(src/'summary.json')
 for key in ('binary_sha256','scheme','control','public_mass_sha256','volume_mm3','bond_stiffness_N_mm','guide_offset_mm','root','material'):
  if any(c[0][key]!=cases[0][0][key] for c in cases):raise ValueError('same binary and physical/control inputs required: '+key)
 if len({c[1]['time'] for c in cases})!=1:raise ValueError('serialized actual epoch differs')
 pairs=[]
 for i,j in itertools.combinations(range(3),2):
  errors={key:relative(cases[i][2][key],cases[j][2][key]) for key in cases[i][2]};pairs.append(dict(cases=[a.cases[i],a.cases[j]],metrics=errors,status='PASS' if all(e['pass_0p1'] for e in errors.values()) else 'FAIL'))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if all(p['status']=='PASS' for p in pairs) else 'FAIL',scope='actual EXACT accepted common-epoch single-film observable comparison;NOT whole time/grasp',time_s=a.time,time_gate_percent=.1,source_summaries=hashes,row_indices={n:c[3] for n,c in zip(a.cases,cases)},pairs=pairs,clock_interpolation=False);write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],time_s=a.time,pairs=[dict(cases=p['cases'],maximum_percent=max(e['relative_percent'] for e in p['metrics'].values() if e['relative_percent'] is not None),failed=[k for k,e in p['metrics'].items() if not e['pass_0p1']]) for p in pairs])))
if __name__=='__main__':main()
