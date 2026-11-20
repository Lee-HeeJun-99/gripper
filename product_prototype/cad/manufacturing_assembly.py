"""B3 manufacturing candidate with executable mesh CSG and neutral CAD recipe.

The B3 finger/route is shared unchanged. New fixtures/drivetrain are NOT simulated
or fabrication-qualified. Manifold is a mesh Boolean kernel,NOT STEP/BRep CAD.
Every output directory must be new. No old geometry is overwritten.
"""
import argparse
import csv
import copy
import hashlib
import importlib.util
import itertools
import json
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import trimesh

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'sofa'))
from generate import mesh, reference_local, world, width, guide_normal, guide_outboard
from finite_guide_product import support, guide_basis
from finite_guide_coupon import eyelet


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load_design(path,seen=None):
 path=Path(path).resolve();seen=set() if seen is None else seen
 if path in seen:raise ValueError('cyclic manufacturing configuration')
 seen.add(path);data=json.loads(path.read_text());parent=data.pop('extends',None)
 result=load_design(path.parent/parent,seen) if parent else {}
 def merge(target,update):
  for key,value in update.items():
   if isinstance(value,dict) and isinstance(target.get(key),dict):merge(target[key],value)
   else:target[key]=value
 merge(result,data);return result
def box(lo,hi):return dict(op='box',lo=list(lo),hi=list(hi))
def cyl(radius,z0,z1,xy=(0,0),sections=64):return dict(op='cylinder',radius=radius,z=[z0,z1],xy=list(xy),sections=sections)
def union(*items):return dict(op='union',items=list(items))
def cut(shape,*tools):return dict(op='difference',items=[shape,*tools])
def transform(shape,matrix):return dict(op='transform',matrix=np.asarray(matrix).tolist(),shape=shape)
def poly(shape):return dict(op='polyhedron',vertices=np.asarray(shape.vertices).tolist(),faces=np.asarray(shape.faces).tolist())
def standoff_positions(drive):
 return [(u,v) for u in drive['standoff_radial_mm'] for v in (drive.get('inner_standoff_tangential_mm',drive['standoff_tangential_mm']) if u==min(drive['standoff_radial_mm']) else drive['standoff_tangential_mm'])]
def sector(angle):
 a=math.radians(angle);m=np.eye(4);m[:2,:2]=[[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]];return m
def root_frame(cfg,angle):
 origin=np.asarray(world(cfg,[0,0,0],angle));m=np.eye(4);m[:3,3]=origin
 m[:3,:3]=np.column_stack([np.asarray(world(cfg,p,angle))-origin for p in ([1,0,0],[0,1,0],[0,0,1])])
 if not np.allclose(m[:3,:3].T@m[:3,:3],np.eye(3),atol=1e-12) or np.linalg.det(m[:3,:3])<0:raise ValueError('invalid root frame')
 return m


def evaluate(op):
 kind=op['op']
 if kind=='box':
  lo,hi=np.asarray(op['lo']),np.asarray(op['hi']);s=trimesh.creation.box(extents=hi-lo);s.apply_translation((lo+hi)/2)
 elif kind=='cylinder':
  z0,z1=op['z'];s=trimesh.creation.cylinder(radius=op['radius'],height=z1-z0,sections=op['sections']);s.apply_translation([*op['xy'],(z0+z1)/2])
 elif kind=='polyhedron':s=trimesh.Trimesh(op['vertices'],op['faces'],process=True)
 elif kind=='transform':s=evaluate(op['shape']);s.apply_transform(op['matrix'])
 elif kind in ('union','difference'):
  items=[evaluate(x) for x in op['items']]
  s=getattr(trimesh.boolean,kind)(items,engine='manifold',check_volume=True)
 else:raise ValueError('unknown CAD operation '+kind)
 if not s.is_watertight or not s.is_winding_consistent or s.volume<=0:raise ValueError('invalid closed solid '+kind)
 return s


