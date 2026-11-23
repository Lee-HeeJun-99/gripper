"""Finite seating cavity and explicit research bondline,not a verified adhesive joint."""
import argparse,json,math,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,poly,cut,sha
from deformed_wire_screen import probes

def worker(a):
 out=BASE/'results'/a.tag;dest=BASE/'meshes'/a.name;dest.mkdir(exist_ok=False);start=time.monotonic();src=BASE/'meshes/b3_supplier_root_mount_v42/full_assembly_recipe.json';routefile=BASE/'meshes/b3_supplier_root_mount_v42/route_mm.json';data=json.loads(src.read_text());parts=data['parts'];eyelet=next(p for p in parts if p['name']=='f0_c0_s0_eyelet');support=next(p for p in parts if p['name']=='f0_c0_s0_support');G=np.eye(4);op=eyelet['shape']
 while op['op']=='transform':G=G@np.array(op['matrix']);op=op['shape']
 ring=evaluate(eyelet['shape']);body=evaluate(support['shape']);local=(ring.vertices-G[:3,3])@G[:3,:3];radius=float(np.linalg.norm(local[:,1:],axis=1).max());length=float(np.ptp(local[:,0]));gap=.05;axis=G[:3,0];centre=G[:3,3]
 tool=trimesh.creation.cylinder(radius=radius+gap,segment=[centre-axis*(length/2+.2),centre+axis*(length/2+.2)],sections=128);seated=evaluate(cut(support['shape'],poly(tool)))
 shell=trimesh.boolean.difference([trimesh.creation.cylinder(radius=radius+gap,segment=[centre-axis*length/2,centre+axis*length/2],sections=128),trimesh.creation.cylinder(radius=radius,segment=[centre-axis*(length/2+.1),centre+axis*(length/2+.1)],sections=128)],engine='manifold');bond=trimesh.boolean.intersection([body,shell],engine='manifold')
 new=[dict(support,shape=poly(seated)),dict(name='f0_c0_s0_bondline_RESEARCH',group='UNSELECTED_adhesive_design_volume',shape=poly(bond))];records=[]
 for p in new:
  shape=evaluate(p['shape']);file=dest/(p['name']+'.stl');file.write_text(shape.export(file_type='stl_ascii'));read=trimesh.load_mesh(file)
  if not read.is_volume or read.body_count!=1:raise ValueError('seating/bondline STL failed readback')
  records.append(dict(part=p['name'],volume_mm3=float(read.volume),STL_sha256=sha(file),closed_singlebody=True))
 replacement={p['name']:p for p in new};full=[replacement.get(p['name'],p) for p in parts]+[new[1]];fixed=[p for p in parts if p['name']!=support['name']];hits=[]
 for p in new:
  shape=evaluate(p['shape'])
  for q in fixed:
   other=evaluate(q['shape'])
   if np.any(np.minimum(shape.bounds[1],other.bounds[1])-np.maximum(shape.bounds[0],other.bounds[0])<=0):continue
   h=trimesh.boolean.intersection([shape,other],engine='manifold')
   if len(h.faces):hits.append(dict(parts=[p['name'],q['name']],volume_mm3=float(h.volume),faces=len(h.faces)))
 h=trimesh.boolean.intersection([seated,bond],engine='manifold')
 if len(h.faces):hits.append(dict(parts=[new[0]['name'],new[1]['name']],volume_mm3=float(h.volume),faces=len(h.faces)))
 route=np.array(json.loads(routefile.read_text()));u=(route[1]-route[0])/np.linalg.norm(route[1]-route[0]);route=np.vstack([route[0]-u*(length/2+.2),route]);wirehits=[]
 for sample,probe in probes(route,.225+.00022275007459783834):
  for name,shape in [('eyelet',ring),('seated_support',seated),('bondline',bond)]:
   if np.any(np.minimum(probe.bounds[1],shape.bounds[1])-np.maximum(probe.bounds[0],shape.bounds[0])<=0):continue
   h=trimesh.boolean.intersection([probe,shape],engine='manifold')
   if len(h.faces):wirehits.append(dict(sample=sample,part=name,volume_mm3=float(h.volume)))
 (dest/'assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=new),indent=2));(dest/'full_assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=full),indent=2))
 result=dict(status='SEATED_EYELET_CAD_REVIEW_REQUIRED_NOT_JOINT_PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),BASE/'cad/manufacturing_assembly.py',BASE/'cad/deformed_wire_screen.py',src,routefile)},records=records,full_part_count=len(full),nominal_UNMEASURED_bondline_radial_gap_mm=gap,eyelet_outer_radius_mm=radius,finite_polygon_seat_radial_clearance_lower_bound_mm=(radius+gap)*math.cos(math.pi/128)-radius,solid_intersections=hits,wire_bore_support_bond_intersections=wirehits,actual_adhesive_material=None,actual_bond_strength_N=None,runtime_s=time.monotonic()-start,STEP_generated=False,fabrication_ready=False,scope='ONEeyelet/support seat andexplicit finite UNSELECTEDadhesive candidate. Allother291originalnamedparts retained;newbondline adds1=>293. Intended bondinterfaces andanyCSGfragments retained,notroundedaway. Actualresearchgap0.05mm isNOTshop tolerance/material property orpress-fitapproval. Rootlocalwireextendedbeyondfullguide length for finitebore check;notactualdynamics/CCD. NoNative/B3/retention/strength/fullassemblyqualification.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--name',a.name,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_SEATED_EYELET_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
