"""Compare only saved valid prefixes of Native load-path contrasts."""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    src=BASE/'results/b3_high_force_isolation1105';base=list(csv.DictReader((src/'finger0.csv').open()))
    q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in base])
    rest=np.fromstring(ET.parse(src/'scene.scn').getroot().find("./Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
    records=[]
    for name in ('b3_reference_deadload1116','b3_recorded_load1117'):
        folder=BASE/'results'/name;rows=list(csv.DictReader((folder/'states.csv').open()));summary=json.loads((folder/'summary.json').read_text())
        v=np.array([np.fromstring(r['q'],sep=' ').reshape(-1,3) for r in rows]);bad=summary['quality']['first_inversion_time_s'];stop=min(207,next((i for i,r in enumerate(rows) if bad is not None and float(r['time_s'])>=bad),len(rows)))
        sampled=[]
        for i in (0,19,39,79,95,159,199):
            if i>=stop:continue
            assert abs(float(rows[i]['time_s'])-float(base[i]['time_s']))<1e-12
            absolute=float(np.linalg.norm(v[i]-q[i]));den=float(np.linalg.norm(q[i]-rest))
            sampled.append(dict(time_s=float(rows[i]['time_s']),state_difference_L2_m=absolute,relative_to_reference_displacement=absolute/den if den else None))
        records.append(dict(case=name,first_step_max_position_error_m=float(abs(v[0]-q[0]).max()),valid_shared_outputs=stop,samples=sampled,source_hashes={f:sha(folder/f) for f in ('states.csv','scene.scn','summary.json')}))
    d=dict(status='DIAGNOSTIC_DIFFERENT_LOAD_LAWS_NOT_EQUIVALENCE',records=records,baseline_hashes={f:sha(src/f) for f in ('finger0.csv','scene.scn')},physical_validation='NOT QUALIFIED',conclusions=['First-step mapped impulse/external load responses agree within1e-12 position;this is not subsequent trajectory equivalence.','Reference-direction dead load remains noninverted but is not the same control law.','Recorded force history inverts without CableConstraint;does not identify the original unique cause because load application and integration differ.','No new100g Holding or stiffness sensitivity is justified as a stability repair.'])
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
