"""Actual bounded-process memory measurements,not an engine leak certificate."""
import csv
import json
import re
import numpy as np
from curve_common import OUT,SDK,sha,write_json


def main():
    target=OUT/'memory_continuation_v1.json'
    if target.exists():raise ValueError('immutable measurement exists')
    names=('full_coarse','full_fine','full_coarse_n41','full_coarse_history1250nm','history1000nm_full24_v1','patch_refinement_v2/local625_prefix82','patch_refinement_v2/local312_prefix82_record200');cases={}
    for name in names:
        path=OUT/name;log=(path/'stdout.log').read_text();memory=[json.loads(line[len('MEM '):])for line in log.splitlines()if line.startswith('MEM ')]
        # Grid logs every1000th BEGIN,not every step. MEM(i) is after i
        # advances,therefore it matches the next logged BEGIN(i),not END(i).
        with(path/'grid.csv').open()as stream:time={int(r['step']):float(r['begin_time'])for r in csv.DictReader(stream)}
        actual_steps=int(re.findall(r'(\d+) iterations done',log)[-1])
        with(path/'contact.csv').open()as stream:last_time=float(list(csv.DictReader(stream))[-1]['time'])
        time[actual_steps]=last_time
        monitor=json.loads((path/'resource_samples.json').read_text())['samples']
        end=max(r['step']for r in memory);lo,hi=(6,13.8)if last_time>14 else(4,6)
        plateau=[r for r in memory if r['step']>0 and lo<=time[r['step']]<=hi]
        slope=None;span=None
        if len(plateau)>=3:
            steps=np.array([r['step']for r in plateau]);live=np.array([r['live_heap']+r['mmap']for r in plateau]);slope=float(np.polyfit(steps-steps[0],live,1)[0]);span=int(live.max()-live.min())
        maxima={key:max(r[key]for r in monitor if key in r)for key in('rss_kib','pss_kib','private_dirty_kib','fd')};fds=[r['fd']for r in monitor]
        cases[name]=dict(actual_steps=actual_steps,max_memory_sample_step=end,actual_simulated_time_s=last_time,monitor_maxima=maxima,fd_range=[min(fds),max(fds)],observed_plateau=dict(time_range_s=[lo,hi],samples=len(plateau),live_plus_mmap_range_bytes=span,ols_bytes_per_step=slope),after_unload=[r for r in memory if r['step']<0],resource_status='PASS'if maxima['rss_kib']*1024<4294967296 else'FAIL',raw_sha256={f:sha(path/f)for f in('stdout.log','resource_samples.json','grid.csv')})
    write_json(target,dict(status='PASS'if all(r['resource_status']=='PASS'for r in cases.values())else'FAIL',driver_binary_sha256=sha(SDK/'bin/graph_probe'),cases=cases,leak_certification='NOT RUN',scope='actual selected executions up to148000steps,including active contact. Quiet windows explicitly shown;short23400step refined prefixes are NOT60k/120k/hours tests. RSS is not live heap;post-unload allocator retention is separate. No LSan,repeat reload or whole-model no-leak certification inferred.'))
    print({name:(r['actual_steps'],r['monitor_maxima']['rss_kib'],r['fd_range'],r['observed_plateau']['ols_bytes_per_step'])for name,r in cases.items()})


if __name__=='__main__':main()
