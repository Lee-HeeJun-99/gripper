"""Same-load attachment phase comparison; never extrapolate to full grasp."""
import argparse,csv,json
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--coarse',default='attachment_window128');p.add_argument('--fine',default='attachment_window129');a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);names=['rail_low6400_100',a.coarse,a.fine];data={};inputs={}
 for name in names:
  directory=ROOT/'results'/('autonomous_film_20261116_'+name)
  if json.loads((directory/'summary.json').read_text())['status']!='PASS':raise RuntimeError('incomplete execution')
  path=directory/'1/journal.csv';inputs[str(path.relative_to(ROOT))]=sha(path);rows=list(csv.DictReader(path.open()));d={key:np.array([float(r[key]) for r in rows]) for key in ('time','skin_tip_z','U_shell','U_attachment','K','tendon_work','cable_length')};d['cable_displacement']=d.pop('cable_length')-200;data[name]=d
 comparisons={}
 for one,two in ((names[0],names[2]),(names[1],names[2])):
  x,y=data[one],data[two];phases={}
  for lo,hi in ((0,1),(1,1.2),(0,1.2)):
   mask=(x['time']>=lo-1e-12)&(x['time']<=hi+1e-12);metrics={}
   for key in x:
    if key=='time':continue
    fine=np.interp(x['time'][mask],y['time'],y[key]);absolute=float(max(abs(x[key][mask]-fine)));scale=float(max(abs(fine)));relative=absolute/scale if scale else (0 if absolute==0 else None);metrics[key]=dict(absolute=absolute,relative=relative,status='PASS' if relative is not None and relative<=.001 else 'FAIL')
   phases[f'{lo}:{hi}']=metrics
  comparisons[one+':'+two]=phases
 ok=all(v['status']=='PASS' for pair in comparisons.values() for phase in pair.values() for v in phase.values());write_json(out/'summary.json',dict(time_status='PASS' if ok else 'FAIL',scope='0–1.2s same-input low-load no-contact transient only;not4s cycle or complete state convergence',inputs=inputs,comparisons=comparisons,full_cycle='FAIL retained',free_grasp='NOT RUN'));print(json.dumps(dict(time_status='PASS' if ok else 'FAIL',attachment_relative={k:{phase:values['U_attachment']['relative'] for phase,values in pair.items()} for k,pair in comparisons.items()})))
if __name__=='__main__':main()
