"""Stock Native RigidMapping load transfer using actual B3 guide reference.
No FEM/contact/cable; this isolates mapping and public mass, not full joints.
"""
import argparse,csv,json,copy,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
from native_bending_coupon import guarded,add,flat

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True)
    p.add_argument('--load',choices=['translation','couple'],required=True);a=p.parse_args()
    src=BASE/'results/b3_high_force_isolation1105';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    old=ET.parse(src/'scene.scn').getroot();g=old.find("./Node[@name='guides0']")
    frame=np.fromstring(g.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)[0]
    points=np.fromstring(g.find("./Node[@name='anchors']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)[:3]
    root=ET.Element('Node',name='root',dt='0.00001',gravity='0 0 0')
    plugins=['AnimationLoop','Constraint.Lagrangian.Solver','LinearSolver.Direct','Mass','MechanicalLoad','ODESolver.Backward','StateContainer','Mapping.NonLinear']
    for n in plugins:add(root,'RequiredPlugin',pluginName='Sofa.Component.'+n)
    binary=next(Path(n.get('pluginName')) for n in old.iter('RequiredPlugin') if 'libReGripProductSequence.so' in n.get('pluginName',''))
    add(root,'RequiredPlugin',pluginName=str(binary));add(root,'DefaultAnimationLoop')
    add(root,'BlockGaussSeidelConstraintSolver',name='constraints',tolerance='1e-10',maxIterations=1000,computeConstraintForces=1)
    add(root,'EulerImplicitSolver',rayleighMass=0,rayleighStiffness=0)
    add(root,'SparseLDLSolver',template='CompressedRowSparseMatrixd')
    body=add(root,'Node',name='body');add(body,'MechanicalObject',name='frames',template='Rigid3d',position=' '.join(map(str,frame)))
    body.append(copy.deepcopy(g.find('UniformMass')))
    add(body,'NativeRigidJournal',body='@frames',solver='@../constraints',auditMass=1,filename=str(out/'rigid.csv'))
    child=add(body,'Node',name='anchors');add(child,'MechanicalObject',name='points',template='Vec3d',position=flat(points))
    forces=np.zeros((3,3))
    if a.load=='translation':forces[:,2]=1e-6/3
    else:forces[0,2]=1e-6;forces[1,2]=-1e-6
    add(child,'ConstantForceField',indices='0 1 2',forces=flat(forces))
    add(child,'RigidMapping',input='@../frames',output='@points',globalToLocalCoords=1,rigidIndexPerPoint='0 0 0',mapMatrices=1)
    add(child,'NativePointJournal',body='@points',filename=str(out/'points.csv'))
    ET.ElementTree(root).write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes())
    r=points-frame[:3]
    def skew(v):return np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    J=np.concatenate([np.column_stack([np.eye(3),-skew(x)]) for x in r])
    cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','4','--hideProgressBar',str(out/'scene.scn')]
    pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),binary_sha256=sha(binary),binary=str(binary),SDK='/home/ubuntu/SOFA/v26.06.00',load=a.load,force_N=forces.tolist(),reference_frame=frame.tolist(),reference_points=points.tolist(),command=cmd,estimated_runtime_s=1,child_limit_s=60,memory_GiB=4,three_point_rank=int(np.linalg.matrix_rank(J)),two_point_rank=int(np.linalg.matrix_rank(J[:6])))
    (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',60)
    logs=''.join((out/'process'/f).read_text() for f in ('stdout.log','stderr.log'))
    result=dict(status='FAIL_EXECUTION',process=proc,physical_validation='NOT QUALIFIED',scope='Native mapping/mass coupon only;not FEM joint or grasp qualification')
    if proc['exit_code']==0 and '[ERROR]' not in logs and (out/'rigid.csv').exists():
        rows=list(csv.DictReader((out/'rigid.csv').open()));pr=list(csv.DictReader((out/'points.csv').open()))
        mass=json.loads((out/'rigid.csv.mass.json').read_text())['elements'][0];M=np.array(mass['matrix'])
        expected=np.linalg.solve(M,J.T@forces.ravel())*1e-5
        v=np.fromstring(rows[0]['rigid_v'],sep=' ');err=np.linalg.norm(v-expected)/np.linalg.norm(expected)
        maxmap=0
        for row,point in zip(rows,pr):
            q=np.fromstring(row['rigid_q'],sep=' ');actual=np.fromstring(point['q'],sep=' ').reshape(-1,3)
            predicted=Rotation.from_quat(q[3:]).apply(r)+q[:3]
            maxmap=max(maxmap,float(abs(actual-predicted).max()))
        result.update(status='PASS_MAPPING_COUPON_ONLY' if len(rows)==4 and len(pr)==4 and err<=.001 and maxmap<=1e-12 else 'FAIL_MAPPING_COUPON',outputs=len(rows),public_mass_matrix=M.tolist(),first_velocity_expected=expected.tolist(),first_velocity_actual=v.tolist(),first_step_velocity_relative_error=float(err),mapped_position_max_error_m=maxmap,three_point_rank=pre['three_point_rank'],two_point_rank=pre['two_point_rank'],physical_work_energy=None)
    (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

if __name__=='__main__':main()
