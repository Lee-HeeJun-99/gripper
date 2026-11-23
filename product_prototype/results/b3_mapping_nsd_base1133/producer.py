"""Native stabilized geometric-mapping tangent contrast,not force-law change.
Exact nonsymmetric mode1 is NOT fed to the symmetric LDL solver. Mode2 is
the installed Native symmetrized NSD projection,not an exact tangent claim.
"""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--reference',choices=['b3_rail_back_hold1129','b3_rail_back_half1130'],required=True);a=p.parse_args()
    src=BASE/'results'/a.reference;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);tree=ET.parse(src/'scene.scn');root=tree.getroot()
    mapping=root.find("./Node[@name='guides0']/Node[@name='anchors']/RigidMapping");assert mapping is not None and mapping.get('geometricStiffness') is None;mapping.set('geometricStiffness','2')
    for n in root.iter():
        for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
    for name in ('mesh.json','config.json'):shutil.copy2(src/name,out/name)
    tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes());dt=float(root.get('dt'));steps=int(round(1/dt))
    cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',str(out/'scene.scn')]
    header=Path('/home/ubuntu/SOFA/v26.06.00/include/Sofa.Component.Mapping.NonLinear/sofa/component/mapping/nonlinear/RigidMapping.inl')
    pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),reference_scene_sha256=sha(src/'scene.scn'),SDK='/home/ubuntu/SOFA/v26.06.00',native_header_sha256=sha(header),command=cmd,dt_s=dt,expected_outputs=steps,changed='ONE anchorRigidMapping geometricStiffness default0→2:Native symmetrized NSD projected tangent;same kinematic map/mass/force/control.',estimated_runtime_s=15,child_limit_s=120,memory_GiB=4,binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')})
    (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120)
    rows=list(csv.DictReader((out/'finger0.csv').open())) if (out/'finger0.csv').exists() else [];quality=None
    if rows:
        q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);rest=np.fromstring(root.find("./Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);t=np.array(json.loads((out/'mesh.json').read_text())['tetrahedra']);D0=(rest[t[:,1:]]-rest[t[:,0,None]]).transpose(0,2,1)
        ratios=np.linalg.det((q[:,t[:,1:]]-q[:,t[:,0,None]]).transpose(0,1,3,2))/np.linalg.det(D0);bad=np.argwhere(ratios<=0)
        quality=dict(all_states_finite=bool(np.isfinite(q).all()),minimum_signed_volume_ratio=float(ratios.min()),first_inversion_time_s=float(rows[bad[0,0]]['time_s']) if len(bad) else None,inverted_element_samples=len(bad))
    errors=sum((out/'process'/f).read_text().count('[ERROR]') for f in ('stdout.log','stderr.log'));complete=proc['exit_code']==0 and not errors and len(rows)==steps
    status='FAIL_NONFINITE' if quality and not quality['all_states_finite'] else 'INVERSION_OBSERVED' if quality and quality['inverted_element_samples'] else 'NO_SAVED_INVERSION_MAPPING_TANGENT_CONTRAST' if complete else 'FAIL_EXECUTION'
    d=dict(status=status,process=proc,outputs=len(rows),quality=quality,sofa_errors=errors,physical_validation='NOT QUALIFIED',holding='NOT RUN',exact_tangent=False)
    (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
