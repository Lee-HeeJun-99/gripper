"""Synchronized PARTIAL journal; unknown terms are null, not fabricated zero."""
import csv,json
import numpy as np
from history_common import ROOT,OUT,write_json,sha,identity
from trial_validation import read_states
from closure_validation_suite import logged
def main():
    identity();out=OUT/'energy_partial';out.mkdir(exist_ok=False);trial=OUT/'grasp/repeated';config=json.loads((trial/'config.json').read_text());actual=json.loads((trial/'metrics.json').read_text())
    if not actual.get('execution_completed') or config['shape']!=0:raise ValueError('scope: actual complete isotropic sphere run only')
    exe=ROOT/'build/history_20261115/history_stored_energy';c=logged(['g++','-std=c++17','-O2','-Wall','-Wextra','diagnostics/contact_history/StoredEnergy.cpp','-o',exe],out/'compile',120)
    if c['exit_code']:raise RuntimeError('compile')
    states=read_states(trial/'state.txt');obj=config['object_index'];n=config['nodes'];m=config['beam_material'];inp=out/'input.txt'
    with inp.open('w') as f:
        f.write(f'{n} {len(states)}\n'+ ' '.join(str(m[k]) for k in ('EA','GAy','GAz','GJ','EIy','EIz'))+'\n')
        for row in states:
            x=np.array(row['X']).reshape(obj+1,7);v=np.array(row['V']).reshape(obj+1,6);f.write(str(row['time'])+'\n');np.savetxt(f,np.column_stack((x,v)),fmt='%.17g')
    process=logged([exe,inp,out/'stored.csv'],out/'evaluate',120)
    if process['exit_code']:raise RuntimeError('energy evaluation')
    def rows(path):return list(csv.DictReader(path.open()))
    stored=rows(out/'stored.csv');contact={round(float(r['time']),8):r for r in rows(trial/'contact.csv')};layers=[{round(float(r['time']),8):r for r in rows(trial/f'layer{i}.csv')} for i in range(3)]
    with (out/'journal.csv').open('w',newline='') as f:
        fields=['time','beam_U','kinetic_K','contact_tangent_U','contact_plastic_D','contact_detachment_D','layer_plastic_D','pressure'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in stored:
            t=round(float(r['time']),8)
            if t not in contact:continue
            ct=contact[t];lr=[l[t] for l in layers];w.writerow(dict(time=t,beam_U=r['beam_U'],kinetic_K=r['kinetic_K'],contact_tangent_U=ct['elastic_energy'],contact_plastic_D=ct['friction_dissipation'],contact_detachment_D=ct['release_dissipation'],layer_plastic_D=sum(float(l['dissipated']) for l in lr),pressure=lr[0]['pressure']))
    result=dict(status='BLOCKED',partial_journal_status='PASS',origin='actual saved SOFA states evaluated OFFLINE with frozen energy strain kernel; synchronized existing end-event CSV, not new time stepping',frames=len(stored),recording_stride_steps=config['stride'],synchronization='time labels agree, but CSV contact energy is PRE history commit; state after AnimateEnd. No total closure is claimed.',unknown=dict(layer_stored_energy=None,normal_contact_energy=None,actuator_work=None,pressure_parameter_work=None,rayleigh_stiffness_dissipation=None,numerical_energy_term=None,total_closure=None),reason='sampled end-event records lack pre/post-commit inventory and force-stage work; a per-step in-engine journal remains necessary',initial=stored[0],final=stored[-1],source_sha256=sha(ROOT/'tools/history_energy.py'),kernel_sha256=sha(ROOT/'models/conservative_beam/EnergyKernel.h'),trial_metrics_sha256=sha(trial/'metrics.json'),artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file()})
    write_json(out/'metrics.json',result);print(result['status'],result['frames'],result['final'])
if __name__=='__main__':main()
