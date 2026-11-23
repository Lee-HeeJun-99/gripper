"""One-variable Native no-contact inversion contrasts against frozen1105.

No new force/ODE implementation. Polar is a different FEM formulation, not a
certified repair. Zero input tests load necessity, not guide independence.
"""
import argparse, csv, json, shutil, subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE, sha
from native_bending_coupon import guarded

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--tag', required=True)
    p.add_argument('--contrast', choices=['zero-input','polar','two-point-joint'], required=True)
    a=p.parse_args()
    src=BASE/'results/b3_high_force_isolation1105'
    out=BASE/'results'/a.tag
    out.mkdir(exist_ok=False)
    tree=ET.parse(src/'scene.scn'); root=tree.getroot()
    if a.contrast=='zero-input':
        nodes=list(root.iter('NativeCableSequence'))
        assert len(nodes)==1 and nodes[0].get('maximumForceN')=='2.5'
        nodes[0].set('maximumForceN','0')
    elif a.contrast=='polar':
        nodes=list(root.iter('TetrahedronFEMForceField'))
        assert len(nodes)==1 and nodes[0].get('method')=='large'
        nodes[0].set('method','polar')
    else:
        # Release third FEM node of each rigid triangle; retain the first two.
        # Unused mapped anchor remains massless; full FEM node becomes free.
        # This changes joint kinematics, NOT material or cable route at rest.
        mapping=root.find("./Node[@name='finger0']/SubsetMultiMapping")
        pairs=np.fromstring(mapping.get('indexPairs'),sep=' ',dtype=int).reshape(-1,2)
        free=root.find("./Node[@name='free0']/MechanicalObject")
        fq=np.fromstring(free.get('position'),sep=' ').reshape(-1,3).tolist()
        full=np.fromstring(root.find("./Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
        released=[]
        for i,(owner,index) in enumerate(pairs):
            if owner==1 and index%3==2:
                pairs[i]=[0,len(fq)]; fq.append(full[i].tolist()); released.append(i)
        assert len(released)==12
        free.set('position',' '.join(format(x,'.17g') for row in fq for x in row))
        mapping.set('indexPairs',' '.join(map(str,pairs.ravel())))
        (out/'released_nodes.json').write_text(json.dumps(released))
    for n in root.iter():
        for k,v in list(n.attrib.items()):
            n.set(k,v.replace(str(src),str(out)))
    for name in ('mesh.json','config.json'): shutil.copy2(src/name,out/name)
    tree.write(out/'scene.scn')
    shutil.copy2(Path(__file__),out/'producer.py')
    cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','240','--hideProgressBar',str(out/'scene.scn')]
    pre=dict(contrast=a.contrast,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),command=cmd,SDK='/home/ubuntu/SOFA/v26.06.00',steps=240,dt_s=.0025,memory_GiB=4,child_limit_s=120,estimated_runtime_s=5,binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')},physical_validation='NOT QUALIFIED')
    (out/'preflight.json').write_text(json.dumps(pre,indent=2))
    proc=guarded(cmd,out/'process',120)
    rows=list(csv.DictReader((out/'finger0.csv').open())) if (out/'finger0.csv').exists() else []
    quality=None
    if rows:
        tet=np.array(json.loads((out/'mesh.json').read_text())['tetrahedra'])
        q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows])
        rest=np.fromstring(root.find("./Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
        d0=np.linalg.det((rest[tet[:,1:]]-rest[tet[:,0,None]]).transpose(0,2,1))
        ratio=np.linalg.det((q[:,tet[:,1:]]-q[:,tet[:,0,None]]).transpose(0,1,3,2))/d0
        bad=np.argwhere(ratio<=0)
        quality=dict(minimum_determinant_ratio=float(ratio.min()),inverted_element_samples=len(bad),first_inversion_time_s=float(rows[bad[0,0]]['time_s']) if len(bad) else None,first_element_id=int(bad[0,1]) if len(bad) else None,maximum_node_motion_mm=float(np.linalg.norm(q-rest,axis=2).max()*1000))
    errors=sum((out/'process'/f).read_text().count('[ERROR]') for f in ('stdout.log','stderr.log'))
    complete=proc['exit_code']==0 and errors==0 and len(rows)==240
    result=dict(status='INVERSION_OBSERVED' if quality and quality['inverted_element_samples'] else 'NO_SAVED_INVERSION_BOUNDED_SCOPE' if complete else 'FAIL_EXECUTION',contrast=a.contrast,process=proc,outputs=len(rows),sofa_errors=errors,quality=quality,physical_validation='NOT QUALIFIED',holding='NOT RUN_NO_OBJECT',energy_work=None)
    (out/'summary.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result))

if __name__=='__main__': main()
