"""Bounded union geometry references and facet sensitivity,not SOFA qualification."""
import argparse,json,sys
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);test=BASE/'sofa/test_finite_union.py';testprocess=guarded([sys.executable,test,'-v'],out/'test',480);runs=[]
 for n in (32,64):
  tag=a.tag+'_facets'+str(n);proc=guarded([sys.executable,BASE/'sofa/finite_union_moments.py','--tag',tag,'--segments',str(n)],out/str(n),480);runs.append(dict(segments=n,case=tag,process=proc))
 records=[]
 if testprocess['exit_code']==0 and all(r['process']['exit_code']==0 for r in runs):
  source=[json.loads((BASE/'results'/r['case']/'summary.json').read_text()) for r in runs]
  for x,y in zip(source[0]['records'],source[1]['records']):
   def relative(key):
    a=np.asarray(x[key]);b=np.asarray(y[key]);den=max(np.linalg.norm(a),np.linalg.norm(b));absolute=float(np.linalg.norm(a-b));return dict(absolute_error=absolute,relative_error=float(absolute/den) if den else 0.)
   records.append(dict(cable=x['cable'],station_mm=x['station_mm'],volume=relative('union_volume_mm3'),normalized_inertia=relative('conditional_uniform_density_union_normalized_inertia_mm2'),COM=relative('conditional_uniform_density_union_COM_local_mm')))
 result=dict(status='PASS_UNION_GEOMETRIC_REFERENCES_ONLY' if records else 'FAIL_UNION_REFERENCE',scope='Independent box analytic references,rigid objectivity,annular sector decomposition;conditional common-density geometric union only. Facet differences recorded,NOT physical FEM/contact mesh Gate.',test_sha256=sha(test),producer_sha256=sha(Path(__file__)),test_process=testprocess,runs=runs,records=records,physical_mass_kg=None,CAD_STEP='NOT GENERATED')
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'test_finite_union.py').write_bytes(test.read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
