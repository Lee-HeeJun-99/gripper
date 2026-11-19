"""Stock RigidMapping + BilateralLagrangianConstraint guide brackets.
This is a NEW explicit hardware model,not a correction to the old massless model.
"""
import numpy as np
from generate import world,width
def flat(v):return ' '.join(format(float(x),'.17g') for row in v for x in row)
def install(root,finger,c,mesh,angle,index,add,out,mapped=False,bridges=False,uniform_ribs=False):
 add(root,'RequiredPlugin',pluginName='Sofa.Component.Constraint.Lagrangian.Model') if index==0 else None
 guides=add(root,'Node',name=f'guides{index}');root.remove(guides);root.insert(list(root).index(finger),guides);local=np.array(mesh['local_positions_mm']);frames=[];anchor_nodes=[];anchor_world=[];anchor_indices=[];cable_indices=[[],[]]
 for j,side in enumerate((-1,1)):
  for station in c['tendon']['guide_stations']:
   xa=round(station/5)*5;xa=min(95,xa);positions=[]
   xc=xa-5 if mapped and station==90 else xa+5
   for x,y in ((xa,side*width(c,xa)/2),(xa,side*(width(c,xa)/2-2)),(xc,side*width(c,xc)/2)):
    matches=np.flatnonzero(np.max(abs(local-np.array([x,y,0])),axis=1)<1e-10)
    if len(matches)!=1:raise ValueError('explicit rail attachment vertex required')
    anchor_nodes.append(int(matches[0]));positions.append(np.array(world(c,[x,y,0],angle))*.001)
   centre=np.mean(positions,axis=0);frame=len(frames);frames.append([*centre,0,0,0,1]);anchor_world.extend(positions);anchor_indices.extend([frame]*3);cable_indices[j].append(frame)
 mass=.00001;tensors=[];merge_error=None
 if bridges:
  n=len(c['tendon']['guide_stations']);old=np.array(frames);combined=[];before=np.zeros((3,3));after=np.zeros((3,3));eye=np.eye(3)
  for k in range(n):
   left,right=old[k,:3],old[k+n,:3];centre=(left+right)/2;d=(left-right)/2;I=1e-6*eye+np.dot(d,d)*eye-np.outer(d,d);tensors.append(I.tolist());combined.append([*centre,0,0,0,1])
   for p in (left,right):before+=mass*(1e-6*eye+np.dot(p,p)*eye-np.outer(p,p))
   after+=2*mass*(I+np.dot(centre,centre)*eye-np.outer(centre,centre))
  frames=combined;anchor_indices=[k%n for k in anchor_indices];cable_indices=[[k%n for k in group] for group in cable_indices];mass*=2;merge_error=float(np.max(abs(before-after)))
 add(guides,'EulerImplicitSolver');add(guides,'SparseLDLSolver',name='linear');add(guides,'MechanicalObject',name='frames',template='Rigid3d',position=flat(frames))
 if uniform_ribs:
  # New physical rib candidate,NOT an equivalent-mass fix to legacy DiagonalMass.
  origin=np.array(world(c,[0,0,0],angle));basis=np.column_stack([np.array(world(c,p,angle))-origin for p in ([1,0,0],[0,1,0],[0,0,1])]);principal=np.array([24**2+.5**2,3**2+.5**2,24**2+3**2])/12*1e-6;I=basis@np.diag(principal)@basis.T;tensors=[I.tolist() for _ in frames];merge_error=None
  add(guides,'UniformMass',template='Rigid3d',vertexMass=' '.join(format(x,'.17g') for x in [mass,36e-9,*I.reshape(-1)]));c['uniform_rib_design']=dict(dimensions_mm=[3,24,.5],mass_per_rib_kg=mass,scope='assumed lightweight rigid cross-rib replacing independent brackets;new inertia and transverse constraint,NOT measured or equal-inertia contrast;rib/support collision not yet modeled')
 elif bridges:
  add(guides,'MeshTopology',name='massTopology',position=flat(np.array(frames)[:,:3]));add(guides,'DiagonalMass',template='Rigid3d,Rigid3d',geometryState='@frames',topology='@massTopology',vertexMass=' '.join(format(x,'.17g') for I in tensors for x in [mass,2e-8,*np.array(I).reshape(-1)]))
 else:add(guides,'UniformMass',template='Rigid3d',vertexMass='.00001 1e-8 1e-6 0 0 0 1e-6 0 0 0 1e-6')
 add(guides,'GenericConstraintCorrection')
 anchors=add(guides,'Node',name='anchors');add(anchors,'MechanicalObject',name='points',template='Vec3d',position=flat(anchor_world));add(anchors,'RigidMapping',input='@../frames',output='@points',globalToLocalCoords=1,rigidIndexPerPoint=' '.join(map(str,anchor_indices)))
 if mapped:
  if len(set(anchor_nodes))!=len(anchor_nodes):raise ValueError('rigidified subsets must be disjoint')
  all_world=np.array([world(c,x,angle) for x in local])*.001;selected={node:k for k,node in enumerate(anchor_nodes)};free_nodes=[k for k in range(len(local)) if k not in selected];free_index={node:k for k,node in enumerate(free_nodes)};free=add(root,'Node',name=f'free{index}');root.remove(free);root.insert(list(root).index(finger),free);add(free,'MechanicalObject',name='dofs',template='Vec3d',position=flat(all_world[free_nodes]));add(free,'FixedProjectiveConstraint',indices=' '.join(str(free_index[k]) for k in free_nodes if local[k,0]<=5));fixed=finger.find('FixedProjectiveConstraint')
  if fixed is not None:finger.remove(fixed)
  pairs=[v for k in range(len(local)) for v in ((1,selected[k]) if k in selected else (0,free_index[k]))];add(finger,'SubsetMultiMapping',template='Vec3d,Vec3d',input=f'@../free{index}/dofs @../guides{index}/anchors/points',output='@dofs',indexPairs=' '.join(map(str,pairs)),mapMatrices=1)
  anchors.find('RigidMapping').set('mapMatrices','1')
 else:add(root,'BilateralLagrangianConstraint',template='Vec3d',object1=f'@finger{index}/dofs',object2=f'@guides{index}/anchors/points',first_point=' '.join(map(str,anchor_nodes)),second_point=' '.join(map(str,range(len(anchor_nodes)))))
 for j in (0,1):
  cable=finger.find(f"./Node[@name='cable{j}']");finger.remove(cable);guides.append(cable);mapping=cable.find('BarycentricMapping');cable.remove(mapping);add(cable,'RigidMapping',input='@../frames',output='@points',globalToLocalCoords=1,rigidIndexPerPoint=' '.join(map(str,cable_indices[j])))
  add(cable,'SphereCollisionModel',radius=np.hypot(c['tendon']['guide_outer_radius'],1.)*.001,group=index+1)
  finger.find('NativeCableSequence').set('cable'+str(j),f'@../guides{index}/cable{j}/actuator')
 add(guides,'NativeRigidJournal',body='@frames',solver='@../constraints',auditMass=1,filename=str(out/f'guide_frames{index}.csv'))
 return dict(type='native rigid brackets with3 noncollinear rail points each',frames=len(frames),attachment_nodes=anchor_nodes,mass_per_bracket_kg=mass,normalized_inertia_m2=None if uniform_ribs else [1e-6]*3,normalized_inertia_tensors_m2=tensors or None,ideal_cross_bridge=bridges,mass_merge_inertia_error_kg_m2=merge_error,bridge_scope='uniform 24x3x0.5mm assumed rigid rib;new inertia;not matched legacy bridge' if uniform_ribs else 'ideal zero-added-mass connector;real rib mass/volume/compliance NOT validated' if bridges else None,collision='conservative enclosing sphere sqrt(OD_radius^2+half_length1mm^2);wire swept collision NOT implemented',mass_and_inertia='research assumptions,not measured',joint='native SubsetMultiMapping rigidification' if mapped else 'bilateral rigid attachment replaces local rail deformation;different physical design')
