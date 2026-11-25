"""Native axial compliant-pivot torsion, independent of prior bending coupon."""
import argparse,csv,copy,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from native_bending_coupon import guarded
from finite_hardware_grasp_pilot import flat
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());E=250e6;nu=.3;radius=.00025;L=.003;G=E/(2*(1+nu));J=np.pi*radius**4/2;theta=json.loads((BASE/'results/bellcrank_link1843/summary.json').read_text())['maximum_angle_rad'];moment=theta*G*J/L;records=[]
 for count in (3,5,9):
  folder=out/f'n{count}';folder.mkdir();src=BASE/f'results/root_flexure1850/n{count}/scene.scn';root=ET.parse(src).getroot();node=root.find("Node[@name='flexure']");node.find('ConstantForceField').set('forces',flat([[0,0,0,moment,0,0]]))
  for e in root.iter():
   if e.get('filename'):e.set('filename',str(folder/Path(e.get('filename')).name))
  ET.ElementTree(root).write(folder/'scene.scn');process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','3','--hideProgressBar',folder/'scene.scn'],folder/'process',60);logs=''.join((folder/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));record=dict(nodes=count,process=process,status='FAIL_NATIVE_TORSIONAL_PIVOT',source_scene_sha256=sha(src),scene_sha256=sha(folder/'scene.scn'),errors=[s for s in logs.splitlines() if '[ERROR]'in s])
  if process['exit_code']==0 and '[ERROR]'not in logs:
   rows=list(csv.DictReader((folder/'states.csv').open()));states=[np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in rows];assert len(states)==3;q=states[-1];rv=Rotation.from_quat(q[-1,3:]).as_rotvec();angle=float(rv[0]);reference_error=abs(angle-theta)/abs(theta);rest=np.zeros((count,3));rest[:,0]=np.linspace(0,L,count);translation_error=float(abs(q[:,:3]-rest).max());stationarity=float(abs(states[-1]-states[-2]).max());record.update(status='PASS_STATIC_TORSIONAL_PIVOT_REFERENCE_ONLY' if reference_error<=.01 and max(translation_error,stationarity)<=1e-12 else 'FAIL_STATIC_TORSION_REFERENCE_OR_DRIFT',tip_angle_rad=angle,angle_reference_relative_error=reference_error,maximum_centreline_translation_m=translation_error,last_state_change=stationarity)
  records.append(record)
 pairs=[dict(nodes=[x['nodes'],y['nodes']],angle_relative_difference=abs(x['tip_angle_rad']-y['tip_angle_rad'])/max(abs(x['tip_angle_rad']),abs(y['tip_angle_rad']))) for k,x in enumerate(records) for y in records[k+1:] if 'tip_angle_rad'in x and 'tip_angle_rad'in y]
 result=dict(status='PASS_STATIC_TORSIONAL_PIVOT_MESH_REFERENCE_SCOPE' if all(r['status']=='PASS_STATIC_TORSIONAL_PIVOT_REFERENCE_ONLY' for r in records) and len(pairs)==3 and all(r['angle_relative_difference']<=.01 for r in pairs) else 'FAIL_OR_BLOCKED_STATIC_TORSIONAL_PIVOT',records=records,mesh_pairs=pairs,configuration=dict(length_m=L,radius_m=radius,E_assumed_Pa=E,nu_assumed=nu,G_Pa=G,J_m4=J,target_angle_rad=theta,applied_moment_Nm=moment),reference_outer_shear_strain=radius*theta/L,actual_allowable_shear_strain=None,root_torque_reaction_Nm=None,strain_energy_J=None,source_sha256=sha(Path(__file__)),scope='Pure torsion in stock circular BeamFEM, canonical beam axisX; physical vertical pivot requires corresponding frame placement and compound force/bending tests. Torsional model is distinct from bending; no zero-relative-error floor added, centreline translation checked absolute1e-12. Assumed linear material at3.44percent reference shear, actual validity NOT MEASURED. No dynamic/transmission/Finger/grasp/hardware PASS.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