def material_surfaces(cfg):
 verts,tets,_=mesh(cfg);v=np.asarray(verts);t=np.asarray(tets);q=np.asarray([reference_local(cfg,p) for p in v]);result={}
 masks={'skin':np.all(v[t,2]>=0,axis=1),'rail_left':np.all(v[t,2]<=0,axis=1)&(v[t,1].mean(axis=1)<0),'rail_right':np.all(v[t,2]<=0,axis=1)&(v[t,1].mean(axis=1)>0)}
 for name,mask in masks.items():
  faces={}
  for a,b,c,d in t[mask]:
   for f in ((b,c,d),(a,d,c),(a,b,d),(a,c,b)):faces.setdefault(tuple(sorted(f)),[]).append(f)
  s=trimesh.Trimesh(q,[f[0] for f in faces.values() if len(f)==1],process=True)
  if not s.is_volume:raise ValueError('invalid B3 material surface')
  result[name]=s
 return result


def recipe(cfg,design):
 parts=[];mates=[];c=design['cassette'];drive=design['drive'];mount=design['mount'];clear=c['pocket_clearance_mm'];holes=c['bolt_clearance_diameter_mm']/2;fast=design.get('fastener_proxies',{});fasteners=fast.get('enabled',False)
 def add(name,shape,group,finger=None,role='manufacturing_candidate',**meta):
  parts.append(dict(name=name,shape=shape,group=group,finger=finger,role=role,**meta))
 surfaces=material_surfaces(cfg);ring,_=eyelet(cfg,64)
 saddle=design.get('support_design',{}).get('rail_bondline_clearance_mm')
 keepouts=None
 if saddle is not None:
  if saddle<=0:raise ValueError('positive proposed bondline clearance required')
  expanded=copy.deepcopy(cfg);expanded['finger']['root_width']+=2*saddle;expanded['finger']['tip_width']+=2*saddle;expanded['finger']['rail_width']+=2*saddle;expanded['finger']['rail_thickness']+=saddle
  keepouts=material_surfaces(expanded)
 palm=cyl(cfg['palm']['outer_radius'],5,13);palm=cut(palm,cyl(cfg['palm']['inner_radius'],4,14))
 for finger,angle in enumerate(cfg['palm']['angles_deg']):
  R=root_frame(cfg,angle);S=sector(angle);f=cfg['finger'];w=c['width_mm']/2
  carrier=box([c['root_x_mm'][0],-w,-c['backing_mm']],[5,w,0])
  for side in (-1,1):
   y0=side*f['root_width']/2;y1=side*(f['root_width']/2-f['rail_width'])
   carrier=cut(carrier,box([-.1,min(y0,y1)-c['rail_groove_clearance_mm'],-f['rail_thickness']-c['rail_groove_clearance_mm']],[5.1,max(y0,y1)+c['rail_groove_clearance_mm'],.1]))
  for y in c['retaining_bolt_y_mm']:
   carrier=cut(carrier,cyl(holes,-5,1,(c['retaining_bolt_x_mm'],y)),cyl((c['nut_across_flats_mm']+2*c['nut_pocket_clearance_mm'])/math.sqrt(3),-c['nut_thickness_mm'],.1,(c['retaining_bolt_x_mm'],y),6))
  clamp=box([0,-w,f['skin_thickness']],[5,w,f['skin_thickness']+c['clamp_thickness_mm']])
  for y in (-14,14):
   tool=cyl(holes,-5,5,(2.5,y));carrier=cut(carrier,tool);clamp=cut(clamp,tool)
  # Pocket is longer than carrier for downward extraction;front5mm stays clamped.
  pocket=transform(box([-9,-w-clear,-c['backing_mm']-clear],[20,w+clear,f['skin_thickness']+c['clamp_thickness_mm']+clear]),R)
  palm=cut(palm,pocket)
  lo,hi=mount['radial_range_mm'];z0,z1=mount['z_range_mm'];adapter=transform(box([lo,-mount['tangential_width_mm']/2,z0],[hi,mount['tangential_width_mm']/2,z1]),S);adapter=cut(adapter,pocket)
  if fasteners:
   bosses=[transform(cyl(4,-12,-4,(c['retaining_bolt_x_mm'],y)),R) for y in c['retaining_bolt_y_mm']]
   adapter=cut(union(adapter,*bosses),pocket,box([-100,-100,5],[100,100,30]))
   for y in (-14,14):adapter=cut(adapter,transform(cyl(holes,-20,5,(2.5,y)),R),transform(cyl((c['nut_across_flats_mm']+.4)/math.sqrt(3),-6.6,-3.8,(2.5,y),6),R))
   if fast.get('clamp_head_access_radius_mm'):
    for y in (-14,14):adapter=cut(adapter,transform(cyl(fast['clamp_head_access_radius_mm'],3.0,20,(2.5,y)),R))
   if fast.get('retaining_head_spotface_radius_mm'):
    for y in (-14,14):adapter=cut(adapter,transform(cyl(fast['retaining_head_spotface_radius_mm'],-20,-12,(c['retaining_bolt_x_mm'],y)),R))
  for y in mount['seat_bolt_tangential_mm']:
   tool=transform(cyl(mount['seat_bolt_hole_mm']/2,-10,14,(mount['seat_bolt_radial_mm'],y)),S);adapter=cut(adapter,tool);palm=cut(palm,tool)
  for y in c['retaining_bolt_y_mm']:
   adapter=cut(adapter,transform(cyl(holes,-20,4,(c['retaining_bolt_x_mm'],y)),R))
  add(f'f{finger}_mount',adapter,'mount',finger)
  add(f'f{finger}_carrier',transform(carrier,R),'cartridge',finger)
  add(f'f{finger}_root_clamp',transform(clamp,R),'clamp',finger)
  for name,shape in surfaces.items():add(f'f{finger}_{name}',transform(poly(shape),R),'finger',finger,role='shared_B3_manufactured_reference')
  for cable,side in enumerate((-1,1)):
   for k,x in enumerate(cfg['tendon']['guide_stations']):
    p=[x,side*(width(cfg,x)/2+guide_outboard(cfg,x)),guide_normal(cfg,x)];G=np.eye(4);G[:3,:3]=guide_basis(cfg,np.asarray(p),angle);G[:3,3]=world(cfg,p,angle);join=f'f{finger}_c{cable}_s{k}'
    add(join+'_eyelet',transform(poly(ring),G),'eyelet',finger,join_id=join)
    bracket=poly(support(cfg,x,side,angle))
    if keepouts is not None:bracket=cut(bracket,transform(poly(keepouts['rail_left' if side<0 else 'rail_right']),R))
    add(join+'_support',bracket,'support',finger,join_id=join)
    mates.append(dict(parts=[join+'_eyelet',join+'_support'],type='intended_bond_overlap_NOT_strength_verified'))
  dr0,dr1=drive['deck_radial_range_mm'];dz0,dz1=drive['deck_z_range_mm'];deck=box([dr0,-drive['deck_width_mm']/2,dz0],[dr1,drive['deck_width_mm']/2,dz1])
  for u,v in standoff_positions(drive):
   deck=cut(deck,cyl(1.7,16,21,(u,v)));add(f'f{finger}_standoff_{u}_{v}',transform(cut(cyl(3,13,17,(u,v)),cyl(1.7,12,18,(u,v))),S),'standoff',finger)
   if drive.get('drill_standoff_palm_holes'):palm=cut(palm,transform(cyl(1.7,4,14,(u,v)),S))
  add(f'f{finger}_motor_deck',transform(deck,S),'drive_deck',finger)
  u=drive['motor_center_radius_mm'];a,b,h=drive['motor_envelope_mm'];z=drive['motor_base_z_mm']
  add(f'f{finger}_motor_ENVELOPE',transform(box([u-a/2,-b/2,z],[u+a/2,b/2,z+h]),S),'motor_envelope',finger,role='supplier_bbox_envelope_NOT_mount_or_output_axis_verified')
  z0,z1=drive['drum_z_range_mm'];r=drive['drum_effective_wire_radius_mm']-cfg['tendon']['wire_radius'];spool=union(cyl(r,z0,z1,(u,0)),cyl(drive['drum_flange_radius_mm'],z0,z0+1,(u,0)),cyl(drive['drum_flange_radius_mm'],z0+2.5,z0+3.5,(u,0)),cyl(drive['drum_flange_radius_mm'],z1-1,z1,(u,0)))
  spool=cut(spool,cyl(drive['drum_bore_mm']/2,z0-1,z1+1,(u,0)));add(f'f{finger}_two_channel_drum',transform(spool,S),'drum',finger,role='parameterized_generic_drum_NOT_motor_horn_fit_verified')
  if fasteners:
   def screw(label,xy,seat,length,matrix):
    shape=union(cyl(fast['nominal_shank_radius_mm'],seat-length,seat,xy),cyl(fast['head_radius_mm'],seat,seat+fast['head_height_mm'],xy));add(f'f{finger}_{label}',transform(shape,matrix),'fastener_proxy',finger,role='nominal_geometry_NOT_thread_or_supplier_verified')
   def nut(label,xy,z,matrix):
    shape=cut(cyl(fast['nut_across_flats_mm']/math.sqrt(3),z,z+fast['nut_thickness_mm'],xy,6),cyl(fast['unthreaded_proxy_bore_mm']/2,z-1,z+fast['nut_thickness_mm']+1,xy));add(f'f{finger}_{label}',transform(shape,matrix),'fastener_proxy',finger,role='hex_envelope_and_unthreaded_bore_NOT_threaded_CAD')
   for u,v in standoff_positions(drive):
    outer=u==mount['seat_bolt_radial_mm'];screw(f'deck_bolt_{u}_{v}',(u,v),20,35 if outer else 20,S);nut(f'deck_nut_{u}_{v}',(u,v),(-7 if outer else 5)-2.4,S)
   for y in (-14,14):
    screw(f'clamp_bolt_{y}',(2.5,y),f['skin_thickness']+c['clamp_thickness_mm'],12,R);nut(f'clamp_nut_{y}',(2.5,y),-6.4,R)
    # Head is on the outward/negative normal side:flip a local screw assembly.
    flip=np.eye(4);flip[0,0]=-1;flip[2,2]=-1
    screw(f'retaining_bolt_{y}',(-c['retaining_bolt_x_mm'],y),12,12,R@flip);nut(f'retaining_nut_{y}',(c['retaining_bolt_x_mm'],y),-2.4,R)
  mates.extend([dict(parts=[f'f{finger}_mount','palm'],type='flat_z5_seat_and_two_M3_clearance_holes'),dict(parts=[f'f{finger}_carrier',f'f{finger}_mount'],type='clearance_pocket_two_normal_axis_M3_retaining_screws_captive_nuts_UNVERIFIED')])
 add('palm',palm,'palm')
 return dict(units='mm',baseline_config=cfg,manufacturing_config=design,parts=parts,mates=mates)


