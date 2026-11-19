"""Actual modern assembly versus native legacy K/force FD; diagnostic only.
Only stock FastTriangularBendingSprings is active to isolate its derivative paths.
Failed Native states are never interpreted as accepted physical solutions.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,add,sha,guarded
from observer_identity import compiled_observer

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    binary,compiled_source=compiled_observer('410')
    source=BASE/'results/native_shell_loaded408/21_3/scene.scn';root=ET.parse(source).getroot()
    root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.LinearSystem'))
    root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
    node=root.find('./Node');node.remove(node.find('TriangleFEMForceField'))
    add(node,'MatrixLinearSystem',template='CompressedRowSparseMatrixd',name='system')
    solver=node.find('SparseLDLSolver');solver.set('template','CompressedRowSparseMatrixd');solver.set('linearSystem','@system')
    add(node,'NativeElasticMatrixObserver',body='@dofs',elastic='@bending',filename=str(out/'native'))
    add(node,'NativeAssembledMatrixObserver',system='@system',filename=str(out/'assembled.csv'))
    node.find('NativePointJournal').set('filename',str(out/'FAILED_STATES_NOT_PHYSICS.csv'))
    ET.ElementTree(root).write(out/'scene.scn')
    process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',out/'scene.scn'],out/'process',480)
    q=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);K=np.zeros((q.size,q.size));A=K.copy()
    result=dict(scope='Constant linear spring derivative-path diagnostic,NOT accepted bending or B3 physics',process=process,
        binary_sha256=sha(binary),scene_sha256=sha(out/'scene.scn'),status='BLOCKED_MATRIX_UNAVAILABLE')
    if (out/'native.matrix.csv').exists() and (out/'assembled.csv').exists():
        for row in csv.DictReader((out/'native.matrix.csv').open()):K[int(row['i']),int(row['j'])]=float(row['K_N_per_m'])
        for row in csv.DictReader((out/'assembled.csv').open()):A[int(row['i']),int(row['j'])]=float(row['A'])
        free=np.ones(q.size,dtype=bool)
        for i in np.fromstring(node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int):free[3*i:3*i+3]=False
        reference=K[np.ix_(free,free)];actual=A[np.ix_(free,free)]
        fd=[dict(epsilon_m=float(r['epsilon_m']),relative=float(r['force_fd_error_N_per_m'])/float(r['force_fd_norm_N_per_m'])) for r in csv.DictReader((out/'native.fd.csv').open())]
        result.update(status='DERIVATIVE_PATH_COMPARISON_ONLY',modern_vs_legacy_relative=float(np.linalg.norm(actual-reference)/np.linalg.norm(reference)),
            modern_symmetry_relative=float(np.linalg.norm(actual-actual.T)/np.linalg.norm(actual)),legacy_force_fd=fd,
            physical_static_status='FAIL_OR_NOT_QUALIFIED;derivative matrices are diagnostic even when states fail')
    (out/'Observer.cpp').write_bytes(compiled_source.read_bytes())
    (out/'CMakeLists.txt').write_bytes((BASE/'results/native_bending_matrix_paths415/CMakeLists.txt').read_bytes())
    (out/'ldd.txt').write_text(subprocess.check_output(['ldd',str(binary)],text=True))
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
