"""Bounded native K/force queries, projected spectrum and q/v observer regression.
No matrix solve or new physics implementation; failed native solves stay failed.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.linalg import eigvalsh
from native_bending_coupon import BASE,ROOT,add,sha,guarded

def main():
    csv.field_size_limit(64*1024*1024)
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    build=BASE/'cad/build_elastic_observer400';binary=build/'libReGripElasticObserver.so'
    deps=subprocess.check_output(['ldd',str(binary)],text=True)
    if any('libSofa' in line and '=>' in line and '/home/ubuntu/SOFA/v26.06.00/' not in line for line in deps.splitlines()):raise ValueError('nonmatching SDK dependency')
    (out/'ldd.txt').write_text(deps)
    for name in ('Observer.cpp','CMakeLists.txt'):
        (out/name).write_bytes((BASE/'sofa/native_elastic_observer'/name).read_bytes())
    (out/'CMakeCache.txt').write_bytes((build/'CMakeCache.txt').read_bytes())
    records=[]
    for name,source in [('solid_tetra',BASE/'results/native_traction_cross3_389/tetra_21'),
                        ('solid_hexa',BASE/'results/native_traction_cross3_389/hexa_21'),
                        ('thin_tetra',BASE/'results/native_static_bending372/21')]:
        d=out/name;d.mkdir();tree=ET.parse(source/'scene.scn');root=tree.getroot()
        root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
        journal=root.find('.//NativePointJournal');journal.set('filename',str(d/'states.csv'))
        node=root.find('./Node');ff=node.find('TetrahedronFEMForceField')
        if ff is None:ff=node.find('HexahedronFEMForceField')
        ff.set('name','elastic')
        add(node,'NativeElasticMatrixObserver',body='@dofs',elastic='@elastic',filename=str(d/'native'))
        q=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)
        if q.size>4096:raise ValueError('dense diagnostic matrix preflight limit')
        tree.write(d/'scene.scn')
        process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
        record=dict(case=name,process=process,scene_sha256=sha(d/'scene.scn'),status='FAIL_NATIVE_SOLVE',observer_state_identity=None)
        matrixfile=d/'native.matrix.csv'
        if matrixfile.exists():
            K=np.zeros((q.size,q.size))
            for row in csv.DictReader(matrixfile.open()):K[int(row['i']),int(row['j'])]=float(row['K_N_per_m'])
            fixed=np.fromstring(node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int)
            free=np.ones(q.size,dtype=bool)
            for i in fixed:free[3*i:3*i+3]=False
            A=K[np.ix_(free,free)];eigen=eigvalsh((A+A.T)/2)
            fd=list(csv.DictReader((d/'native.fd.csv').open()))
            record.update(matrix_sha256=sha(matrixfile),projected_min_eigenvalue_N_per_m=float(eigen[0]),
                projected_max_eigenvalue_N_per_m=float(eigen[-1]),
                symmetric_part_condition=float(eigen[-1]/eigen[0]) if eigen[0]>0 else None,
                symmetry_relative=float(np.max(abs(K-K.T))/np.max(abs(K))),
                force_fd=[dict(epsilon_m=float(r['epsilon_m']),relative=float(r['force_fd_error_N_per_m'])/float(r['force_fd_norm_N_per_m'])) for r in fd])
        logs=''.join((d/'process'/n).read_text() for n in ('stdout.log','stderr.log'))
        if process['exit_code']==0 and '[ERROR]' not in logs and 'Line search failed' not in logs and 'failed to converge' not in logs:
            def read(path):return list(csv.DictReader(path.open()))
            observed=read(d/'states.csv');reference=read(source/'states.csv')
            error=max(float(np.max(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')))) for x,y in zip(observed,reference) for key in ('q','v'))
            times=all(x['time_s']==y['time_s'] for x,y in zip(observed,reference))
            record.update(status='COMPLETED_NATIVE_DIAGNOSTIC',observer_state_identity=dict(max_qv_error=error,time_identity=times,count_identity=len(observed)==len(reference)==2,status='PASS_STRICT_API_ONLY' if error<=1e-12 and times and len(observed)==len(reference)==2 else 'FAIL'))
        records.append(record)
    result=dict(scope='Native initial elastic matrix/FD and isolated observer state regression; not B3 certification',
                source_sha256=sha(Path(__file__)),observer_source_sha256=sha(out/'Observer.cpp'),
                binary_sha256=sha(binary),sdk='/home/ubuntu/SOFA/v26.06.00',records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
