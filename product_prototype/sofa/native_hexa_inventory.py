"""Independent small-strain Q1 hexa quadrature on ACTUAL native accepted states.
No solve, state correction, force injection or new ForceField. nu=0 reference only.
"""
import argparse,csv,itertools,json
import xml.etree.ElementTree as ET
import numpy as np
from native_bending_coupon import BASE,sha

def main():
    csv.field_size_limit(64*1024*1024)
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='native_pure_bending396');a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);source=BASE/'results'/a.case
    data=json.loads((source/'summary.json').read_text());records=[]
    signs=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]])
    for r in data['records']:
        if r['model']!='hexa' or r['status']!='COMPLETED_PURE_BENDING_DIAGNOSTIC':continue
        d=source/f"hexa_{r['nx']}_cross{r['cross']}";scene=ET.parse(d/'scene.scn');top=scene.find('.//MeshTopology')
        q=np.fromstring(top.get('position'),sep=' ').reshape(-1,3);hexes=np.fromstring(top.get('hexahedra'),sep=' ',dtype=int).reshape(-1,8)
        rows=list(csv.DictReader((d/'states.csv').open()));actual=np.fromstring(rows[-1]['q'],sep=' ').reshape(-1,3);u=actual-q
        internal=np.zeros_like(q);energy=0.;volume=0.;maxstrain=0.;mindet=float('inf')
        for h in hexes:
            for gp in itertools.product((-1/np.sqrt(3),1/np.sqrt(3)),repeat=3):
                gp=np.array(gp);factors=1+signs*gp
                dn=np.column_stack([signs[:,i]*np.prod(factors[:,[j for j in range(3) if j!=i]],axis=1)/8 for i in range(3)])
                J=q[h].T@dn;det=np.linalg.det(J)
                if det<=0:raise ValueError('invalid reference hexa')
                grad=dn@np.linalg.inv(J);du=u[h].T@grad;strain=(du+du.T)/2;stress=1e6*strain
                energy+=.5*np.sum(stress*strain)*det;volume+=det
                internal[h]+=grad@stress.T*det;maxstrain=max(maxstrain,float(np.max(abs(strain))))
                mindet=min(mindet,float(np.linalg.det(actual[h].T@dn)/det))
        load=scene.find('.//ConstantForceField');ids=np.fromstring(load.get('indices'),sep=' ',dtype=int)
        external=np.zeros_like(q);external[ids]=np.fromstring(load.get('forces'),sep=' ').reshape(-1,3)
        fixed=q[:,0]==0;residual=internal-external;reaction=residual[fixed].sum(axis=0)
        moment=np.cross(q[fixed],residual[fixed]).sum(axis=0)+np.cross(q,external).sum(axis=0)
        work=float(np.sum(external*u));relative=abs(2*energy-work)/max(abs(2*energy),abs(work))
        maxres=float(np.linalg.norm(residual[~fixed]))
        records.append(dict(nx=r['nx'],cross=r['cross'],independent_quadrature_energy_J=energy,
            native_potential_energy_J=None,external_work_at_final_load_J=work,
            linear_energy_identity_relative_error=relative,free_residual_norm_N=maxres,
            support_reaction_N=reaction.tolist(),force_balance_N=(reaction+external.sum(axis=0)).tolist(),
            moment_balance_Nm=moment.tolist(),max_abs_gauss_strain=maxstrain,reference_volume_m3=volume,
            minimum_deformed_gauss_J_ratio=mindet,
            status='PASS_DIAGNOSTIC_INVENTORY_ONLY' if relative<=.001 and maxres<=1e-12 else 'FAIL_DIAGNOSTIC_INVENTORY'))
    (out/'producer.py').write_bytes(__import__('pathlib').Path(__file__).read_bytes())
    (out/'summary.json').write_text(json.dumps(dict(scope='Independent Q1 small-strain nu=0 inventory on stored native states;not dynamic/native-energy/B3 certification',source_summary_sha256=sha(source/'summary.json'),records=records),indent=2));print(json.dumps(records,indent=2))

if __name__=='__main__':main()
