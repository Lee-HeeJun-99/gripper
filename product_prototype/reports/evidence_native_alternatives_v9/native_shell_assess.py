"""All-pair Native shell checks and unfitted constitutive reference-field energy.
The reference-field tensor is algebra on native K,NOT a driven SOFA trajectory.
"""
import argparse,csv,itertools,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,sha

def main():
    csv.field_size_limit(64*1024*1024)
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[];pairs=[];linearity=[];tensors=[]
    cases=['native_shell_pcg416','native_shell_pcg_refine417']
    for name in cases:
        data=json.loads((BASE/'results'/name/'summary.json').read_text())
        records.extend([dict(r,case=name) for r in data['records'] if 'tip_m' in r])
    for x,y in itertools.combinations(records,2):
        if x['ny']!=y['ny']:continue
        error=abs(x['tip_m']-y['tip_m'])/max(abs(x['tip_m']),abs(y['tip_m']))
        pairs.append(dict(nx=[x['nx'],y['nx']],ny=x['ny'],relative=error,gate=.01,status='PASS_PAIR_ONLY' if error<=.01 else 'FAIL_MESH_GATE'))
    half=json.loads((BASE/'results/native_shell_pcg_half418/summary.json').read_text())
    for x in records:
        for y in half['records']:
            if (x['nx'],x['ny'])!=(y['nx'],y['ny']) or 'tip_m' not in y:continue
            source=BASE/'results'/x['case']/f"{x['nx']}_{x['ny']}";other=BASE/'results/native_shell_pcg_half418'/f"{y['nx']}_{y['ny']}"
            q0=np.fromstring(ET.parse(source/'scene.scn').find('.//MechanicalObject').get('position'),sep=' ')
            full=list(csv.DictReader((source/'states.csv').open()));small=list(csv.DictReader((other/'states.csv').open()))
            error=max(float(np.max(abs((np.fromstring(f['q'],sep=' ')-q0)-2*(np.fromstring(s['q'],sep=' ')-q0)))) for f,s in zip(full,small))
            linearity.append(dict(nx=x['nx'],ny=x['ny'],absolute_scaled_state_error_m=error,gate_m=1e-12,status='PASS_LOAD_LINEARITY_ONLY' if error<=1e-12 and len(full)==len(small)==2 else 'FAIL'))
    for label,d in [('coarse',BASE/'results/native_bending_matrix_paths415')]+[(f'81_{ny}',BASE/'results/native_shell_tensor_probe420'/f'81_{ny}') for ny in (3,5)]:
        node=ET.parse(d/'scene.scn').find('./Node');q=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3)
        matrix=d/('native.matrix.csv' if label=='coarse' else 'rest_probe.matrix.csv');K=np.zeros((q.size,q.size))
        for row in csv.DictReader(matrix.open()):K[int(row['i']),int(row['j'])]=float(row['K_N_per_m'])
        phi=np.zeros((q.size,3));phi[2::3]=np.array([q[:,0]**2/2,q[:,1]**2/2,q[:,0]*q[:,1]]).T
        D=float(node.find('FastTriangularBendingSprings').get('bendingStiffness'));C=phi.T@K@phi/(.1*.02)
        tensors.append(dict(case=label,source_matrix_sha256=sha(matrix),reference_curvature_tensor_over_input_D=(C/D).tolist(),
            desired_nu0_tensor_over_D=np.diag([1.,1.,2.]).tolist(),scope='unconstrained quadratic reference fields,NOT actual prescribed/deformed Native output;no fitted parameter applied'))
    result=dict(scope='Native static shell diagnostics,NOT B3,stress-free precurve,grasp,time or continuum certification',
                mesh_pairs=pairs,load_linearity=linearity,constitutive_reference_fields=tensors,
                gate='FAIL_MESH_AND_CONSTITUTIVE_QUALIFICATION;NO_B3_PROMOTION')
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
