"""All exact canonical epochs,not just the most favorable last row."""
import argparse,csv,itertools,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
from film_transmission_time import relative
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);a=p.parse_args();data=[];hashes={}
 for name in a.cases:
  src=ROOT/'results'/('autonomous_film_'+name);meta=json.loads((src/'summary.json').read_text())
  if meta['status']!='PASS' or meta['process']['exit_code'] or not meta['all_contexts_exact']:raise ValueError('complete actual exact-plan trajectories required')
  for file,digest in meta['raw_hashes'].items():
   if sha(src/file)!=digest:raise ValueError('actual plan raw changed')
  states=list(csv.DictReader((src/'actual.csv').open()));fields=list(csv.DictReader((src/'film_0.csv').open()));epochs={}
  for time in meta['canonical_epochs']:
   indices=[i for i,r in enumerate(states) if float(r['time'])==time]
   if len(indices)!=1:raise ValueError('exact canonical epoch missing;no interpolation')
   i=indices[0];row=states[i];field=fields[i]
   if float(field['time'])!=time:raise ValueError('field epoch differs')
   q=np.fromstring(row['q'],sep=' ');v=np.fromstring(row['v'],sep=' ');values={k:float(field[k]) for k in ('U_shell','U_attachment','K')};values.update(shape(q));values['q']=q;values['v']=v;epochs[time]=values
  data.append((meta,epochs));hashes[name]=sha(src/'summary.json')
 for key in ('binary_sha256','reference_binary_sha256','public_mass_sha256','physical_input','canonical_epochs'):
  if any(d[0][key]!=data[0][0][key] for d in data):raise ValueError('same physical model/control/common epoch list required')
 for key,default in (('startup_epochs',1),('graded_expansion',False)):
  if any(d[0].get(key,default)!=data[0][0].get(key,default) for d in data):raise ValueError('same refinement FAMILY required;design-plan contrast is separate')
 comparisons=[]
 for time in data[0][0]['canonical_epochs']:
  pairs=[]
  for i,j in itertools.combinations(range(3),2):
   errors={k:relative(data[i][1][time][k],data[j][1][time][k]) for k in data[i][1][time]};pairs.append(dict(cases=[a.cases[i],a.cases[j]],metrics=errors,status='PASS' if all(e['pass_0p1'] for e in errors.values()) else 'FAIL'))
  comparisons.append(dict(time_s=time,status='PASS' if all(p['status']=='PASS' for p in pairs) else 'FAIL',pairs=pairs))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if all(e['status']=='PASS' for e in comparisons) else 'FAIL',scope='actual deterministic local-plan ALL exact canonical epochs;NOT contact/all-time/mesh/energy/grasp certification',time_gate_percent=.1,source_summaries=hashes,epochs=comparisons,interpolation=False);write_json(out/'summary.json',result);print(json.dumps(dict(status=result['status'],epochs=[dict(time_s=e['time_s'],status=e['status'],maximum_percent=max(m['relative_percent'] for p in e['pairs'] for m in p['metrics'].values() if m['relative_percent'] is not None),failed=sorted({k for p in e['pairs'] for k,m in p['metrics'].items() if not m['pass_0p1']})) for e in comparisons])))
if __name__=='__main__':main()
