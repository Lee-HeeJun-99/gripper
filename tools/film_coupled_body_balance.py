"""Independent regular-contact body momentum/kinematics/partial work identity."""
import argparse,csv,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();source=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((source/'identity.json').read_text());summary=json.loads((source/'summary.json').read_text())
    if summary['status']!='PASS':raise ValueError('complete coupled process required')
    states=list(csv.DictReader((source/'coupled.states.csv').open()));rows=list(csv.DictReader((source/'coupled.rows.csv').open()));events=list(csv.DictReader((source/'coupled.events.csv').open()))
    if events:raise ValueError('this independent smooth balance does not straddle impact;use event inventories')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');mass=meta['body_mass'];inertia=mass*meta['inertia_per_mass'];force=np.array([0,0,meta.get('body_force_z',0.)]);damping=meta['rayleigh_mass'];oldv=np.fromstring(meta['initial_body_velocity'],sep=' ');v,w=oldv[:3],oldv[3:];center=np.fromstring(meta['initial_body_center'],sep=' ');time=0.;records=[]
    for index,state in enumerate(states):
        t=float(state['time']);h=t-time;nextv=np.fromstring(state['body_velocity'],sep=' ');nextw=np.fromstring(state['body_omega'],sep=' ');nextc=np.fromstring(state['body_center'],sep=' ');position=np.zeros(3);projection=np.zeros(3)
        for row in rows:
            if int(row['step'])!=index+1:continue
            impulse=-np.array([float(row[k]) for k in ('nx','ny','nz')])*float(row['impulse'])
            if row['stage']=='1':position+=impulse
            elif row['stage']=='2':projection+=impulse
            else:raise ValueError('unexpected collision in smooth identity')
        unprojected=nextv-projection/mass;middle=(v+unprojected)/2;spin=(w+nextw)/2;residual=mass*(nextv-v)+h*damping*mass*middle-h*force-position-projection;angular=inertia*(nextw-w)+h*damping*inertia*spin;kinematic=nextc-center-h*middle
        external=h*force.dot(middle);damping_work=-h*damping*mass*middle.dot(middle);contact_work=middle.dot(position);projection_work=.5*(unprojected+nextv).dot(projection);kinetic_change=.5*mass*(nextv-v).dot(nextv+v);energy_error=kinetic_change-external-damping_work-contact_work-projection_work
        records.append(dict(time=t,momentum_residual=float(np.linalg.norm(residual)),angular_residual=float(np.linalg.norm(angular)),position_residual=float(np.linalg.norm(kinematic)),body_energy_identity_residual=float(energy_error),external_work=external,body_damping_work=damping_work,body_contact_work=contact_work,body_projection_work=projection_work))
        time=t;v,w,center=nextv,nextw,nextc
    errors={k:max(abs(r[k]) for r in records) for k in ('momentum_residual','angular_residual','position_residual','body_energy_identity_residual')};valid=all(v<=1e-12 for v in errors.values())
    with (out/'body_balance.csv').open('x') as f:
        writer=csv.DictWriter(f,fieldnames=records[0]);writer.writeheader();writer.writerows(records)
    write_json(out/'summary.json',dict(status='PASS' if valid else 'FAIL',scope='body-only smooth constraint momentum and work identity;NOT full film/body energy or angular certification',case=a.case,maximum_residuals=errors,source_hashes={f:sha(source/f) for f in ('identity.json','summary.json','coupled.states.csv','coupled.rows.csv')},unmeasured=['full nodal fixture reaction inventory','film/rail damping work','synchronized tendon quadrature','full nonlinear angular momentum identity']))
    print(json.dumps(dict(status='PASS' if valid else 'FAIL',errors=errors)))
if __name__=='__main__':main()
