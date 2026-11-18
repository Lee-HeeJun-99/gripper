"""All-pair local shape errors;avoid absolute rigid-position norm masking film."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_transmission_linear import mapping,shape
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text())
 if m['process']['exit_code']!=0 or m['status'] not in ('PASS','FAIL'):raise ValueError('completed reference,not partial CSV required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('reference raw changed')
 rows=list(csv.DictReader((src/'states.csv').open()));P=mapping();values=[]
 for r in rows:
  q=np.fromstring(r['q'],sep=' ');v=np.fromstring(r['v'],sep=' ');item={'all_film_q':q[:1947],'all_film_v':v[:1947]}
  for f in range(3):
   for key,value in shape(P@q[649*f:649*(f+1)]).items():item[f'finger{f}_{key}']=np.array([value])
  values.append(item)
 pairs={}
 for i in range(len(rows)):
  for j in range(i+1,len(rows)):
   pair={}
   for key in values[i]:
    x,y=values[i][key],values[j][key];absolute=float(np.linalg.norm(x-y));scale=float(max(np.linalg.norm(x),np.linalg.norm(y)));relative=absolute/scale if scale else 0.;pair[key]=dict(absolute=absolute,relative=relative,status='PASS' if relative<=.001 else 'FAIL')
   pairs[rows[i]['steps']+'_'+rows[j]['steps']]=pair
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(ROOT/'tools/film_transmission_linear.py',out/'shape_helper.py');r=dict(status='PASS' if all(v['status']=='PASS' for pair in pairs.values() for v in pair.values()) else 'FAIL',scope='read-only all-pair local film/curvature errors ONLY;NOT macro trajectory/actual SOFA/wrapping/grasp certification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),reference_summary_sha256=sha(src/'summary.json'),shape_helper_sha256=sha(out/'shape_helper.py'),pairs=pairs,relative_gate=.001,shape_definition='existing displacement+rest mean-line/discrete turn curvature,NOT contact coverage',absolute_rigid_position_excluded=True);write_json(out/'summary.json',r);print(json.dumps(dict(status=r['status'],scope=r['scope'],maximum_relative=max(v['relative'] for pair in pairs.values() for v in pair.values()),failing_keys={pair:[key for key,v in metrics.items() if v['status']=='FAIL'] for pair,metrics in pairs.items()})))
if __name__=='__main__':main()
