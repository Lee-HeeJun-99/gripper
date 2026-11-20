"""Native finite-eyelet COM-frame equivalence, explicit 10mg research mass.
No support union or hardware calibration. No SDK/custom physics changes.
"""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
from analyse import BASE,sha,rotation
from finite_guide_coupon import eyelet
from finite_mass_reference import moments
from native_bending_coupon import flat,guarded
from observer_identity import compiled_pair_rows

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--free',action='store_true');p.add_argument('--inertia-frame',choices=('body','world-frozen'),default='body');p.add_argument('--mapped-mass',action='store_true');p.add_argument('--spin-mode',choices=('extracted','principal'),default='extracted');p.add_argument('--dt',type=float,choices=(.0025,.00125,.000625),default=.0025);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);steps=round(.01/a.dt)
 src=BASE/'results/b3_finite_mapped552';meta=json.loads((src/'summary.json').read_text());cfg=json.loads((src/'config.json').read_text());ring,_=eyelet(cfg,32);volume,com,I=moments(ring.vertices,ring.faces);mass=1e-5;records=[];initial=[]
 binary,frozen=compiled_pair_rows()
 physical=BASE/'cad/build_default_control332/libReGripProductSequence.so'
 if sha(physical)!=meta['physical_binary_sha256']:raise ValueError('physical binary mismatch')
 # Proper cyclic axis permutation: same COM/world solid/inertia, not a new mass model.
 bases=[np.eye(3),np.array([[0.,0.,1.],[1.,0.,0.],[0.,1.,0.]])]
 for variant,P in enumerate(bases):
  d=out/str(variant);d.mkdir();root=ET.parse(src/'5/scene.scn').getroot();root.set('dt',str(a.dt))
  for item in root.iter():
   if item.get('filename'):item.set('filename',str(d/Path(item.get('filename')).name))
  if a.free:
   # Both surfaces remain in the scene; skip contact pipeline only in this isolated free-spin reference.
   for tag in ('CollisionPipeline','BruteForceBroadPhase','BVHNarrowPhase','CollisionResponse','LocalMinDistance','NativeDetectionPairs','NativeResponseRows'):
    for item in list(root):
     if item.tag==tag:root.remove(item)
  for i,data in enumerate(meta['models']):
   parent=root.find(f"./Node[@name='guide{i}']");parent.remove(parent.find("Node[@name='supportCollision']"));col=parent.find("Node[@name='collision']");target=np.array(data['vertices_m']);c=target.mean(axis=0);U,_,Vt=np.linalg.svd((ring.vertices-com).T@(target-c));R=Vt.T@U.T
   if np.linalg.det(R)<0:raise ValueError('orientation fit failed')
   Rnew=R@P;qold=np.array(meta['initial_rigid_q'][i]);vold=np.array(meta['initial_rigid_v'][i]);v=np.r_[vold[:3]+np.cross(vold[3:],c-qold[:3]),vold[3:]];q=np.r_[c,Rotation.from_matrix(Rnew).as_quat()];In=P.T@I@P*1e-6;Iworld=R@I@R.T*1e-6
   if a.spin_mode=='principal':v[3:]=R[:,0]*np.linalg.norm(vold[3:])
   if a.inertia_frame=='world-frozen':In=Iworld
   parent.find('MechanicalObject').set('position',flat([q]));parent.find('MechanicalObject').set('velocity',flat([v]));parent.find('UniformMass').set('vertexMass',flat([[mass,volume*1e-9,*In.ravel()]]))
   if a.mapped_mass:
    # Six equal positive quadrature masses reproduce the same volume COM/covariance.
    # Native RigidMapping pulls their Cartesian mass to the parent, no custom mass solver.
    covariance=np.trace(I)/2*np.eye(3)-I;values,axes=np.linalg.eigh(covariance)
    if np.any(values<=0):raise ValueError('invalid geometric covariance')
    local=np.concatenate([axes.T*np.sqrt(3*values)[:,None],-axes.T*np.sqrt(3*values)[:,None]])*.001
    points=local@R.T+c;parent.remove(parent.find('UniformMass'));parent.find('NativeRigidJournal').set('auditMass','0');child=ET.SubElement(parent,'Node',name='massQuadrature');ET.SubElement(child,'MechanicalObject',name='points',template='Vec3d',position=flat(points));ET.SubElement(child,'UniformMass',template='Vec3d',totalMass=str(mass),compute_mapping_inertia='1');ET.SubElement(child,'RigidMapping',input='@../frames',output='@points',globalToLocalCoords='1',mapMasses='1',mapMatrices='1');ET.SubElement(child,'NativePointJournal',body='@points',filename=str(d/f'mass{i}.csv'))
   # globalToLocalCoords=1 reconstructs unchanged WORLD finite vertices in either COM frame.
   if variant==0:initial.append(dict(q=q.tolist(),v=v.tolist(),world_inertia_kg_m2=(mass*Iworld).tolist(),input_normalized_inertia_m2=In.tolist()))
  ET.ElementTree(root).write(d/'scene.scn');proc=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',d/'scene.scn'],d/'process',480)
  logs=''.join((d/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));records.append(dict(variant=variant,process=proc,scene_sha256=sha(d/'scene.scn'),errors=logs.count('[ERROR]')))
 metrics=[]
 if all(r['process']['exit_code']==0 and not r['errors'] for r in records):
  for i in (0,1):
   x=list(csv.DictReader((out/f'0/mapped{i}_eyelet.csv').open()));y=list(csv.DictReader((out/f'1/mapped{i}_eyelet.csv').open()));rx=list(csv.DictReader((out/f'0/guide{i}.csv').open()));ry=list(csv.DictReader((out/f'1/guide{i}.csv').open()))
   if len(x)!=steps or len(y)!=steps:raise ValueError('incomplete states')
   err={key:max(float(np.max(abs(np.fromstring(u[key],sep=' ')-np.fromstring(v[key],sep=' ')))) for u,v in zip(x,y)) for key in ('q','v')}
   err['impulse']=max(float(np.max(abs(np.fromstring(u['object_impulse_Ns_Nms'],sep=' ')-np.fromstring(v['object_impulse_Ns_Nms'],sep=' ')))) for u,v in zip(rx,ry));metrics.append(dict(body=i,errors=err))
 passed=len(metrics)==2 and max(v for r in metrics for v in r['errors'].values())<=1e-12
 result=dict(status='PASS_COM_BASIS_STRICT_API' if passed else 'FAIL_COM_BASIS_EQUIVALENCE',scope='Actual Native finite EYELETS ONLY;COM,anisotropic geometry inertia and 10mg assumed mass. Basis permutation represents identical intended physical state. world-frozen tests Native constant-world inertia convention ONLY,NOT orientation-updated physical rigid inertia. Not old lumped-model equivalence,physical hardware calibration,B3 or time convergence.',inertia_frame=a.inertia_frame,free_reference=a.free,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),physical_binary_sha256=sha(physical),row_binary_sha256=sha(binary),source_summary_sha256=sha(src/'summary.json'),SDK='/home/ubuntu/SOFA/v26.06.00',initial=initial,records=records,metrics=metrics,strict_gate=1e-12,dt_s=.0025,steps=4,assumed_mass_kg=mass,physical_density=None)
 result['mapped_mass']=a.mapped_mass
 result['spin_mode']=a.spin_mode
 result['dt_s']=a.dt;result['steps']=steps
 if a.mapped_mass:result['scope']='Native UniformMass Vec3 + RigidMapping positive six-point mass quadrature,matching geometric COM/inertia exactly. Frame-equivalence test ONLY;gyro,momentum,energy,event/time convergence still require independent verification. No custom physics,no physical density/join/B3 qualification.'
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
