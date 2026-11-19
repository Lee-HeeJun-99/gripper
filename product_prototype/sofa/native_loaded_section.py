"""Loaded native sections plus PRIVATE linear backward-error reference.
SciPy's matrix solution is NOT a SOFA accepted state and is never installed into
MechanicalObject. Native ForceField only queries it in a separate local buffer.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.linalg import solve
from native_bending_coupon import BASE,ROOT,flat,sha,guarded
from observer_identity import compiled_observer

def main():
    csv.field_size_limit(64*1024*1024)
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--load',type=float,default=1e-6)
    p.add_argument('--origin-shift',type=float,nargs=3,default=[0,0,0])
    p.add_argument('--components',nargs='+',choices=['skin_only','one_rail','two_rails'],default=['skin_only','one_rail','two_rails']);a=p.parse_args()
    if not 0<a.load<=1e-4:raise ValueError('diagnostic small-load range')
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    binary,compiled_source=compiled_observer('406')
    deps=subprocess.check_output(['ldd',str(binary)],text=True)
    if any('libSofa' in s and '=>' in s and '/home/ubuntu/SOFA/v26.06.00/' not in s for s in deps.splitlines()):raise ValueError('SDK mismatch')
    (out/'ldd.txt').write_text(deps)
    (out/'Observer.cpp').write_bytes(compiled_source.read_bytes())
    (out/'CMakeCache.txt').write_bytes((BASE/'cad/build_elastic_probe406/CMakeCache.txt').read_bytes())
    records=[]
    for component in a.components:
        source=BASE/'results/native_section_spectrum405'/f'{component}_control'
        root=ET.parse(source/'scene.scn').getroot();node=root.find('./Node')
        q=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)
        n=q.size;K=np.zeros((n,n))
        matrix=BASE/'results/native_section_spectrum405'/f'{component}_observed/native.matrix.csv'
        for r in csv.DictReader(matrix.open()):K[int(r['i']),int(r['j'])]=float(r['K_N_per_m'])
        fixed=np.fromstring(node.find('FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int)
        free=np.ones(n,dtype=bool)
        for i in fixed:free[3*i:3*i+3]=False
        # Same physical Skin tip nodes/forces in all three component cases.
        tip=np.flatnonzero((q[:,2]==q[:,2].min())&(q[:,0]<=.05))
        q=q+np.array(a.origin_shift)
        F=np.zeros_like(q);F[tip,0]=-a.load/len(tip)
        u=np.zeros(n);u[free]=solve(K[np.ix_(free,free)],F.ravel()[free],assume_a='gen')
        probe=q+u.reshape(-1,3);represented=(probe-q).ravel()
        ideal_res=(K@u-F.ravel())[free];represented_res=(K@represented-F.ravel())[free]
        d=out/component;d.mkdir()
        np.savez(d/'PRIVATE_matrix_reference_NOT_ACCEPTED_STATE.npz',K=K,q_reference=q,u_linear_reference=u,probe_positions=probe,force=F,free=free)
        runs=[]
        for label,loaded,observed in [('zero_probe',False,True),('loaded_control',True,False),('loaded_probe',True,True)]:
            trial=d/label;trial.mkdir();tree=ET.parse(source/'scene.scn');rt=tree.getroot();nd=rt.find('./Node')
            nd.find('MechanicalObject').set('position',flat(q))
            load=nd.find('ConstantForceField');load.set('indices',' '.join(map(str,tip)));load.set('forces',flat(F[tip] if loaded else np.zeros_like(F[tip])))
            nd.find('NewtonRaphsonSolver').set('relativeSuccessiveStoppingThreshold','1e-12')
            nd.find('NativePointJournal').set('filename',str(trial/'states.csv'))
            if observed:
                rt.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
                ET.SubElement(nd,'NativeElasticMatrixObserver',dict(body='@dofs',elastic='@elastic',filename=str(trial/'native'),probePositions=flat(probe)))
            tree.write(trial/'scene.scn')
            process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',trial/'scene.scn'],trial/'process',480)
            logs=''.join((trial/'process'/f).read_text() for f in ('stdout.log','stderr.log'))
            valid=process['exit_code']==0 and not any(s in logs for s in ('[ERROR]','Line search failed','failed to converge'))
            run=dict(label=label,process=process,status='FAIL_NATIVE_SOLVE',actual_state_error_m=None)
            if valid:
                rows=list(csv.DictReader((trial/'states.csv').open()))
                if len(rows)==2:
                    actual=np.fromstring(rows[-1]['q'],sep=' ').reshape(-1,3)
                    run.update(status='COMPLETED_NATIVE_STATIC_ONLY',actual_state_error_m=float(np.max(abs(actual-(probe if loaded else q)))),
                               actual_skin_tip_displacement_m=float(-(actual-q)[tip,0].mean()))
            if observed and (trial/'native.probe.csv').exists():
                force_rows=list(csv.DictReader((trial/'native.probe.csv').open()))
                f=np.array([[float(r[k]) for k in ('fx_N','fy_N','fz_N')] for r in force_rows]).ravel()
                run.update(private_native_force_residual_N=float(np.linalg.norm((f+F.ravel())[free])),
                    private_native_force_vs_K_defect_N=float(np.linalg.norm((f+K@represented)[free])))
                actual_K=np.zeros_like(K)
                for row in csv.DictReader((trial/'native.matrix.csv').open()):actual_K[int(row['i']),int(row['j'])]=float(row['K_N_per_m'])
                run['initial_K_vs_original_relative']=float(np.linalg.norm(actual_K-K)/np.linalg.norm(K))
            runs.append(run)
        records.append(dict(component=component,force_N=a.load,tip_nodes=len(tip),tip_load_positions_m=q[tip].tolist(),
            matrix_sha256=sha(matrix),private_linear_residual_N=float(np.linalg.norm(ideal_res)),
            private_represented_linear_residual_N=float(np.linalg.norm(represented_res)),
            position_rounding_max_m=float(np.max(abs(represented-u))),
            private_reference_skin_tip_m=float(-u.reshape(-1,3)[tip,0].mean()),runs=runs))
    data=dict(scope='Native LOADED static tests plus private backward-error reference;private positions NOT accepted states;no B3/mesh/time qualification',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(Path(__file__)),
        observer_source_sha256=sha(out/'Observer.cpp'),binary_sha256=sha(binary),sdk='/home/ubuntu/SOFA/v26.06.00',
        force_gate_N=1e-12,origin_shift_m=a.origin_shift,reference_K_scope='original405 matrix; translation invariance checked independently in native observer',records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))

if __name__=='__main__':main()
