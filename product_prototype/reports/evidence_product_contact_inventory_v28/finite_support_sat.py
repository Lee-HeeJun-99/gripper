"""Saved-state convex support/support SAT,NOT candidate dynamics/swept CCD."""
import argparse,csv,itertools,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha,rotation
sys.path.insert(0,str(BASE/'cad'))
from finite_guide_product import support
def sat(a,b,fa,fb,ea,eb):
    na=np.cross(a[fa[:,1]]-a[fa[:,0]],a[fa[:,2]]-a[fa[:,0]]);nb=np.cross(b[fb[:,1]]-b[fb[:,0]],b[fb[:,2]]-b[fb[:,0]]);da=a[ea[:,1]]-a[ea[:,0]];db=b[eb[:,1]]-b[eb[:,0]];da/=np.linalg.norm(da,axis=1)[:,None];db/=np.linalg.norm(db,axis=1)[:,None];cross=np.cross(da[:,None,:],db[None,:,:]).reshape(-1,3);cross=cross[np.linalg.norm(cross,axis=1)>64*np.finfo(float).eps];axes=np.concatenate((na,nb,cross));axes/=np.linalg.norm(axes,axis=1)[:,None];pa=a@axes.T;pb=b@axes.T;separation=np.maximum(pb.min(axis=0)-pa.max(axis=0),pa.min(axis=0)-pb.max(axis=0));best=float(separation.max());roundoff=128*np.finfo(float).eps*max(float(np.max(abs(a))),float(np.max(abs(b))),float(np.ptp(a,axis=0).max()),float(np.ptp(b,axis=0).max()))
    return best,('SEPARATED' if best>roundoff else 'STRICT_CONVEX_OVERLAP' if best<-roundoff else 'NUMERICALLY_UNCERTAIN')
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--target',choices=('support','eyelet-envelope'),default='support');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_alarm_window485';cfg=json.loads((src/'config.json').read_text());tree=ET.parse(src/'scene.scn');parts=[];envelopes=[];times=None;design=json.loads((BASE/'meshes/finite_eyelet_support_v11/geometry.json').read_text())
 # Independent exact reference boxes:translation2=separated;translation0.5=overlap.
 import trimesh
 cube=trimesh.creation.box();edges=cube.edges_unique;assert sat(cube.vertices,cube.vertices+[2,0,0],cube.faces,cube.faces,edges,edges)[1]=='SEPARATED';assert sat(cube.vertices,cube.vertices+[.5,0,0],cube.faces,cube.faces,edges,edges)[1]=='STRICT_CONVEX_OVERLAP'
 for f,angle in enumerate(cfg['palm']['angles_deg']):
  rr=list(csv.DictReader((src/f'guide_frames{f}.csv').open()));t=np.array([float(r['time_s']) for r in rr]);q=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in rr]);rest=np.fromstring(tree.find(f"./Node[@name='guides{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,7)
  if times is None:times=t
  else:assert np.array_equal(t,times)
  for cable,side in enumerate((-1,1)):
   for k,x in enumerate(cfg['tendon']['guide_stations']):
    idx=cable*6+k;mesh=support(cfg,x,side,angle);local=(mesh.vertices*.001-rest[idx,:3])@rotation(rest[idx,3:]);rot=np.array([rotation(v[idx,3:]) for v in q]);vertices=np.einsum('tij,vj->tvi',rot,local)+q[:,idx,None,:3];parts.append(dict(finger=f,cable=cable,station_mm=x,vertices=vertices,faces=mesh.faces,edges=mesh.edges_unique,lo=vertices.min(axis=1),hi=vertices.max(axis=1)))
    if a.target=='eyelet-envelope':
     guide=next(g for g in design['guides'] if g['finger']==f and g['cable']==cable and g['station_mm']==x);ro=cfg['tendon']['guide_outer_radius'];box=trimesh.creation.box(extents=[cfg['tendon'].get('guide_length_mm',2.),2*ro,2*ro]);reference=box.vertices@np.array(guide['basis']).T+guide['center_mm'];localbox=(reference*.001-rest[idx,:3])@rotation(rest[idx,3:]);mapped=np.einsum('tij,vj->tvi',rot,localbox)+q[:,idx,None,:3];envelopes.append(dict(finger=f,cable=cable,station_mm=x,vertices=mapped,faces=box.faces,edges=box.edges_unique,lo=mapped.min(axis=1),hi=mapped.max(axis=1)))
 records=[];broad=0;narrow=0;overlap=0;uncertain=0;worst=None
 pairs=itertools.combinations(parts,2) if a.target=='support' else itertools.product(parts,envelopes)
 for left,right in pairs:
  if a.target=='support' and left['finger']==right['finger']:continue
  if a.target!='support' and all(left[key]==right[key] for key in ('finger','cable','station_mm')):continue # intended own support/eyelet bond excluded explicitly
  broad+=len(times);mask=np.all(left['hi']>=right['lo'],axis=1)&np.all(right['hi']>=left['lo'],axis=1)
  for k in np.flatnonzero(mask):
   narrow+=1;distance,status=sat(left['vertices'][k],right['vertices'][k],left['faces'],right['faces'],left['edges'],right['edges']);r=dict(time_s=float(times[k]),left={key:left[key] for key in ('finger','cable','station_mm')},right={key:right[key] for key in ('finger','cable','station_mm')},maximum_separating_axis_gap_mm=distance*1000,status=status)
   if worst is None or distance*1000<worst['maximum_separating_axis_gap_mm']:worst=r
   if status!='SEPARATED':records.append(r)
   overlap+=status=='STRICT_CONVEX_OVERLAP';uncertain+=status=='NUMERICALLY_UNCERTAIN'
 result=dict(status='FAIL_FROZEN_SUPPORT_OVERLAP' if overlap else 'UNCERTAIN_FROZEN_SUPPORT_CLEARANCE' if uncertain else 'NO_SAVED_SUPPORT_SUPPORT_OVERLAP_FROZEN_REPLAY_ONLY',scope='Exact proposed convex support hulls under OLD Native485 sampled transforms. Native dynamics of supports NOT RUN. SAT overlap depth proxy is not Euclidean penetration depth;negative confirms intersecting convex hulls only at that saved pose. Eyelet/support,samefinger,wire/Palm,skin and swept intervals NOT certified.',source_sha256=sha(Path(__file__)),source_config_sha256=sha(src/'config.json'),broad_pair_frames=broad,narrow_pair_frames=narrow,strict_overlapping_pair_frames=overlap,numerically_uncertain_pair_frames=uncertain,worst=worst,records=records)
 result['target']=a.target
 if a.target=='eyelet-envelope':
  result['status']='POTENTIAL_FROZEN_SUPPORT_GUIDE_ENVELOPE_INTERFERENCE' if overlap or uncertain else 'NO_SAVED_SUPPORT_GUIDE_ENVELOPE_OVERLAP_FROZEN_REPLAY_ONLY'
  result['scope']='Proposed support hull vs finite oriented BOX enclosing actual eyelet. Includes samefinger/different-guide pairs;own intended bond excluded. Box overlap is NOT actual ring overlap;separation is sufficient for faceted/analytic eyelet clearance at OLD485 saved states. NOT new hardware dynamics,swept/contact/assembly certification.'
 (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
