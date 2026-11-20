"""Sufficient fixed-sector clearance certificate on OLD saved motion only.
Convex hulls and eyelet triangles are inside a sector iff every vertex is inside.
Negative sector margin is NOT proof that two solids intersect.
"""
import argparse,csv,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha,rotation
from finite_guide_coupon import eyelet
sys.path.insert(0,str(BASE/'cad'))
from finite_guide_product import support
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_alarm_window485';cfg=json.loads((src/'config.json').read_text());cad=BASE/'meshes/finite_eyelet_support_v11';design=json.loads((cad/'geometry.json').read_text());shape,_=eyelet(cfg,64);tree=ET.parse(src/'scene.scn');records=[];inputs={}
 for f,angle in enumerate(cfg['palm']['angles_deg']):
  file=src/f'guide_frames{f}.csv';rr=list(csv.DictReader(file.open()));time=np.array([float(r['time_s']) for r in rr]);q=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in rr]);rest=np.fromstring(tree.find(f"./Node[@name='guides{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7);inputs[str(file.relative_to(BASE.parent))]=sha(file);a0=np.radians(angle);radial=np.array([np.cos(a0),np.sin(a0)]);tangent=np.array([-np.sin(a0),np.cos(a0)])
  for cable,side in enumerate((-1,1)):
   for k,x in enumerate(cfg['tendon']['guide_stations']):
    idx=cable*6+k;rot=np.array([rotation(qi[idx,3:]) for qi in q]);guide=next(g for g in design['guides'] if g['finger']==f and g['cable']==cable and g['station_mm']==x);eye=shape.vertices@np.array(guide['basis']).T+guide['center_mm'];hull=support(cfg,x,side,angle)
    for label,vertices in [('eyelet',eye),('support',hull.vertices)]:
     local=(vertices*.001-rest[idx,:3])@rotation(rest[idx,3:]);mapped=np.einsum('tij,vj->tvi',rot,local)+q[:,idx,None,:3];r=mapped[:,:,:2]@radial;t=mapped[:,:,:2]@tangent;margin=((np.sqrt(3)*r-abs(t))/2).min(axis=1);ii=int(np.argmin(margin));hold=(time>=1.6)&(time<=2);records.append(dict(finger=f,cable=cable,station_mm=x,part=label,minimum_signed_sector_margin_mm=float(margin[ii]*1000),worst_time_s=float(time[ii]),negative_frames=int(np.count_nonzero(margin<0)),minimum_hold_margin_mm=float(margin[hold].min()*1000)))
 minimum=min(r['minimum_signed_sector_margin_mm'] for r in records);result=dict(status='FROZEN_MOTION_SAVED_SECTOR_CERTIFICATE' if minimum>0 else 'FROZEN_MOTION_SECTOR_CERTIFICATE_NOT_ESTABLISHED',scope='Proposed finite eyelets/supports on ACTUAL OLD485 rigid transforms. Positive all-vertex sector margin is sufficient to separate different-finger parts at SAVED times only;negative margin is not an actual intersection. No new hardware dynamics,swept clearance,within-finger joint clearance,wire/Palm/skin certification.',source_sha256=sha(Path(__file__)),source_CAD_sha256=sha(cad/'geometry.json'),inputs=inputs,minimum_margin_mm=minimum,minimum_hold_margin_mm=min(r['minimum_hold_margin_mm'] for r in records),conditional_different_finger_solid_gap_lower_bound_mm=2*minimum if minimum>0 else None,records=records)
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k not in ('records','inputs')},indent=2))
if __name__=='__main__':main()