def check_intersections(parts,shapes):
 positive=[];tested=0;touching=[];invalid=[]
 for (i,p),(j,q) in itertools.combinations(enumerate(parts),2):
  if np.any(np.minimum(shapes[i].bounds[1],shapes[j].bounds[1])-np.maximum(shapes[i].bounds[0],shapes[j].bounds[0])<=0):continue
  tested+=1;s=trimesh.boolean.intersection([shapes[i],shapes[j]],engine='manifold',check_volume=True)
  volume=float(s.volume) if not s.is_empty else 0.
  if not s.is_empty and (volume<0 or not s.is_watertight):invalid.append(dict(parts=[p['name'],q['name']],signed_volume_mm3=volume,watertight=bool(s.is_watertight),classification='INVALID_OR_BOUNDARY_KERNEL_RESULT_NOT_CLEARANCE_PASS'))
  if volume>1e-6:
   intended=p.get('join_id') is not None and p.get('join_id')==q.get('join_id')
   positive.append(dict(parts=[p['name'],q['name']],volume_mm3=volume,classification='intended_bond_overlap' if intended else 'UNRESOLVED_STATIC_INTERFERENCE'))
  elif volume>0:touching.append(dict(parts=[p['name'],q['name']],volume_mm3=volume,classification='mesh_float32_boundary_uncertainty_NOT_clearance_PASS'))
 return dict(positive_overlaps=positive,small_boundary_residuals=touching,invalid_or_boundary_kernel_results=invalid,mesh_intersections_evaluated=tested,scope='Static Boolean INTERSECTION VOLUMES using manifold float32 mesh kernel;AABB rejection for disjoint pairs. No swept clearance/contact or micron-tolerance certification;1e-6mm3 reporting threshold is NOT physicsGate.')


