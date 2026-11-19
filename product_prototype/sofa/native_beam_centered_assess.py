"""Actual centered native static coupon checks; fine failed trials stay excluded."""
import argparse,csv,json
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from native_bending_coupon import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    source=BASE/'results/native_beam_accepted452';data=json.loads((source/'summary.json').read_text());records=[];states=[]
    for record in data['records']:
        if record['status']!='PASS_SMALL_LOAD_STATE_AND_FORCE_ONLY':raise ValueError('unqualified actual force/API trial')
        folder=source/record['case'];q0=np.fromstring(ET.parse(folder/'scene.scn').find('./Node/MechanicalObject').get('position'),sep=' ').reshape(-1,7)
        rows=list(csv.DictReader((folder/'accepted.csv').open()));rr=[r for r in rows if int(r['step'])==2]
        q=np.array([[float(r[k]) for k in ('x_m','y_m','z_m')] for r in rr]);quat=np.array([[float(r[k]) for k in ('qx','qy','qz','qw')] for r in rr]);rot=Rotation.from_quat(quat).as_rotvec()
        x=np.maximum(q0[:,0]+.05-.005,0);L=.095;EI=250e6*(.002*.0005**3/12);F=record['force_N']
        w=-F*x*x*(3*L-x)/(6*EI);theta=F*x*(2*L-x)/(2*EI)
        axial=-F*F/(8*EI*EI)*(4*L*L*x**3/3-L*x**4+x**5/5)
        records.append(dict(case=record['case'],force_N=F,actual_tip_m=float(-q[-1,2]),Euler_tip_m=float(-w[-1]),
            all_node_transverse_reference_error_m=float(np.max(abs(q[:,2]-w))),all_node_rotation_reference_error_rad=float(np.max(abs(rot[:,1]-theta))),
            all_node_second_order_axial_reference_error_m=float(np.max(abs(q[:,0]-(q0[:,0]+axial)))),
            reference_scope='Euler/second-order are approximate analytical references,NOT SOFA prescribed states or exact nonlinear solution'))
        states.append((q0,q,rot));
    full0,full,fullrot=states[0];half0,half,halfrot=states[1]
    displacement_error=float(np.max(abs((full-full0[:,:3])-2*(half-half0[:,:3]))))
    zerror=float(np.max(abs(full[:,2]-2*half[:,2])))
    result=dict(scope='Actual21-node STATIC Rail coupon only;NOT B3,Skin,time/mesh convergence or grasp',source_summary_sha256=sha(source/'summary.json'),producer_sha256=sha(Path(__file__)),
        records=records,load_scaling=dict(full_vs_twice_half_displacement_error_m=displacement_error,
        transverse_relative_error=zerror/float(np.max(abs(full[:,2]))),rotation_relative_error=float(np.max(abs(fullrot-2*halfrot)))/float(np.max(abs(fullrot))),
        status='PASS_ABSOLUTE_LOAD_SCALING_ONLY' if displacement_error<=1e-12 else 'FAIL_ABSOLUTE_LOAD_SCALING',gate_m=1e-12),
        spatial_gate='FAIL_OR_BLOCKED:41/81 actual native solves449 failed;no all-pair mesh certification')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axis=plt.subplots(figsize=(7,4))
    for record,(q0,q,rotation) in zip(records,states):axis.plot((q0[:,0]+.05)*1e3,q[:,2]*1e6,'o-',label=f"actual native {record['force_N']:.1e}N")
    axis.set_xlabel('Reference station [mm]');axis.set_ylabel('Actual transverse position [micrometre]')
    axis.set_title('452: static Rail profile;different axis units,NOT aspect-preserving')
    axis.legend();fig.tight_layout();fig.savefig(out/'actual_native_static_profiles.png',dpi=160);plt.close(fig)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
