"""Finite root redirect screen. Rest CAD only; NOT fixed-pullpoint equivalence."""
import argparse,json,math,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,transform,sha
from lead_pulley_candidate import wheel_recipe
from rounded_wire_path import fillet
from deformed_wire_screen import probes
from pulley_fork_candidate import fork_recipe
from manufacturing_assembly import cyl

def corner_frame(a,b,c,radius):
 u=b-a;v=c-b
 if radius<=0 or np.linalg.norm(u)==0 or np.linalg.norm(v)==0:raise ValueError('undefined root corner')
 u=u/np.linalg.norm(u);v=v/np.linalg.norm(v)
 axis=np.cross(u,v)
 if np.linalg.norm(axis)==0:raise ValueError('collinear corner has no pulley axis')
 axis=axis/np.linalg.norm(axis)
 theta=math.atan2(np.linalg.norm(np.cross(u,v)),float(u@v))
 trim=radius*math.tan(theta/2)
 centre=b-u*trim+radius*np.cross(axis,u)
 frame=trimesh.geometry.align_vectors([0,0,1],axis);frame[:3,3]=centre
 return frame,theta,trim

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);p.add_argument('--fork',action='store_true');a=p.parse_args()
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
 dest=BASE/'meshes'/a.name;dest.mkdir(exist_ok=False)
 start=time.monotonic();src=BASE/'meshes/b3_thrust_shims_v29/full_assembly_recipe.json';lead=BASE/'results/product_motor_lead748/summary.json'
 inputs=[Path(__file__),src,lead,BASE/'cad/lead_pulley_candidate.py',BASE/'cad/rounded_wire_path.py',BASE/'cad/deformed_wire_screen.py',BASE/'cad/manufacturing_assembly.py',BASE/'cad/pulley_fork_candidate.py']
 hashes={str(x.relative_to(BASE)):sha(x) for x in inputs}
 (out/'producer.py').write_bytes(Path(__file__).read_bytes())
 parent=json.loads(src.read_text());parts=parent['parts'];solids=[(x['name'],evaluate(x['shape'])) for x in parts];records=[];new=[];hits=[]
 for wire in json.loads(lead.read_text())['records']:
  if wire['model']!='perimeter_rounded_candidate':continue
  f,c=wire['finger'],wire['cable'];oldroute=np.array(wire['route_mm']);pull=oldroute[0]
  eye=next(x for x in parts if x['name']==f'f{f}_c{c}_s0_eyelet');first=np.array(eye['shape']['matrix'])[:3,3]
  # The first straight outgoing segment has unchanged direction before turn1.
  direction=oldroute[1]-pull;direction/=np.linalg.norm(direction)
  endpoint=pull+direction*8
  route,sag,_=fillet(np.array([first,pull,endpoint]),2.)
  M,theta,trim=corner_frame(first,pull,endpoint,2.)
  name=f'f{f}_c{c}_root_redirect';op=transform(wheel_recipe(),M);solid=evaluate(op)
  path=dest/(name+'.stl');path.write_text(solid.export(file_type='stl_ascii'));read=trimesh.load_mesh(path)
  if not read.is_volume or read.body_count!=1:raise ValueError('root wheel STL invalid')
  new.append(dict(name=name,group='unmounted_root_redirect',finger=f,shape=op))
  module=[(name,solid)]
  if a.fork:
   arc=route[np.linalg.norm(route-M[:3,3],axis=1)<2.000000001]-M[:3,3]
   facing=arc.sum(axis=0);facing-=M[:3,2]*(M[:3,2]@facing);facing/=np.linalg.norm(facing)
   F=M.copy();F[:3,:3]=np.column_stack((facing,np.cross(M[:3,2],facing),M[:3,2]))
   for suffix,local in [('fork',fork_recipe()),('pin',cyl(.5,-2.4,2.4))]:
    partname=name+'_'+suffix;shapeop=transform(local,F);body=evaluate(shapeop);file=dest/(partname+'.stl');file.write_text(body.export(file_type='stl_ascii'))
    loaded=trimesh.load_mesh(file)
    if not loaded.is_volume or loaded.body_count!=1:raise ValueError('root fork/pin readback invalid')
    new.append(dict(name=partname,group='unmounted_root_'+suffix,finger=f,shape=shapeop));module.append((partname,body))
  for i,(left,shape) in enumerate(module):
   for other,body in solids+module[i+1:]:
    if np.any(np.minimum(shape.bounds[1],body.bounds[1])-np.maximum(shape.bounds[0],body.bounds[0])<=0):continue
    hit=trimesh.boolean.intersection([shape,body],engine='manifold')
    if len(hit.faces):hits.append(dict(parts=[left,other],volume_mm3=float(hit.volume)))
  wirehits=[]
  for sample,probe in probes(route,.25+sag):
   for other,body in solids+module:
    if np.any(np.minimum(probe.bounds[1],body.bounds[1])-np.maximum(probe.bounds[0],body.bounds[0])<=0):continue
    hit=trimesh.boolean.intersection([probe,body],engine='manifold')
    if len(hit.faces):wirehits.append(dict(sample=sample,part=other,volume_mm3=float(hit.volume)))
  records.append(dict(part=name,STL_sha256=sha(path),turn_angle_deg=math.degrees(theta),trim_mm=trim,centre_mm=M[:3,3].tolist(),route_mm=route.tolist(),wire_intersections=wirehits,path_length_change_mm=float(np.linalg.norm(np.diff(route,axis=0),axis=1).sum()-np.linalg.norm(first-pull)-8),conditional_resultant_N=3*math.sin(theta/2),mass_kg=None))
  solids.extend(module)
 if hashes!={str(x.relative_to(BASE)):sha(x) for x in inputs}:raise ValueError('source identity changed')
 (dest/'assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=new),indent=2))
 result=dict(status='ROOT_REDIRECT_REQUIRES_REDESIGN' if hits or any(x['wire_intersections'] for x in records) else 'REST_ROOT_WHEEL_SCREEN_CLEAR_NOT_MOUNTED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,solid_intersections=hits,runtime_s=time.monotonic()-start,finite_forks_and_pin_proxies=a.fork,STEP_generated=False,fabrication_ready=False,scope='Six finite unmounted OD6 wheels at R2 wire fillets,wireD0.5. Actual Manifold intersections with all280 rest parts and new modules;unchanged collisions. Root corner is NEW mechanism,not old Native pullpoint. Optional finite forks/pin proxies are NOT mounted or retained. No bearings,strength,friction,continuous motion or SOFA validation. Conditional resultant at assumed1.5N equal branch tension;not measured.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ('status','runtime_s','solid_intersections')},indent=2))
if __name__=='__main__':main()
