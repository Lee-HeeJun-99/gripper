"""Registered supported parallel winches on actual three-Finger/free100g native scene."""
import argparse,copy,csv,json,re,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
from native_bending_coupon import guarded
from finite_hardware_grasp_pilot import flat
from winch_transfer_assess import unique_row,read

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--full',action='store_true');p.add_argument('--prefix');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());src=BASE/'results/yoke_hold_diagnostic1741';template=BASE/'results/registered_winch_full1892';bank=BASE/'results/parallel_bank1893';assert json.loads((template/'summary.json').read_text())['status']=='PASS_REGISTERED_LEVER_FULL_SINGLE_CLOSING_ONLY';assert json.loads((bank/'summary.json').read_text())['status']=='PASS_COMMON_AXIS_BANK_NECESSARY_GEOMETRY_ONLY'
 if a.full:
  assert a.prefix;prior=json.loads((BASE/'results'/a.prefix/'summary.json').read_text());assert prior['status']=='VALID_UNBRACED_OBJECT_CONTACT_PREFIX_ONLY';assert prior['process']['runtime_s']*2/.6*1.3<420,'Full-run cost forecast exceeds limit'
 root=ET.parse(src/'scene.scn').getroot();proto=ET.parse(template/'scene.scn').getroot();dt=float(root.get('dt'));assert dt==float(proto.get('dt'));root.insert(0,ET.Element('RequiredPlugin',pluginName='Sofa.Component.Mapping.Linear'));probe=BASE/'cad/build_cable_phase1831/libReGripCablePhase.so';assert sha(probe)=='9140d6a0be5283118412fa86df18a88a06dcba875602f3c9cba783b50f8cde96';root.insert(0,ET.Element('RequiredPlugin',pluginName=str(probe)))
 for i in range(3):
  finger=root.find(f"Node[@name='finger{i}']");finger.remove(finger.find('NativeCableSequence'));ET.SubElement(finger,'NativePointJournal',body='@dofs',filename=str(out/f'skin{i}.csv'))
  for j in range(2):
   old=root.find(f"Node[@name='guides{i}']/Node[@name='cable{j}']");act=old.find('CableConstraint');origin=np.fromstring(act.get('pullPoint'),sep=' ');old.remove(act);side=0 if origin[1]>0 else 1;drive=copy.deepcopy(proto.find(f"Node[@name='winch{side}']"));name=f'drive_{i}_{j}';drive.set('name',name);oldorigin=np.fromstring(drive.find("Node[@name='ports']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)[1];shift=origin-oldorigin
   for e in drive.iter():
    if e.tag in ('MechanicalObject','MeshTopology') and e.get('position'):
     width=7 if e.get('template')=='Rigid3d' else 3;q=np.fromstring(e.get('position'),sep=' ').reshape(-1,width);q[:,:3]+=shift;e.set('position',flat(q))
    if e.tag=='CableConstraint':e.set('pullPoint',flat(np.fromstring(e.get('pullPoint'),sep=' ')+shift))
    if e.tag in ('TriangleCollisionModel','LineCollisionModel','PointCollisionModel'):e.set('group',str(20+2*i+j))
    if e.get('filename'):e.set('filename',str(out/(name+'_'+Path(e.get('filename')).name.split('_',1)[-1])))
   root.append(drive);controller=copy.deepcopy(next(c for c in proto.findall('NativeCableSequence') if c.get('body')==f'@winch{side}/ports/points'))
   for key in ('body','cable0','cable1'):controller.set(key,controller.get(key).replace(f'@winch{side}/',f'@{name}/'))
   controller.set('hold','2.5');controller.set('release','3.0');controller.set('filename',str(out/f'{name}_commands.csv'));root.append(controller);route=np.fromstring(old.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);tendon=ET.SubElement(root,'Node',name=f'tendon_{i}_{j}');ET.SubElement(tendon,'MechanicalObject',template='Vec3d',name='points',position=flat(np.vstack([origin,route])));ET.SubElement(tendon,'SubsetMultiMapping',template='Vec3d,Vec3d',input=f'@../{name}/ports/points @../guides{i}/cable{j}/points',output='@points',indexPairs='0 1 '+' '.join(f'1 {k}' for k in range(len(route))),mapMatrices='1');ET.SubElement(tendon,'CableConstraint',template='Vec3d',name='output',indices=' '.join(map(str,range(len(route)+1))),hasPullPoint='0',valueType='displacement',value='0',minForce='0');ET.SubElement(root,'NativeCablePhase',body=f'@{name}/ports/points',solver='@constraints',cable=f'@{name}/ports/input',filename=str(out/f'{name}_phases.csv'))
 for e in root.iter():
  for k,v in list(e.attrib.items()):e.set(k,v.replace(str(src),str(out)))
 for name in ('config.json','mesh.json','holding_protocol.json'):(out/name).write_bytes((src/name).read_bytes())
 duration=2. if a.full else .6;steps=round(duration/dt);ET.ElementTree(root).write(out/'scene.scn');pre=dict(source_sha256=sha(Path(__file__)),source_scene_sha256=sha(src/'scene.scn'),scene_sha256=sha(out/'scene.scn'),template_scene_sha256=sha(template/'scene.scn'),bank_preflight_sha256=sha(bank/'summary.json'),duration_s=duration,steps=steps,dt_s=dt,object_mass_kg=.1,gravity_m_s2=np.fromstring(root.get('gravity'),sep=' ').tolist(),holding_protocol_sha256=sha(out/'holding_protocol.json'),actuation='Six actual1.5N capped Native displacement inputs with derived registered-lever stroke, closing.5s held through2s; six internal C2tendons. Compared to1741force input: new geometry/mass/route/mode/timing, not one-variable dominance claim.',scope='Original free100gR30sphere,3Skin/Rail/Guide/Support and collisions all retained. Added all6finite registered levers/collisions and physical aggregate mass. Parallel global axes, ideal supported bearing/shaft bond/terminated-wire anchors. No actual bearing/friction/finite-wire sliding/material/hardware qualification, no q/v state write or SDK change.',binary_sha256={e.get('pluginName'):sha(Path(e.get('pluginName'))) for e in root.iter('RequiredPlugin') if e.get('pluginName','').startswith('/')});(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(steps),'--hideProgressBar',out/'scene.scn'],out/'process',420);logs=''.join((out/'process'/n).read_text(errors='replace') for n in ('stdout.log','stderr.log'));valid=process['exit_code']==0 and '[ERROR]'not in logs;metrics={}
 if valid:
  tet=np.array(json.loads((src/'mesh.json').read_text())['tetrahedra']);det=lambda q:np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));qualities=[]
  for i in range(3):
   rows=read(out/f'skin{i}.csv');assert len(rows)==steps;q0=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);d0=det(q0);qualities.append(min(float((det(np.fromstring(r['q'],sep=' ').reshape(-1,3))/d0).min()) for r in rows))
  objects=read(out/'object.csv');assert len(objects)==steps;q=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in objects]);v=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in objects]);forces=[];cableforces=[]
  for i in range(3):
   for j in range(2):
    rows=[r for r in read(out/f'drive_{i}_{j}_phases.csv') if r['phase']=='accepted_end'];assert len(rows)==steps;actual=[];output=[]
    for r in rows:
     lam=np.fromstring(r['lambda_Ns'],sep=' ');actual.append(float(lam[unique_row(r['J'],0)]/dt));output.append(float(lam[unique_row(r['J'],1)]/dt))
    forces.extend(actual);cableforces.append(dict(finger=i,tendon=j,maximum_input_N=max(actual),maximum_output_N=max(output)))
  groups={k:np.zeros((steps,6)) for k in ('skin','rail','guide','support','winch','unknown')};time_index={float(r['time_s']):k for k,r in enumerate(objects)};pairs={};skin_fingers=set();internal=0;rootcontact=0
  for r in __import__('csv').DictReader((out/'response_rows.csv').open()):
   model=[r['model0'],r['model1']];lam=float(r['lambda_Ns']);index=time_index[float(r['time_s'])];imp=np.fromstring(r['object_impulse_Ns_Nms'],sep=' ')
   if any(n.startswith('/object/') for n in model):
    other=next(n for n in model if not n.startswith('/object/'));group='skin' if '/skinCollision/'in other else 'rail' if '/railCollision/'in other else 'guide' if other.startswith('/guides') else 'support' if other.startswith('/floor/') else 'winch' if other.startswith('/drive_') else 'unknown';groups[group][index]+=imp
    if group=='skin' and lam!=0:skin_fingers.add(int(re.search(r'/finger(\d+)',other)[1]))
   if lam!=0:
    key=tuple(model);pairs[key]=pairs.get(key,0)+1
    if all(n.startswith('/guides') for n in model):internal+=1
    if any(n.startswith('/drive_') for n in model):rootcontact+=1
  total=np.array([np.fromstring(r['object_impulse_Ns_Nms'],sep=' ') for r in objects]);part_error=float(abs(total-sum(groups.values())).max());metrics=dict(minimum_saved_volume_ratios=qualities,actual_skin_contact_fingers=sorted(skin_fingers),nonzero_guide_guide_rows=internal,nonzero_new_root_contact_rows=rootcontact,contact_pairs=[dict(pair=list(k),nonzero_rows=v) for k,v in pairs.items()],actual_tendon_forces=cableforces,object_final_position_m=q[-1,:3].tolist(),object_final_speed_mm_s=float(np.linalg.norm(v[-1,:3])*1000),object_partition_error_Ns=part_error,mean_object_force_groups_N={k:(f[:,:3]/dt).mean(0).tolist() for k,f in groups.items()});valid=min(qualities)>0 and max(forces)<=1.5+1e-12 and min(forces)>=-1e-12 and part_error<=1e-12
  if not a.full:valid=valid and internal==0 and rootcontact==0 and skin_fingers=={0,1,2}
 d=dict(status=('RUN_COMPLETED_NOT_QUALIFIED' if a.full else 'VALID_UNBRACED_OBJECT_CONTACT_PREFIX_ONLY') if valid else 'FAIL_PARALLEL_WINCH_PREFIX_OR_EXECUTION',process=process,metrics=metrics,dt_s=dt,gravity_m_s2=pre['gravity_m_s2'],holding_protocol_sha256=pre['holding_protocol_sha256'],source_sha256=sha(Path(__file__)),scope=pre['scope']+' No grasp verdict until original Holding window/force/source assessment; prefix may not be expanded if internal bracing is present.');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d,indent=2))
if __name__=='__main__':main()
