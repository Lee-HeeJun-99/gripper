"""Honest separate convergence gates; failed prerequisite blocks grasp study."""
import csv,json,re,hashlib
from pathlib import Path
import numpy as np
from history_common import ROOT,OUT,write_json,sha
COMPARISONS=[('normal_8_16','base','normal_q16',.01),('normal_16_32','normal_q16','normal_q32',.01),('tangent_cell_2_4','base','cell_order4',.01),('history_01_005','base','history_half',.01),('history_005_0025','history_half','history_quarter',.01),('mesh_11_21','base','n21',.01),('mesh_21_41','n21','n41',.01),('time_half','base','dt_half',.001),('time_quarter','dt_half','dt_quarter',.001),('repeat','base','repeated',1e-6)]
def comparison(a,b,limit):
    differences={};absolute={}
    for key in ('hold_displacement_mm','hold_rotation_increment_rad'):
        x,y=a[key],b[key];absolute[key]=abs(x-y);differences[key]=abs(x-y)/abs(y) if y else (0. if x==0 else float('inf'))
    return dict(status='PASS' if all(v<=limit for v in differences.values()) else 'FAIL',limit=limit,relative_difference=differences,absolute_difference=absolute,denominator='absolute fine value, unchanged criterion')
def main():
    results={};memory={};sources={};attempts={}
    for d in sorted((OUT/'grasp').iterdir()):
        file=d/'metrics.json' if (d/'metrics.json').exists() else d/'recovered_metrics.json'
        if not file.exists():continue
        r=json.loads(file.read_text());sources[d.name]=str(file.relative_to(ROOT))
        if not r.get('config',{}).get('profile_only'):attempts[d.name]=r
        if not r.get('config',{}).get('profile_only') and 'hold_displacement_mm'in r:results[d.name]=r
        log=d/'stdout.log';mem=[]
        for line in log.read_text().splitlines():
            if line.startswith('MEM '):mem.append(json.loads(line[4:]))
        if mem:
            run=[m for m in mem if m['step']>=0];tail=[m for m in run if m['step']>=10000];last=[m for m in mem if m['step']<0];dt=r['config']['dt']
            hold=[m for m in run if 6<=m['step']*dt<14]
            slope=float(np.polyfit([m['step'] for m in hold],[m['live_heap']+m['mmap'] for m in hold],1)[0]) if len(hold)>2 else None
            memory[d.name]=dict(steps=max(m['step'] for m in run),peak_rss=max(m['rss'] for m in run),last_unload=last[-1] if last else None,post_warmup_live_heap_bytes_range=[min(m['live_heap']+m['mmap'] for m in tail),max(m['live_heap']+m['mmap'] for m in tail)] if tail else None,hold_proxy_slope_bytes_per_step=slope,scope='mallinfo2 arena-live+mmap proxy, not complete allocation trace; RSS is not leak proof; FD/PSS NOT RUN',dt=dt)
    checks={}
    for name,a,b,limit in COMPARISONS:
        if a not in results or b not in results:
            failed={n:attempts[n].get('failure_reason','physical metrics unavailable') for n in (a,b) if n in attempts and n not in results}
            checks[name]=dict(status='FAIL' if failed else 'NOT RUN',coarse=a,fine=b,failed_attempts=failed);continue
        ra,rb=results[a],results[b]
        if ra['identity']['history_build']!=rb['identity']['history_build']:raise ValueError('compiled model mismatch')
        immutable=['shape','axis','load','mu','normal_k','tangent_k','tension','pressure','rayleigh_mass','beam_material']
        if any(ra['config'][key]!=rb['config'][key] for key in immutable):raise ValueError('different physical problem')
        checks[name]=dict(comparison(ra,rb,limit),coarse=a,fine=b)
        if not (ra.get('bounded_hold_pass') and rb.get('bounded_hold_pass')):
            checks[name].update(status='FAIL',failure_reason='underlying physical hold/equilibrium gate failed')
    summary=dict(status='FAIL' if any(c['status']=='FAIL' for c in checks.values()) else 'EXPERIMENTAL',comparisons=checks,grasp_optimization='BLOCKED',reason='all contact/history/space/time and needed energy prerequisites must pass; no grasp objectives executed',cases={name:{k:r.get(k) for k in ('status','bounded_hold_pass','hold_displacement_mm','hold_rotation_increment_rad','global_force_residual','global_moment_residual','recovery_pass','friction_dissipation')} for name,r in results.items()},sources=sources)
    write_json(OUT/'convergence.json',summary);write_json(OUT/'memory_observation.json',memory)
    target=ROOT/'reports/history_evidence';target.mkdir(exist_ok=True);write_json(target/'convergence.json',summary);write_json(target/'memory.json',memory)
    with (target/'convergence.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['comparison','status','limit','translation_relative_error','rotation_relative_error'])
        for name,r in checks.items():writer.writerow([name,r['status'],r.get('limit'),r.get('relative_difference',{}).get('hold_displacement_mm'),r.get('relative_difference',{}).get('hold_rotation_increment_rad')])
    print({name:r['status'] for name,r in checks.items()})
if __name__=='__main__':main()