def drawing(design,assembly,shapes,path):
 # All outlines are actual mesh triangle edges,not a prescribed deformed pose.
 colors={'finger':'#1685a5','eyelet':'#bd791f','support':'#ab955c','palm':'#304d6a','mount':'#5c8291','motor_envelope':'#d19dbb','drum':'#aa373b'}
 panels=[]
 for label,axes,origin,scale in [('TOP',(0,1),(210,220),2.3),('FRONT',(0,2),(620,110),2.0),('SIDE',(1,2),(1040,110),2.0)]:
  lines=[]
  for part,s in zip(assembly['parts'],shapes):
   edges=s.vertices[s.edges_unique];pts=edges[:,:,list(axes)]*scale;pts[:,:,0]+=origin[0];pts[:,:,1]=origin[1]-pts[:,:,1]
   # Downsample only planar display edges;full geometry remains in STL/recipe.
   for edge in pts[::max(1,len(pts)//120)]:lines.append(f'<path d="M{edge[0,0]:.3f},{edge[0,1]:.3f} L{edge[1,0]:.3f},{edge[1,1]:.3f}"/>')
   panels.append('<g fill="none" stroke="'+colors.get(part['group'],'#68766b')+'" stroke-width="0.45">'+''.join(lines)+'</g>');lines=[]
  panels.append(f'<text x="{origin[0]-90}" y="35">{label}:design rest geometry</text>')
 caption='B3 L100 / distal40deg / start70;root R50,3x120deg. Palm OD128/ID60,t8. Carrier13x36x4;M3 holes3.4;clearance0.2 provisional. NO motion/strength/STEP/fabrication qualification.'
 path.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="570"><rect width="1400" height="570" fill="white"/><g font-family="sans-serif" font-size="14">'+''.join(panels)+f'<text x="20" y="500">{caption}</text><text x="20" y="530">Motor bounding boxes20x26x34 only;output axis,bolt pattern,drum connection and full drivetrain NOT VERIFIED.</text></g></svg>')


def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--config',type=Path,default=BASE/'config/manufacturing_b3_v12.json');a=p.parse_args()
 if Path(a.name).name!=a.name:raise ValueError('unique local design name required')
 out=BASE/'meshes'/a.name;draw=BASE/'drawings'/a.name;out.mkdir(exist_ok=False);draw.mkdir(exist_ok=False);start=time.monotonic();design=load_design(a.config);source=BASE/design['baseline_geometry']
 if sha(source)!=design['baseline_sha256']:raise ValueError('baseline B3 geometry source changed')
 cfg=json.loads(source.read_text());assembly=recipe(cfg,design);shapes=[];manifest=[]
 for part in assembly['parts']:
  shape=evaluate(part['shape']);shapes.append(shape);name=part['name']+'.stl';shape.export(out/name)
  manifest.append(dict(name=part['name'],group=part['group'],vertices=len(shape.vertices),triangles=len(shape.faces),watertight=bool(shape.is_watertight),volume_mm3=float(shape.volume),bounds_mm=shape.bounds.tolist(),sha256=sha(out/name),mass_kg=None))
 (out/'assembly_recipe.json').write_text(json.dumps(assembly,indent=2));(out/'assembly_static_reference.stl').write_bytes(trimesh.util.concatenate(shapes).export(file_type='stl'))
 interference=check_intersections(assembly['parts'],shapes)
 drawing(design,assembly,shapes,draw/'orthographic.svg')
 with (draw/'BOM.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['part','quantity','material','specification_status','mass_kg','unit_cost_KRW'])
  for group in sorted({p['group'] for p in assembly['parts']}):w.writerow([group,sum(p['group']==group for p in assembly['parts']),'UNSELECTED' if group!='motor_envelope' else 'XL330 size envelope candidate','DESIGN_ONLY_NOT_QUALIFIED','NULL','NULL'])
  for row in [('M3 clamp bolt and nut',6,'TBD','nominal length to verify on root stack'),('M3 retaining bolt and nut',6,'TBD','normal-axis provisionalM3x12;thread and tool access unverified'),('M3 mount bolt and nut',6,'TBD','vertical provisionalM3x25;thread unverified'),('M3 deck bolt and nut',12,'TBD','standoff/deck stack length to verify'),('wire',6,'TBD','diameter0.5 baseline;minimum bend radius unknown'),('contact pad',3,'UNSELECTED','NOT MODELED;optional newphysical geometry'),('motor interface adapter',3,'UNSELECTED','supplier horn/holes BLOCKED')]:w.writerow([*row,'NULL','NULL'])
 environment=dict(executables={k:shutil.which(k) for k in ('FreeCADCmd','freecadcmd','openscad')},python_modules={k:importlib.util.find_spec(k) is not None for k in ('FreeCAD','OCP','OCC','cadquery','manifold3d')},boolean_engines=sorted(str(x) for x in trimesh.boolean.engines_available))
 result=dict(status='PARAMETRIC_MESH_ASSEMBLY_CREATED_NOT_FABRICATION_READY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=BASE.parent,text=True).strip(),producer_sha256=sha(Path(__file__)),baseline_sha256=sha(source),design_sha256=sha(a.config),dependency_hashes={str(x.relative_to(BASE.parent)):sha(x) for x in (BASE/'cad/generate.py',BASE/'cad/finite_guide_product.py',BASE/'sofa/finite_guide_coupon.py')},environment=environment,parts=manifest,interference=interference,manufactured_reference=True,actual_sofa_result=False,STEP_generated=False,full_BRep_assembly_verified=False,moving_clearance_verified=False,fastener_access_verified=False,wire_bend_radius_verified=False,material_strength_verified=False,fabrication_ready=False,runtime_s=time.monotonic()-start)
 for directory in (out,draw):
  (directory/'config.json').write_bytes(a.config.read_bytes());(directory/'checks.json').write_text(json.dumps(result,indent=2))
 (draw/'assembly_recipe.json').write_bytes((out/'assembly_recipe.json').read_bytes());(draw/'generator.py').write_bytes(Path(__file__).read_bytes())
 print(json.dumps(dict(parts=len(manifest),unresolved_interferences=sum(x['classification'].startswith('UNRESOLVED') for x in interference['positive_overlaps']),intended_overlaps=sum(x['classification']=='intended_bond_overlap' for x in interference['positive_overlaps']),runtime_s=result['runtime_s'],environment=environment),indent=2))


if __name__=='__main__':main()
