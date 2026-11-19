"""Fine native Rail FAILED-frame force inventory; NEVER equilibrium/PASS data."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,sha,guarded
from observer_identity import compiled_observer

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);binary,compiled=compiled_observer('451')
    (out/'Observer.cpp').write_bytes(compiled.read_bytes());(out/'CMakeLists.txt').write_bytes((BASE/'results/native_beam_accepted452/CMakeLists.txt').read_bytes())
    (out/'CMakeCache.txt').write_bytes((BASE/'cad/build_accepted_observer451/CMakeCache.txt').read_bytes())
    (out/'ldd.txt').write_text(subprocess.check_output(['ldd',str(binary)],text=True));records=[]
    for nx in (41,81):
        d=out/str(nx);d.mkdir();source=BASE/'results/native_rectangular_centered_refine449'/str(nx)/'scene.scn'
        tree=ET.parse(source);root=tree.getroot();node=root.find('./Node')
        for plugin in (str(binary),'Sofa.Component.LinearSystem'):root.insert(0,ET.Element('RequiredPlugin',pluginName=plugin))
        ET.SubElement(node,'MatrixLinearSystem',dict(template='CompressedRowSparseMatrixd',name='diagnosticSystem'))
        node.find('SparseLDLSolver').set('linearSystem','@diagnosticSystem')
        ET.SubElement(node,'NativeRigidTangentObserver',dict(body='@dofs',elastic='@elastic',interpolation='@interpolation',system='@diagnosticSystem',filename=str(d/'initial'),amplitude='0'))
        ET.SubElement(node,'NativeRigidAcceptedObserver',dict(body='@dofs',elastic='@elastic',filename=str(d/'FAILED_FRAME_DIAGNOSTIC.csv')))
        node.find('./Node/NativePointJournal').set('filename',str(d/'FAILED_CENTERS_NOT_ACCEPTED.csv'));tree.write(d/'scene.scn')
        process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','1','--hideProgressBar',d/'scene.scn'],d/'process',480)
        q0=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)
        fixed=np.fromstring(node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int);free=np.ones(nx,dtype=bool);free[fixed]=False
        r=dict(nx=nx,process=process,source_scene_sha256=sha(source),scene_sha256=sha(d/'scene.scn'),status='BLOCKED_FAILED_FRAME_UNAVAILABLE',fixed_nodes=fixed.tolist())
        if (d/'FAILED_FRAME_DIAGNOSTIC.csv').exists():
            rows=list(csv.DictReader((d/'FAILED_FRAME_DIAGNOSTIC.csv').open()))
            if len(rows)==nx:
                q=np.array([[float(row[k]) for k in ('x_m','y_m','z_m','qx','qy','qz','qw')] for row in rows]);f=np.array([[float(row[k]) for k in ('fx_N','fy_N','fz_N','tx_Nm','ty_Nm','tz_Nm')] for row in rows]);F=np.zeros_like(f);F[-1,2]=-1e-8;res=f+F
                K=np.zeros((6*nx,6*nx))
                for row in csv.DictReader((d/'initial.dforce.csv').open()):K[int(row['i']),int(row['j'])]=float(row['K'])
                envelope=np.zeros((nx,6));envelope[:,:3]=np.abs(np.spacing(q[:,:3]))*.5
                estimate=(np.abs(K)@envelope.ravel()).reshape(-1,6)
                index=int(np.flatnonzero(free)[np.argmax(abs(res[free,0]))])
                np.savez(d/'FAILED_STATE_AND_INITIAL_K_NOT_EQUILIBRIUM.npz',q_failed=q,q_reference=q0,initial_K=K,force=f,external_force=F,free=free)
                r.update(status='FAILED_FRAME_DIAGNOSTIC_ONLY',free_axial_residual_N=float(np.linalg.norm(res[free,0])),free_transverse_residual_N=float(np.linalg.norm(res[free,1:3])),free_torque_residual_Nm=float(np.linalg.norm(res[free,3:])),
                    largest_axial_node=index,largest_axial_residual_N=float(res[index,0]),one_ULP_x_m=float(abs(np.spacing(q[index,0]))),
                    initial_linear_half_ULP_force_envelope_N=float(np.linalg.norm(estimate[free,:3])),
                    envelope_scope='initial linear absolute-K half-ULP envelope;NOT lower bound,nonlinear proof or residual floor',
                    failed_tip_displacement_m=float(-q[-1,2]),state_qualification='FAIL449 preserved;frame is not accepted equilibrium')
        records.append(r)
    result=dict(scope='Failed fine-frame diagnostics only;NO equilibrium,mesh or B3 PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),producer_sha256=sha(Path(__file__)),binary_sha256=sha(binary),observer_source_sha256=sha(compiled),sdk='/home/ubuntu/SOFA/v26.06.00',records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
