"""Read saved Native states; never modify trajectories or prior verdicts."""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
    for name in ['b3_high_force_isolation1105','b3_zero_input1107','b3_polar_contrast1108','b3_two_point_joint1109']:
        src=BASE/'results'/name;root=ET.parse(src/'scene.scn').getroot()
        mesh=json.loads((src/'mesh.json').read_text());t=np.array(mesh['tetrahedra']);local=np.array(mesh['local_positions_mm'])
        rest=np.fromstring(root.find("./Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
        rows=list(csv.DictReader((src/'finger0.csv').open()));q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows])
        D0=(rest[t[:,1:]]-rest[t[:,0,None]]).transpose(0,2,1)
        D=(q[:,t[:,1:]]-q[:,t[:,0,None]]).transpose(0,1,3,2)
        F=D@np.linalg.inv(D0);ratio=np.linalg.det(F);bad=np.argwhere(ratio<=0)
        stop=int(bad[0,0]) if len(bad) else len(rows)
        skin=np.all(local[t,2]>=0,axis=1)
        singular=np.linalg.svd(F[:stop,skin],compute_uv=False)
        pairs=np.fromstring(root.find("./Node[@name='finger0']/SubsetMultiMapping").get('indexPairs'),sep=' ',dtype=int).reshape(-1,2)
        rec=dict(case=name,outputs=len(rows),valid_saved_prefix_outputs=stop,first_inversion_time_s=float(rows[stop]['time_s']) if len(bad) else None,first_element_id=int(bad[0,1]) if len(bad) else None,maximum_absolute_skin_principal_Green_strain_before_inversion=float(abs((singular**2-1)/2).max()) if stop else None,source_hashes={f:sha(src/f) for f in ('scene.scn','finger0.csv','mesh.json')},energy_work=None)
        if len(bad):
            nodes=t[bad[0,1]];rec.update(first_element_nodes=nodes.tolist(),first_element_material_centroid_mm=local[nodes].mean(0).tolist(),first_element_rigid_owned_nodes=nodes[pairs[nodes,0]==1].tolist(),first_element_is_skin=bool(skin[bad[0,1]]))
        records.append(rec)
    result=dict(status='DIAGNOSTIC_ONLY_NOT_CAUSAL_CERTIFICATION',records=records,conclusions=['No-input full joint is stable only over saved0.6s interval.','Polar rotation formulation alone does not prevent inversion.','Releasing third rigid attachment point is unstable;reject this joint candidate.','No individual thin-Skin versus bonded-Rail cause is established. No100g performance rerun justified.'],next='Isolate load transfer with a validated Native guide-joint coupon before another full high-force grasp.')
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

if __name__=='__main__':main()
