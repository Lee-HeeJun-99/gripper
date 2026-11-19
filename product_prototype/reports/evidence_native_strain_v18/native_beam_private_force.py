"""Native force query at PRIVATE linearized reference; NEVER accepted coordinates.
Amplitude scaling changes the test load,not dt. Stock unloaded native scene only.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial.transform import Rotation
from native_bending_coupon import BASE,ROOT,flat,sha,guarded
from observer_identity import compiled_observer

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True)
    p.add_argument('--reference',choices=['linear','second-order'],default='linear')
    p.add_argument('--reinforce-length',action='store_true',help='NEW native force approximation candidate,not an equivalent numerical fix');a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    build=BASE/'cad/build_private_rigid441';binary,compiled_source=compiled_observer('441')
    deps=subprocess.check_output(['ldd',str(binary)],text=True)
    if any('libSofa' in s and '=>' in s and '/home/ubuntu/SOFA/v26.06.00/' not in s for s in deps.splitlines()):raise ValueError('SDK mismatch')
    (out/'ldd.txt').write_text(deps)
    (out/'Observer.cpp').write_bytes(compiled_source.read_bytes())
    (out/'CMakeLists.txt').write_bytes((BASE/'results/native_beam_private_force442/CMakeLists.txt').read_bytes())
    (out/'CMakeCache.txt').write_bytes((build/'CMakeCache.txt').read_bytes())
    reference=BASE/'results/native_beam_precision_assess440/PRIVATE_LINEAR_REFERENCE_NOT_ACCEPTED_STATE.npz'
    data=np.load(reference);K=data['K'];u=data['u_linear_reference'].reshape(-1,6);F=data['F'].reshape(-1,6)
    source=BASE/'results/native_beam_reference_precision439/flat_straight0_control'
    control=list(csv.DictReader((source/'states.csv').open()));records=[]
    for scale in (1.,.5,.1,.01):
        d=out/f'scale_{scale:g}';d.mkdir();tree=ET.parse(source/'scene.scn');root=tree.getroot();node=root.find('./Node')
        if a.reinforce_length:node.find('AdaptiveBeamForceFieldAndMass').set('reinforceLength','1')
        q=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);probe=q.copy();query_u=scale*u.copy()
        if a.reference=='second-order':
            # PRIVATE geometric hypothesis only: -1/2 integral(w'(s)^2 ds),
            # Euler cantilever slope at free length95mm;NOT solved equilibrium.
            x=np.maximum(q[:,0]-.005,0);L=.095;EI=250e6*(.002*.0005**3/12);force_scale=scale*1e-6
            query_u[:,0]-=force_scale**2/(8*EI**2)*(4*L**2*x**3/3-L*x**4+x**5/5)
        probe[:,:3]+=query_u[:,:3];probe[:,3:]=(Rotation.from_rotvec(query_u[:,3:])*Rotation.from_quat(q[:,3:])).as_quat()
        if not np.isfinite(probe).all() or np.max(abs(np.linalg.norm(probe[:,3:],axis=1)-1))>1e-12:raise ValueError('invalid PRIVATE Rigid3 pose')
        represented=np.column_stack([probe[:,:3]-q[:,:3],(Rotation.from_quat(probe[:,3:])*Rotation.from_quat(q[:,3:]).inv()).as_rotvec()])
        np.savez(d/'PRIVATE_QUERY_NOT_ACCEPTED_STATE.npz',q_reference=q,q_private=probe,u_scaled=scale*u,u_query=query_u,u_represented=represented,F_scaled=scale*F)
        root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
        ET.SubElement(node,'NativeRigidTangentObserver',dict(body='@dofs',elastic='@elastic',filename=str(d/'native'),privatePositions=flat(probe)))
        node.find('./Node/NativePointJournal').set('filename',str(d/'states.csv'));tree.write(d/'scene.scn')
        process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
        logs=''.join((d/'process'/f).read_text() for f in ('stdout.log','stderr.log'))
        r=dict(scale=scale,force_N=scale*1e-6,process=process,scene_sha256=sha(d/'scene.scn'),status='FAIL_QUERY')
        if process['exit_code']==0 and not any(s in logs for s in ('[ERROR]','Line search failed','failed to converge','Unused Attribute')):
            rows=list(csv.DictReader((d/'states.csv').open()))
            force=np.array([[float(row[k]) for k in ('fx_N','fy_N','fz_N','tx_Nm','ty_Nm','tz_Nm')] for row in csv.DictReader((d/'native.probe.csv').open())])
            residual=force+scale*F;represented_residual=(-K@represented.ravel()).reshape(-1,6)+scale*F
            force_defect=force+(K@represented.ravel()).reshape(-1,6)
            representation_error=(K@(represented-query_u).ravel()).reshape(-1,6)
            errors={key:max(float(np.max(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')))) for x,y in zip(rows,control)) for key in ('q','v')}
            r.update(status='PRIVATE_FORCE_QUERY_ONLY' if len(rows)==len(control)==2 and all(v==0 for v in errors.values()) else 'FAIL_STATE_IDENTITY',actual_state_error=errors,
                actual_times_identical=[x['time_s'] for x in rows]==[x['time_s'] for x in control],
                free_axial_residual_N=float(np.linalg.norm(residual[2:,0])),free_transverse_residual_N=float(np.linalg.norm(residual[2:,1:3])),
                free_torque_residual_Nm=float(np.linalg.norm(residual[2:,3:])),
                represented_linear_force_residual_N=float(np.linalg.norm(represented_residual[2:,:3])),
                represented_linear_torque_residual_Nm=float(np.linalg.norm(represented_residual[2:,3:])),
                nonlinear_vs_represented_force_N=float(np.linalg.norm(force_defect[2:,:3])),
                coordinate_representation_force_error_N=float(np.linalg.norm(representation_error[2:,:3])),
                global_internal_force_N=force[:,:3].sum(axis=0).tolist(),
                global_internal_moment_Nm=(np.cross(probe[:,:3],force[:,:3]).sum(axis=0)+force[:,3:].sum(axis=0)).tolist())
        records.append(r)
    result=dict(scope='Native PRIVATE reference query only;actual unloaded state unchanged;NOT loaded equilibrium,trajectory or B3',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),producer_sha256=sha(Path(__file__)),
        binary_sha256=sha(binary),observer_source_sha256=sha(out/'Observer.cpp'),reference_sha256=sha(reference),
        private_reference_type=a.reference,reinforce_length_candidate=a.reinforce_length,
        model_scope='native reinforceLength changes axial force approximation;NOT equivalent solver fix' if a.reinforce_length else 'baseline native force model',sdk='/home/ubuntu/SOFA/v26.06.00',records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
