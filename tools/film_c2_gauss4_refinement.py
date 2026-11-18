"""Same-binary nonlinear startup refinement;no frozen-reference substitution."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--actual',action='store_true');p.add_argument('--cases',nargs=3,default=('20261119_c2_gauss4_probe1668','20261119_c2_gauss4_half1669','20261119_c2_gauss4_quarter1670'));a=p.parse_args();names=a.cases;folders=[ROOT/'results'/('autonomous_film_'+n) for n in names];meta=[json.loads((f/'summary.json').read_text()) for f in folders];data=[]
 if len({m.get('Newton_tolerance_Ns',1e-18) for m in meta})!=1:raise ValueError('time refinement must preserve Newton stopping input')
 for folder,m in zip(folders,meta):
  qualified=(m.get('status')=='PASS' and m.get('contact')=='NONE' and m.get('duration_s') in (.0002,.001) and m['duration_s']==meta[0]['duration_s'] and max(m['endpoint_max_abs'].values())<=1e-12 and max(m['ALL_four_stages_max_abs'].values())<=1e-12) if a.actual else (m.get('toy_gate')=='PASS' and m.get('FD_query_state_stages_EXACT'))
  if not qualified or m['binary_sha256']!=meta[0]['binary_sha256'] or m['source_hashes']!=meta[0]['source_hashes']:raise ValueError('same binary/ALL sources/qualified nonlinear cases required')
  for name,digest in m['raw_hashes'].items():
   if sha(folder/name)!=digest:raise ValueError('immutable startup raw changed')
  row=list(csv.DictReader((folder/('actual.csv' if a.actual else 'plain.csv')).open()))[-1];data.append(row)
 if len({x['time'] for x in data})!=1:raise ValueError('identical accumulated physical endpoint required')
 errors={}
 for l,h in ((0,1),(1,2),(0,2)):
  x,y=data[l],data[h];pair={}
  for key in ('q','v'):
   u,v=np.fromstring(x[key],sep=' '),np.fromstring(y[key],sep=' ')
   for name,part in (('all',slice(None)),('Skin',slice(0,315)),('Rails',slice(315,None))):
    absolute=float(np.linalg.norm(u[part]-v[part]));scale=float(max(np.linalg.norm(u[part]),np.linalg.norm(v[part])));relative=absolute/scale if scale else 0.;pair[name+'_'+key]=dict(absolute=absolute,relative=relative,status='PASS' if relative<=.001 else 'FAIL')
  sx,sy=shape(np.fromstring(x['q'],sep=' ')),shape(np.fromstring(y['q'],sep=' '))
  for key in sx:
   absolute=abs(sx[key]-sy[key]);scale=max(abs(sx[key]),abs(sy[key]));relative=absolute/scale if scale else 0.;pair[key]=dict(absolute=absolute,relative=relative,status='PASS' if relative<=.001 else 'FAIL')
  errors[str(l)+'_'+str(h)]=pair
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');r=dict(status='PASS' if all(x['status']=='PASS' for pair in errors.values() for x in pair.values()) else 'FAIL',scope='independent SAME nonlinear FEM200us8/16/32-substep state/shape comparison ONLY;NOT actual SOFA/full time/energy/grasp',source_commit=meta[0]['source_commit'],source_summary_hashes={n:sha(f/'summary.json') for n,f in zip(names,folders)},binary_sha256=meta[0]['binary_sha256'],ALL_model_sources_EXACT=True,Newton_residual_tolerance=(meta[0].get('Newton_tolerance_Ns',1e-24) if a.actual else meta[0].get('Newton_tolerance_Ns',1e-18)),relative_gate=.001,absolute_floor='NONE',energy='NOT ASSESSED',work='NOT ASSESSED',errors=errors,worst=max((dict(pair=label,quantity=k,**v) for label,pair in errors.items() for k,v in pair.items()),key=lambda x:x['relative']),selected_SOFA_method=None);r['scope']=('actual SOFA SAME nonlinear bounded window all-pair state/shape comparison ONLY;NOT full time/energy/contact/grasp' if a.actual else r['scope']);write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k!='errors'}))
if __name__=='__main__':main()
