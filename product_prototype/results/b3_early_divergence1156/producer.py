"""Read-only localization of the existing no-contact time-pair failure."""
import argparse,csv,json,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    if Path(a.tag).name!=a.tag:raise ValueError('local unique tag required')
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    cases=['b3_rail_back_hold1129','b3_rail_back_half1130'];rows=[];paths=[]
    for case in cases:
        f=BASE/'results'/case/'finger0.csv';paths.append(f)
        rows.append(list(csv.DictReader(f.open())))
    root=ET.parse(BASE/'results'/cases[0]/'scene.scn').getroot()
    rest=np.fromstring(root.find("./Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)
    mesh=json.loads((BASE/'results'/cases[0]/'mesh.json').read_text());local=np.array(mesh['local_positions_mm']);tet=np.array(mesh['tetrahedra']);D0=(rest[tet[:,1:]]-rest[tet[:,0,None]]).transpose(0,2,1);skin=local[:,2]==.1
    events={};trace=[]
    for r in rows[0]:
        t=float(r['time_s'])
        if t>.1+1e-12:break
        h=min(rows[1],key=lambda x:abs(float(x['time_s'])-t));assert abs(float(h['time_s'])-t)<1e-12
        bq,hq=[np.fromstring(z['q_m'],sep=' ').reshape(-1,3) for z in (r,h)]
        diff=np.linalg.norm(bq-hq,axis=1);bn=np.linalg.norm(bq[skin]-rest[skin]);hn=np.linalg.norm(hq[skin]-rest[skin]);den=max(bn,hn)
        relative=float(np.linalg.norm((bq-hq)[skin])/den) if den!=0 else None
        quality=[]
        for q in (bq,hq):
            F=(q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1)@np.linalg.inv(D0)
            s=np.linalg.svd(F,compute_uv=False);quality.append(dict(min_volume_ratio=float(np.linalg.det(F).min()),max_absolute_principal_Green_strain=float(abs((s*s-1)/2).max())))
        i=int(diff.argmax());item=dict(time_s=t,command_N=float(r['command_N']),skin_relative_error=relative,skin_absolute_L2_difference_m=float(np.linalg.norm((bq-hq)[skin])),maximum_node_difference_m=float(diff[i]),maximum_difference_node=i,maximum_difference_local_mm=local[i].tolist(),quality=quality)
        trace.append(item)
        for key,condition in [('first_time_gate_failure',relative is not None and relative>.001),('first_1um_node_difference',diff[i]>1e-6),('first_10um_node_difference',diff[i]>1e-5),('first_100um_node_difference',diff[i]>1e-4)]:
            if condition and key not in events:events[key]=item
    d=dict(status='DIAGNOSTIC_ONLY_NO_PHYSICAL_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in paths},events=events,outputs=len(trace),interval_s=[trace[0]['time_s'],trace[-1]['time_s']],contact='NO OBJECT_OR_SUPPORT_IN_SOURCE_SCENES',interpretation='No-contact early time sensitivity exists; does not uniquely identify integrator, mapping or FEM cause. Absolute values retained; no relative floor.',material_allowables=None,energy_work=None,next='Minimal low-amplitude joint linear-response coupon, same mass/rest mapping; do not increase force or adopt footprint candidate.')
    (out/'trace.json').write_text(json.dumps(trace,indent=2));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d))

if __name__=='__main__':main()
