"""Stock BeamAdapter initial reference inventory; diagnostic assembly, no solve law.
Same-state modern assembly versus full addDForce; keep force/torque units apart.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,ROOT,flat,sha,guarded
from observer_identity import compiled_observer

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    build=BASE/'cad/build_reference_precision438';binary,compiled_source=compiled_observer('438')
    deps=subprocess.check_output(['ldd',str(binary)],text=True)
    if any('libSofa' in line and '=>' in line and '/home/ubuntu/SOFA/v26.06.00/' not in line for line in deps.splitlines()):raise ValueError('SDK mismatch')
    (out/'ldd.txt').write_text(deps)
    (out/'Observer.cpp').write_bytes(compiled_source.read_bytes())
    (out/'CMakeLists.txt').write_bytes((BASE/'results/native_beam_reference_precision439/CMakeLists.txt').read_bytes())
    (out/'CMakeCache.txt').write_bytes((build/'CMakeCache.txt').read_bytes());records=[]
    for geometry,straight in [('flat',True),('flat',False),('curved',False)]:
        for observed in (False,True):
            d=out/f'{geometry}_straight{int(straight)}_{"observed" if observed else "control"}';d.mkdir()
            tree=ET.parse(BASE/'results/native_rectangular_rest423/21/scene.scn');root=tree.getroot();node=root.find('./Node')
            q=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)
            if geometry=='flat':q[:,:3]=np.column_stack([np.linspace(0,.1,21),np.zeros(21),np.zeros(21)]);q[:,3:]=[0,0,0,1]
            node.find('MechanicalObject').set('position',flat(q));node.find('BeamInterpolation').set('straight',str(int(straight)))
            if observed:
                root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.LinearSystem'));root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
                ET.SubElement(node,'MatrixLinearSystem',dict(template='CompressedRowSparseMatrixd',name='system'))
                node.find('SparseLDLSolver').set('linearSystem','@system')
                ET.SubElement(node,'NativeRigidTangentObserver',dict(body='@dofs',elastic='@elastic',interpolation='@interpolation',system='@system',filename=str(d/'native'),amplitude='0'))
            node.find('./Node/NativePointJournal').set('filename',str(d/'states.csv'));tree.write(d/'scene.scn')
            process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480)
            logs=''.join((d/'process'/f).read_text() for f in ('stdout.log','stderr.log'))
            r=dict(geometry=geometry,straight=straight,observed=observed,process=process,scene_sha256=sha(d/'scene.scn'),status='FAIL_NATIVE_REST',state_error_m=None)
            if process['exit_code']==0 and not any(s in logs for s in ('[ERROR]','Line search failed','failed to converge')):
                rows=list(csv.DictReader((d/'states.csv').open()))
                if len(rows)==2:
                    r.update(status='REST_POSITION_DIAGNOSTIC',state_error_m=max(float(np.max(abs(np.fromstring(row['q'],sep=' ').reshape(-1,3)-q[:,:3]))) for row in rows))
            if (d/'native.initial.csv').exists():
                force=np.array([[float(row[k]) for k in ('fx_N','fy_N','fz_N','tx_Nm','ty_Nm','tz_Nm')] for row in csv.DictReader((d/'native.initial.csv').open())])
                lengths=np.fromstring((d/'native.lengths.txt').read_text(),sep=' ');chords=np.linalg.norm(np.diff(q[:,:3],axis=0),axis=1)
                r.update(initial_free_force_norm_N=float(np.linalg.norm(force[2:,:3])),initial_free_torque_norm_Nm=float(np.linalg.norm(force[2:,3:])),
                    native_lengths_m=lengths.tolist(),geometric_chords_m=chords.tolist(),max_length_minus_chord_m=float(np.max(abs(lengths-chords))),
                    length_scope='curved interpolation length is spline arc estimate,not equal to chord by definition')
                A=np.zeros((6*len(q),6*len(q)));D=A.copy()
                for filename,matrix in [('native.assembled.csv',A),('native.dforce.csv',D)]:
                    for row in csv.DictReader((d/filename).open()):matrix[int(row['i']),int(row['j'])]=float(row['K'])
                groups={'translation':np.array([6*i+k for i in range(2,len(q)) for k in range(3)]),
                        'rotation':np.array([6*i+k for i in range(2,len(q)) for k in range(3,6)])}
                blocks={}
                for rn,ri in groups.items():
                    for cn,ci in groups.items():
                        reference=D[np.ix_(ri,ci)];actual=A[np.ix_(ri,ci)];denom=np.linalg.norm(reference)
                        blocks[rn+'_'+cn]=dict(absolute_frobenius=float(np.linalg.norm(actual-reference)),relative=float(np.linalg.norm(actual-reference)/denom) if denom!=0 else None)
                r['same_state_matrix_blocks']=blocks
            records.append(r)
    result=dict(scope='Initial native reference/derivative inventory only;NOT loaded bending,B3 or grasp certification',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(Path(__file__)),binary_sha256=sha(binary),
        observer_source_sha256=sha(out/'Observer.cpp'),sdk='/home/ubuntu/SOFA/v26.06.00',records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
