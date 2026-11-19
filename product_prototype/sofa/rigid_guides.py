"""Stock RigidMapping + BilateralLagrangianConstraint guide brackets.
This is a NEW explicit hardware model,not a correction to the old massless model.
"""
import numpy as np
from generate import world,width
def flat(v):return ' '.join(format(float(x),'.17g') for row in v for x in row)
def install(root,finger,c,mesh,angle,index,add,out,mapped=False):
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
 add(guides,'EulerImplicitSolver');add(guides,'SparseLDLSolver',name='linear');add(guides,'MechanicalObject',name='frames',template='Rigid3d',position=flat(frames));add(guides,'UniformMass',template='Rigid3d',vertexMass='.00001 1e-8 1e-6 0 0 0 1e-6 0 0 0 1e-6');add(guides,'GenericConstraintCorrection')
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
  add(cable,'SphereCollisionModel',radius=c['tendon']['guide_outer_radius']*.001,group=index+1)
  finger.find('NativeCableSequence').set('cable'+str(j),f'@../guides{index}/cable{j}/actuator')
 add(guides,'NativeRigidJournal',body='@frames',solver='@../constraints',filename=str(out/f'guide_frames{index}.csv'))
 return dict(type='native rigid brackets with3 noncollinear rail points each',frames=len(frames),attachment_nodes=anchor_nodes,mass_per_bracket_kg=.00001,normalized_inertia_m2=[1e-6]*3,collision='bounding spheres of actual guide outer radius;wire swept collision NOT implemented',mass_and_inertia='research assumptions,not measured',joint='native SubsetMultiMapping rigidification' if mapped else 'bilateral rigid attachment replaces local rail deformation;different physical design')
