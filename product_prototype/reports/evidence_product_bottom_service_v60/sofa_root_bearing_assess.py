"""Actual ideal-bearing Native DOF/API checks;not physical bearing calibration."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];inputs=[Path(__file__)]
 for case,spin in [('product_root_bearing832',False),('product_root_bearing_spin833',True)]:
  folder=BASE/'results'/case;meta=json.loads((folder/'summary.json').read_text());rows=list(csv.DictReader((folder/'wheel.csv').open()));q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in rows]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in rows]);imp=np.array([np.fromstring(r['object_impulse_Ns_Nms'],sep=' ') for r in rows]);t=np.array([float(r['time_s']) for r in rows]);tree=ET.parse(folder/'scene.scn');joint=tree.find("./Node[@name='wheel']/PartialFixedProjectiveConstraint");mass=np.array(json.loads((folder/'wheel.csv.mass.json').read_text())['elements'][0]['matrix']);free=np.array([2,5]);previous=np.array([0,0,0 if spin else .01,0,0,1 if spin else 0.]);residual=[]
  for vel,pulse in zip(v,imp):residual.append(float(abs((mass@(vel-previous)-pulse)[free]).max()));previous=vel
  reference=np.c_[np.zeros((len(t),2)),np.sin(t/2),np.cos(t/2)] if spin else None;binary_hashes={}
  for plugin in tree.getroot().findall('RequiredPlugin'):
   binary=Path(plugin.get('pluginName'))
   if binary.is_file():binary_hashes[str(binary)]=sha(binary)
  inputs.extend([folder/f for f in ('summary.json','wheel.csv','scene.scn','wheel.csv.mass.json')]);records.append(dict(case=case,spin_only=spin,state_rows=len(rows),fixed_directions=joint.get('fixedDirections'),locked_velocity_max_abs=float(abs(v[:,[0,1,3,4]]).max()),locked_position_max_abs_m=float(abs(q[:,:2]).max()),quaternion_norm_max_error=float(abs(np.linalg.norm(q[:,3:],axis=1)-1).max()),free_DOF_impulse_balance_max_abs_Ns_or_Nms=max(residual),spin_velocity_error_rad_s=float(abs(v[:,5]-1).max()) if spin else None,spin_analytic_quaternion_max_abs_error=float(abs(q[:,3:]-reference).max()) if spin else None,spin_contact_impulse_max_abs_Ns_Nms=float(abs(imp).max()) if spin else None,loaded_observer_binary_hashes=binary_hashes,SDK='/home/ubuntu/SOFA/v26.06.00',projective_reaction_work_J=None,physical_radial_friction=None,physical_qualification=False))
 d=dict(status='PASS_IDEAL_BEARING_DOF_API_SCOPE_ONLY' if all(r['locked_velocity_max_abs']==0 and r['locked_position_max_abs_m']==0 and r['quaternion_norm_max_error']<=1e-12 for r in records) and records[1]['spin_velocity_error_rad_s']<=1e-12 else 'FAIL_IDEAL_BEARING_DOF_API',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x):sha(x) for x in inputs},records=records,scope='TestsNativeidealjoint4locked/2freeDOFcontract onactualruns. ProjectiveDOFreaction/workunmeasured;onlyunrestrictedz/spinimpulsebalanceexamined. Analyticalspinreference isseparatefromNative output. NOactualbearingfriction/clearance/threadstrength/time/mesh/holdingqualification.',fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
