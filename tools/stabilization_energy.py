"""Measured partial energy/work audit; never substitutes zero for unavailable terms."""
import csv
import json
import numpy as np
from stabilization_common import OUT,write_json,sha
from trial_validation import read_states

def main():
    records={}
    for p in sorted((OUT/'grasp').glob('*/metrics.json')):
        r=json.loads(p.read_text());c=r['config']
        if r['status']=='FAIL' or (p.parent/'analysis_failure.json').exists() or c['duration']<8:continue
        raw=read_states(p.parent/'state.txt');obj=c['object_index'];mass=.00004/obj;I=.0001*c['object_inertia_per_mass'];ke=[]
        for frame in raw:
            v=np.array(frame['V']).reshape(-1,6);ke.append(float(.5*mass*np.sum(v[:obj]**2)+.5*.0001*np.sum(v[obj,:3]**2)+.5*I*np.sum(v[obj,3:]**2)))
        with (p.parent/'state.txt.csv').open() as stream:component=list(csv.DictReader(stream))
        with (p.parent/'contact.csv').open() as stream:contact=list(csv.DictReader(stream))
        end=c.get('hold_until',8);length=np.array([float(row['cable_length']) for row in component]);time=np.array([float(row['time']) for row in component]);T=np.where((time>=.5-1e-9)&(time<end+2-1e-9),.001,0)
        cable_work=float(np.sum(-.5*(T[:-1]+T[1:])*np.diff(length)))
        on=min(raw,key=lambda f:abs(f['time']-6));off=min(raw,key=lambda f:abs(f['time']-end));work=c['load']*(off['X'][7*obj+c['axis']]-on['X'][7*obj+c['axis']])
        records[p.parent.name]=dict(max_kinetic_energy=max(ke),final_kinetic_energy=ke[-1],sampled_cable_work=cable_work,external_load_work=work,
            distributed_friction_dissipation=float(contact[-1]['friction_dissipation']),layer_friction_dissipation=float(component[-1]['friction_dissipation']),
            component_energy_scope='layer+cable+normal penalty only',beam_elastic_energy=None,rayleigh_dissipation=None,total_energy_balance_status='BLOCKED',
            reason='actual BeamFEM getPotentialEnergy API says not implemented; full damping/beam work not independently reconstructed',
            source_metrics_sha256=sha(p),units='model F*mm; no measured energy data')
    write_json(OUT/'energy_audit.json',dict(records=records,full_system_balance='BLOCKED',gravity='explicit scene gravity zero, not an omitted nonzero term',conservative_contact_kernel='normal penalty only',friction_law='power=-mu*Fn*|vt|^2/sqrt(|vt|^2+speed^2)<=0'))
    print('partial actual energy/work records',len(records),'global balance BLOCKED')

if __name__=='__main__':main()
