"""Kinematic strain history from saved valid Native states, not material gates."""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
    for name in ('b3_high_force_isolation1105','b3_zero_input1107','b3_reference_deadload1116','b3_recorded_load1117'):
        folder=BASE/'results'/name;root=ET.parse(folder/'scene.scn').getroot();m=json.loads((folder/'mesh.json').read_text());t=np.array(m['tetrahedra']);local=np.array(m['local_positions_mm'])
        rest=np.fromstring(root.find("./Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
        fname='finger0.csv' if (folder/'finger0.csv').exists() else 'states.csv';rows=list(csv.DictReader((folder/fname).open()));field='q_m' if fname=='finger0.csv' else 'q'
        q=np.array([np.fromstring(r[field],sep=' ').reshape(-1,3) for r in rows]);F=(q[:,t[:,1:]]-q[:,t[:,0,None]]).transpose(0,1,3,2)@np.linalg.inv((rest[t[:,1:]]-rest[t[:,0,None]]).transpose(0,2,1));ratio=np.linalg.det(F)
        bad=np.flatnonzero(np.any(ratio<=0,axis=1));stop=int(bad[0]) if len(bad) else len(rows)
        s=np.linalg.svd(F[:stop],compute_uv=False);green=np.max(abs((s*s-1)/2),axis=2);skin=np.all(local[t,2]>=0,axis=1)
        metrics=[]
        for i in range(stop):metrics.append(dict(time_s=float(rows[i]['time_s']),skin_max_absolute_principal_Green_strain=float(green[i,skin].max()),rail_max_absolute_principal_Green_strain=float(green[i,~skin].max()),minimum_volume_ratio=float(ratio[i].min())))
        with (out/(name+'.csv')).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(metrics[0]));w.writeheader();w.writerows(metrics)
        rec=dict(case=name,valid_outputs=stop,first_inversion_s=float(rows[stop]['time_s']) if len(bad) else None,source_hashes={fn:sha(folder/fn) for fn in (fname,'mesh.json','scene.scn')},diagnostic_thresholds_not_material_limits={})
        for level in (.01,.1):
            hit=np.flatnonzero(np.max(green[:,skin],axis=1)>level)
            if len(hit):
                i=int(hit[0]);ids=np.flatnonzero(skin);j=int(ids[np.argmax(green[i,skin])]);entry=dict(time_s=float(rows[i]['time_s']),element_id=j,material_centroid_mm=local[t[j]].mean(0).tolist())
            else:entry=None
            rec['diagnostic_thresholds_not_material_limits'][str(level)]=entry
        records.append(rec)
    d=dict(status='KINEMATIC_HISTORY_ONLY_NOT_MATERIAL_FAILURE_GATE',records=records,material_allowable_strain=None,physical_validation='NOT QUALIFIED',deformed_tangent='NOT MEASURED: existing compiled elastic observer queries tangent only at initial bwdInit state; private probePositions queries forces,not deformed tangent. No stale dynamic checkpoint installed.')
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
