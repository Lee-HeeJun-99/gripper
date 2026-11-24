"""Read-only Native/independent reference comparison for new traction control."""
import csv,json,subprocess,argparse
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from layer_face_load import tip_load
from layer_bending_reference import reference
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/layer_traction_native1282';m=json.loads((src/'mesh.json').read_text());q=np.array(m['q0']);t=np.array(m['tetrahedra']);F,_,_=tip_load(q,t,[0,0,-5e-5]);r=reference(q,t,F);rows=list(csv.DictReader((src/'layer0.csv').open()));actual=np.fromstring(rows[-1]['q'],sep=' ').reshape(-1,3)-q
 error=float(abs(actual-r['u']).max());last=np.array([np.fromstring(v['v'],sep=' ').reshape(-1,3) for v in rows[-50:]])
 d=dict(status='PASS_SCOPED_SMALL_STRAIN_REFERENCE' if error<=1e-12 else 'FAIL_REFERENCE',max_displacement_error_m=error,native_tip_m=float(actual[q[:,0]==.04,2].mean()),reference_tip_m=r['reference_tip_m'],reference_free_residual_N=r['reference_free_residual_N'],reference_root_reaction_N=r['reference_root_reaction_N'],last50_max_node_speed_m_s=float(np.linalg.norm(last,axis=2).max()),inputs={str(f.relative_to(BASE)):sha(f) for f in (src/'scene.scn',src/'mesh.json',src/'layer0.csv',src/'preflight.json')},source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),physical_validation='NOT QUALIFIED',scope='Read-only endpoint comparison to independent linear CST. No all-time, mesh, contact, energy or grasp certification. Reference reaction is NOT measured Native root reaction.',native_root_reaction_N=None,native_energy_J=None)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
