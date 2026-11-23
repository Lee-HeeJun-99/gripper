"""Single physical design variable: critical Guide footprint span5→10mm.
Keep3points/rank6,restshape/material/mass/routing/force;hardware support
geometry/mass is NOT finalized by this ideal joint comparison.
"""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--half',action='store_true');p.add_argument('--zero',action='store_true');a=p.parse_args();src=BASE/'results'/('b3_rail_back_half1130' if a.half else 'b3_rail_back_hold1129');out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    tree=ET.parse(src/'scene.scn');root=tree.getroot();q0=np.fromstring(root.find("./Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);local=np.array(json.loads((src/'mesh.json').read_text())['local_positions_mm']);mapping=root.find("./Node[@name='finger0']/SubsetMultiMapping");pairs=np.fromstring(mapping.get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);owned={int(i):int(j) for i,(owner,j) in enumerate(pairs) if owner==1};changes=[]
    for body in (3,9):
        old=next(i for i,j in owned.items() if j==3*body+2);assert local[old,0]==75 and local[old,2]==-.5
        candidates=np.flatnonzero((local[:,0]==80)&(local[:,2]==-.5)&(np.sign(local[:,1])==np.sign(local[old,1])))
        new=int(candidates[np.argmax(abs(local[candidates,1]))]);assert new not in owned
        k=owned.pop(old);owned[new]=k;changes.append(dict(guide=body,anchor_index=k,old_node=old,new_node=new,old_local_mm=local[old].tolist(),new_local_mm=local[new].tolist()))
    assert len(owned)==36 and len(set(owned.values()))==36;fq=[];anchors=np.zeros((36,3));newpairs=[]
    for i in range(len(q0)):
        if i in owned:newpairs.append([1,owned[i]]);anchors[owned[i]]=q0[i]
        else:newpairs.append([0,len(fq)]);fq.append(q0[i])
    fmt=lambda x:' '.join(format(float(v),'.17g') for v in np.array(x).ravel())
    root.find("./Node[@name='free0']/MechanicalObject").set('position',fmt(fq));mapping.set('indexPairs',' '.join(str(v) for pair in newpairs for v in pair));root.find("./Node[@name='guides0']/Node[@name='anchors']/MechanicalObject").set('position',fmt(anchors))
    fixed=np.fromstring(root.find("./Node[@name='free0']/FixedProjectiveConstraint").get('indices'),sep=' ',dtype=int);assert np.all(np.array(fq)[fixed]==q0[fixed])
    areas=[float(np.linalg.norm(np.cross(anchors[3*i+1]-anchors[3*i],anchors[3*i+2]-anchors[3*i]))) for i in range(12)];assert min(areas)>0
    if a.zero:next(root.iter('NativeCableSequence')).set('maximumForceN','0')
    for n in root.iter():
        for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
    for f in ('config.json','mesh.json'):shutil.copy2(src/f,out/f)
    tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());dt=float(root.get('dt'));steps=int(round(1/dt))
    cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')]
    pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),SDK='/home/ubuntu/SOFA/v26.06.00',command=cmd,changes=changes,twice_triangle_areas_m2=areas,zero_control=a.zero,dt_s=dt,expected_outputs=steps,estimated_runtime_s=15,child_limit_s=120,memory_GiB=4,physical_support_connection='NOT MODELED_OR_FABRICATION_QUALIFIED',binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')})
    (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120)
    rows=list(csv.DictReader((out/'finger0.csv').open())) if (out/'finger0.csv').exists() else [];quality=None
    if rows:
        q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);t=np.array(json.loads((out/'mesh.json').read_text())['tetrahedra']);D0=(q0[t[:,1:]]-q0[t[:,0,None]]).transpose(0,2,1);ratio=np.linalg.det((q[:,t[:,1:]]-q[:,t[:,0,None]]).transpose(0,1,3,2))/np.linalg.det(D0);bad=np.argwhere(ratio<=0)
        quality=dict(all_states_finite=bool(np.isfinite(q).all()),minimum_signed_volume_ratio=float(ratio.min()),first_inversion_time_s=float(rows[bad[0,0]]['time_s']) if len(bad) else None,inverted_element_samples=len(bad),maximum_node_motion_mm=float(np.linalg.norm(q-q0,axis=2).max()*1000))
    errors=sum((out/'process'/f).read_text().count('[ERROR]') for f in ('stdout.log','stderr.log'));status='FAIL_NONFINITE' if quality and not quality['all_states_finite'] else 'INVERSION_OBSERVED' if quality and quality['inverted_element_samples'] else 'NO_SAVED_INVERSION_BOUNDED_FOOTPRINT' if proc['exit_code']==0 and errors==0 and len(rows)==steps else 'FAIL_EXECUTION'
    d=dict(status=status,process=proc,outputs=len(rows),quality=quality,sofa_errors=errors,physical_validation='NOT QUALIFIED',holding='NOT RUN_NO_OBJECT',energy_work=None);(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
