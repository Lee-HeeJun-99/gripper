"""Actual all-pair rail-aspect time assessment at recorded physical clocks."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();names=('20261119_rail_aspect_actual_peak1658','20261119_rail_aspect_actual_half1659','20261119_rail_aspect_actual_quarter1660');sources=[ROOT/'results'/('autonomous_film_'+n) for n in names];meta=[json.loads((f/'summary.json').read_text()) for f in sources]
 if any(m['status']!='PASS' for m in meta) or len({m['binary_sha256'] for m in meta})!=1 or any(m['duration_s']!=.01 for m in meta):raise ValueError('completed same-binary same-input10ms actual trials required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');errors=[];summaries={}
 for thickness in ('.075','.1','.125'):
  key=str(float(thickness));data=[]
  for folder,m in zip(sources,meta):
   d=folder/('rail'+key);trial=m['trials'][key]
   for f,digest in trial['raw_hashes'].items():
    if sha(d/f)!=digest:raise ValueError('actual raw changed')
   state=list(csv.DictReader((d/'actual.csv').open()));field=list(csv.DictReader((d/'film.csv').open()));reference=list(csv.DictReader((d/'reference.csv').open()));rows=[]
   for s,f,r in zip(state,field,reference):
    if s['time']!=f['time'] or s['time']!=r['time']:raise ValueError('actual Field/reference clock identity differs')
    row={k:np.fromstring(s[k],sep=' ') for k in ('q','v')}
    for k in ('U_shell','U_attachment','K','T_per_rail','cable_length','tendon_work'):row[k]=np.array([float(f[k])])
    for k in ('U_skin','U_rails','stage_tendon_work_Nmm'):row[k]=np.array([float(r[k])])
    row['cable_shortening']=np.array([200-float(f['cable_length'])]);rows.append(row)
   data.append((np.array([float(x['time']) for x in state]),rows))
  def at(dataset,t):
   clocks,rows=dataset;j=int(np.searchsorted(clocks,t))
   if j<len(clocks) and clocks[j]==t:return rows[j],0.
   if j==0 or j==len(clocks):raise ValueError('no time extrapolation permitted')
   lo,hi=clocks[j-1],clocks[j];weight=(t-lo)/(hi-lo);return {k:(1-weight)*rows[j-1][k]+weight*rows[j][k] for k in rows[0]},min(t-lo,hi-t)
  groups={}
  for l,h in ((0,1),(1,2),(0,2)):
   for t,x in zip(*data[l]):
    y,alignment=at(data[h],t);quantities={k:(x[k],y[k]) for k in x if k not in ('q','v')}
    for k in ('q','v'):
     quantities['all_'+k]=(x[k],y[k]);quantities['Skin_'+k]=(x[k][:315],y[k][:315]);quantities['Rails_'+k]=(x[k][315:],y[k][315:])
    sx,sy=shape(x['q']),shape(y['q'])
    for k in sx:quantities[k]=(np.array([sx[k]]),np.array([sy[k]]))
    for k,(u,v) in quantities.items():
     absolute=float(np.linalg.norm(u-v));scale=float(max(np.linalg.norm(u),np.linalg.norm(v)));relative=absolute/scale if scale else 0.;record=dict(rail_thickness_mm=float(thickness),left_dt_s=meta[l]['nominal_dt_s'],right_dt_s=meta[h]['nominal_dt_s'],actual_comparison_time_s=float(t),quantity=k,absolute=absolute,relative=relative,status='PASS' if relative<=.001 else 'FAIL',nearest_fine_clock_distance_s=alignment);errors.append(record)
     group='legacy_sampled_work' if k=='tendon_work' else 'stage_work' if k=='stage_tendon_work_Nmm' else 'state_energy_shape';groups.setdefault(group,[]).append(relative)
  summaries[key]={k:dict(status='PASS' if max(v)<=.001 else 'FAIL',maximum_relative=max(v)) for k,v in groups.items()}
 with (out/'all_pair_errors.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(errors[0]));w.writeheader();w.writerows(errors)
 r=dict(status='PASS' if all(x['status']=='PASS' for x in errors) else 'FAIL',scope='actual free-coupon0→10ms all-pair200/100/50us time assessment ONLY;NOT contact/grasp',input_summary_hashes={n:sha(f/'summary.json') for n,f in zip(names,sources)},binary_sha256=meta[0]['binary_sha256'],relative_gate=.001,absolute_floor='NONE',time_alignment='linear interpolation at recorded left physical clocks,NO row-index matching/time overwrite/extrapolation;roundoff-sized interpolation distances recorded',maximum_nearest_clock_distance_s=max(x['nearest_fine_clock_distance_s'] for x in errors),results=summaries,worst=max(errors,key=lambda x:x['relative']),failures=sum(x['status']=='FAIL' for x in errors),comparisons=len(errors),contact='NOT RUN',whole_energy='BLOCKED',selected_design=None,raw_hashes={'all_pair_errors.csv':sha(out/'all_pair_errors.csv')});write_json(out/'summary.json',r);print(json.dumps(r))
if __name__=='__main__':main()
