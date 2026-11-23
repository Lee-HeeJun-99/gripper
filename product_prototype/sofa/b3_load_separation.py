"""Controlled trajectory differences, NOT linear superposition/energy proof."""
import csv,json,argparse,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    if Path(a.tag).name!=a.tag:raise ValueError('local case name required')
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    names=['b3_rail_back_hold1129','b3_rail_back_half1130','b3_rail_back_zero1127','b3_rail_back_zero_half1157'];data=[];files=[]
    for name in names:
        f=BASE/'results'/name/'finger0.csv';files.append(f);data.append(list(csv.DictReader(f.open())))
    roots=[ET.parse(BASE/'results'/n/'scene.scn').getroot() for n in names]
    for root in roots:assert root.get('gravity')=='0 0 -9.81'
    for root in roots[2:]:assert next(root.iter('NativeCableSequence')).get('maximumForceN')=='0'
    rest=np.fromstring(roots[0].find("./Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
    local=np.array(json.loads((BASE/'results'/names[0]/'mesh.json').read_text())['local_positions_mm']);skin=local[:,2]==.1;trace=[]
    for r in data[0]:
        t=float(r['time_s'])
        if t>.1+1e-12:break
        matched=[min(rows,key=lambda x:abs(float(x['time_s'])-t)) for rows in data];assert max(abs(float(z['time_s'])-t) for z in matched)<1e-12
        q=[np.fromstring(z['q_m'],sep=' ').reshape(-1,3)[skin] for z in matched];f0,f1,z0,z1=q
        norm=lambda x:float(np.linalg.norm(x))
        total=f0-f1;zero=z0-z1;increment=(f0-z0)-(f1-z1)
        trace.append(dict(time_s=t,command_N=float(r['command_N']),driven_pair_difference_m=norm(total),gravity_only_pair_difference_m=norm(zero),difference_of_input_responses_m=norm(increment),gravity_only_displacement_base_m=norm(z0-rest[skin]),driven_minus_zero_base_m=norm(f0-z0),difference_decomposition_residual_m=norm(total-zero-increment)))
    d=dict(status='CONTROLLED_LOAD_DIAGNOSTIC_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in files},first_common_output=trace[0],last_common_output=trace[-1],maximum_decomposition_residual_m=max(x['difference_decomposition_residual_m'] for x in trace),scope='Same geometry/mass/gravity; zero Cable at both dt. Differences are controlled nonlinear trajectories, NOT superposition or unique causal attribution.',physical_validation='NOT QUALIFIED',energy_work=None,holding='NOT RUN')
    (out/'summary.json').write_text(json.dumps(d,indent=2));(out/'trace.json').write_text(json.dumps(trace,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))

if __name__=='__main__':main()
