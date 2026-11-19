"""Quantitative native-prototype audit;real saved states,not prescribed poses."""
import argparse,csv,json,math,hashlib,os
from pathlib import Path
import numpy as np
import xml.etree.ElementTree as ET
import trimesh
BASE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open()))
def cable_node(tree,f,j):
 node=tree.find(f"./Node[@name='finger{f}']/Node[@name='cable{j}']")
 return node if node is not None else tree.find(f"./Node[@name='guides{f}']/Node[@name='cable{j}']")
def rotation(q):
 x,y,z,w=q;return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
def analyse(case,out):
 src=BASE/'results'/case;m=json.loads((src/'summary.json').read_text());mesh=json.loads((src/'mesh.json').read_text());tree=ET.parse(src/'scene.scn');tets=np.array(mesh['tetrahedra']);tri=np.array(mesh['triangles']);s=json.loads((src/'config.json').read_text())['simulation'];result=dict(source_summary_sha256=sha(src/'summary.json'),source_binary_sha256=m.get('binary_sha256'),status='ANALYSED_NOT_GRASP_CERTIFIED',contact_area=None,pressure=None,root_reaction=None,initial_geometry_valid=None)
 sphere=read(src/'object.csv') if (src/'object.csv').exists() else None;obj=np.array([np.fromstring(r['rigid_q'],sep=' ') for r in sphere]) if sphere else None;vobj=np.array([np.fromstring(r['rigid_v'],sep=' ') for r in sphere]) if sphere else None
 control=tree.find('./Node/NativeCableSequence');closing_time=float(control.get('closing','.5'));hold_end=float(control.get('hold','1'))
 if sphere:
  impulses=np.array([np.fromstring(r.get('object_impulse_Ns_Nms',''),sep=' ') for r in sphere]);hold=[i for i,r in enumerate(sphere) if closing_time+.1*(hold_end-closing_time)<=float(r['time_s'])<=hold_end];result['object']=dict(final_translation_mm=(1000*(obj[-1,:3]-np.array(s['sphere_center_mm'])*.001)).tolist(),hold_translation_range_mm=(1000*np.ptp(obj[hold,:3],axis=0)).tolist() if hold else None,max_upward_displacement_mm=float(1000*(obj[:,2]-s['sphere_center_mm'][2]*.001).max()),max_solver_error=max(float(r.get('solver_error',0)) for r in sphere),max_solver_iterations=max(int(r.get('solver_iterations',0)) for r in sphere),holding='NOT QUALIFIED:pedestal/external load isolation incomplete',lift='NOT RUN:palm has not been lifted')
  if impulses.shape==(len(sphere),6) and m['object']=='free':
   mass=s['sphere_mass_kg'];dt=m['dt_s'];prev=np.vstack([np.zeros(3),vobj[:-1,:3]]);res=mass*(vobj[:,:3]-prev)-mass*np.array(m.get('gravity_m_s2',[0,0,0]))*dt-impulses[:,:3];result['object'].update(momentum_max_abs_Ns=float(np.abs(res).max()),peak_contact_resultant_N=float(np.linalg.norm(impulses[:,:3]/dt,axis=1).max()),contact_wrench_scope='all native object rows,includes pedestal when present;fixed-object projected rows are NOT reactions')
 sphere_collision=tree.find("./Node[@name='object']/Node[@name='collision']/SphereCollisionModel");R=float(sphere_collision.get('radius')) if sphere_collision is not None else None
 if obj is not None and R is not None:
  result['object']['hold_rise_mm']=[float(1000*(obj[hold,2]-s['sphere_center_mm'][2]*.001).min()),float(1000*(obj[hold,2]-s['sphere_center_mm'][2]*.001).max())] if hold else None
  if tree.find("./Node[@name='floor']/MeshTopology") is not None:
   floor_z=np.fromstring(tree.find("./Node[@name='floor']/MeshTopology").get('position'),sep=' ').reshape(-1,3)[0,2];result['object']['minimum_hold_floor_clearance_mm']=float(1000*(obj[hold,2]-R-floor_z).min())
 qAll=[];gAll=[];result['fingers']=[]
 for f in range(m['fingers']):
  rows=read(src/f'finger{f}.csv');q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);v=np.array([np.fromstring(r['v_m_s'],sep=' ').reshape(-1,3) for r in rows]);rest=np.fromstring(tree.find(f"./Node[@name='finger{f}']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);det0=np.linalg.det((rest[tets[:,1:]]-rest[tets[:,0],None,:]).transpose(0,2,1));dets=np.linalg.det((q[:,tets[:,1:]]-q[:,tets[:,0],None,:]).transpose(0,1,3,2));tip=np.flatnonzero(np.array(mesh['local_positions_mm'])[:,0]==100);displacement=np.linalg.norm(q[:,tip].mean(axis=1)-rest[tip].mean(axis=0),axis=1);forces=np.array([[float(r[k])/m['dt_s'] for k in ('cable0_force_raw','cable1_force_raw')] for r in rows]);item=dict(min_initial_tet_det_m3=float(det0.min()),min_volume_ratio=float((dets/det0).min()),max_tip_node_mean_displacement_mm=float(displacement.max()*1000),residual_tip_node_mean_displacement_mm=float(displacement[-1]*1000),peak_tendon_force_N=float(forces.max()),force_units='native CableModel.force is impulse;divide by actual dt (installed CableModel header)',first_command_m=float(rows[0]['command_m']))
  local=np.array(mesh['local_positions_mm']);top=np.flatnonzero((local[:,0]==100)&(local[:,2]==.1));order=np.argsort(local[top,1]);top=top[order];yy=local[top,1];weights=np.zeros(len(top));weights[:-1]+=np.diff(yy)/2;weights[1:]+=np.diff(yy)/2;weights/=weights.sum();skin_tip=np.sum(q[:,top]*weights[None,:,None],axis=1);skin_rest=np.sum(rest[top]*weights[:,None],axis=0);skin_motion=np.linalg.norm(skin_tip-skin_rest,axis=1)
  centres=np.stack([q[:,np.flatnonzero((local[:,0]==x)&(local[:,2]==.1))[1:3]].mean(axis=1) for x in np.unique(local[:,0])],axis=1);segments=np.diff(centres,axis=1);lengths=np.linalg.norm(segments,axis=2)
  if np.any(lengths<=0):raise ValueError('undefined collapsed centreline')
  tangent=segments/lengths[:,:,None];angle=np.arccos(np.clip(np.sum(tangent[:,:-1]*tangent[:,1:],axis=2),-1,1));curvature=angle/((lengths[:,:-1]+lengths[:,1:])/2)
  item.update(reference_width_mean_skin_tip_peak_mm=float(skin_motion.max()*1000),reference_width_mean_skin_tip_final_mm=float(skin_motion[-1]*1000),max_discrete_skin_centreline_curvature_per_mm=float(curvature.max()/1000))
  tracking=[]
  for j in (range(m.get('cables_per_finger',2)) if 'guide0_q_m' in rows[0] else ()):
   node=cable_node(tree,f,j);cable=node.find('CableConstraint');pull=np.fromstring(cable.get('pullPoint'),sep=' ');initial=np.fromstring(node.find('MechanicalObject').get('position'),sep=' ').reshape(-1,3);length0=np.linalg.norm(np.diff(np.vstack([pull,initial]),axis=0),axis=1).sum();stroke=[]
   for row in rows:
    origin=pull.copy();origin[2]+=float(control.get('liftHeight','0'))*np.clip((float(row['time_s'])-1)/.5,0,1);path=np.vstack([origin,np.fromstring(row[f'guide{j}_q_m'],sep=' ').reshape(-1,3)]);stroke.append(length0-np.linalg.norm(np.diff(path,axis=0),axis=1).sum())
   command=np.array([float(row['command_m']) for row in rows]);error=np.array(stroke)-command;k=min(range(len(rows)),key=lambda i:abs(float(rows[i]['time_s'])-hold_end));tracking.append(dict(cable=j,hold_time_s=float(rows[k]['time_s']),command_mm=float(command[k]*1000),actual_path_shortening_mm=float(stroke[k]*1000),hold_error_mm=float(error[k]*1000),maximum_absolute_error_mm=float(np.abs(error).max()*1000),scope='actual mapped path length;not pre-correction CableModel displacement'))
  item['cable_tracking']=tracking
  if 'guide0_q_m' in rows[0]:gAll.append(np.array([np.concatenate([np.fromstring(row[k],sep=' ').reshape(-1,3) for k in ('guide0_q_m','guide1_q_m')]) for row in rows]))
  if obj is not None and R is not None:
   gaps=[];angles=[]
   for i in range(len(rows)):
    closest=trimesh.triangles.closest_point(q[i,tri],np.repeat(obj[i,None,:3],len(tri),axis=0));delta=closest-obj[i,:3];g=np.linalg.norm(delta,axis=1)-R;gaps.append(float(g.min()))
    if i in (round(closing_time/m['dt_s'])-1,round(hold_end/m['dt_s'])-1):
     near=np.flatnonzero(g<=s['contact_distance_mm']*.001+1e-9);angles.append(dict(time_s=float(rows[i]['time_s']),near_surface_triangles=len(near),normal_z_range=[float((delta[near,2]/np.linalg.norm(delta[near],axis=1)).min()),float((delta[near,2]/np.linalg.norm(delta[near],axis=1)).max())] if len(near) else None,scope='geometric proximity ONLY;not pressure-bearing contact area/wrapping'))
   item.update(min_triangle_sphere_gap_mm=min(gaps)*1000,near_surface=angles)
   if 'guide0_q_m' in rows[0]:
    minimum=1e10
    for j in range(m.get('cables_per_finger',2)):
     pull=np.fromstring(cable_node(tree,f,j).find('CableConstraint').get('pullPoint'),sep=' ');lift_height=float(tree.find(f"./Node[@name='finger{f}']/NativeCableSequence").get('liftHeight','0'))
     for i,row in enumerate(rows):
      moved_pull=pull.copy();moved_pull[2]+=lift_height*np.clip((float(row['time_s'])-1)/.5,0,1);path=np.vstack([moved_pull,np.fromstring(row[f'guide{j}_q_m'],sep=' ').reshape(-1,3)]);a=path[:-1];d=np.diff(path,axis=0);u=np.clip(np.sum((obj[i,:3]-a)*d,axis=1)/np.sum(d*d,axis=1),0,1);minimum=min(minimum,float(np.linalg.norm(a+u[:,None]*d-obj[i,:3],axis=1).min()-R-.00025))
    item['minimum_sampled_finite_wire_sphere_gap_mm']=minimum*1000
  result['fingers'].append(item);qAll.append(q)
 result['initial_geometry_valid']=all(f['min_initial_tet_det_m3']>0 for f in result['fingers'])
 if (src/'support.csv').exists() and obj is not None:
  support=read(src/'support.csv');supportq=np.array([np.fromstring(row['q'],sep=' ') for row in support]);supporttime=np.array([float(row['time_s']) for row in support]);supportrest=np.fromstring(tree.find("./Node[@name='floor']/MechanicalObject").get('position'),sep=' ');expected=np.repeat(supportrest[None,:],len(support),axis=0);expected[:,2]-=.04*np.clip((supporttime-1)/.5,0,1);support_error=float(np.max(np.abs(supportq-expected)));result['support_withdrawal']=dict(status='FAIL' if obj[-1,2]<s['sphere_center_mm'][2]*.001-.005 else 'NOT QUALIFIED',object_final_drop_mm=float(1000*(s['sphere_center_mm'][2]*.001-obj[-1,2])),support_rows=len(support),support_position_error_m=support_error,support_api_status='PASS' if support_error<=1e-12 else 'FAIL',scope='independent support withdrawal;fixture work NOT MEASURED;not lift')
 if len(gAll)==3:
  minimum=min(float(np.linalg.norm(gAll[i][:,:,None,:]-gAll[j][:,None,:,:],axis=3).min()) for i,j in ((0,1),(1,2),(0,2)))
  result['guide_interfinger_bounding_ball_clearance_mm']=minimum*1000-2*math.sqrt(1.5**2+1**2)
  result['guide_clearance_scope']='only sampled mapped guides;bounding balls enclose radius1.5/length2;negative cannot alone prove solid overlap;skin/rail self-collision NOT qualified'
 if 'support_withdrawal' in result and float(sphere[-1]['time_s'])>hold_end+1e-12:
  result['support_withdrawal'].update(status='POST_UNLOAD_FINAL_POSITION_NOT_HOLD_VERDICT',note='final drop after commanded unloading is not a hold-window failure;use predeclared holding_assess and release_assess separately')
 if m.get('lift','').startswith('EXPERIMENTAL') and obj is not None:
  hold=np.array([i for i,row in enumerate(sphere) if 1.6<=float(row['time_s'])<=2]);rise=1000*(obj[hold,2]-s['sphere_center_mm'][2]*.001)
  result['object']['lift']='FAIL:object does not follow driven palm by >=5mm during1.6-2s' if rise.min()<5 else 'OBSERVED_EXPERIMENTAL_RISE_NOT_CERTIFIED'
  result['object']['minimum_lift_hold_rise_mm']=float(rise.min())
 if (src/'motion_commands.json').exists() and 'support_withdrawal' in result:
  commands=json.loads((src/'motion_commands.json').read_text());wanted=next(x for x in commands['commands'] if x['node']=='floor');knots=np.array(wanted['keyTimes_s']);values=np.array(wanted['movements_m']);expected=np.stack([np.interp(supporttime,knots,values[:,j])+supportrest[j] for j in range(3)],axis=1);error=float(np.max(abs(supportq-expected)));result['support_withdrawal'].update(support_position_error_m=error,support_api_status='PASS' if error<=1e-12 else 'FAIL',support_clock='declared end-clock motion_commands;not legacy linear-motion assumption')
 # Orthographic projection of ACTUAL saved positions,no deformation scaling.
 os.environ.setdefault('MPLCONFIGDIR','/tmp/regrip-matplotlib');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 from matplotlib.collections import PolyCollection
 fig,axes=plt.subplots(1,4,figsize=(14,4));P=np.array([[.70710678,-.70710678,0],[.40824829,.40824829,.81649658]])
 for ax,t in zip(axes,(closing_time/2,closing_time,hold_end,len(qAll[0])*m['dt_s'])):
  i=min(len(qAll[0])-1,max(0,round(t/m['dt_s'])-1))
  for f,q in enumerate(qAll):
   ax.add_collection(PolyCollection((q[i,tri]*1000)@P.T,facecolor=('teal','goldenrod','royalblue')[f],edgecolor='black',linewidth=.1,alpha=.45))
   if tree.find(f"./Node[@name='guides{f}']") is not None:
    offset=0
    for j in range(m.get('cables_per_finger',2)):
     cable=cable_node(tree,f,j);count=len(np.fromstring(cable.find('MechanicalObject').get('position'),sep=' '))//3;positions=gAll[f][i,offset:offset+count];offset+=count;pull=np.fromstring(cable.find('CableConstraint').get('pullPoint'),sep=' ');path=np.vstack([pull,positions])*1000;uv=path@P.T;ax.plot(uv[:,0],uv[:,1],color='saddlebrown',lw=.6)
     proxy=cable.find('SphereCollisionModel')
     if proxy is not None:
      for centre in positions*1000:ax.add_patch(plt.Circle(centre@P.T,1000*float(proxy.get('radius')),color='grey',alpha=.25))
  if obj is not None:
   if R is not None:ax.add_patch(plt.Circle((obj[i,:3]*1000)@P.T,R*1000,fill=False,color='crimson'))
   else:
    topology=tree.find("./Node[@name='object']/Node[@name='collision']/MeshTopology");vertices=np.fromstring(topology.get('position'),sep=' ').reshape(-1,3);faces=np.fromstring(topology.get('triangles'),sep=' ',dtype=int).reshape(-1,3);world=vertices@rotation(obj[i,3:7]).T+obj[i,:3];ax.add_collection(PolyCollection((world[faces]*1000)@P.T,facecolor='crimson',edgecolor='crimson',alpha=.15,linewidth=.3))
  ax.autoscale();ax.set_aspect('equal');ax.set_title(f'Actual SOFA t={(i+1)*m["dt_s"]:.3f}s');ax.set(xlabel='Projected mm',ylabel='Projected mm')
 fig.suptitle(case+' — actual native states,NO deformation scaling;grey=guide collision proxies');fig.tight_layout();fig.savefig(out/(case+'.png'));plt.close(fig)
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);r={c:analyse(c,out) for c in a.cases}
 # Same-binary NO-contact time refinement,all common output clocks,no floor.
 names=['native_single_010','native_single_half_011','native_single_quarter_012']
 if set(names).issubset(a.cases) and all((BASE/'results'/n/'summary.json').exists() for n in names):
  data=[read(BASE/'results'/n/'finger0.csv') for n in names];summary=[json.loads((BASE/'results'/n/'summary.json').read_text()) for n in names];errors=[]
  if len({s['binary_sha256'] for s in summary})!=1:raise ValueError('same binary time test required')
  tree=ET.parse(BASE/'results'/names[0]/'scene.scn');rest=np.fromstring(tree.find('./Node/MechanicalObject').get('position'),sep=' ')
  for i,j in ((0,1),(1,2),(0,2)):
   ratio=round(summary[i]['dt_s']/summary[j]['dt_s'])
   for k,row in enumerate(data[i]):
    other=data[j][(k+1)*ratio-1];clock=abs(float(row['time_s'])-float(other['time_s']))
    if clock>1e-10:raise ValueError('actual output clocks not aligned')
    for key in ('q_m','v_m_s','cable0_force_raw','cable1_force_raw'):
     x=np.fromstring(row[key],sep=' ');y=np.fromstring(other[key],sep=' ')
     if key=='q_m':x=x-rest;y=y-rest
     if 'force' in key:x=x/summary[i]['dt_s'];y=y/summary[j]['dt_s']
     absolute=float(np.linalg.norm(x-y));denom=max(float(np.linalg.norm(x)),float(np.linalg.norm(y)));relative=absolute/denom if denom else 0;errors.append(dict(pair=f'{i}_{j}',time_s=row['time_s'],clock_difference_s=clock,quantity=key,absolute=absolute,relative=relative,status='PASS' if relative<=.001 else 'FAIL'))
  with (out/'time_errors.csv').open('w') as s:w=csv.DictWriter(s,fieldnames=errors[0]);w.writeheader();w.writerows(errors)
  r['native_no_contact_time']=dict(status='FAIL' if any(e['status']=='FAIL' for e in errors) else 'PASS',scope='all common NO-contact state/motion/force outputs;not whole energy/contact',gate=.001,absolute_floor=None,worst=max(errors,key=lambda e:e['relative']))
 (out/'summary.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
if __name__=='__main__':main()
