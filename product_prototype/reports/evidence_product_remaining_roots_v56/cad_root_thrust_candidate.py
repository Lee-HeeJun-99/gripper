"""Finite Root thrust lands/wider grooves;all earlier obstacles retained."""
import argparse,json,math,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,cyl,union,cut,transform,evaluate,sector,sha
from deformed_wire_screen import probes

def wheel(groove):
 if not 0<groove<1.8:raise ValueError('nonpositive flange thickness')
 h=groove/2
 return cut(union(cyl(1.75,-h,h),cyl(3.,-.9,-h),cyl(3.,h,.9)),cyl(.6,-1,1))

def lands(cfg):
 inner=cfg['land_fork_span']/2;outer=cfg['land_outer_z'];r=cfg['land_outer_radius'];b=cfg['land_bore_radius']
 if not 0<inner<1.4<outer or not 0<b<r:raise ValueError('invalid land or missing overlap with original fork')
 return union(cut(cyl(r,inner,outer),cyl(b,inner-.1,outer+.1)),cut(cyl(r,-outer,-inner),cyl(b,-outer-.1,-inner+.1)))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);p.add_argument('--mode',choices=['lands-only','wide-only','combined'],required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);dest=BASE/'meshes'/a.name;dest.mkdir(exist_ok=False);start=time.monotonic();src=BASE/'meshes/b3_compact_root_v36/full_assembly_recipe.json';cfgfile=BASE/'config/root_thrust_v37.json';rootwire=BASE/'results/product_root_fork780/summary.json';leadwire=BASE/'results/product_motor_lead748/summary.json';sources=[Path(__file__),src,cfgfile,rootwire,leadwire,BASE/'cad/manufacturing_assembly.py',BASE/'cad/deformed_wire_screen.py'];before={str(x.relative_to(BASE)):sha(x) for x in sources};(out/'producer.py').write_bytes(Path(__file__).read_bytes());cfg=json.loads(cfgfile.read_text());parent=json.loads(src.read_text());lookup={p['name']:p for p in parent['parts']};new=[];records=[]
 for f in range(3):
  S=sector(f*120)
  for c in range(2):
   base=f'f0_c{c}';M=np.array(lookup[base+'_root_redirect']['shape']['matrix']);entries=[]
   if a.mode!='wide-only':entries.append((f'f{f}_c{c}_root_mounted_bridge',union(lookup[base+'_root_mounted_bridge']['shape'],transform(lands(cfg),M))))
   if a.mode!='lands-only':entries.append((f'f{f}_c{c}_root_redirect',transform(wheel(cfg['new_groove_width']),M)))
   for name,local in entries:
    op=local if f==0 else transform(local,S);shape=evaluate(op);file=dest/(name+'.stl');file.write_text(shape.export(file_type='stl_ascii'));loaded=trimesh.load_mesh(file)
    if not loaded.is_volume or loaded.body_count!=1:raise ValueError('thrust CAD readback failed '+name)
    old=lookup[name];new.append(dict(old,shape=op));records.append(dict(part=name,saved_STL_sha256=sha(file),volume_mm3=float(shape.volume),closed_positive_singlebody=True,mass_kg=None))
 replacements={p['name']:p for p in new};fixed=[p for p in parent['parts'] if p['name'] not in replacements];full=[replacements.get(p['name'],p) for p in parent['parts']];newsolids=[evaluate(p['shape']) for p in new];fixedsolids=[evaluate(p['shape']) for p in fixed];hits=[]
 for i,(left,body) in enumerate(zip(new,newsolids)):
  for right,other in list(zip(fixed,fixedsolids))+list(zip(new[i+1:],newsolids[i+1:])):
   if np.any(np.minimum(body.bounds[1],other.bounds[1])-np.maximum(body.bounds[0],other.bounds[0])<=0):continue
   hit=trimesh.boolean.intersection([body,other],engine='manifold')
   if len(hit.faces):hits.append(dict(parts=[left['name'],right['name']],volume_mm3=float(hit.volume)))
 wirehits=[];wires=json.loads(rootwire.read_text())['records']+[r for r in json.loads(leadwire.read_text())['records'] if r['model']=='perimeter_rounded_candidate']
 for r in wires:
  for sample,probe in probes(np.array(r['route_mm']),.25+2*(1-math.cos(math.radians(.5)))):
   for part,body in zip(new,newsolids):
    if np.any(np.minimum(probe.bounds[1],body.bounds[1])-np.maximum(probe.bounds[0],body.bounds[0])<=0):continue
    hit=trimesh.boolean.intersection([probe,body],engine='manifold')
    if len(hit.faces):wirehits.append(dict(sample=sample,part=part['name'],volume_mm3=float(hit.volume),classification='INTENDED_WHEEL_CONTACT_REQUIRES_REFERENCE_CHECK' if part['group']=='unmounted_root_redirect' else 'OBSTACLE'))
 if before!={str(x.relative_to(BASE)):sha(x) for x in sources}:raise ValueError('source changed during CAD run')
 for filename,data in [('assembly_recipe.json',dict(units='mm',parts=new)),('full_assembly_recipe.json',dict(units='mm',parts=full))]:(dest/filename).write_text(json.dumps(data,indent=2))
 d=dict(status='ROOT_THRUST_CAD_REVIEW_REQUIRED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=before,mode=a.mode,records=records,solid_intersections=hits,wire_intersections=wirehits,runtime_s=time.monotonic()-start,part_count=len(full),fabrication_ready=False,STEP_generated=False,scope='Only6Root wheels and/or6Root integral bridges changed;18oldturnpulley/shim assemblies remain untouched withtheir oldFAILs. Integralannularlands overlaporiginalfork0.05mm;newnominalspan2.0mm. Widergroove1.0 vs0.8;wheelwidth1.8/OD6/pitchR2unchanged. Intendedwheelprobecontact retained,not obstaclefreePASS. No thread/material/friction/wear/axialload/Native dynamic qualification;canonicalfirstsector changes meshrepresentation,notdigitalidentity.')
 (out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(dict(parts=len(records),solid_hits=len(hits),wire_obstacles=sum(r['classification']=='OBSTACLE' for r in wirehits),intended_wheel_probe_hits=sum(r['classification']!='OBSTACLE' for r in wirehits),runtime_s=d['runtime_s']),indent=2))
if __name__=='__main__':main()
