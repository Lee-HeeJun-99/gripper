"""All aligned actual physical output clocks;endpoint PASS is not full-window PASS."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);a=p.parse_args();parents=[ROOT/'results'/('autonomous_film_'+x) for x in a.cases];meta=[json.loads((x/'summary.json').read_text()) for x in parents];data=[]
 for parent,m in zip(parents,meta):
  if m['status']!='PASS' or m['binary_sha256']!=meta[0]['binary_sha256'] or m['source_hashes']!=meta[0]['source_hashes']:raise ValueError('same actual binary/model required')
  if sha(parent/'actual.csv')!=m['raw_hashes']['actual.csv']:raise ValueError('immutable actual raw changed')
  data.append(list(csv.DictReader((parent/'actual.csv').open())))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');records=[];clock_error=0
 for lo,hi in ((0,1),(1,2),(0,2)):
  times=np.array([float(x['time']) for x in data[hi]])
  for row in data[lo]:
   t=float(row['time']);j=int(np.argmin(abs(times-t)));distance=abs(times[j]-t);clock_error=max(clock_error,distance)
   other=data[hi][j];values={}
   if distance:
    right=int(np.searchsorted(times,t));left=right-1
    if left<0 or right>=len(times):raise ValueError('physical-time interpolation would extrapolate;REJECT')
    alpha=(t-times[left])/(times[right]-times[left]);other={key:' '.join(format(x,'.17g') for x in ((1-alpha)*np.fromstring(data[hi][left][key],sep=' ')+alpha*np.fromstring(data[hi][right][key],sep=' '))) for key in ('q','v')}
   for key in ('q','v'):
    x,y=np.fromstring(row[key],sep=' '),np.fromstring(other[key],sep=' ')
    for name,part in (('all',slice(None)),('Skin',slice(0,315)),('Rails',slice(315,None))):values[name+'_'+key]=(float(np.linalg.norm(x[part]-y[part])),float(max(np.linalg.norm(x[part]),np.linalg.norm(y[part]))))
   sx,sy=shape(np.fromstring(row['q'],sep=' ')),shape(np.fromstring(other['q'],sep=' '))
   for key in sx:values[key]=(abs(sx[key]-sy[key]),max(abs(sx[key]),abs(sy[key])))
   for key,(absolute,scale) in values.items():
    relative=absolute/scale if scale else None;records.append(dict(pair=str(lo)+'_'+str(hi),time_s=t,matched_time_s=float(times[j]),quantity=key,absolute=absolute,relative=relative,status='EXACT_ZERO' if scale==0 and absolute==0 else 'PASS' if relative is not None and relative<=.001 else 'FAIL'))
 with (out/'errors.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 worst=max((x for x in records if x['relative'] is not None),key=lambda x:x['relative']);r=dict(status='FAIL' if any(x['status']=='FAIL' for x in records) else 'PASS',scope='actual SOFA all common output-clock state/shape comparison;NOT continuum-between-outputs/energy/contact/grasp',source_summary_hashes={name:sha(parent/'summary.json') for name,parent in zip(a.cases,parents)},binary_sha256=meta[0]['binary_sha256'],relative_gate=.001,absolute_floor='NONE',clock_matching='explicit fine-state linear interpolation at coarse physical times;NO extrapolation or raw time overwrite',maximum_clock_distance_s=clock_error,worst=worst,number_of_compared_observables=len(records),errors_sha256=sha(out/'errors.csv'),endpoint_only_prior_result='not revoked;must not be called full-window convergence',energy='NOT ASSESSED',work='NOT ASSESSED');write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
