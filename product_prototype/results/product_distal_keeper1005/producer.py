"""Actual distal split keeper candidate,not assumed Root-copy or joint strength."""
import argparse,json,math,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,box,cyl,cut,union,transform
from assembly_recipe_io import resolve_recipe

def axial(radius,x0,x1):
 R=np.eye(4);R[:3,:3]=[[0,0,1],[1,0,0],[0,1,0]]
 return transform(cyl(radius,x0,x1),R)

def keeper_shapes(old_local,cfg):
 d=cfg['design'];lo,hi=d['housing_X_mm'];outer=axial(d['outer_radius_mm'],lo,hi);pocket=axial(d['pocket_radius_mm'],*d['pocket_X_mm']);wire=axial(d['wire_bore_radius_mm'],lo-1,hi+1);yl,yh=d['wing_Y_mm'];z0=d['base_bottom_Z_mm'];top=d['cap_wing_top_Z_mm'];holes=[];nuts=[];screws=[];entries=[]
 lower=union(old_local,cut(outer,box([lo-1,-10,0],[hi+1,10,10])),box([lo,yl,z0],[hi,yh,0]));upper=union(cut(outer,box([lo-1,-10,-10],[hi+1,10,0])),box([lo,yl,0],[hi,yh,top]))
 for x,y in d['bolt_centres_XY_mm']:
  holes.append(cyl(d['clearance_hole_radius_mm'],z0-1,top+2,(x,y)));nb=d['nut_bottom_Z_mm'];nt=nb+max(cfg['nut']['height_mm']);p0,p1=d['nut_pocket_Z_mm'];AF=d['nut_pocket_AF_mm'];pocketnut=cyl(AF/math.sqrt(3),p0,p1,(x,y),sections=6);entry=box([x-1.91,y,p0],[x+1.91,yh+1,p1]);entries.extend([pocketnut,entry])
  nut=cut(cyl(max(cfg['nut']['AF_mm'])/math.sqrt(3),nb,nt,(x,y),sections=6),cyl(.81,nb-.1,nt+.1,(x,y)));nuts.append(nut)
  length=cfg['screw']['nominal_length_mm'];head=max(cfg['screw']['head_height_mm']);tip=top-length;hexradius=cfg['screw']['hex_AF_mm']/math.sqrt(3);screw=cut(union(cyl(.8,tip,top,(x,y)),cyl(max(cfg['screw']['head_diameter_mm'])/2,top,top+head,(x,y))),cyl(hexradius,top+head-cfg['screw']['nominal_drive_depth_mm'],top+head+.2,(x,y),sections=6));screws.append(screw)
 return [cut(lower,pocket,wire,*holes,*entries),cut(upper,pocket,wire,*holes),*screws,*nuts]

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results'/a.case/'assembly_delta_recipe.json';spec=BASE/'config/distal_keeper_v52.json';cfg=json.loads(spec.read_text());parts,hashes=resolve_recipe(src);lookup={p['name']:p for p in parts};prefix=f'f{a.finger}_c{a.cable}';op=lookup[prefix+'_s5_eyelet']['shape'];G=np.eye(4)
 while op['op']=='transform':G=G@np.asarray(op['matrix']);op=op['shape']
 support=lookup[prefix+'_s5_support'];old_local=transform(support['shape'],np.linalg.inv(G));local=keeper_shapes(old_local,cfg);names=[prefix+'_s5_support',prefix+'_s5_keeper_cover',prefix+'_s5_keeper_screw0',prefix+'_s5_keeper_screw1',prefix+'_s5_keeper_nut0',prefix+'_s5_keeper_nut1'];new=[];bodies=[];records=[]
 for name,shape in zip(names,local):
  part=dict(name=name,group='UNQUALIFIED_DISTAL_SPLIT_KEEPER',shape=transform(shape,G),role='CATALOG_NOMINAL_FASTENER_ENVELOPES_NOT_THREAD_FIT');body=evaluate(part['shape']);file=out/(name+'.stl');file.write_text(body.export(file_type='stl_ascii'));saved=trimesh.load_mesh(file)
  if not saved.is_volume or saved.body_count!=1:raise ValueError('invalid/disconnected saved keeper:'+name)
  new.append(part);bodies.append(body);records.append(dict(part=name,STL_SHA256=sha(file),CAD_volume_mm3=float(saved.volume)))
 removed=[support['name']];fixed=[p for p in parts if p['name'] not in removed];obstacles=[evaluate(p['shape']) for p in fixed];hits=[]
 for i,(p,body) in enumerate(zip(new,bodies)):
  for q,other in [*zip(fixed,obstacles),*zip(new[i+1:],bodies[i+1:])]:
   if np.any(np.minimum(body.bounds[1],other.bounds[1])-np.maximum(body.bounds[0],other.bounds[0])<=0):continue
   h=trimesh.boolean.intersection([body,other],engine='manifold')
   if len(h.faces):hits.append(dict(parts=[p['name'],q['name']],faces=len(h.faces),signed_volume_mm3=float(h.volume)))
 (out/'assembly_delta_recipe.json').write_text(json.dumps(dict(units='mm',parent_recipe=str(src.relative_to(BASE)),parent_SHA256=sha(src),remove_names=removed,add_parts=new),indent=2));(out/'keeper_frame.json').write_text(json.dumps(G.tolist(),indent=2))
 for f in (Path(__file__),spec,BASE/'cad/assembly_recipe_io.py',BASE/'cad/manufacturing_assembly.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='DISTAL_KEEPER_STATIC_REVIEW' if hits else 'ONE_DISTAL_KEEPER_STATIC_SCREEN_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,solid_intersections=hits,candidate_part_count=len(fixed+new),target_finger=a.finger,target_cable=a.cable,runtime_s=time.monotonic()-start,actual_preload_N=None,actual_retention_N=None,fabrication_ready=False,scope='ONEactualdistalGframe;finiteupper/lowerhousing,front/rearaxialshoulders,throughwirebore,twoM1.6nominalcapbolts/nuts. Allhardware/finitewireguidesretained;threadhelixnotmodeled. Realinner1.4distalringnotRoot1.2copy. Splitplane/bearingfacesintersectionsretained,NOTdiscarded aszero. Unverifiedmanufacturing/threads/material/preload/strength/assemblytool/service/slackescape,wirelaw,movingclearance/Native/holding/STEP;notkinematicorphysicalretentionPASS.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],hits=hits,runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_distal_basal1000');p.add_argument('--finger',type=int,choices=(0,1,2),default=0);p.add_argument('--cable',type=int,choices=(0,1),default=0);p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--finger',str(a.finger),'--cable',str(a.cable),'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_DISTAL_KEEPER_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s','solid_intersections') if k in d},indent=2))
if __name__=='__main__':main()
