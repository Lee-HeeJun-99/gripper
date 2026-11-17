"""Independent actual event M/J/pre/post oracle;small enumeration is TEST ONLY."""
import argparse,csv,itertools,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();source=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((source/'identity.json').read_text());summary=json.loads((source/'summary.json').read_text())
    if summary['status']!='PASS':raise ValueError('complete actual coupled experiment required')
    snapshots=list(csv.DictReader((source/'coupled.event_states.csv').open()));events=list(csv.DictReader((source/'coupled.events.csv').open()));rows=list(csv.DictReader((source/'coupled.rows.csv').open()));scene=ET.parse(source/'scene.scn');nx=int(scene.find('.//FilmRailTendon').get('nx'));mass=np.fromstring(scene.find("Node[@name='assembly']/DiagonalMass").get('vertexMass'),sep=' ');indices=np.full(3*len(mass),-1,dtype=int);weights=np.ones(3*len(mass));nf=0
    for offset,ny in ((0,5),(5*nx,3),(8*nx,3)):
        for i in range(1,nx):
            for j in range(ny):
                for d in range(3):
                    if i!=1 or d!=2:indices[3*(offset+i*ny+j)+d]=nf;nf+=1
        for j in range(ny):indices[3*(offset+ny+j)+2]=indices[3*(offset+2*ny+j)+2];weights[3*(offset+ny+j)+2]=.25
    diagonal=np.zeros(nf+6)
    for a_,k in enumerate(indices):
        if k>=0:diagonal[k]+=weights[a_]**2*mass[a_//3]
    diagonal[nf:nf+3]=meta['body_mass'];diagonal[nf+3:]=meta['body_mass']*meta['inertia_per_mass']
    def pack(s):
        v=np.fromstring(s['local_velocity'],sep=' ');result=np.zeros(nf+6)
        for index,k in enumerate(indices):
            if k>=0 and weights[index]==1:result[k]=v[index]
        result[nf:nf+3]=np.fromstring(s['body_velocity'],sep=' ');result[nf+3:]=np.fromstring(s['body_omega'],sep=' ');return result
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');records=[]
    for time in sorted(set(r['time'] for r in events),key=float):
        pre=next(s for s in snapshots if s['time']==time and s['stage']=='pre');post=next(s for s in snapshots if s['time']==time and s['stage']=='post');owned=[r for r in rows if r['time']==time and r['stage']=='0'];atoms=[r for r in events if r['time']==time]
        if len(owned)>16:raise ValueError('test oracle limited16;not a production subset solver')
        if any(pre[k]!=post[k] for k in ('body_center','body_quaternion','local_displacement')):raise ValueError('impact changes position/orientation')
        before,after=pack(pre),pack(post);J=np.array([np.fromstring(r['jacobian'],sep=' ') for r in owned]);p=np.array([float(r['impulse']) for r in owned]);W=(J/diagonal)@J.T;incoming=J@before;normal=J@after;rank=int(np.linalg.matrix_rank(J));oracle=None
        for nactive in range(len(p)+1):
            for active in itertools.combinations(range(len(p)),nactive):
                trial=np.zeros(len(p))
                if active:
                    sub=np.ix_(active,active);trial[list(active)]=np.linalg.lstsq(W[sub],-incoming[list(active)],rcond=None)[0]
                velocity=incoming+W@trial
                if np.min(trial)>=-1e-18 and np.min(velocity)>=-1e-10 and max([abs(velocity[i]) for i in active],default=0.)<=1e-10:oracle=before+(J.T@trial)/diagonal;break
            if oracle is not None:break
        if oracle is None:raise ValueError('independent oracle has no certified solution')
        residual=float(np.linalg.norm(diagonal*(after-before)-J.T@p));error=float(np.linalg.norm(oracle-after));loss=-.5*p.dot(J@(before+after));energy_error=abs(loss-float(atoms[0]['impact_loss']));angular_J=float(np.linalg.norm(J[:,nf+3:]));body_J_error=max(float(np.linalg.norm(J[i,nf:nf+3]+np.array([float(r[k]) for k in ('nx','ny','nz')]))) for i,r in enumerate(owned));valid=residual<=1e-12 and error<=1e-10 and energy_error<=1e-18 and np.min(p)>=0 and np.min(normal)>=-1e-10 and angular_J==0 and body_J_error<=1e-12
        records.append(dict(status='PASS' if valid else 'FAIL',time=float(time),rows=len(p),rank=rank,individual_impulse_unique=rank==len(p),momentum_residual=residual,oracle_velocity_error=error,stable_impact_loss=loss,energy_error=energy_error,sphere_rotation_J_norm=angular_J,body_translation_J_error=body_J_error,positions_unchanged=True,body_velocity_before=before[nf:nf+3].tolist(),body_velocity_after=after[nf:nf+3].tolist()))
    status='PASS' if records and all(r['status']=='PASS' for r in records) else 'FAIL';write_json(out/'summary.json',dict(status=status,scope='actual event snapshots vs independent mass/active-subset reference;NOT full nonlinear dynamics/energy/grasp',records=records,case=a.case,hashes={f:sha(source/f) for f in ('identity.json','scene.scn','coupled.event_states.csv','coupled.events.csv','coupled.rows.csv')}));print(json.dumps(dict(status=status,records=records)))
if __name__=='__main__':main()
