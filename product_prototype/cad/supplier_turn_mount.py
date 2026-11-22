"""Reconstructed bolted branch with three supplier-sized forks; design only."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,sha,evaluate,union,cut,cyl,transform,poly
from palm_bridge_candidate import rod
from supplier_root_module import module_fork
from supplier_root_wheel import supplier_dimensions,wheel_mesh
from root_redirect_candidate import corner_frame

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'meshes/b3_supplier_eyelet_seat_v43/full_assembly_recipe.json';turnfile=BASE/'results/product_supplier_turn872/assembly_recipe.json';routefile=BASE/'results/product_supplier_turn872/summary.json';thrust=BASE/'config/root_thrust_v37.json';supplier=BASE/'config/wire_bend_supplier_v40.json'
 if a.cable==1:
  src=BASE/'results/product_supplier_mount875/full_assembly_recipe.json';routefile=BASE/'results/product_supplier_path870/summary.json'
 parent=json.loads(src.read_text());points=np.array(json.loads(routefile.read_text())['design_polyline_local_mm'] if a.cable==0 else json.loads(routefile.read_text())['records'][1]['design_polyline_local_mm']);points[1:3,0]=74.;cfg=json.loads(thrust.read_text());d=supplier_dimensions(json.loads(supplier.read_text()));prefix=f'f0_c{a.cable}';side=1 if a.cable==0 else -1;old=next(p for p in parent['parts'] if p['name']==prefix+'_root_mounted_bridge')
 if a.cable==0:turns=json.loads(turnfile.read_text())['parts'];rootbits=old['shape']['items'][1:]
 else:
  # Explicit legacy V39 union structure:thrustlands+(boss+(oldbranch+fork+3rods)).
  # Preserve ALL Root pieces;replace only the actual old three-turn branch.
  outer=old['shape']['items'];middle=outer[0]['items'];inner=middle[0]['items']
  if len(outer)!=2 or len(middle)!=2 or len(inner)!=5 or inner[0]['op']!='difference':raise ValueError('legacy Root structure changed:reject blind extraction')
  rootbits=[*inner[1:],middle[1],outer[1]];turns=[];wheel,_=wheel_mesh(d)
  for k in (1,2,3):
   M,_,_=corner_frame(*points[k-1:k+2],d['wire_centre_pitch_radius_mm']);turns.append(dict(name=prefix+f'_turn{k}',shape=transform(poly(wheel),M)))
 # Rebuild the entire three-fork branch, preserving both original bolted feet,
 # their bores and all independent Root mounting components.
 bits=[cyl(3.5,13,18,(x,side*30)) for x in (44,52)]
 bits += [rod([44,side*30,15],[52,side*30,15],2),rod([52,side*30,15],[52,side*50,15],2),rod([52,side*50,15],[58,side*50,15],2)]
 new=[];replaced=set();frames=[]
 for k,turn in enumerate(turns,1):
  name=turn['name'];u=points[k]-points[k-1];u/=np.linalg.norm(u);v=points[k+1]-points[k];v/=np.linalg.norm(v);M,_,_=corner_frame(*points[k-1:k+2],d['wire_centre_pitch_radius_mm']);facing=(u-v)/np.linalg.norm(u-v);F=M.copy();F[:3,:3]=np.column_stack([facing,np.cross(M[:3,2],facing),M[:3,2]]);frames.append(F.tolist());fork=transform(module_fork(d['flange_outer_radius_mm'],cfg),F);bits.append(fork)
  back=(F@[-9.375,0,0,1])[:3];far=(F@[-12,0,0,1])[:3];outside=far.copy();outside[1]=side*50;end=np.array([58,side*50,far[2]])
  if k==3 and a.turn3_rise:
   raised=far+np.array([0,0,a.turn3_rise]);outside[2]+=a.turn3_rise;end[2]+=a.turn3_rise
   bits += [rod(back,far,1.5),rod(far,raised,1.5),rod(raised,outside,1.5),rod(outside,end,1.5),rod(end,[58,side*50,15],2)]
  else:bits += [rod(back,far,1.5),rod(far,outside,1.5),rod(outside,end,1.5),rod(end,[58,side*50,15],2)]
  # Same finite headed pin/nut proxies and dimensions as existing turn axles.
  new += [turn,dict(name=name+'_headed_pin',group='headed_pin_proxy',shape=transform(union(cyl(.5,-2.45,3.7),cyl(1.25,-3.45,-2.45)),F)),dict(name=name+'_axle_nut',group='axle_nut_proxy',shape=transform(cut(cyl(1.25/np.cos(np.pi/6),2.45,3.25,sections=6),cyl(.55,2.3,3.4)),F))]
  replaced.update([name,name+'_headed_pin',name+'_axle_nut',name+'_thrust_shim0',name+'_thrust_shim1'])
 branch=union(*bits)
 for x in (44,52):branch=cut(branch,cyl(1.7,1,21,(x,side*30)))
 new.append(dict(old,shape=union(branch,*rootbits)));replaced.add(old['name']);lookup={p['name']:p for p in parent['parts']}
 if not replaced<=lookup.keys():raise ValueError('unmatched replacement')
 fixed=[p for p in parent['parts'] if p['name'] not in replaced];solids=[];records=[]
 for p in new:
  body=evaluate(p['shape']);file=out/(p['name']+'.stl');file.write_text(body.export(file_type='stl_ascii'));read=trimesh.load_mesh(file)
  if not read.is_volume or read.body_count!=1:raise ValueError('invalid/disconnected saved mesh:'+p['name'])
  solids.append(body);records.append(dict(part=p['name'],volume_mm3=float(read.volume),STL_sha256=sha(file),singlebody=True))
 fixedsolids=[evaluate(p['shape']) for p in fixed];hits=[]
 for i,(p,body) in enumerate(zip(new,solids)):
  for q,other in list(zip(fixed,fixedsolids))+list(zip(new[i+1:],solids[i+1:])):
   if np.any(np.minimum(body.bounds[1],other.bounds[1])-np.maximum(body.bounds[0],other.bounds[0])<=0):continue
   h=trimesh.boolean.intersection([body,other],engine='manifold')
   if len(h.faces):hits.append(dict(parts=[p['name'],q['name']],volume_mm3=float(h.volume),faces=len(h.faces)))
 (out/'assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=new),indent=2));(out/'full_assembly_recipe.json').write_text(json.dumps(dict(units='mm',parts=fixed+new),indent=2))
 result=dict(status='TURN_MOUNT_REVIEW_REQUIRED' if hits else 'TURN_MOUNT_NOMINAL_SOLIDS_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src,turnfile,routefile,thrust,supplier,BASE/'cad/supplier_root_module.py',BASE/'cad/palm_bridge_candidate.py')},records=records,solid_intersections=hits,replaced_parts=sorted(replaced),frames=frames,full_part_count=len(fixed+new),runtime_s=time.monotonic()-start,fabrication_ready=False,scope='ONE branch rebuilt with finite connected forks and original two Palm feet/bores. Root connection bits retained. Three old loose shims pairs replaced by integral lands,not omitted without substitute. Native dynamics,wire envelope,service,actual threads/retention/tolerance/material/strength NOT qualified;no STEP.')
 result['turn3_support_rise_mm']=a.turn3_rise
 result['changed_cable']=a.cable;result['scope']+=' Second-channel option independently evaluates rebuilt geometry against retained first channel;its legacy Root is deliberately retained and still supplier-bend INCOMPATIBLE.' if a.cable==1 else ''
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cable',type=int,choices=(0,1),default=0);p.add_argument('--turn3-rise',type=float,default=0);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--cable',str(a.cable),'--turn3-rise',str(a.turn3_rise),'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_MOUNT_CHILD',process=proc),indent=2))
 print((out/'summary.json').read_text())
if __name__=='__main__':main()
