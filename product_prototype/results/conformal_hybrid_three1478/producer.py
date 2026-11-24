"""New manufactured conformal cradle,not prescribed dynamic wrapping.
Radius/placement derive from R30+.5mm initialinnerface allowance;route is
derived from finite-guide/object/sector clearances,not offset performance scan.
"""
import argparse,csv,json,math,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
from mechanism_candidates import world,width,guide_normal,guide_outboard,stl
from native_bending_coupon import guarded
def flat(a):return ' '.join(format(float(x),'.17g') for x in np.asarray(a).ravel())
def make(root,c,m,dorsal_terminal=False):
 centre=np.array(c['simulation']['sphere_center_mm']);assert np.array_equal(centre[:2],[0,0]);R=c['simulation']['sphere_radius_mm'];skin=c['finger']['skin_thickness'];Rc=R+.5+skin;start=c['finger']['precurve']['start_mm'];span=100-start;tilt=math.radians(c['palm']['root_angle_deg']);c['finger']['precurve']=dict(start_mm=start,angle_deg=math.degrees(span/Rc),reference='NEW manufactured stress-free circular cradle;not prescribed deformation');c['palm']['mount_radius']=start*math.sin(tilt)+Rc*math.cos(tilt);dz=float(centre[2]+start*math.cos(tilt)-Rc*math.sin(tilt));proxy=float(root.find("Node[@name='guides0']/Node[@name='cable0']/SphereCollisionModel").get('radius'))*1000;last=c['tendon']['guide_stations'][-1];theta=tilt+(last-start)/Rc;sector=2*(proxy+c['tendon']['sector_margin_mm']);desired=R+proxy+.5;A=1+3*math.cos(theta)**2;B=-2*math.sqrt(3)*math.cos(theta)*sector;C=sector**2-desired**2;d=(-B+math.sqrt(B*B-4*A*C))/(2*A);offset= min(c['tendon']['normal_offset'],Rc-d);assert offset>0
 if dorsal_terminal:offset=-c['finger']['rail_thickness']
 u=(last-90)/10;h=u*u*(3-2*u);tip=3+(offset-3)/h;c['tendon']['distal_profile']=dict(start_mm=90,tip_offset_mm=tip)
 def ref(p,angle):return np.array(world(c,p,angle))+[0,0,dz]
 local=np.array(m['local_positions_mm']);tet=np.array(m['tetrahedra']);records=[];groups=[];routes=[]
 for i,angle in enumerate((0,120,240)):
  f=root.find(f"Node[@name='finger{i}']");g=root.find(f"Node[@name='guides{i}']");old=np.fromstring(f.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);q=np.array([ref(p,angle) for p in local])*.001;pairs=np.fromstring(f.find('SubsetMultiMapping').get('indexPairs'),sep=' ',dtype=int).reshape(-1,2);free=np.empty(((pairs[:,0]==0).sum(),3));anchors=np.empty((36,3))
  for k,(owner,index) in enumerate(pairs):
   if owner==0:free[index]=q[k]
   else:anchors[index]=q[k]
  f.find('MechanicalObject').set('position',flat(q));f.find('MeshTopology').set('position',flat(q));root.find(f"Node[@name='free{i}']/MechanicalObject").set('position',flat(free));a=g.find("Node[@name='anchors']");a.find('MechanicalObject').set('position',flat(anchors));owners=np.fromstring(a.find('RigidMapping').get('rigidIndexPerPoint'),sep=' ',dtype=int);frames=np.fromstring(g.find('MechanicalObject').get('position'),sep=' ').reshape(-1,7);assert np.max(abs(frames[:,3:]-[0,0,0,1]))==0
  for k in range(len(frames)):frames[k,:3]=anchors[owners==k].mean(0)
  g.find('MechanicalObject').set('position',flat(frames))
  for name in ('skinCollision','railCollision'):
   n=f.find(f"Node[@name='{name}']");ids=np.fromstring(n.find('SubsetMapping').get('indices'),sep=' ',dtype=int);n.find('MechanicalObject').set('position',flat(q[ids]));n.find('MeshTopology').set('position',flat(q[ids]))
  wiregap=[];guidegap=[];points=[]
  for j,side in enumerate((-1,1)):
   n=g.find(f"Node[@name='cable{j}']");path=np.array([ref([x,side*(width(c,x)/2+guide_outboard(c,x)),guide_normal(c,x)],angle) for x in [0]+c['tendon']['guide_stations']]);n.find('MechanicalObject').set('position',flat(path[1:]*.001));n.find('CableConstraint').set('pullPoint',flat(path[0]*.001));points.extend(path[1:]);routes.append(path.tolist());delta=np.diff(path,axis=0);u=np.clip(np.sum((centre-path[:-1])*delta,axis=1)/np.sum(delta*delta,axis=1),0,1);wiregap.append(float(np.linalg.norm(path[:-1]+u[:,None]*delta-centre,axis=1).min()-R-.25));guidegap.append(float(np.linalg.norm(path[1:]-centre,axis=1).min()-R-proxy))
  groups.append(np.array(points));n=f.find("Node[@name='skinCollision']");ids=np.fromstring(n.find('SubsetMapping').get('indices'),sep=' ',dtype=int);faces=ids[np.fromstring(n.find('MeshTopology').get('triangles'),sep=' ',dtype=int).reshape(-1,3)];tri=q[faces]*1000;near=trimesh.triangles.closest_point(tri,np.repeat(centre[None],len(tri),axis=0));det=np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1));old_det=np.linalg.det((old[tet[:,1:]]-old[tet[:,0,None]]).transpose(0,2,1));records.append(dict(finger=i,initial_skin_gap_mm=float(np.linalg.norm(near-centre,axis=1).min()-R),initial_wire_gap_mm=min(wiregap),initial_guide_gap_mm=min(guidegap),minimum_reference_det_m3=float(det.min()),discrete_material_volume_ratio=float(det.sum()/old_det.sum())))
 gap=min(float(np.linalg.norm(groups[i][:,None]-groups[j][None,:],axis=2).min()-2*proxy) for i in range(3) for j in range(i));c['research_root_translation_z_mm']=dz;geometry=dict(innerface_radius_mm=Rc-skin,base_reference_radius_mm=Rc,reference_angle_deg=c['finger']['precurve']['angle_deg'],root_radius_mm=c['palm']['mount_radius'],root_translation_z_mm=dz,dorsal_terminal=dorsal_terminal,distal_last_guide_normal_offset_mm=offset,distal_profile_tip_offset_mm=tip,minimum_interfinger_guide_sphere_gap_mm=gap,records=records,routes_mm=routes,scope='New manufactured reference and necessary finite-route placement;not isolatedone-variable efficiency gain. Originalassigned masses/idealguideinertias retained,actualvolumechangesexplicit;not equaldensity/volume proof or CADhardwarequalification. No object relocation/forceddeformation. Initialpolyline stays in its eroded convex120deg sector via sharedguide_outboard;not dynamicwire/bore/wholehardware validation. Dorsal option after1472actualGuide-first collision puts98mm terminal on existingRailbackplane(-.5mm),retains hardwarecollision size and allDOFs;not collision disable or randomoffset sweep.')
 valid=gap>.2 and all(min(r['initial_skin_gap_mm'],r['initial_wire_gap_mm'],r['initial_guide_gap_mm'])>=c['simulation']['contact_distance_mm'] and r['minimum_reference_det_m3']>0 for r in records);return geometry,valid
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--native',action='store_true');p.add_argument('--single',action='store_true');p.add_argument('--dorsal-terminal',action='store_true');p.add_argument('--load-sized',action='store_true');p.add_argument('--duration',type=float,choices=[.25,.6,1.0,1.2,2.],default=.25);p.add_argument('--pilot');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_railback_grasp1001298';root=ET.parse(src/'scene.scn').getroot();c=json.loads((src/'config.json').read_text());m=json.loads((src/'mesh.json').read_text());force=json.loads((BASE/'results/grasp_load_budget1465/summary.json').read_text())['proposed_force_N_per_cable'] if a.load_sized else 1.5
 for control in root.iter('NativeCableSequence'):control.set('maximumForceN',format(force,'.17g'))
 geo,valid=make(root,c,m,a.dorsal_terminal);(out/'geometry.json').write_text(json.dumps(geo,indent=2));(out/'config.json').write_text(json.dumps(c,indent=2));(out/'mesh.json').write_bytes((src/'mesh.json').read_bytes());(out/'producer.py').write_bytes(Path(__file__).read_bytes());q=np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3)*1000;stl(out/'manufactured_reference_finger0.stl',q,m['triangles'])
 if not valid or not a.native:
  ET.ElementTree(root).write(out/'reference.scn');(out/'summary.json').write_text(json.dumps(dict(status='PASS_INITIAL_CONFORMAL_REFERENCE_ONLY' if valid else 'REJECT_CONFORMAL_REFERENCE',geometry=geo,Native='NOT RUN'),indent=2));print(json.dumps(dict(status=valid,geometry=geo)));return
 if a.single:
  for n in list(root):
   if n.tag=='Node' and n.get('name') not in ('finger0','guides0','free0','object'):root.remove(n)
  ET.SubElement(root.find("Node[@name='object']"),'FixedProjectiveConstraint',{'indices':'0'})
  # Journals remain but the fixed object's projected Jacobian is NOT totalreaction.
 for n in root.iter():
  for k,v in list(n.attrib.items()):n.set(k,v.replace(str(src),str(out)))
 ET.ElementTree(root).write(out/'scene.scn');protocol=json.loads((BASE/'results/nonuniform_hold1001438/holding_protocol.json').read_text());(out/'holding_protocol.json').write_text(json.dumps(protocol,indent=2));forecast=30.
 if a.duration>.25 or not a.single:
  assert a.pilot;pr=json.loads((BASE/'results'/a.pilot/'summary.json').read_text());pm=json.loads((BASE/'results'/a.pilot/'preflight.json').read_text());assert pr['status']=='VALID_BOUNDED_EXPLORATION_ONLY' and pm['geometry']==geo and pm['force_N_per_cable']==force;forecast=pr['process']['runtime_s']*a.duration/pr['duration_s']*(10 if pr.get('single') and not a.single else 2);assert forecast<420
 command=['/home/ubuntu/SOFA/v26.06.00/bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n',str(round(a.duration/.0025)),'--hideProgressBar',str(out/'scene.scn')];pre=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),scene_sha256=sha(out/'scene.scn'),source_scene_sha256=sha(src/'scene.scn'),geometry=geo,command=command,single_fixed_sphere=a.single,duration_s=a.duration,forecast_s=forecast,memory_GiB=4,child_limit_s=420,SDK='/home/ubuntu/SOFA/v26.06.00',force_N_per_cable=force,load_sized_hybrid=a.load_sized,load_budget_source_sha256=sha(BASE/'results/grasp_load_budget1465/summary.json') if a.load_sized else None,binary_hashes={n.get('pluginName'):sha(Path(n.get('pluginName'))) for n in root.iter('RequiredPlugin') if n.get('pluginName','').startswith('/')},fixed_sphere_reaction='NOT MEASURED when fixed:projectedobjectJacobian is not total reaction');(out/'preflight.json').write_text(json.dumps(pre,indent=2));process=guarded(command,out/'process',420);logs=''.join((out/'process'/f).read_text(errors='replace') for f in ('stdout.log','stderr.log'));quality=[];counts=[];first=None;tet=np.array(m['tetrahedra'])
 for i in range(1 if a.single else 3):
  rows=list(csv.DictReader((out/f'finger{i}.csv').open())) if (out/f'finger{i}.csv').exists() else [];counts.append(len(rows));q0=np.fromstring(root.find(f"Node[@name='finger{i}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);det0=np.linalg.det((q0[tet[:,1:]]-q0[tet[:,0,None]]).transpose(0,2,1));minimum=1.;finite=True
  for row in rows:
   q=np.fromstring(row['q_m'],sep=' ').reshape(-1,3);finite&=bool(np.isfinite(q).all());rat=np.linalg.det((q[tet[:,1:]]-q[tet[:,0,None]]).transpose(0,2,1))/det0;minimum=min(minimum,float(rat.min()))
   if rat.min()<=0 and first is None:first=dict(finger=i,time_s=float(row['time_s']),tet=int(np.argmin(rat)))
  quality.append(dict(minimum_saved_volume_ratio=minimum,finite=finite))
 ok=process['exit_code']==0 and '[ERROR]'not in logs and counts==[round(a.duration/.0025)]*len(counts) and all(r['finite'] and r['minimum_saved_volume_ratio']>0 for r in quality);d=dict(status='VALID_BOUNDED_EXPLORATION_ONLY' if ok else 'FAIL_EXECUTION_OR_INVERSION',duration_s=a.duration,single=a.single,process=process,outputs=counts,qualities=quality,first_inversion=first,holding='NOT ASSESSED',physical_validation='NOT QUALIFIED');(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
