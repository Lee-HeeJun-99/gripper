"""Palm-connected root fork/retention CAD candidate;not physical qualification."""
import argparse,json,math,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,cyl,cut,union,transform,evaluate,sector,sha
from palm_bridge_candidate import rod
from deformed_wire_screen import probes

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);p.add_argument('--retention',choices=['loose-nut','threaded-boss'],default='loose-nut');p.add_argument('--canonical',action='store_true');a=p.parse_args()
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);target=BASE/'meshes'/a.name;target.mkdir(exist_ok=False);start=time.monotonic()
 parentfile=BASE/'meshes/b3_thrust_shims_v29/full_assembly_recipe.json';rootfile=BASE/'meshes/b3_root_fork_v31/assembly_recipe.json';wirefile=BASE/'results/product_root_fork780/summary.json';leadfile=BASE/'results/product_motor_lead748/summary.json'
 sources=[Path(__file__),parentfile,rootfile,wirefile,leadfile,*[BASE/'cad'/s for s in ('manufacturing_assembly.py','palm_bridge_candidate.py','deformed_wire_screen.py')]];hashes={str(s.relative_to(BASE)):sha(s) for s in sources}
 (out/'producer.py').write_bytes(Path(__file__).read_bytes())
 parent=json.loads(parentfile.read_text());roots=json.loads(rootfile.read_text());parts=[];newsolids=[];records=[];removed=[];canonical={}
 for f,angle in enumerate((0,120,240)):
  S=sector(angle)
  for c,side in enumerate((1,-1)):
   prefix=f'f{f}_c{c}';bridge=next(p for p in parent['parts'] if p['name']==prefix+'_bridge');fork=next(p for p in roots['parts'] if p['name']==prefix+'_root_redirect_fork');M=np.array(fork['shape']['matrix']);connection=(M@[-5.5,0,0,1])[:3]
   # Join existing bolted bridge behind the wire, outside Palm OD128.
   waypoints=[connection,*[(S@np.array([x,side*y,z,1]))[:3] for x,y,z in ((58,44,-8),(58,44,15),(52,44,15))]]
   mounted=union(bridge['shape'],fork['shape'],*[rod(b,e,1.5) for b,e in zip(waypoints,waypoints[1:])]);removed.extend([bridge['name'],fork['name'],prefix+'_root_redirect_pin'])
   # Outward head fixes removal direction found in782/783;nut is on inner side.
   H=M.copy()
   if side<0:H[:3,:3]=M[:3,:3]@np.diag([1,-1,-1])
   if a.retention=='threaded-boss':
    # New manufacturing hypothesis:integral tapped boss,not a removed obstacle.
    # Through-hole remains finite;thread form/material engagement are unqualified.
    boss=transform(cut(cyl(1.5,-4.4,-2.2),cyl(.55,-4.5,-2.1)),H)
    mounted=union(mounted,boss)
   pin=transform(union(cyl(.5,-3.7,2.45),cyl(1.25,2.45,3.45)),H)
   nut=transform(cut(cyl(1.25/math.cos(math.pi/6),-3.25,-2.45,sections=6),cyl(.55,-3.4,-2.3)),H)
   entries=[(prefix+'_root_mounted_bridge',mounted,'root_integral_bridge'),(prefix+'_root_headed_pin',pin,'root_headed_pin_proxy')]
   if a.retention=='loose-nut':entries.append((prefix+'_root_axle_nut',nut,'root_axle_nut_proxy'))
   for name,op,group in entries:
    if a.canonical:
     if f==0:canonical[c,group]=op
     else:op=transform(canonical[c,group],S)
    body=evaluate(op);file=target/(name+'.stl');file.write_text(body.export(file_type='stl_ascii'));read=trimesh.load_mesh(file)
    if not read.is_volume or read.body_count!=1:raise ValueError('root mounting disconnected or invalid '+name)
    parts.append(dict(name=name,group=group,finger=f,shape=op));newsolids.append(body);records.append(dict(part=name,saved_STL_sha256=sha(file),volume_mm3=float(body.volume),closed_positive_singlebody=True,mass_kg=None))
 fixed=[p for p in parent['parts']+roots['parts'] if p['name'] not in removed];fixedsolids=[evaluate(p['shape']) for p in fixed];hits=[]
 for i,(left,solid) in enumerate(zip(parts,newsolids)):
  for right,body in list(zip(fixed,fixedsolids))+list(zip(parts[i+1:],newsolids[i+1:])):
   if np.any(np.minimum(solid.bounds[1],body.bounds[1])-np.maximum(solid.bounds[0],body.bounds[0])<=0):continue
   hit=trimesh.boolean.intersection([solid,body],engine='manifold')
   if len(hit.faces):hits.append(dict(parts=[left['name'],right['name']],volume_mm3=float(hit.volume)))
 wires=json.loads(wirefile.read_text())['records']+[r for r in json.loads(leadfile.read_text())['records'] if r['model']=='perimeter_rounded_candidate'];wirehits=[]
 for r in wires:
  for sample,probe in probes(np.array(r['route_mm']),.25+2*(1-math.cos(math.radians(.5)))):
   for part,body in zip(parts,newsolids):
    if np.any(np.minimum(probe.bounds[1],body.bounds[1])-np.maximum(probe.bounds[0],body.bounds[0])<=0):continue
    hit=trimesh.boolean.intersection([probe,body],engine='manifold')
    if len(hit.faces):wirehits.append(dict(sample=sample,part=part['name'],volume_mm3=float(hit.volume)))
 if hashes!={str(s.relative_to(BASE)):sha(s) for s in sources}:raise ValueError('producer dependencies changed')
 for file,data in [('assembly_recipe.json',dict(units='mm',parts=parts)),('full_assembly_recipe.json',dict(units='mm',parts=fixed+parts))]:(target/file).write_text(json.dumps(data,indent=2))
 result=dict(status='ROOT_MOUNT_REVIEW_REQUIRED' if hits or wirehits else 'ROOT_MOUNT_REFERENCE_MESH_CLEAR_NOT_PRODUCT_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,retention=a.retention,canonical_sector=a.canonical,records=records,solid_intersections=hits,wire_intersections=wirehits,full_part_count=len(fixed+parts),runtime_s=time.monotonic()-start,STEP_generated=False,fabrication_ready=False,scope='Finite connected root forks reuse original12bolted bridge feet/Palm holes;no collision disabled. New6headedpins,headoutboard;loose nuts OR separate integral threaded-boss hypothesis. Optional canonicalfirstsector rotation changes tessellation representation,not nominal configuration;NO digitalidentity claim. Thread shape,material/thread engagement/preload/strength/deflection/wheelendplay/tolerance and movingwire alignment unqualified. Fullrecipe includes prior unresolved mating/seam contacts;only changedparts screened. No SOFA execution.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:result[k] for k in ('status','full_part_count','runtime_s','solid_intersections','wire_intersections')},indent=2))
if __name__=='__main__':main()
