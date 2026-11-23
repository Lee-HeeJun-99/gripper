"""Actual cartridge internal joins and retaining-bolt axis access,not drive fit."""
import argparse,json,subprocess,sys,time
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha,cyl,union,transform
from assembly_recipe_io import resolve_recipe
from distal_cartridge_service import classify
from distal_keeper_service import intersections

def bolt_envelopes(shape,travel=18,axis_reach=20):
 G=np.eye(4)
 while shape['op']=='transform':G=G@np.asarray(shape['matrix']);shape=shape['shape']
 if shape['op']!='union' or len(shape['items'])!=2:raise ValueError('two-cylinder nominal bolt required')
 shaft,head=shape['items']
 if any(s['op']!='cylinder' for s in (shaft,head)):raise ValueError('unknown nominal bolt shape')
 if shaft['xy']!=head['xy'] or shaft['z'][1]!=head['z'][0]:raise ValueError('bolt shaft/head datum mismatch')
 if not(0<shaft['radius']<head['radius'] and travel>0 and axis_reach>0):raise ValueError('invalid bolt envelope parameters')
 x,y=head['xy'];sweep=union(cyl(shaft['radius'],shaft['z'][0],shaft['z'][1]+travel,(x,y),shaft.get('sections',64)),cyl(head['radius'],head['z'][0],head['z'][1]+travel,(x,y),head.get('sections',64)))
 axis=cyl(head['radius'],head['z'][1],head['z'][1]+axis_reach,(x,y),head.get('sections',64))
 return transform(sweep,G),transform(axis,G),dict(travel_mm=travel,axis_reach_mm=axis_reach,axis_screen_radius_mm=head['radius'],world_axis=G[:3,2].tolist(),source_shaft_Z_mm=shaft['z'],source_head_Z_mm=head['z'],source_XY_mm=head['xy'])

def internal_joins(parts,moving,finger):
 names={p['name'] for p in parts};moving=set(moving);prefix=f'f{finger}';rows=[]
 for p in parts:
  n=p['name']
  if n.startswith(prefix+'_') and n.endswith('_bondline_RESEARCH'):
   stem=n.removesuffix('_bondline_RESEARCH');members=[stem+'_eyelet',stem+'_support',n]
   if not set(members)<=names:raise ValueError('explicit bond endpoints absent')
   rows.append(dict(join='EXPLICIT_EYELET_SUPPORT_BOND',members=members,all_members_move=all(m in moving for m in members),actual_adhesive=None,physical_strength_qualified=False))
 for rail in ('rail_left','rail_right'):
  members=[prefix+'_skin',prefix+'_'+rail];rows.append(dict(join='ASSUMED_SKIN_RAIL_BOND',members=members,all_members_move=all(m in moving for m in members),actual_adhesive=None,physical_strength_qualified=False))
 members=[prefix+s for s in ('_carrier','_root_clamp','_skin','_rail_left','_rail_right','_clamp_bolt_-14','_clamp_bolt_14','_clamp_nut_-14','_clamp_nut_14')]
 if not set(members)<=names:raise ValueError('intact clamp stack absent')
 rows.append(dict(join='INTACT_ROOT_CLAMP_STACK',members=members,all_members_move=all(m in moving for m in members),physical_preload_N=None,physical_strength_qualified=False))
 return rows

def worker(a):
 start=time.monotonic();out=BASE/'results'/a.tag;src=BASE/'results'/a.case/'assembly_delta_recipe.json';parts,hashes=resolve_recipe(src);solids={p['name']:evaluate(p['shape']) for p in parts};byname={p['name']:p for p in parts};records=[];cuts=[]
 for finger in (0,1,2):
  moving,removed,fixed=classify(parts,finger);joins=internal_joins(parts,moving,finger);cuts.append(dict(finger=finger,moving_names=moving,removed_names=removed,fixed_names=fixed,internal_joins=joins,needs_internal_bond_cut_for_DECLARED_partition=any(not j['all_members_move'] for j in joins),physical_cut_qualified=False,wire_disconnect_qualified=False,nut_temporary_retention_qualified=False))
  for name in removed:
   sweep,axis,detail=bolt_envelopes(byname[name]['shape']);records.append(dict(bolt=name,**detail,continuous_bolt_envelope_intersections=intersections(evaluate(sweep),[(n,b) for n,b in solids.items() if n!=name]),axis_envelope_intersections=intersections(evaluate(axis),[(n,b) for n,b in solids.items() if n!=name]),actual_drive_geometry=None,actual_thread_fit=None))
 for f in (Path(__file__),BASE/'cad/distal_cartridge_service.py',BASE/'cad/distal_keeper_service.py',BASE/'cad/manufacturing_assembly.py',BASE/'cad/assembly_recipe_io.py'):hashes[str(f.relative_to(BASE))]=sha(f)
 hits=any(r['continuous_bolt_envelope_intersections'] or r['axis_envelope_intersections'] for r in records)
 result=dict(status='ROOT_RETAINING_ACCESS_GEOMETRY_REVIEW' if hits else 'SIX_NOMINAL_RETAINING_AXES_CLEAR_DRIVE_AND_NUT_RETENTION_UNQUALIFIED',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,cartridge_partitions=cuts,assembly_part_count=len(parts),actual_joint_cut_qualified=False,physical_service_qualified=False,fabrication_ready=False,runtime_s=time.monotonic()-start,scope='Same actual294part REST assembly. Six original nominal two-cylinder retaining bolts:union of separately swept shaft/head contains whole18mm translation,not filled-concavity hull. Head-radius20mm approach cylinder is an AXIS SPACE screen,NOT actual driver/hex/head/hand fit because original proxies have no drive geometry. Only own bolt omitted for approach;all other hardware including nuts remains. Bond endpoint identities and Skin/Rail joins stay together in declared cartridge partition;do not cut adhesives merely for exchange. This doesNOTprove completeness of physical joints,actual preload/thread/adhesive/nut capture/wire disconnect or whole service sequence. No Native/holding/STEP qualification.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],runtime_s=result['runtime_s'],bolts=len(records))))

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',default='product_distal_bottom1018');p.add_argument('--worker',action='store_true');a=p.parse_args()
 if any(Path(n).name!=n for n in (a.tag,a.case)):p.error('local names required')
 if a.worker:worker(a);return
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());sys.path.insert(0,str(BASE/'sofa'));from native_bending_coupon import guarded
 cmd=[sys.executable,str(Path(__file__).resolve()),'--tag',a.tag,'--case',a.case,'--worker'];proc=guarded(cmd,out/'process',420);(out/'launcher.json').write_text(json.dumps(dict(command=cmd,process=proc),indent=2))
 if not(out/'summary.json').exists():(out/'summary.json').write_text(json.dumps(dict(status='FAIL_ROOT_DISCONNECT_CHILD',process=proc),indent=2))
 d=json.loads((out/'summary.json').read_text());print(json.dumps({k:d[k] for k in ('status','runtime_s') if k in d}))
if __name__=='__main__':main()
