"""Native dead-load contrast: remove CableConstraint, retain guide/FEM joints.
Same reference cable wrench and sampled C2 envelope, NOT same follower load.
"""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded,add,flat

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    src=BASE/'results/b3_high_force_isolation1105';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    tree=ET.parse(src/'scene.scn');root=tree.getroot();g=root.find("./Node[@name='guides0']")
    frames=np.fromstring(g.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7)
    anchors=g.find("./Node[@name='anchors']");points=np.fromstring(anchors.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)
    wrench=np.zeros((12,6));forces=np.zeros((36,3));residual=[]
    for c in range(2):
        cable=g.find(f"./Node[@name='cable{c}']")
        q=np.fromstring(cable.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)
        origin=np.fromstring(cable.find('CableConstraint').get('pullPoint'),sep=' ')
        path=np.vstack([origin,q]);segments=np.diff(path,axis=0);u=segments/np.linalg.norm(segments,axis=1)[:,None]
        for j in range(6):
            f=-u[j]+(u[j+1] if j<5 else 0);i=c*6+j
            wrench[i,:3]=f;wrench[i,3:]=np.cross(q[j]-frames[i,:3],f)
    def skew(v):return np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    for i in range(12):
        J=np.concatenate([np.column_stack([np.eye(3),-skew(x-frames[i,:3])]) for x in points[3*i:3*i+3]])
        f=np.linalg.lstsq(J.T,wrench[i],rcond=None)[0];forces[3*i:3*i+3]=f.reshape(3,3)
        residual.append(float(np.linalg.norm(J.T@f-wrench[i])))
    for c in range(2):
        cable=g.find(f"./Node[@name='cable{c}']");cable.remove(cable.find('CableConstraint'))
    for parent in root.iter():
        for child in list(parent):
            if child.tag=='NativeCableSequence':parent.remove(child)
    root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.MechanicalLoad'))
    times=np.arange(241)*.0025;z=np.clip((times+.0025)/.5,0,1);scale=2.5*(10*z**3-15*z**4+6*z**5)
    for i,f in enumerate(forces):
        add(anchors,'LinearForceField',template='Vec3d',name=f'deadLoad{i}',points=str(i),times=' '.join(map(str,[*times,10.])),forces=flat(np.vstack([scale[:,None]*f,2.5*f])))
    add(root.find("./Node[@name='finger0']"),'NativePointJournal',body='@dofs',filename=str(out/'states.csv'))
    for n in root.iter():
        for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
    for name in ('mesh.json','config.json'):shutil.copy2(src/name,out/name)
    tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes())
    cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','240','--hideProgressBar',str(out/'scene.scn')]
    pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),reference_scene_sha256=sha(src/'scene.scn'),SDK='/home/ubuntu/SOFA/v26.06.00',command=cmd,reference_unit_tension_wrenches=wrench.tolist(),anchor_unit_tension_forces=forces.tolist(),maximum_reference_wrench_reconstruction_error=max(residual),time_keys_s=times.tolist(),tension_keys_N=scale.tolist(),load_law='Global-direction dead loads from reference cable wrenches;piecewise-linear sampled C2 beginning at physical end clock. Not equivalent to evolving cable geometry.',estimated_runtime_s=5,child_limit_s=120,memory_GiB=4,binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')})
    (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120)
    rows=list(csv.DictReader((out/'states.csv').open())) if (out/'states.csv').exists() else []
    quality=None
    if rows:
        t=np.array(json.loads((out/'mesh.json').read_text())['tetrahedra']);rest=np.fromstring(root.find("./Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
        q=np.array([np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in rows]);D0=(rest[t[:,1:]]-rest[t[:,0,None]]).transpose(0,2,1)
        ratios=np.linalg.det((q[:,t[:,1:]]-q[:,t[:,0,None]]).transpose(0,1,3,2))/np.linalg.det(D0)
        bad=np.argwhere(ratios<=0);quality=dict(minimum_signed_volume_ratio=float(ratios.min()),first_inversion_time_s=float(rows[bad[0,0]]['time_s']) if len(bad) else None,first_element_id=int(bad[0,1]) if len(bad) else None,inverted_element_samples=len(bad),max_node_motion_mm=float(np.linalg.norm(q-rest,axis=2).max()*1000))
    errors=sum((out/'process'/f).read_text().count('[ERROR]') for f in ('stdout.log','stderr.log'))
    result=dict(status='INVERSION_WITHOUT_CABLE_CONSTRAINT' if quality and quality['inverted_element_samples'] else 'NO_SAVED_INVERSION_DIFFERENT_LOAD_LAW' if proc['exit_code']==0 and not errors and len(rows)==240 else 'FAIL_EXECUTION',process=proc,outputs=len(rows),sofa_errors=errors,quality=quality,physical_validation='NOT QUALIFIED',holding='NOT RUN',energy_work=None)
    (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

if __name__=='__main__':main()
