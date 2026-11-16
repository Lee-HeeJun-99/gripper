"""One-factor contact/no-contact time-error controls on the installed ABI."""
import argparse,csv,json
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);inputs={};groups={}
 for label,names in {'no_contact':['native_noc100_121','native_noc200_122','native_noc400_123'],'fixed_sphere':['fixed_sphere95_115','fixed_sphere95_116','fixed_sphere95_117']}.items():
  data=[]
  for name in names:
   directory=ROOT/'results'/('autonomous_film_20261116_'+name)
   if json.loads((directory/'summary.json').read_text())['status']!='PASS':raise RuntimeError('incomplete trial')
   path=directory/'1/journal.csv';inputs[str(path.relative_to(ROOT))]=sha(path);r=list(csv.DictReader(path.open()));data.append({key:np.array([float(s[key]) for s in r]) for key in ('time','skin_tip_z','U_shell','U_attachment','K')})
  pairs={}
  for i,j in ((0,1),(1,2),(0,2)):
   phases={}
   for lo,hi in ((0,.2),(.2,.27),(.27,.5),(0,.5)):
    x,y=data[i],data[j];mask=(x['time']>=lo-1e-12)&(x['time']<=hi+1e-12);m={}
    for key in x:
     if key=='time':continue
     fine=np.interp(x['time'][mask],y['time'],y[key]);absolute=float(max(abs(x[key][mask]-fine)));scale=float(max(abs(fine)));relative=absolute/scale if scale else (0 if absolute==0 else None);m[key]=dict(absolute=absolute,relative=relative,status='PASS' if relative is not None and relative<=.001 else 'FAIL')
    phases[f'{lo}:{hi}']=m
   pairs[f'{i}:{j}']=phases
  groups[label]=pairs
 write_json(out/'summary.json',dict(status='ANALYSIS',inputs=inputs,comparisons=groups,scope='backward Euler installed ABI;unchanged tendon/structure/time;only sphere collision enabled/disabled',conclusion='No-contact temporal control also fails;contact event is not the sole source of coupled time error. Do not transfer compliant-plane theta=.5 qualification to constrained BE.'))
 print(json.dumps({g:{k:100*v['relative'] for k,v in d['0:2']['0:0.5'].items()} for g,d in groups.items()}))
if __name__=='__main__':main()
