"""Finite bridge/axle-retention candidates;threads,preload and strength unqualified."""
import argparse,csv,json,math,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,box,cyl,union,cut,transform,poly,evaluate,sector,sha
from deformed_wire_screen import probes

def rod(a,b,r):
 a=np.asarray(a);b=np.asarray(b);d=b-a
 if np.linalg.norm(d)==0:raise ValueError('zero bridge span')
 M=trimesh.geometry.align_vectors([0,0,1],d/np.linalg.norm(d));M[:3,3]=(a+b)/2
 return transform(cyl(r,-np.linalg.norm(d)/2,np.linalg.norm(d)/2),M)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);p.add_argument('--topology',choices=['direct','tower'],required=True);p.add_argument('--backbone',choices=['outer','behind-pulley'],default='outer');a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);target=BASE/'meshes'/a.name;draw=BASE/'drawings'/a.name;target.mkdir(exist_ok=False);draw.mkdir(exist_ok=False);start=time.monotonic();sources=[BASE/'meshes'/n/'assembly_recipe.json' for n in ('b3_manufacturing_bore_v21','b3_lead_pulley_modules_v22','b3_pulley_fork_modules_v23')];parent,wheels,forks=[json.loads(s.read_text()) for s in sources];parts=[];shapes=[];records=[];backbone_x=58. if a.backbone=='behind-pulley' else 78.
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());producer_hash=sha(__file__)
 def add(name,op,group):
  shape=evaluate(op);file=target/(name+'.stl');file.write_text(shape.export(file_type='stl_ascii'));loaded=trimesh.load_mesh(file)
  if not loaded.is_volume or loaded.body_count!=1:raise ValueError('new bridge/retention STL readback failed '+name)
  parts.append(dict(name=name,shape=op,group=group));shapes.append(shape);records.append(dict(part=name,saved_STL_sha256=sha(file),volume_mm3=float(shape.volume),closed_positive_singlebody=True,mass_kg=None))
 palm=next(p['shape'] for p in parent['parts'] if p['name']=='palm')
 for f,angle in enumerate(parent['baseline_config']['palm']['angles_deg']):
  S=sector(angle)
  for c,side in enumerate((1,-1)):
   feet=[np.array([x,side*30,15.]) for x in (44,52)];bits=[transform(cyl(3.5,13,18,(foot[0],foot[1])),S) for foot in feet];tower=np.array([backbone_x,side*50,15.]);bits.extend([transform(rod(feet[0],feet[1],2.),S),transform(rod(feet[1],[52,side*50,15],2.),S),transform(rod([52,side*50,15],tower,2.),S)])
   if a.topology=='tower':
    zs=[(np.asarray(p['shape']['matrix'])@np.array([-10,0,0,1]))[2]+(12 if '_turn2_' in p['name'] else 5) for p in forks['parts'] if p['group']=='fork' and p['name'].startswith(f'f{f}_c{c}_')]
    bits.append(transform(rod([backbone_x,side*50,min(zs)-2],[backbone_x,side*50,max(zs)+2],2.),S))
   for k in range(1,4):
    name=f'f{f}_c{c}_turn{k}';fork=next(p for p in forks['parts'] if p['name']==name+'_fork');M=np.asarray(fork['shape']['matrix']);connection=(M@np.array([-5.5,0,0,1]))[:3];bits.append(fork['shape'])
    if a.topology=='tower':
     back=(M@np.array([-10,0,0,1]))[:3];raised=back+np.array([0,0,5]);local=(np.linalg.inv(S)@np.r_[raised,1])[:3];outside=(S@np.array([local[0],side*(56 if k==2 else 50),local[2],1]))[:3]
     if k==2:
      higher=outside+np.array([0,0,7]);endpoint=(S@np.array([backbone_x,side*50,local[2]+7,1]))[:3];tail=[rod(outside,higher,1.5),rod(higher,endpoint,1.5)]
     else:endpoint=(S@np.array([backbone_x,side*50,local[2],1]))[:3];tail=[rod(outside,endpoint,1.5)]
     bits.extend([rod(connection,back,1.5),rod(back,raised,1.5),rod(raised,outside,1.5),*tail])
    else:bits.append(rod(connection,(S@np.r_[feet[1],1])[:3],1.5))
    # Nominal M1-like headed pin/thread/nut envelope,NOT supplier/thread CAD.
    add(name+'_headed_pin',transform(union(cyl(.5,-2.45,3.7),cyl(1.25,-3.45,-2.45)),M),'headed_pin_proxy')
    add(name+'_axle_nut',transform(cut(cyl(1.25/math.cos(math.pi/6),2.45,3.25,sections=6),cyl(.55,2.3,3.4)),M),'axle_nut_proxy')
   bridge=union(*bits)
   for j,foot in enumerate(feet):
    bore=transform(cyl(1.7,1,21,foot[:2]),S);bridge=cut(bridge,bore);palm=cut(palm,bore)
    add(f'f{f}_c{c}_mount_bolt{j}',transform(union(cyl(1.5,2.1,18.1,foot[:2]),cyl(2.8,18.1,21.1,foot[:2])),S),'mount_bolt_proxy')
    add(f'f{f}_c{c}_mount_nut{j}',transform(cut(cyl(5.5/math.sqrt(3),2.5,4.9,foot[:2],sections=6),cyl(1.6,2.4,5,foot[:2])),S),'mount_nut_proxy')
   add(f'f{f}_c{c}_bridge',bridge,'integral_bridge_forks')
 add('palm_bridge_bores',palm,'palm_new_holes')
 fixed=[p for p in parent['parts'] if p['name']!='palm']+wheels['parts'];fixed_shapes=[evaluate(p['shape']) for p in fixed];hits=[]
 for i,(part,left) in enumerate(zip(parts,shapes)):
  for other,right in list(zip(fixed,fixed_shapes))+list(zip(parts[i+1:],shapes[i+1:])):
   if np.any(np.minimum(left.bounds[1],right.bounds[1])-np.maximum(left.bounds[0],right.bounds[0])<=0):continue
   hit=trimesh.boolean.intersection([left,right],engine='manifold')
   if len(hit.faces):hits.append(dict(parts=[part['name'],other['name']],signed_volume_mm3=float(hit.volume)))
 lead_source=BASE/'results/product_motor_lead748/summary.json';leads=json.loads(lead_source.read_text());wirehits=[]
 for wire in [r for r in leads['records'] if r['model']=='perimeter_rounded_candidate']:
  for sample,probe in probes(np.asarray(wire['route_mm']),.25+2*(1-math.cos(math.radians(.5)))):
   for part,solid in zip(parts,shapes):
    if np.any(np.minimum(probe.bounds[1],solid.bounds[1])-np.maximum(probe.bounds[0],solid.bounds[0])<=0):continue
    hit=trimesh.boolean.intersection([probe,solid],engine='manifold')
    if len(hit.faces):wirehits.append(dict(finger=wire['finger'],cable=wire['cable'],sample=sample,part=part['name'],signed_volume_mm3=float(hit.volume)))
 recipe=dict(units='mm',parts=parts,scope='New parts only;parent referenced by hash. Nominal threaded proxies,not qualified strength/assembly.');full=dict(units='mm',parts=fixed+parts)
 for directory in (target,draw):
  (directory/'assembly_recipe.json').write_text(json.dumps(recipe,indent=2));(directory/'full_assembly_recipe.json').write_text(json.dumps(full,indent=2))
 if producer_hash!=sha(__file__):raise ValueError('bridge producer changed during execution')
 result=dict(status='FINITE_BRIDGE_CANDIDATE_NOT_PRODUCT_QUALIFICATION',topology=a.topology,backbone=a.backbone,backbone_x_mm=backbone_x,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),producer_sha256=producer_hash,input_hashes={str(s.relative_to(BASE.parent)):sha(s) for s in sources+[lead_source]},records=records,nonempty_solid_intersections=hits,wire_intersections=wirehits,runtime_s=time.monotonic()-start,STEP_generated=False,fabrication_ready=False,scope='TwoM3-like bolts/branch at(44/52,+/-30),12newPalmbores.6integralbridges include18forks;18headedpin/18nut proxies retain axles nominally with0.1mm combined axialplay. Samewire/wheels/feet;outerorbehind-pulley backbone changesloadpath/envelope,notactuationinput. No supplier/thread/preload/tolerance/materialstrength,wirefatigue or Native dynamics qualification. Changed only candidateCAD,not historicalparts orcollisionmodels.')
 for directory in (out,draw):(directory/'summary.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(dict(parts=len(parts),solid_hits=len(hits),wire_hits=len(wirehits),runtime_s=result['runtime_s']),indent=2))
if __name__=='__main__':main()
