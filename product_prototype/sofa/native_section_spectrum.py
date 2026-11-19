"""Skin/one-rail/two-rail INITIAL native spectra; not loaded stiffness or dynamics.
Zero-load q/v is checked with/without the existing diagnostic observer.
"""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from scipy.linalg import eigvalsh
from native_bending_coupon import BASE,ROOT,flat,sha,guarded

def main():
    csv.field_size_limit(64*1024*1024)
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    source=BASE/'results/native_static_bending372/21/scene.scn'
    original=ET.parse(source);top=original.find('.//MeshTopology')
    q=np.fromstring(top.get('position'),sep=' ').reshape(-1,3)
    tets=np.fromstring(top.get('tetrahedra'),sep=' ',dtype=int).reshape(-1,4)
    # Original straight mount maps local positive Skin thickness INWARD:
    # world radial x = 50mm - local thickness z (cad/generate.py:world).
    centres=q[tets].mean(axis=1);skin=centres[:,0]<.05
    expected_skin_volume_m3=210e-9
    skin_points=q[tets[skin]]
    skin_volume=np.linalg.det((skin_points[:,1:]-skin_points[:,0,None,:]).transpose(0,2,1)).sum()/6
    if abs(skin_volume-expected_skin_volume_m3)>1e-18:raise ValueError('Skin material classification/analytical volume mismatch')
    fixed=set(np.fromstring(original.find('.//FixedProjectiveConstraint').get('indices'),sep=' ',dtype=int))
    binary=BASE/'cad/build_elastic_observer400/libReGripElasticObserver.so';records=[]
    for name,selected in [('skin_only',skin),('one_rail',skin|(centres[:,1]>0)),('two_rails',np.ones(len(tets),dtype=bool))]:
        elements=tets[selected];nodes=np.unique(elements);mapping={old:new for new,old in enumerate(nodes)}
        elements=np.array([[mapping[i] for i in t] for t in elements]);reference=q[nodes]
        det=np.linalg.det((reference[elements[:,1:]]-reference[elements[:,0],None,:]).transpose(0,2,1))
        if np.any(det<=0):raise ValueError('nonpositive reference tetra')
        states=[];processes=[]
        for observed in (False,True):
            d=out/f'{name}_{"observed" if observed else "control"}';d.mkdir()
            root=ET.parse(source).getroot();node=root.find('./Node');top=node.find('MeshTopology')
            top.set('position',flat(reference));top.set('tetrahedra',flat(elements));top.attrib.pop('triangles',None)
            node.find('MechanicalObject').set('position',flat(reference))
            node.find('FixedProjectiveConstraint').set('indices',' '.join(str(mapping[i]) for i in nodes if i in fixed))
            load=node.find('ConstantForceField');load.set('indices','0');load.set('forces','0 0 0')
            node.find('NativePointJournal').set('filename',str(d/'states.csv'))
            node.find('TetrahedronFEMForceField').set('name','elastic')
            if observed:
                root.insert(0,ET.Element('RequiredPlugin',pluginName=str(binary)))
                ET.SubElement(node,'NativeElasticMatrixObserver',dict(body='@dofs',elastic='@elastic',filename=str(d/'native')))
            ET.ElementTree(root).write(d/'scene.scn')
            process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','2','--hideProgressBar',d/'scene.scn'],d/'process',480);processes.append(process)
            logs=''.join((d/'process'/f).read_text() for f in ('stdout.log','stderr.log'))
            if process['exit_code']!=0 or '[ERROR]' in logs or 'failed to converge' in logs:raise ValueError(f'invalid zero-load diagnostic:{d}')
            states.append(list(csv.DictReader((d/'states.csv').open())))
        error=max(float(np.max(abs(np.fromstring(x[key],sep=' ')-np.fromstring(y[key],sep=' ')))) for x,y in zip(*states) for key in ('q','v'))
        rest=max(float(np.max(abs(np.fromstring(r['q'],sep=' ').reshape(-1,3)-reference))) for r in states[1])
        K=np.zeros((reference.size,reference.size));d=out/f'{name}_observed'
        for row in csv.DictReader((d/'native.matrix.csv').open()):K[int(row['i']),int(row['j'])]=float(row['K_N_per_m'])
        free=np.ones(reference.size,dtype=bool)
        for i in nodes:
            if i in fixed:free[3*mapping[i]:3*mapping[i]+3]=False
        A=K[np.ix_(free,free)];eigen=eigvalsh((A+A.T)/2)
        records.append(dict(component=name,nodes=len(nodes),tetrahedra=len(elements),reference_volume_m3=float(det.sum()/6),
            initial_min_eigenvalue_N_per_m=float(eigen[0]),initial_max_eigenvalue_N_per_m=float(eigen[-1]),
            symmetric_part_condition=float(eigen[-1]/eigen[0]) if eigen[0]>0 else None,
            observer_qv_difference=error,rest_position_error_m=rest,processes=processes,
            status='PASS_INITIAL_ZERO_LOAD_IDENTITY_ONLY' if error<=1e-12 and rest<=1e-12 and len(states[0])==len(states[1])==2 else 'FAIL'))
    data=dict(scope='Initial native small-method spectra only;added physical volume is intentional;no loaded stiffness ratio,no bending/time/guide/B3 qualification',
        source_scene_sha256=sha(source),source_sha256=sha(Path(__file__)),binary_sha256=sha(binary),sdk='/home/ubuntu/SOFA/v26.06.00',E_Pa=250e6,nu=.3,material_provenance='local positive Skin z maps to world x<50mm;210mm3 analytic Skin volume asserted',records=records)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(data,indent=2));print(json.dumps(data,indent=2))

if __name__=='__main__':main()
