"""Separate actual input/scene identity from failed time convergence."""
import argparse,csv,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    names=['b3_rail_back_hold1129','b3_rail_back_half1130'];trees=[];rows=[]
    for name in names:
        folder=BASE/'results'/name;root=ET.parse(folder/'scene.scn').getroot()
        for n in root.iter():
            for k,v in list(n.attrib.items()):n.set(k,v.replace(str(folder),'OUTPUT'))
        root.set('dt','DT');trees.append(ET.tostring(root));rows.append(list(csv.DictReader((folder/'finger0.csv').open())))
    eq=trees[0]==trees[1];input_error=max(abs(float(r['command_N'])-float(rows[1][2*i+1]['command_N'])) for i,r in enumerate(rows[0]));impulse=[]
    for rr,dt in zip(rows,[.0025,.00125]):
        impulse.append(max(abs(float(r['command_Ns'])/dt-float(r['command_N'])) for r in rr))
    d=dict(status='PASS_INPUT_SCENE_IDENTITY_ONLY' if eq and input_error<=1e-12 and max(impulse)<=1e-12 else 'FAIL_INPUT_IDENTITY',normalized_scenes_equal_except_dt_output=eq,max_common_time_command_difference_N=input_error,max_command_impulse_over_dt_error_N=impulse,time_convergence='FAIL_PRESERVED_1131',physical_validation='NOT QUALIFIED',conclusion='No observed command mismatch or undeclared scene change explains time-pair differences;does not isolate unique ODE/mapping/cable cause.',input_hashes={str((BASE/'results'/n/f).relative_to(BASE)):sha(BASE/'results'/n/f) for n in names for f in ('scene.scn','finger0.csv')})
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))

if __name__=='__main__':main()
