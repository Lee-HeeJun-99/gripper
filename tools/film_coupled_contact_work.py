"""Regular normal constraint work is a DISCRETE diagnostic,not friction heat."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_coupled_audit import gaps
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');records={}
    for name in a.cases:
        folder=ROOT/'results'/('autonomous_film_'+name);meta=json.loads((folder/'identity.json').read_text());summary=json.loads((folder/'summary.json').read_text());states=list(csv.DictReader((folder/'coupled.states.csv').open()));owned=list(csv.DictReader((folder/'coupled.rows.csv').open()));eventStates=list(csv.DictReader((folder/'coupled.event_states.csv').open()))
        if summary['status']!='PASS' or meta.get('adaptive') or len(states)!=meta['steps']:raise ValueError('completed uniform macro owner trace required')
        scene=ET.parse(folder/'scene.scn');nx=int(scene.find('.//FilmRailTendon').get('nx'));root=np.fromstring(scene.find("MechanicalObject[@name='dofs']").get('position'),sep=' ')
        if np.any(root!=0):raise ValueError('this diagnostic requires declared zero initial film state')
        topology=scene.find('.//TriangleSetTopologyContainer');rest=np.fromstring(topology.get('position'),sep=' ').reshape(-1,3);tri=np.fromstring(topology.get('triangles'),sep=' ',dtype=int).reshape(-1,3)
        classified={kind:dict(rows=0,signed_work=0.,absolute_work=0.) for kind in ('newborn','already_touching')}
        indices=np.full(root.size,-1,dtype=int);weights=np.ones(root.size);nf=0
        for offset,ny in ((0,5),(5*nx,3),(8*nx,3)):
            for i in range(1,nx):
                for j in range(ny):
                    for d in range(3):
                        if i!=1 or d!=2:indices[3*(offset+i*ny+j)+d]=nf;nf+=1
            for j in range(ny):indices[3*(offset+ny+j)+2]=indices[3*(offset+2*ny+j)+2];weights[3*(offset+ny+j)+2]=.25
        previousQ=np.zeros(root.size);previousC=np.fromstring(meta['initial_body_center'],sep=' ');previousTime=0.;normalWork=0.;projection=0.;rows=[]
        for step,state in enumerate(states,1):
            end=float(state['time']);h=meta['duration']/meta['steps'];q0=previousQ;c0=previousC
            if int(state['event']):
                events=[e for e in eventStates if e['stage']=='post' and previousTime-1e-14<=float(e['time'])<=end+1e-14]
                if len(events)!=1:raise ValueError('event/remainder stage cannot be uniquely reconstructed')
                event=events[0];q0=np.fromstring(event['local_displacement'],sep=' ');c0=np.fromstring(event['body_center'],sep=' ');h=end-float(event['time'])
            q1=np.fromstring(state['local_displacement'],sep=' ');c1=np.fromstring(state['body_center'],sep=' ');y=np.zeros(nf+6)
            if h>0:
                for k,index in enumerate(indices):
                    if index>=0 and weights[k]==1:y[index]=(q1[k]-q0[k])/h
                y[nf:nf+3]=(c1-c0)/h
            start_gaps=gaps((rest+q0.reshape(-1,3))[tri],c0,meta['buffer_radius']);value=0.
            for row in owned:
                if int(row['step'])!=step or row['stage']!='1':continue
                if h<=0:raise ValueError('constraint impulse without a positive regular interval')
                J=np.fromstring(row['jacobian'],sep=' ')
                if np.linalg.norm(J[nf+3:])!=0:raise ValueError('sphere-only diagnostic;nonradial torque unsupported')
                contribution=float(row['impulse'])*J.dot(y);value+=contribution
                kind='newborn' if start_gaps[int(row['triangle'])]>1e-10 else 'already_touching'
                classified[kind]['rows']+=1;classified[kind]['signed_work']+=contribution;classified[kind]['absolute_work']+=abs(contribution)
            normalWork+=value;projection+=float(state['projection_loss']);rows.append(dict(time=end,endpoint_constraint_work=value,cumulative_endpoint_constraint_work=normalWork,projection_loss=float(state['projection_loss']),cumulative_projection_loss=projection,attachment_energy=float(state['U_attachment'])));previousQ=q1;previousC=c1;previousTime=end
        target=out/(name+'.csv')
        with target.open('x') as f:writer=csv.DictWriter(f,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
        records[name]=dict(signed_regular_constraint_work=normalWork,jacobian_geometry_time=meta.get('regular_contact_jacobian_time','endpoint'),signed_projection_loss=projection,by_start_gap=classified,classification_gap_tolerance=1e-10,maximum_absolute_constraint_step_work=max(abs(r['endpoint_constraint_work']) for r in rows),csv_column_note='endpoint_constraint_work is legacy column name;actual J is archived used row,see jacobian_geometry_time',source_hashes={f:sha(folder/f) for f in ('identity.json','scene.scn','coupled.states.csv','coupled.rows.csv','coupled.event_states.csv')})
    write_json(out/'summary.json',dict(status='EXPERIMENTAL',scope='measured discrete regular constraint work;NOT physical Coulomb heat or global energy certificate',cases=records,limitations=['uses actual archived contact-row direction;velocity at midpoint','event-frame remainder reconstructed from stored event state/time','no missing full-system work inferred from this diagnostic']));print(json.dumps(records))
if __name__=='__main__':main()
