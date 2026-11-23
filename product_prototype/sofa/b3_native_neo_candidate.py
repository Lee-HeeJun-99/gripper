"""Independent Native finite-strain material candidate, not fitted stiffness.
Initial E/nu matched;geometry/control/joints unchanged. NOT measured material.
"""
import argparse,csv,json,shutil,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    src=BASE/'results/b3_high_force_isolation1105';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    tree=ET.parse(src/'scene.scn');root=tree.getroot();root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.SolidMechanics.FEM.HyperElastic'))
    ff=root.find("./Node[@name='finger0']/TetrahedronFEMForceField");E=float(ff.get('youngModulus'));nu=float(ff.get('poissonRatio'));mu=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu))
    attrs={k:v for k,v in ff.attrib.items() if k not in ('method','youngModulus','poissonRatio')};ff.tag='TetrahedronHyperelasticityFEMForceField';ff.attrib.clear();ff.attrib.update(attrs);ff.set('materialName','NeoHookean');ff.set('ParameterSet',f'{mu:.17g} {lam:.17g}')
    for n in root.iter():
        for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
    for f in ('mesh.json','config.json'):shutil.copy2(src/f,out/f)
    # Inherited config remains provenance,not the authoritative changed law.
    (out/'material_override.json').write_text(json.dumps(dict(law='Native NeoHookean',E_initial_Pa=E,nu_initial=nu,mu_Pa=mu,lambda_Pa=lam,measured=False),indent=2))
    tree.write(out/'scene.scn');(out/'producer.py').write_bytes(Path(__file__).read_bytes())
    cmd=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','240','--hideProgressBar',str(out/'scene.scn')]
    pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_scene_sha256=sha(src/'scene.scn'),command=cmd,SDK='/home/ubuntu/SOFA/v26.06.00',changed='Material law ONLY:Native corotational→Native compressible NeoHookean,matched infinitesimal E/nu. Not same finite-strain physics.',expected_outputs=240,estimated_runtime_s=25,estimate_basis='Conservative10x original1105 cost;measure actual before fullgrasp',child_limit_s=120,memory_GiB=4,binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')})
    (out/'preflight.json').write_text(json.dumps(pre,indent=2));proc=guarded(cmd,out/'process',120)
    rows=list(csv.DictReader((out/'finger0.csv').open())) if (out/'finger0.csv').exists() else [];errors=sum((out/'process'/f).read_text().count('[ERROR]') for f in ('stdout.log','stderr.log'));quality=None
    if rows:
        q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);rest=np.fromstring(root.find("./Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);t=np.array(json.loads((out/'mesh.json').read_text())['tetrahedra'])
        finite=np.all(np.isfinite(q),axis=(1,2));n=int(np.flatnonzero(~finite)[0]) if not finite.all() else len(rows);q=q[:n]
        D0=(rest[t[:,1:]]-rest[t[:,0,None]]).transpose(0,2,1);ratio=np.linalg.det((q[:,t[:,1:]]-q[:,t[:,0,None]]).transpose(0,1,3,2))/np.linalg.det(D0) if n else np.empty((0,len(t)))
        bad=np.argwhere(ratio<=0);quality=dict(all_states_finite=bool(finite.all()),first_nonfinite_time_s=float(rows[n]['time_s']) if n<len(rows) else None,first_inversion_time_s=float(rows[bad[0,0]]['time_s']) if len(bad) else None,first_element_id=int(bad[0,1]) if len(bad) else None,minimum_signed_volume_ratio=float(ratio.min()) if n else None,inverted_element_samples=len(bad),max_node_motion_mm=float(np.linalg.norm(q-rest,axis=2).max()*1000) if n else None)
    complete=proc['exit_code']==0 and not errors and len(rows)==240
    status='FAIL_NONFINITE_STATE' if quality and not quality['all_states_finite'] else 'INVERSION_OBSERVED' if quality and quality['inverted_element_samples'] else 'NO_SAVED_INVERSION_NEW_MATERIAL_ONLY' if complete else 'FAIL_EXECUTION'
    d=dict(status=status,process=proc,outputs=len(rows),sofa_errors=errors,quality=quality,holding='NOT RUN_NO_OBJECT',physical_validation='NOT QUALIFIED',material_validation='NOT MEASURED',energy_work=None)
    (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
