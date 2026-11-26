"""Conservative swept AABB containment check independent of sampled fragments."""
import json,sys
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,common
p=ROOT/'validation/finger/AK_root_retention1/summary.json';d=json.loads(p.read_text())
assert sha(REPO/d['producer']['path'])==d['producer']['SHA256']
fixed={n:read(REPO/r['path']) for n,r in d['inputs'].items() if 'ROOT' in n}
for r in d['inputs'].values():assert sha(REPO/r['path'])==r['SHA256']
rows=[]
for r in d['rows']:
    if r['dz_mm']!=0:continue
    b=r['bounds_mm']; envelope=box(b[0],b[1],b[2]-.5,b[3]-b[0],b[4]-b[1],b[5]-b[2]+1)
    pairs={n:common(envelope,s) for n,s in fixed.items()}
    # Transverse motion into the actual touching clamp must be rejected.
    dx=-.1 if r['part']=='F0_SKIN' else .1
    control=box(b[0]+dx,b[1],b[2],b[3]-b[0],b[4]-b[1],b[5]-b[2])
    control_overlap=max(common(control,s) for s in fixed.values())
    rows.append(dict(part=r['part'],swept_envelope_overlap_mm3=pairs,continuous_axial_clear=all(v<=1e-8 for v in pairs.values()),
        transverse_negative_control_overlap_mm3=control_overlap,negative_control_rejected=control_overlap>1e-8))
passed=all(r['continuous_axial_clear'] and r['negative_control_rejected'] for r in rows) and len(rows)==3
out=ROOT/'validation/finger/AK_root_retention_verify1';out.mkdir(parents=True,exist_ok=False)
dump(out/'summary.json',dict(status='CONTINUOUS_LOCAL_ESCAPE_VERIFIED' if passed else 'ENVELOPE_CHECK_FAIL',rows=rows,source=ref(p),producer=ref(__import__('pathlib').Path(__file__)),
    scope='Conservative solid AABB enclosing every root-fragment translation in [-0.5,+0.5]mm; only listed root clamps/fasteners',
    whole_system_release=False,limitations=['No full-Finger escape claim','No friction/preload/elastic or strength solution','No release or global energy certification']))
print(json.dumps(dict(passed=passed,rows=rows)));raise SystemExit(0 if passed else 2)
