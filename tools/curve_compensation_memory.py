"""Quantify completed same-model runs; RSS alone is not leak certification."""
import json
import numpy as np
from curve_common import OUT,write_json


def main():
    target=OUT/'bounded_memory_v1.json'
    if target.exists():raise ValueError('refuse overwritten memory evidence')
    cases={}
    for path in sorted((OUT/'grasp').iterdir()):
        if not(path/'metrics.json').exists():continue
        r=json.loads((path/'metrics.json').read_text());dt=r['config']['dt']
        lines=(path/'stdout.log').read_text().splitlines();m=[json.loads(s[4:])for s in lines if s.startswith('MEM ')]
        hold=[x for x in m if x['step']>=0 and 6<=x['step']*dt<14]
        completed=[x for x in m if x['step']>=0];unloaded=[x for x in m if x['step']<0]
        row=dict(actual_steps=max((x['step']for x in completed),default=None),dt=dt,full_contact_hold_simulated_seconds=8 if not r['config']['profile_only']else None,process=r['process'])
        if hold:
            x=np.array([v['step']for v in hold]);y=np.array([v['live_heap']+v['mmap']for v in hold]);row['hold_arena_live_plus_mmap_proxy']=dict(samples=len(hold),minimum_bytes=int(y.min()),maximum_bytes=int(y.max()),OLS_bytes_per_step=float(np.polyfit(x,y,1)[0])if len(hold)>1 else None)
        row['after_unload']=unloaded
        samples_path=path/'resource_samples.json'
        if samples_path.exists():
            data=json.loads(samples_path.read_text());samples=data['samples'];row['proc_monitor_error']=data['monitor_error'];row['proc_sample_count']=len(samples)
            for key in('rss_kib','pss_kib','private_dirty_kib','fd'):
                values=[s[key]for s in samples if key in s]
                row[key]=dict(minimum=min(values),maximum=max(values),last=values[-1])if values else None
        else:row['proc_sampling']='NOT RUN'
        row['scope']='native same-parent2s proc samples and SDK mallinfo2 proxy;full-wall ranges are not exact hold-window PSS;no allocation trace or hours-soak certificate'
        cases[path.name]=row
    write_json(target,dict(status='EXPERIMENTAL',cases=cases,known_144000_step_case='quarterdt',memory_cap_bytes=4294967296,LSan='NOT RUN',continuous_240000_steps='NOT RUN',hours_soak='NOT RUN',new_energy_driver_proc_sampling='NOT RUN;its4GiBcap is enforced but no retroactive same-parent samples invented'))
    print({n:(r['actual_steps'],r.get('hold_arena_live_plus_mmap_proxy'))for n,r in cases.items()if r.get('actual_steps',0)>=60000})


if __name__=='__main__':main()
