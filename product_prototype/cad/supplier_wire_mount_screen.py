"""Finite wire envelope against rebuilt lead assembly; all contact hits retained."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,sha,evaluate
from rounded_wire_path import fillet
from deformed_wire_screen import probes
from supplier_root_wheel import supplier_dimensions

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results/product_supplier_mount875/full_assembly_recipe.json';leadfile=BASE/'results/product_supplier_turn872/summary.json';rootfile=BASE/'meshes/b3_supplier_root_mount_v42/route_mm.json';cfgfile=BASE/'config/wire_bend_supplier_v40.json'
 if a.cable==1:src=BASE/'results/product_supplier_second882/full_assembly_recipe.json';leadfile=BASE/'results/product_supplier_path870/summary.json'
 if a.complete_root:src=BASE/'results/product_supplier_second_root886/full_assembly_recipe.json';rootfile=BASE/'results/product_supplier_second_root886/route_mm.json'
 if a.assembly_recipe:src=a.assembly_recipe.resolve()
 parts=json.loads(src.read_text())['parts'];d=supplier_dimensions(json.loads(cfgfile.read_text()));points=np.array(json.loads(leadfile.read_text())['design_polyline_local_mm'] if a.cable==0 else json.loads(leadfile.read_text())['records'][1]['design_polyline_local_mm']);points[1:3,0]=74.;lead,sag,trims=fillet(points,d['wire_centre_pitch_radius_mm']);route=np.vstack([np.array(json.loads(rootfile.read_text())),lead[1:]]) if a.cable==0 or a.complete_root else lead;solids=[evaluate(p['shape']) for p in parts];hits=[];count=0;radius=d['wire_diameter_mm']/2+max(sag,.00022275007459783834)
 for sample,probe in probes(route,radius):
  count+=1
  for part,body in zip(parts,solids):
   if np.any(np.minimum(probe.bounds[1],body.bounds[1])-np.maximum(probe.bounds[0],body.bounds[0])<=0):continue
   h=trimesh.boolean.intersection([probe,body],engine='manifold')
   if len(h.faces):
    classification='UNRESOLVED_OBSTACLE'
    if part['name'] in (f'f0_c{a.cable}_root_redirect',f'f0_c{a.cable}_turn1',f'f0_c{a.cable}_turn2',f'f0_c{a.cable}_turn3','f0_two_channel_drum'):classification='INTENDED_WHEEL_OR_DRUM_PROXIMITY_NOT_CONTACT_QUALIFICATION'
    hits.append(dict(sample=sample,part=part['name'],volume_mm3=float(h.volume),faces=len(h.faces),classification=classification))
 result=dict(status='WIRE_ENVELOPE_REVIEW_REQUIRED' if any(h['classification']=='UNRESOLVED_OBSTACLE' for h in hits) else 'WIRE_OBSTACLE_SCREEN_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src,leadfile,rootfile,cfgfile,BASE/'cad/deformed_wire_screen.py',BASE/'cad/rounded_wire_path.py')},wire_radius_mm=d['wire_diameter_mm']/2,envelope_radius_mm=radius,route_mm=route.tolist(),probe_count=count,intersections=hits,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='ONE rest-design path f0/c0 including translated first guide→Root→three turns→drum. Circumscribed64gon cylinders/spheres plus arc sagitta;hits can be conservative. All actual solid obstacles retained. Intended wheel proximity is recorded,not discarded or contact PASS. Other five wires,full finger path,moving clearances,wire friction/fatigue/strength and Native dynamics NOT qualified.')
 if a.cable==1:result['scope']='SECOND channel LEAD ONLY .45mm design envelope,pull→3supplier-sized turns→drum. Root arc deliberately NOT included because legacy Root remains bend-INCOMPATIBLE;do not claim whole-path clearance. All281finite solids retained,intended proximities recorded. No moving-wire/contact-law/Native/product qualification.'
 if a.complete_root:result['scope']='SECOND channel translated firstguide→rebuiltRoot→3turns→drum finite .45mm design envelope. All282solid obstacles retained,intended wheel proximities recorded. Not fullfinger/allchannels/movingclearance,wirelaw/Native/material/joint/strength or productqualification. Unselected bondline and translated Skin attachment unqualified.'
 result['cable']=a.cable
 result['assembly_part_count']=len(parts)
 result['scope']=result['scope'].replace('All282solid',f'All{len(parts)}solid').replace('All281finite',f'All{len(parts)}finite')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],probe_count=count,unresolved_hits=sum(h['classification']=='UNRESOLVED_OBSTACLE' for h in hits),runtime_s=result['runtime_s']),indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cable',choices=(0,1),type=int,default=0);p.add_argument('--complete-root',action='store_true');p.add_argument('--assembly-recipe',type=Path);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if a.complete_root and a.cable!=1:p.error('--complete-root requires second channel')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--cable',str(a.cable),'--worker']+(['--complete-root'] if a.complete_root else [])+(['--assembly-recipe',str(a.assembly_recipe.resolve())] if a.assembly_recipe else []);proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_WIRE_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
