"""Strict actual rigid collision representation versus free object API states."""
import argparse,json
from pathlib import Path
import numpy as np
from skin_load_assess import BASE,read,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);meta=json.loads((src/'summary.json').read_text())
 if meta['status']!='RUN_COMPLETED_NOT_QUALIFIED':raise ValueError('completed actual trial required')
 body=read(src/'object.csv');coll=read(src/'collision_object.csv')
 if len(body)!=len(coll) or len(body)!=meta['steps']:raise ValueError('all completed API states required')
 clock=max(abs(float(x['time_s'])-float(y['time_s'])) for x,y in zip(body,coll));errors={key:max(float(np.max(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')))) for x,y in zip(body,coll)) for key in ('rigid_q','rigid_v')};result=dict(status='PASS' if max(clock,*errors.values())<=1e-12 else 'FAIL',scope='STRICT1e-12 actual free-body vs IdentityMapping Rigid3 collision pose/velocity only,NOT contact or time-convergence certification',case=a.case,rows=len(body),clock_error_s=clock,component_errors=errors,source_sha256=sha(Path(__file__)),input_hashes={f.name:sha(f) for f in (src/'summary.json',src/'object.csv',src/'collision_object.csv')});(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
