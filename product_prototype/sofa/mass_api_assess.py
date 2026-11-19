"""Check public native element mass matrices and opt-in query purity."""
import argparse,csv,json,hashlib
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1]
def read(p):return list(csv.DictReader(p.open()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='native_mass_api_purity_139');a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);m=json.loads((src/'summary.json').read_text())
 if m['status']!='RUN_COMPLETED_NOT_QUALIFIED':raise ValueError('invalid process is not mass evidence')
 observed=json.loads((src/'guide_frames0.csv.mass.json').read_text())['elements'];g=m['rigid_guides'][0];checks=[]
 for i,item in enumerate(observed):
  mass=g['mass_per_bracket_kg'];I=np.array(g['normalized_inertia_tensors_m2'][i]) if g.get('normalized_inertia_tensors_m2') else np.diag(g['normalized_inertia_m2']);M=np.array(item['matrix']);expected=np.zeros((6,6));expected[:3,:3]=mass*np.eye(3);expected[3:,3:]=mass*I;checks.append(dict(index=i,mass_relative=abs(item['mass_kg']-mass)/mass,translation_block_relative=float(np.linalg.norm(M[:3,:3]-expected[:3,:3])/np.linalg.norm(expected[:3,:3])),rotation_block_relative=float(np.linalg.norm(M[3:,3:]-expected[3:,3:])/np.linalg.norm(expected[3:,3:])),coupling_block_max=float(np.max(abs(M[:3,3:])))))
 prior=BASE/'results/rigidified_out14_actuation_131';old=read(prior/'finger0.csv');rows=read(src/'finger0.csv');error=max(float(np.max(abs(np.fromstring(row[key],sep=' ')-np.fromstring(old[i][key],sep=' ')))) for i,row in enumerate(rows) for key in ('q_m','v_m_s','guide0_q_m','guide1_q_m'));result=dict(status='PASS' if len(observed)==g['frames'] and all(max(c[k] for k in ('mass_relative','translation_block_relative','rotation_block_relative','coupling_block_max'))<=1e-12 for c in checks) and error<=1e-12 else 'FAIL',scope='public INITIAL element mass matrices and4-step passive-query purity,NOT global mass/energy/grasp certification',gate=1e-12,mass_checks=checks,query_purity_max_state_difference=error,source_sha256=sha(Path(__file__)),input_hashes={str(p):sha(p) for p in (src/'summary.json',src/'guide_frames0.csv.mass.json',src/'finger0.csv',prior/'finger0.csv')});(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
