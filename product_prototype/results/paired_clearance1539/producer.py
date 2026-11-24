"""Actual saved-state guide-sphere pair attribution;not solid CAD/swept CCD."""
import argparse,csv,json,itertools,re
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from analyse import BASE,sha,cable_node,rotation

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=BASE/'results'/a.case;out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);tree=ET.parse(src/'scene.scn');cfg=json.loads((src/'config.json').read_text());stations=cfg['tendon']['guide_stations'];groups=[];mapping_error=0.;times=None;inputs={};pairs=[]
    for f in range(3):
        paths=[src/f'finger{f}.csv',src/f'guide_frames{f}.csv'];rows=list(csv.DictReader(paths[0].open()));frames=list(csv.DictReader(paths[1].open()));t=np.array([float(r['time_s']) for r in rows]);tf=np.array([float(r['time_s']) for r in frames]);assert np.array_equal(t,tf)
        if times is None:times=t
        else:assert np.array_equal(times,t)
        rigid=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in frames]);initial=np.fromstring(tree.find(f"./Node[@name='guides{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7)
        for j in (0,1):
            node=cable_node(tree,f,j);model=node.find('SphereCollisionModel');radius=float(model.get('radius'));q=np.array([np.fromstring(r[f'guide{j}_q_m'],sep=' ').reshape(-1,3) for r in rows]);assert q.shape[1]==len(stations)
            rest=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);indices=np.fromstring(node.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int)
            for k,idx in enumerate(indices):
                local=rotation(initial[idx,3:]).T@(rest[k]-initial[idx,:3]);reconstructed=np.array([frame[idx,:3]+rotation(frame[idx,3:])@local for frame in rigid]);mapping_error=max(mapping_error,float(np.max(abs(reconstructed-q[:,k]))))
            groups.append(dict(finger=f,cable=j,radius=radius,q=q,model=f'/guides{f}/cable{j}/{model.get("name","SphereCollisionModel1")}'))
        for path in paths:inputs[path.name]=sha(path)
    trace=np.full(len(times),np.inf)
    for g,h in itertools.combinations(groups,2):
        if g['finger']==h['finger']:continue
        gap=np.linalg.norm(g['q'][:,:,None]-h['q'][:,None,:],axis=3)-g['radius']-h['radius'];trace=np.minimum(trace,gap.min(axis=(1,2)))
        for i,j in itertools.product(range(len(stations)),repeat=2):
            values=gap[:,i,j];idx=int(np.argmin(values));negative=np.flatnonzero(values<0)
            if len(negative):pairs.append(dict(finger0=g['finger'],cable0=g['cable'],side0=(-1,1)[g['cable']],station0_mm=stations[i],finger1=h['finger'],cable1=h['cable'],side1=(-1,1)[h['cable']],station1_mm=stations[j],minimum_gap_mm=float(values[idx]*1000),worst_time_s=float(times[idx]),first_negative_s=float(times[negative[0]]),last_negative_s=float(times[negative[-1]]),negative_frames=len(negative),centre0_m=g['q'][idx,i].tolist(),centre1_m=h['q'][idx,j].tolist()))
    pairs.sort(key=lambda r:r['minimum_gap_mm']);detected={}
    path=src/('detector.csv' if (src/'detector.csv').exists() else 'detection_pairs.csv')
    if path.exists():
        inputs[path.name]=sha(path)
        for row in csv.DictReader(path.open()):
            if all(re.match(r'/guides\d+/cable\d+/',row[k]) for k in ('model0','model1')):
                key=' | '.join(sorted([row['model0'],row['model1']]));detected[key]=detected.get(key,0)+1
    with (out/'sampled_gap.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['actual_time_s','minimum_native_guide_sphere_gap_mm']);w.writerows(zip(times,trace*1000))
    result=dict(status='FAIL_SAMPLED_NATIVE_GUIDE_SPHERES' if pairs else 'NO_SAMPLED_GUIDE_SPHERE_OVERLAP',scope='Actual synchronous saved mapped guide centers and native sphere radii ONLY;negative proxy gap not proof of exact solid eyelet/support intersection;NOT swept CCD,whole assembly or grasp PASS',case=a.case,source_sha256=sha(Path(__file__)),inputs={**inputs,'scene.scn':sha(src/'scene.scn'),'config.json':sha(src/'config.json')},actual_frames=len(times),mapping_max_error_m=mapping_error,mapping_state_api='PASS' if mapping_error<=1e-12 else 'FAIL',minimum_gap_mm=float(trace.min()*1000),negative_frame_count=int(np.count_nonzero(trace<0)),offending_pairs=pairs,actual_native_detector_guide_pair_counts=detected,window_minimum_mm={name:float(trace[(times>=lo)&(times<=hi)].min()*1000) if np.any((times>=lo)&(times<=hi)) else None for name,lo,hi in [('closing',0,.5),('hold',1.6,2),('release',2,2.5),('recovery',2.5,3)]},solid_support_clearance=None)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='offending_pairs'},indent=2));print('Worst pair:',pairs[:1])

if __name__=='__main__':main()
