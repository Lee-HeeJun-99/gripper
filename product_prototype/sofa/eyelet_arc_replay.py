"""Rigidly carried R5 arc proxy on old Native guide trajectory, not new dynamics."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha
def unit(x):return x/np.linalg.norm(x)
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    src=BASE/'results/opposed_nonuniform_mid1398';geom=BASE/'results/eccentric_eyelet1415/summary.json';g=json.loads(geom.read_text());root=ET.parse(src/'scene.scn').getroot();guides=root.find("Node[@name='guides0']");initial=np.fromstring(guides.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);assert np.max(np.abs(initial[:,3:]-[0,0,0,1]))==0
    routes=json.loads((BASE/'results/four_route_gate1408/summary.json').read_text())['routes'];models=[]
    for j in range(2):
        n=guides.find(f"Node[@name='cable{j}']");owners=np.fromstring(n.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);q=np.array(routes[j+2]['route_mm']);arcs=[]
        for k in range(5):
            arc=np.array(next(x for x in g['arcs'] if x['route']==j+2 and x['guide']==k)['points_mm']);owner=owners[k];arcs.append(dict(owner=int(owner),start=arc[0]-initial[owner,:3]*1000,end=arc[-1]-initial[owner,:3]*1000,u=unit(q[k+1]-q[k]),v=unit(q[k+2]-q[k+1])))
        models.append(dict(arcs=arcs,pull=q[0],terminal_owner=int(owners[-1]),terminal_local=q[-1]-initial[owners[-1],:3]*1000))
    def measure(frames):
        rot=Rotation.from_quat(frames[:,3:]);worst=0.;minspan=float('inf')
        for model in models:
            starts=[];ends=[];uin=[];vout=[]
            for arc in model['arcs']:
                owner=arc['owner'];r=rot[owner];origin=frames[owner,:3]*1000;starts.append(origin+r.apply(arc['start']));ends.append(origin+r.apply(arc['end']));uin.append(r.apply(arc['u']));vout.append(r.apply(arc['v']))
            terminal=frames[model['terminal_owner'],:3]*1000+rot[model['terminal_owner']].apply(model['terminal_local']);before=[model['pull']]+ends[:-1];after=starts[1:]+[terminal]
            for k in range(5):
                incoming=starts[k]-before[k];outgoing=after[k]-ends[k];minspan=min(minspan,float(np.linalg.norm(incoming)),float(np.linalg.norm(outgoing)))
                # atan2 avoids arccos loss near exact tangency.
                for expected,actual in ((uin[k],unit(incoming)),(vout[k],unit(outgoing))):worst=max(worst,float(np.degrees(np.arctan2(np.linalg.norm(np.cross(expected,actual)),expected@actual))))
        return worst,minspan
    baseline=measure(initial);history=[]
    for row in csv.DictReader((src/'guide_frames0.csv').open()):
        angle,span=measure(np.fromstring(row['rigid_q'],sep=' ').reshape(-1,7));history.append(dict(time_s=float(row['time_s']),maximum_tangent_mismatch_deg=angle,minimum_link_span_mm=span))
    result=dict(status='REJECT_FIXED_ARC_C1_REPLAY_PROXY' if max(x['maximum_tangent_mismatch_deg'] for x in history)>1e-6 else 'NO_RESOLVED_C1_MISMATCH_IN_REPLAY',initial_tangent_mismatch_deg=baseline[0],maximum_tangent_mismatch_deg=max(x['maximum_tangent_mismatch_deg'] for x in history),endpoint=history[-1],history=history,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),input_hashes={str(x.relative_to(BASE)):sha(x) for x in (geom,src/'scene.scn',src/'guide_frames0.csv')},scope='Actual old Native Rigid3 q, hypothesized attached fixed R5 arcs and straight links;not new hardware trajectory. C1 kinks in this proxy imply smooth finite wire needs changing contact/bend shape;not proof real flexible wire cannot operate. 1e-6deg resolves arithmetic only,not a relaxed physical acceptance. No object/contact/Holding, no q/v edits.',new_Native='NOT RUN')
    (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(result['status'],baseline,result['maximum_tangent_mismatch_deg'],result['endpoint'])
if __name__=='__main__':main()
