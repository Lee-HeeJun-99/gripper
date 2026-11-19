"""One-variable physical sector-margin candidate and labelled frozen-motion screening."""
import argparse,csv,json,sys,subprocess
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha,cable_node,rotation
sys.path.insert(0,str(BASE/'cad'))
from generate import world,width,guide_normal,guide_outboard

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--margin-mm',type=float,default=1.0);a=p.parse_args();src=BASE/'results/force_release_clear_support375';out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);old=json.loads((src/'config.json').read_text());new=json.loads(json.dumps(old));new['tendon']['sector_margin_mm']=a.margin_mm
    if not .5<a.margin_mm<=2:raise ValueError('bounded positive real hardware spacing change')
    tree=ET.parse(src/'scene.scn');groups=[];mapping=0.;changes=[];events=[]
    for f,angle in enumerate(old['palm']['angles_deg']):
        rr=list(csv.DictReader((src/f'finger{f}.csv').open()));fr=list(csv.DictReader((src/f'guide_frames{f}.csv').open()));rigid=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in fr]);time=np.array([float(r['time_s']) for r in rr]);initial=np.fromstring(tree.find(f"./Node[@name='guides{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7)
        for j,side in enumerate((-1,1)):
            node=cable_node(tree,f,j);indices=np.fromstring(node.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);q=np.array([np.fromstring(r[f'guide{j}_q_m'],sep=' ').reshape(-1,3) for r in rr]);rest=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);pred=q.copy()
            for k,x in enumerate(old['tendon']['guide_stations']):
                expected=np.array(world(old,[x,side*(width(old,x)/2+guide_outboard(old,x)),guide_normal(old,x)],angle))*.001;mapping=max(mapping,float(np.max(abs(expected-rest[k]))));target=np.array(world(new,[x,side*(width(new,x)/2+guide_outboard(new,x)),guide_normal(new,x)],angle))*.001;delta=rotation(initial[indices[k],3:]).T@(target-rest[k]);pred[:,k]+=np.array([rotation(qr[indices[k],3:])@delta for qr in rigid]);changes.append(dict(finger=f,cable=j,station_mm=x,old_outboard_mm=guide_outboard(old,x),new_outboard_mm=guide_outboard(new,x),guide_displacement_mm=float(np.linalg.norm(target-rest[k])*1000)))
            groups.append((f,pred,float(node.find('SphereCollisionModel').get('radius'))))
        for k,t in enumerate(time):
            if 2.38<=t<=2.4:events.append(dict(finger=f,time_s=t,solver_error=float(fr[k]['solver_error']),solver_iterations=int(fr[k]['solver_iterations']),max_guide_speed_mm_s=float(np.linalg.norm(np.fromstring(fr[k]['rigid_v'],sep=' ').reshape(-1,6)[:,:3],axis=1).max()*1000)))
    if mapping>1e-12:raise ValueError('shared CAD/native reference mismatch;do not screen mismatched geometry')
    minimum=min(float((np.linalg.norm(q[:,:,None]-r[:,None,:],axis=3)-R-S).min()*1000) for i,(f,q,R) in enumerate(groups) for g,r,S in groups[i+1:] if f!=g)
    result=dict(status='FROZEN_MOTION_SCREEN_ONLY_NOT_DYNAMIC_RESULT',producer_sha256=sha(Path(__file__)),source_config_sha256=sha(src/'config.json'),source_scene_sha256=sha(src/'scene.scn'),geometry_source_sha256=sha(BASE/'cad/generate.py'),shared_initial_guide_error_m=mapping,changed_variable='sector_margin_mm only',old_margin_mm=old['tendon']['sector_margin_mm'],new_margin_mm=a.margin_mm,changes=changes,predicted_frozen_motion_minimum_gap_mm=minimum,original_event_solver=events,warning='New guide lever/mapping changes dynamics and cable path;replayed old motion is NOT candidate SOFA result,clearance PASS or unchanged holding evidence.')
    (out/'config.json').write_text(json.dumps(new,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
