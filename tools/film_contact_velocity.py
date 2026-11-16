"""Accepted-row gap-rate diagnosis,not continuous collision-time reconstruction."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_surface_distance import point_triangles
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();records={};inputs={}
    for name in a.cases:
        directory=ROOT/'results'/('autonomous_film_'+name);summary=json.loads((directory/'summary.json').read_text())
        if summary.get('status')!='PASS' or not summary.get('finite'):raise ValueError('complete finite trajectories only')
        source=directory/'1';tree=ET.parse(source/'scene.scn');center=np.fromstring(tree.find("Node[@name='fixed']/MechanicalObject").get('position'),sep=' ');radius=8+float(tree.find('FilmNativeCoupledCorrection').get('contactDistance'))
        geometry=list(csv.DictReader((source/'contact.csv').open()));velocities={r['time']:r for r in csv.DictReader((source/'momentum.csv').open())};lookup={r['time']:i for i,r in enumerate(geometry)}
        rows=[r for r in csv.DictReader((source/'coupled.csv.owned_rows.csv').open()) if float(r['lambda_impulse'])>0]
        if not rows:raise ValueError('positive contact required')
        first=rows[0]['time'];output=[]
        for row in rows:
            if row['time']!=first:break
            index=lookup[first];g=geometry[index];nodes=np.fromstring(row['support'],sep=' ',dtype=int);J=np.fromstring(row['jacobian'],sep=' ').reshape(-1,3);velocity=velocities[first]
            rates={key:float(np.sum(J*np.fromstring(velocity[key],sep=' ').reshape(-1,3)[nodes])) for key in ('v_begin','v_free','v_accepted')}
            def gap(coordinates):
                q=np.fromstring(coordinates,sep=' ').reshape(-1,3)[nodes]
                if len(q)==3:
                    distance,_,bad=point_triangles(center,q[None,:,:])
                    if bad:raise ValueError('degenerate contact triangle')
                    return float(distance[0]-radius)
                if len(q)==2:
                    edge=q[1]-q[0];d=edge@edge
                    if d<=0:raise ValueError('degenerate contact edge')
                    point=q[0]+np.clip((center-q[0])@edge/d,0,1)*edge
                elif len(q)==1:point=q[0]
                else:raise ValueError('unsupported primitive')
                return float(np.linalg.norm(point-center)-radius)
            gn,gp=gap(g['positions']),gap(g['begin_positions']);older=gap(geometry[index-1]['begin_positions']) if index else None;dt=float(g['dt'])
            output.append(dict(time=float(first),row=int(row['owner_row']),feature=int(row['feature']),lambda_impulse=float(row['lambda_impulse']),accepted_gap=gn,previous_gap=gp,older_gap=older,current_J_normal_rates=rates,BDF2_gap_history_rate=(3*gn-4*gp+older)/(2*dt) if older is not None else None,continuous_birth_fraction=None))
        records[name]=output
        for filename in ('scene.scn','contact.csv','momentum.csv','coupled.csv.owned_rows.csv'):inputs[str((source/filename).relative_to(ROOT))]=sha(source/filename)
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    result=dict(status='EXPERIMENTAL',scope='actual FIRST positive accepted rows;all velocity projections use CURRENT owned J;NOT continuous birth time,impact restitution certification or corrected dynamics',records=records,inputs=inputs,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),script_sha256=sha(__file__))
    write_json(out/'summary.json',result);print(json.dumps(result['records']))
if __name__=='__main__':main()
