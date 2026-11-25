"""Actual saved rigid-frame cable kinematics; independent directional FD check."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha

def length(points):return np.linalg.norm(np.diff(points,axis=0),axis=1).sum()

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    src=BASE/'results/yoke_hold_diagnostic1741';root=ET.parse(src/'scene.scn').getroot();results=[];inputs={"scene.scn":sha(src/'scene.scn')}
    for finger in range(3):
        node=root.find(f"Node[@name='guides{finger}']");initial=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)
        rows=list(csv.DictReader((src/f'guide_frames{finger}.csv').open()));inputs[f'guide_frames{finger}.csv']=sha(src/f'guide_frames{finger}.csv')
        for cable in range(2):
            c=node.find(f"Node[@name='cable{cable}']");mapping=c.find('RigidMapping');owners=np.fromstring(mapping.get('rigidIndexPerPoint'),sep=' ',dtype=int)
            world=np.fromstring(c.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)
            local=Rotation.from_quat(initial[owners,3:]).inv().apply(world-initial[owners,:3]);origin=np.fromstring(c.find('CableConstraint').get('pullPoint'),sep=' ')
            values=[];errors=[];lengths=[]
            for row in rows:
                q=np.fromstring(row['rigid_q'],sep=' ').reshape(-1,7)[owners];v=np.fromstring(row['rigid_v'],sep=' ').reshape(-1,6)[owners]
                arm=Rotation.from_quat(q[:,3:]).apply(local);point=q[:,:3]+arm;velocity=v[:,:3]+np.cross(v[:,3:],arm)
                allpoints=np.vstack([origin,point]);allvelocity=np.vstack([np.zeros(3),velocity]);segment=np.diff(allpoints,axis=0)
                rate=float((segment/np.linalg.norm(segment,axis=1)[:,None]*np.diff(allvelocity,axis=0)).sum());values.append(rate);lengths.append(length(allpoints))
                # World-angular velocity: left-composed rotations; never alter Raw.
                eps=1e-6
                def perturbed(sign):
                    turn=Rotation.from_rotvec(sign*eps*v[:,3:]);return np.vstack([origin,q[:,:3]+sign*eps*v[:,:3]+turn.apply(arm)])
                fd=(length(perturbed(1))-length(perturbed(-1)))/(2*eps);errors.append(abs(fd-rate))
            t=np.array([float(r['time_s']) for r in rows]);hold=(t>=1.6-1e-12)&(t<=2+1e-12);rates=np.array(values)
            error=max(errors);assert error<1e-8
            results.append(dict(finger=finger,cable=cable,hold_rate_min_max_mm_s=[float(rates[hold].min()*1000),float(rates[hold].max()*1000)],maximum_directional_FD_error_m_s=error,initial_saved_length_m=float(lengths[0]),last_saved_length_m=float(lengths[-1])))
    d=dict(status='PASS_SAVED_ACCEPTED_GEOMETRIC_RATE_ONLY',results=results,input_sha256=inputs,source_sha256=sha(Path(__file__)),scope='Same accepted q/v and explicit Scene rigidIndexPerPoint; stationary actual root pullPoint. Directional FD is kinematic validation, not time convergence or Native observer purity. No force-phase measurement, input work, live feedback or improved grasp claimed. No Native execution.')
    (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
