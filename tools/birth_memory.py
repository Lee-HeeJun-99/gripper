"""Finite-window memory observations, NOT a blanket no-leak certificate."""
import json
from birth_common import ROOT,OUT,write_json
def slope(pairs):
    if len(pairs)<2:return None
    x=sum(p[0]for p in pairs)/len(pairs);y=sum(p[1]for p in pairs)/len(pairs)
    d=sum((p[0]-x)**2 for p in pairs)
    return sum((p[0]-x)*(p[1]-y)for p in pairs)/d if d else None
def main():
    result={}
    for folder in [OUT/'grasp',ROOT/'results/birth_20261115/grasp']:
        for path in sorted(folder.glob('*/metrics.json')):
            sample=path.parent/'resource_samples.json'
            if not sample.exists():continue
            raw=json.loads(sample.read_text());s=raw['samples'];mem=[json.loads(t[4:])for t in(path.parent/'stdout.log').read_text().splitlines()if t.startswith('MEM ')]
            tail=[r for r in mem if r['step']>=0];tail=tail[len(tail)//2:]
            result[str(path.parent.relative_to(ROOT))]=dict(status='EXPERIMENTAL',sample_count=len(s),monitor_error=raw.get('monitor_error'),rss_range_kib=[min(r['rss_kib']for r in s),max(r['rss_kib']for r in s)]if s else None,pss_range_kib=[min(r['pss_kib']for r in s if'pss_kib'in r),max(r['pss_kib']for r in s if'pss_kib'in r)]if any('pss_kib'in r for r in s)else None,fd_counts=sorted(set(r['fd']for r in s)),tail_rss_bytes_per_step=slope([(r['step'],r['rss'])for r in tail]),tail_live_heap_bytes_per_step=slope([(r['step'],r['live_heap'])for r in tail]),engine_steps=max((r['step']for r in mem),default=None),unload_heap=[r['live_heap']for r in mem if r['step']<0],scope='tail may include release; not sustained-contact/hours or complete allocation traceback')
    write_json(OUT/'memory_observations.json',result);print('measured memory cases',len(result))
if __name__=='__main__':main()
