"""Correct reference-axis audit of existing1606Raw;never repeatsNative trial."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/spinning_normal_contract1606';prior=json.loads((src/'summary.json').read_text());records=[]
 for r in prior['records']:
  d=src/f"{r['policy']}_spin{int(r['initial_angular_velocity_x_rad_s'])}";root=ET.parse(d/'scene.scn').getroot();dt=float(root.get('dt'));rows=list(csv.DictReader((d/'response1.csv').open()));row=next(x for x in rows if (int(x['row_id'])-int(x['first_row']))%3==0 and float(x['lambda_Ns'])>0);J=np.fromstring(row['object_impulse_Ns_Nms'],sep=' ')/float(row['lambda_Ns']);omega=np.fromstring(root.find("Node[@name='guide1']/MechanicalObject").get('velocity'),sep=' ')[3:];expected=np.cross(Rotation.from_rotvec(dt*omega).apply([0,0,-.03]),J[:3]);state=next(csv.DictReader((d/'guide1.csv').open()));v=np.fromstring(state['rigid_v'],sep=' ');records.append(dict(policy=r['policy'],omega0=omega.tolist(),actual_first_omega=v[3:].tolist(),actual_normal_J_angular_m=J[3:].tolist(),independent_free_rotated_radius_prediction_m=expected.tolist(),maximum_prediction_error_m=float(abs(J[3:]-expected).max()),physical_radial_normal_torque_gate=bool(np.linalg.norm(J[3:])<=1e-12),input_hashes={f:sha(d/f) for f in ('scene.scn','response1.csv','guide1.csv')}))
 d=dict(status='CORRECTED_REFERENCE_AUDIT_NOT_PHYSICAL_PASS',records=records,scope='Original1606NativeRawunchanged;producer1606reference hadYaxis instead ofXaxis,so its reportedpredictionerror isinvalid. This independentlycorrectsreferenceONLY,noNative rerun. Stationarynormalmomentzero;spin generatesnonzeroactualnormalmoment inbothstockMin/Dispatch. Notproof ofwholegraspcausality andnotSDKSolverfix.',source_sha256=sha(Path(__file__)),original_summary_sha256=sha(src/'summary.json'));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
