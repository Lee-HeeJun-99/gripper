"""All-pair,all-common-time native model sensitivity;no relative-error floors."""
import argparse,csv,json,hashlib,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import rotation,cable_node
BASE=Path(__file__).resolve().parents[1]
def read(p):return list(csv.DictReader(p.open()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fingerprint(src):
 tree=ET.parse(src/'scene.scn');root=tree.getroot();root.set('dt','TIME_VARIABLE');commands=json.loads((src/'motion_commands.json').read_text())['commands']
 for node in root.iter():
  if 'filename' in node.attrib:node.set('filename','EXCLUSIVE_JOURNAL')
 for node in root.iter('Node'):
  for move in node.findall('LinearMovementProjectiveConstraint'):
   wanted=next(x for x in commands if x['node']==node.get('name'));move.set('keyTimes',' '.join(format(x,'.17g') for x in wanted['keyTimes_s']))
 return hashlib.sha256(ET.tostring(root)).hexdigest()
def features(src,m):
 if any(x.get('ideal_cross_bridge') for x in m['rigid_guides']):raise ValueError('anisotropic merged-guide kinetic evaluator NOT qualified;do not substitute isotropic1e-6')
 tree=ET.parse(src/'scene.scn');mesh=json.loads((src/'mesh.json').read_text());local=np.array(mesh['local_positions_mm']);c=json.loads((src/'config.json').read_text());F={};kinetic=None;t=None
 for f in range(m['fingers']):
  r=read(src/f'finger{f}.csv');t=np.array([float(x['time_s']) for x in r]);q=np.array([np.fromstring(x['q_m'],sep=' ').reshape(-1,3) for x in r]);v=np.array([np.fromstring(x['v_m_s'],sep=' ').reshape(-1,3) for x in r]);rest=np.fromstring(tree.find(f"./Node[@name='finger{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);F[f'finger{f}_motion_m']=(q-rest).reshape(len(r),-1);F[f'finger{f}_velocity_m_s']=v.reshape(len(r),-1);F[f'finger{f}_cable_force_N']=np.array([[float(x[k])/m['dt_s'] for k in ('cable0_force_raw','cable1_force_raw')] for x in r]);centres=np.stack([q[:,np.flatnonzero((local[:,0]==x)&(local[:,2]==.1))[1:3]].mean(axis=1) for x in np.unique(local[:,0])],axis=1);d=np.diff(centres,axis=1);L=np.linalg.norm(d,axis=2);u=d/L[:,:,None];F[f'finger{f}_curvature_per_m']=np.arccos(np.clip(np.sum(u[:,:-1]*u[:,1:],axis=2),-1,1))/((L[:,:-1]+L[:,1:])/2)
  for j in (0,1):
   cable=cable_node(tree,f,j);pull=np.fromstring(cable.find('CableConstraint').get('pullPoint'),sep=' ');restguide=np.fromstring(cable.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);L0=np.linalg.norm(np.diff(np.vstack([pull,restguide]),axis=0),axis=1).sum();F[f'finger{f}_cable{j}_shortening_m']=np.array([[L0-np.linalg.norm(np.diff(np.vstack([pull,np.fromstring(x[f'guide{j}_q_m'],sep=' ').reshape(-1,3)]),axis=0),axis=1).sum()] for x in r])
  k=.5*c['simulation']['mass_per_finger_kg']/q.shape[1]*np.sum(v*v,axis=(1,2));g=read(src/f'guide_frames{f}.csv');gv=np.array([np.fromstring(x['rigid_v'],sep=' ').reshape(-1,6) for x in g]);F[f'guide{f}_velocities']=gv.reshape(len(g),-1);k+=.5*m['rigid_guides'][f]['mass_per_bracket_kg']*(np.sum(gv[:,:,:3]**2,axis=(1,2))+1e-6*np.sum(gv[:,:,3:]**2,axis=(1,2)));kinetic=k if kinetic is None else kinetic+k
 obj=read(src/'object.csv');q=np.array([np.fromstring(x['rigid_q'],sep=' ') for x in obj]);v=np.array([np.fromstring(x['rigid_v'],sep=' ') for x in obj]);F['object_motion_m']=q[:,:3]-np.array(c['simulation']['sphere_center_mm'])*.001;F['object_velocity_m_s']=v[:,:3];F['object_angular_velocity_rad_s']=v[:,3:];F['object_rotation_matrix_motion']=np.array([rotation(x[3:])-np.eye(3) for x in q]).reshape(len(q),-1);F['object_contact_force_N']=np.array([np.fromstring(x['object_impulse_Ns_Nms'],sep=' ')[:3]/m['dt_s'] for x in obj]);mass=c['simulation']['sphere_mass_kg'];R=c['simulation']['sphere_radius_mm']*.001;kinetic+=.5*mass*(np.sum(v[:,:3]**2,axis=1)+.4*R*R*np.sum(v[:,3:]**2,axis=1));F['kinetic_inventory_J']=kinetic[:,None];return t,F
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=3,required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);sources=[BASE/'results'/x for x in a.cases];meta=[json.loads((s/'summary.json').read_text()) for s in sources]
 if any(m['status']!='RUN_COMPLETED_NOT_QUALIFIED' for m in meta):raise ValueError('partial process is NOT convergence evidence')
 fp=[fingerprint(s) for s in sources]
 if len(set(fp))!=1 or len({m['binary_sha256'] for m in meta})!=1 or len({m['motion_commands_sha256'] for m in meta})!=1:raise ValueError('same physics,binary and declared physical command required')
 data=[features(s,m) for s,m in zip(sources,meta)];records=[];limit=min(t[-1] for t,F in data)
 for i,j in ((0,1),(1,2),(0,2)):
  ti,Fi=data[i];tj,Fj=data[j];ratio=round(meta[i]['dt_s']/meta[j]['dt_s'])
  for k,time in enumerate(ti):
   if time>limit+1e-12:break
   l=(k+1)*ratio-1;clock=abs(time-tj[l])
   if clock>1e-12:raise ValueError('common physical clock API FAIL')
   for key,x in Fi.items():
    u=x[k];v=Fj[key][l];absolute=float(np.linalg.norm(u-v));denom=max(float(np.linalg.norm(u)),float(np.linalg.norm(v)));rel=absolute/denom if denom else 0.;records.append(dict(pair=f'{i}_{j}',time_s=float(time),quantity=key,absolute=absolute,relative=rel,clock_difference_s=clock,status='PASS' if rel<=.001 else 'FAIL'))
 with (out/'errors.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=records[0]);w.writeheader();w.writerows(records)
 result=dict(status='FAIL' if any(x['status']=='FAIL' for x in records) else 'PASS_TIME_SCOPE_ONLY',scope='0..common horizon actual native states/forces/curvature/kinetic inventory,NOT whole energy/mesh/friction/grasp certification',cases=a.cases,physics_fingerprint=fp[0],binary_sha256=meta[0]['binary_sha256'],motion_commands_sha256=meta[0]['motion_commands_sha256'],horizon_s=float(limit),gate=.001,absolute_floor=None,worst=max(records,key=lambda x:x['relative']),metrics={key:max((x for x in records if x['quantity']==key),key=lambda x:x['relative']) for key in data[0][1]},input_hashes={str(s/'summary.json'):sha(s/'summary.json') for s in sources},source_sha256=sha(Path(__file__)))
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='metrics'}))
if __name__=='__main__':main()
