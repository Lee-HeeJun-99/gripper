"""Real catalog maximum terminal envelope at finite distal Eyelet shoulder."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,cyl,transform,cut
from assembly_recipe_io import resolve_recipe

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results/product_remaining_f2lead975/assembly_delta_recipe.json';spec=BASE/'config/termination_candidates_v48.json';parts,hashes=resolve_recipe(src);lookup={p['name']:p for p in parts};solids=[evaluate(p['shape']) for p in parts];cfg=json.loads(spec.read_text());catalog=next(c for c in cfg['candidates'] if c['item']=='NI000001');new=[];bodies=[];records=[];hits=[]
 for finger in range(3):
  for cable in range(2):
   name=f'f{finger}_c{cable}';guide=lookup[name+'_s5_eyelet'];op=guide['shape'];G=np.eye(4)
   while op['op']=='transform':G=G@np.asarray(op['matrix']);op=op['shape']
   local=evaluate(op);end=float(local.bounds[1,0]);previous=evaluate(lookup[name+'_s4_eyelet']['shape']).center_mass;projection=float((previous-G[:3,3])@G[:3,0])
   if projection>=0:raise ValueError('terminal on wrong side of wire pull')
   # cylinder's localZ maps to Eyelet localX;exact shoulder end face.
   R=np.eye(4);R[:3,:3]=[[0,0,1],[1,0,0],[0,1,0]]
   shape=transform(cyl(max(catalog['diameter_mm'])/2,end,end+max(catalog['length_mm'])),G@R);body=evaluate(shape);part=dict(name=name+'_distal_NI000001_MAX_ENVELOPE',group='UNQUALIFIED_SWAGED_TERMINAL_ENVELOPE',shape=shape,role='CATALOG_MAX_BOUND_NOT_ACTUAL_WIRE_ASSEMBLY');new.append(part);bodies.append(body);file=out/(part['name']+'.stl');file.write_text(body.export(file_type='stl_ascii'));saved=trimesh.load_mesh(file)
   if not saved.is_volume or saved.body_count!=1:raise ValueError('invalid saved terminal')
   records.append(dict(part=part['name'],STL_SHA256=sha(file),Eyelet_frame=G.tolist(),shoulder_X_mm=end,previous_guide_axis_projection_mm=projection,nominal_Eyelet_OD_outer_radial_margin_mm=1.5-max(catalog['diameter_mm'])/2))
 supports=[]
 if a.exit_relief:
  for rec in records:
   G=np.asarray(rec['Eyelet_frame']);R=np.eye(4);R[:3,:3]=[[0,0,1],[1,0,0],[0,1,0]];name=rec['part'].replace('_distal_NI000001_MAX_ENVELOPE','_s5_support');old=lookup[name];tool=transform(cyl(1.55,rec['shoulder_X_mm'],rec['shoulder_X_mm']+5.5),G@R);q=dict(old,shape=cut(old['shape'],tool),role='UNQUALIFIED_TERMINAL_EXIT_RELIEF_R1p55');body=evaluate(q['shape']);file=out/(name+'.stl');file.write_text(body.export(file_type='stl_ascii'));saved=trimesh.load_mesh(file)
   if not saved.is_volume or saved.body_count!=1:raise ValueError('exit relief splits or invalidates support')
   supports.append(dict(part=name,old_volume_mm3=float(evaluate(old['shape']).volume),new_volume_mm3=float(body.volume),STL_SHA256=sha(file),actual_strength_N=None));new.append(q);bodies.append(body)
 removed=[r['part'] for r in supports];fixed=[p for p in parts if p['name'] not in removed];fixedbodies=[body for p,body in zip(parts,solids) if p['name'] not in removed]
 for i,(p,body) in enumerate(zip(new,bodies)):
  for q,other in [*zip(fixed,fixedbodies),*zip(new[i+1:],bodies[i+1:])]:
   if np.any(np.minimum(body.bounds[1],other.bounds[1])-np.maximum(body.bounds[0],other.bounds[0])<=0):continue
   h=trimesh.boolean.intersection([body,other],engine='manifold')
   if len(h.faces):hits.append(dict(parts=[p['name'],q['name']],faces=len(h.faces),signed_volume_mm3=float(h.volume)))
 delta=dict(units='mm',parent_recipe=str(src.relative_to(BASE)),parent_SHA256=sha(src),remove_names=removed,add_parts=new);(out/'assembly_delta_recipe.json').write_text(json.dumps(delta,indent=2))
 for f in (Path(__file__),spec,BASE/'cad/assembly_recipe_io.py',BASE/'cad/manufacturing_assembly.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 result=dict(status='DISTAL_TERMINAL_PLACEMENT_REVIEW' if hits else 'SIX_MAX_TERMINAL_ENVELOPES_STATIC_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,solid_intersections=hits,candidate_part_count=len(parts+new),runtime_s=time.monotonic()-start,actual_pullout_N=None,fabrication_ready=False,scope='NI000001maxD2.8/L5envelopes at actual6Eyelet distalfaces;actual.45mmwireassembly NOT procured or simulated. GframefromdeclaredsavedCAD;wirepullprojection checkednegative. No guessed bore/swageinterior,threads/force/preload. ExistingEyelet/support/bond/rail joints UNQUALIFIED. Terminal endface loadpath hypothesisonly,not observedforce;zero-volume/small intersections kept. Slack retention/axial escape/wireinstallation,toolaccess,movingclearance,objectcontact/material/Native/holding/STEP NOT qualified.')
 result['candidate_part_count']=len(fixed+new);result['exit_relief_design_radius_mm']=1.55 if a.exit_relief else None;result['support_changes']=supports
 if a.exit_relief:result['scope']+=' NewR1.55cylindricalSupportexitrelief isEXPLICITphysicaldesignchange,notcollisiondisable/epsilonfloor. Singlebodymeshchecked;minimumwall/material/stress/preload/retentionNOTqualified. Eyeletmatingintersectionsremainrecorded.'
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],hits=hits,runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--exit-relief',action='store_true');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if Path(a.tag).name!=a.tag:p.error('local tag required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--worker']+(['--exit-relief'] if a.exit_relief else []);proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_TERMINAL_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s','solid_intersections') if k in d},indent=2))
if __name__=='__main__':main()
