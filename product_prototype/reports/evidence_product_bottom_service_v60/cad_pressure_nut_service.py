"""Finite service envelopes and geometric nut stops;not thread locking/preload."""
import argparse,json,subprocess,sys,time,math
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,evaluate,sha,cyl,transform,sector
from assembly_recipe_io import resolve_recipe
from rail_continuous_service import envelope
from bridge_assembly_audit import hits

def worker(a):
 out=BASE/'results'/a.tag;start=time.monotonic();src=BASE/'results'/a.case/('assembly_delta_recipe.json' if a.delta else 'full_assembly_recipe.json');frame=BASE/'results/product_captive_nut941/root_frame.json';M=sector(120*a.finger)@np.array(json.loads(frame.read_text()));parts,recipe_hashes=resolve_recipe(src);solids=[evaluate(p['shape']) for p in parts];lookup={p['name']:s for p,s in zip(parts,solids)};prefix=f'f{a.finger}_c1_s0_';screw=prefix+'pressure_adjuster_M1p6';nut=prefix+'pressure_captive_nut_M1p6';pad=prefix+'rail_pressure_pad_RESEARCH';records=[]
 screw_env=evaluate(transform(cyl(.8,.42,11.62,(12,11.5)),M));records.append(dict(part=screw,type='CONSERVATIVE_ALL_LENGTHS_AXIAL_ENVELOPE',intersections=hits(screw_env,parts,solids,[screw])))
 tool=evaluate(transform(cyl((.7/math.sqrt(3))/math.cos(math.pi/64),1.72,13.62,(12,11.5)),M));records.append(dict(part='0p7AF_hex_key_circumscribed_shank_ONLY',type='CONSERVATIVE_ALL_ROLLS_FINITE_TOOL_ENVELOPE',intersections=hits(tool,parts,solids,[screw])))
 def swept(name,delta):
  if not a.local_envelopes:return envelope(lookup[name],M[:3,:3]@delta)
  part=next(p for p in parts if p['name']==name)
  shape=part['shape'];frame0=np.eye(4)
  while shape['op']=='transform':frame0=frame0@np.array(shape['matrix']);shape=shape['shape']
  if not np.array_equal(frame0,M):raise ValueError('explicit Root transform identity required')
  body=envelope(evaluate(shape),delta)
  if not body.is_volume:raise ValueError('invalid Root envelope')
  body.apply_transform(M);return body
 nut_env=swept(nut,np.array([-a.nut_travel,0,0]));records.append(dict(part=nut,type='CONTINUOUS_CONVEX_NUT_ENVELOPE_AFTER_SCREW_REMOVAL',rootward_travel_mm=a.nut_travel,intersections=hits(nut_env,parts,solids,[screw,nut])))
 pad_env=swept(pad,np.array([0,-4.,0]));records.append(dict(part=pad,type='CONTINUOUS_CONVEX_PAD_ENVELOPE_AFTER_NUT_REMOVAL',intersections=hits(pad_env,parts,solids,[screw,nut,pad])))
 moving=[p['name'] for p in parts if p['name'].startswith(prefix) and p['name'] not in (screw,nut,pad)];excluded=[screw,nut,pad,*moving]
 for distance in (0,.25,.5,1,2,4,8):
  for name in moving:
   body=lookup[name].copy();body.apply_translation(distance*(M[:3,0]+M[:3,1]));records.append(dict(part=name,type='SAMPLED_DIAGONAL_ASSEMBLY_REMOVAL',distance_outboard_mm=distance,intersections=hits(body,parts,solids,excluded)))
 stops=[];local=lookup[nut].copy();local.apply_transform(np.linalg.inv(M))
 for angle in (0,3,5,10,30,60):
  R=trimesh.transformations.rotation_matrix(math.radians(angle),[0,0,1],[12,11.5,0]);body=local.copy();body.apply_transform(M@R);stops.append(dict(angle_deg=angle,cage_intersections=hits(body,parts,solids,[p['name'] for p in parts if p['name']!=prefix+'support'])))
 result=dict(status='CAPTIVE_NUT_SERVICE_REVIEW_REQUIRED' if any(r['intersections'] for r in records) else 'CAPTIVE_NUT_ENVELOPES_AND_SAMPLED_SERVICE_CLEAR_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(f.relative_to(BASE)):sha(f) for f in (Path(__file__),src,frame,BASE/'cad/manufacturing_assembly.py',BASE/'cad/rail_continuous_service.py',BASE/'cad/bridge_assembly_audit.py')},records=records,nut_rotation_samples=stops,moving_parts=len(moving),runtime_s=time.monotonic()-start,actual_locking_or_preload_qualified=False,fabrication_ready=False,scope='Unload/unthreadwire;unscrewM1.6adjuster;slidecaptivenut6mmRootward;removePad4mminboard;then7partsubassemblydiagonal8mm sampledscreen. Continuousconvexenvelopesboundfirst4operations,positiveoverlaponconcaveenvelopeswouldbeUNRESOLVED. Nutrotation tests are geometric stops,NOT friction/selflocking/proof torque or zero backlash. Socketshankonly,NOT purchasedwholetool/hand. No helical fit,threadstrength/preload/physicalslip/deformedfinger/movingwire/Native/product qualification.')
 result['Root_local_envelope_construction']=a.local_envelopes
 result['nut_rootward_travel_mm']=a.nut_travel
 result['target_finger']=a.finger;result['input_hashes'].update(recipe_hashes);result['input_hashes']['cad/assembly_recipe_io.py']=sha(BASE/'cad/assembly_recipe_io.py')
 result['scope']=result['scope'].replace('slidecaptivenut6mmRootward',f'slidecaptivenut{a.nut_travel:g}mmRootward')
 if a.local_envelopes:result['scope']+=' EnvelopebuiltfromdeclaredRoot-localCSGthenrigidlyplaced;avoidsnonwatertightworldQhull942,NOTarbitraryfacedeletionorcertifiedfloatingpointCCD.'
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],blocked=sum(bool(r['intersections']) for r in records),runtime_s=result['runtime_s']),indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_captive_nut941');p.add_argument('--finger',type=int,choices=(0,1,2),default=0);p.add_argument('--delta',action='store_true');p.add_argument('--nut-travel',type=float,default=6.);p.add_argument('--local-envelopes',action='store_true');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)) or not np.isfinite(a.nut_travel) or a.nut_travel<=0:p.error('local names and positive finite travel required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--finger',str(a.finger),'--nut-travel',str(a.nut_travel),'--worker']+(['--local-envelopes'] if a.local_envelopes else [])+(['--delta'] if a.delta else []);proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_NUT_SERVICE_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d},indent=2))
if __name__=='__main__':main()
