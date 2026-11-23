"""Changed eyelets on saved Native transforms: frozen-motion screening,NOT new dynamics."""
import argparse,csv,json,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,sha
sys.path.insert(0,str(BASE/'sofa'))
from analyse import rotation
from wire_bore_audit import radial_extent

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--candidate',required=True);args=p.parse_args();out=BASE/'results'/args.tag;out.mkdir(exist_ok=False);source=BASE/'meshes'/args.candidate/'assembly_recipe.json';a=json.loads(source.read_text());cfg=a['baseline_config'];old=BASE/'results/b3_alarm_window485';baseline=BASE/a['manufacturing_config']['baseline_geometry']
 if sha(old/'config.json')!=sha(baseline):raise ValueError('saved motion does not match original manufacturing reference')
 motion=old/'motion_commands.json'
 if any(c['node']!='floor' for c in json.loads(motion.read_text())['commands']):raise ValueError('moving fixture requires actual pullpoint state,not fixed XML')
 scene=old/'scene.scn';tree=ET.parse(scene);records=[];inputs={str(p.relative_to(BASE.parent)):sha(p) for p in (source,scene,old/'config.json',motion)};td=cfg['tendon']
 for f in range(3):
  node=tree.find(f"./Node[@name='guides{f}']");rest=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);file=old/f'guide_frames{f}.csv';rows=list(csv.DictReader(file.open()));inputs[str(file.relative_to(BASE.parent))]=sha(file);times=np.array([float(r['time_s']) for r in rows]);q=np.array([np.fromstring(r['rigid_q'],sep=' ').reshape(-1,7) for r in rows]);cables=list(node.iter('CableConstraint'))
  for c in range(2):
   centres=[];axes=[]
   for k in range(6):
    g=np.asarray(next(p['shape']['matrix'] for p in a['parts'] if p['name']==f'f{f}_c{c}_s{k}_eyelet'));i=c*6+k;restrot=rotation(rest[i,3:]);localcenter=(g[:3,3]*.001-rest[i,:3])@restrot;localaxis=restrot.T@g[:3,0];rots=np.array([rotation(row[i,3:]) for row in q]);centres.append(q[:,i,:3]+np.einsum('nij,j->ni',rots,localcenter));axes.append(np.einsum('nij,j->ni',rots,localaxis))
   pull=np.fromstring(cables[c].get('pullPoint'),sep=' ');points=np.stack([np.tile(pull,(len(times),1)),*centres],axis=1);segments=np.diff(points,axis=1);segments/=np.linalg.norm(segments,axis=2)[:,:,None]
   for k in range(6):
    required=np.array([max(radial_extent(axes[k][j],b,1.,td['wire_radius']) for b in ([segments[j,k]]+([segments[j,k+1]] if k<5 else []))) for j in range(len(times))]);worst=int(required.argmax());bad=required>td['guide_hole_radius'];hold=(times>=1.6)&(times<=2.)
    records.append(dict(finger=f,cable=c,station_mm=td['guide_stations'][k],saved_frames=len(times),failed_frames=int(bad.sum()),failed_hold_frames=int(bad[hold].sum()),maximum_required_bore_radius_mm=float(required[worst]),worst_time_s=float(times[worst]),bore_radius_mm=td['guide_hole_radius']))
 result=dict(status='FROZEN_NATIVE_MOTION_BORE_SCREEN_NOT_CANDIDATE_DYNAMICS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=sha(__file__),inputs=inputs,records=records,scope='V21 finite eyelet centers and axes attached through actual saved Rigid3 body transforms,including reference offsets. Old body frame is NOT eyelet center. Fixed pullpoint verified only for this historical scene. Straight-branch necessary condition;not rounded/friction/dynamic certification. Changed mass/contact can change motion.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(sites_with_failed_frames=sum(r['failed_frames']>0 for r in records),sites_with_hold_failures=sum(r['failed_hold_frames']>0 for r in records),maximum_required_bore_radius_mm=max(r['maximum_required_bore_radius_mm'] for r in records)),indent=2))
if __name__=='__main__':main()
