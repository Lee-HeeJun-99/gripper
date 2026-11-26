"""Independent reimport, root stop and root-only change verification.
No elastic equilibrium/strength claim from rigid collision or bearing inventory.
"""
import sys,json,shutil
from pathlib import Path
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,translate,rotate,bounds,overlap,volume,solid_count,box
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'validation/finger/AO_root_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAO_root1/summary.json';d=json.loads(src.read_text());parent=json.loads((REPO/d['parent']['path']).read_text())
assert sha(REPO/d['parent']['path'])==d['parent']['SHA256']
assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values())
dump(out/'inputs.json',dict(candidate=ref(src),parent=d['parent'],parts=d['part_references'],producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(ROOT/'scripts/baseline_registry.py')]))
parts={n:read(REPO/r['path']) for n,r in d['part_references'].items()};checks={'input_hashes':True,'nominal_interference':not d['interferences'],'part_count':len(parts)==254};meshes=[]
for n in d['changed']:
 s=parts[n];checks[n+'_solid']=BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
 verts=[];edges={}
 for line in (ROOT/'cad/exports/revAO_root1'/f'{n}.stl').read_text().splitlines():
  if line.strip().startswith('vertex'):verts.append(tuple(round(float(x),9) for x in line.split()[1:]))
 for j in range(0,len(verts),3):
  a,b,c=verts[j:j+3]
  for v,w in ((a,b),(b,c),(c,a)):
   k=tuple(sorted((v,w)));edges[k]=edges.get(k,0)+1
 ok=bool(edges) and all(v==2 for v in edges.values());checks[n+'_closed_STL']=ok;meshes.append(dict(part=n,triangles=len(verts)//3,closed=ok))
rows=[];distal=[];inventory=[]
for i in range(3):
 # Transform to local F0 chart for identical independent layer displacements.
 back=rotate(parts[f'F{i}_ROOT_BACK'],-120*i)
 for suffix,t,width,pins in [('SKIN',.3,24,2),('RAIL_L',.2,9,1),('RAIL_R',.2,9,1)]:
  name=f'F{i}_{suffix}';s=rotate(parts[name],-120*i);old=rotate(read(REPO/parent['part_references'][name]['path']),-120*i)
  fragment=BRepAlgoAPI_Common(s,box(45,-25,-7,25,50,17)).Shape()
  original_fragment=BRepAlgoAPI_Common(old,box(45,-25,-7,25,50,17)).Shape()
  for sign in (-1,1):
   samples=[dict(dz_mm=sign*z,intersection_mm3=common(translate(fragment,0,0,sign*z),back)) for z in (.049,.051)]
   control=common(translate(original_fragment,0,0,sign*.051),rotate(read(REPO/parent['part_references'][f'F{i}_ROOT_BACK']['path']),-120*i))
   ok=samples[0]['intersection_mm3']<1e-8 and samples[1]['intersection_mm3']>1e-8 and control<1e-8
   checks[f'{name}_stop_{sign}']=ok;rows.append(dict(part=name,sign=sign,samples=samples,old_design_control_overlap_mm3=control,passed=ok))
  clip=box(40,-25,-110,35,50,103) # Stops at root boundary z=-7.
  a=BRepAlgoAPI_Common(s,clip).Shape();b=BRepAlgoAPI_Common(old,clip).Shape()
  difference=abs(volume(a)+volume(b)-2*common(a,b));ok=difference<1e-8
  checks[name+'_distal_unchanged']=ok;distal.append(dict(part=name,symmetric_difference_mm3=difference,passed=ok))
  removed=volume(old)-volume(s)
  # Unit axial resultant influence, equally shared PET pins only as a declared contrast.
  bearing_area=t*2*pins;net_area=t*(width-2.1*pins)
  inventory.append(dict(part=name,removed_volume_mm3=removed,projected_bearing_area_mm2=bearing_area,minimum_net_section_mm2=net_area,mean_bearing_MPa_per_N=1/bearing_area,mean_net_stress_MPa_per_N=1/net_area,actual_load_N=None,elastic_strain=None,allowable_MPa=None,capacity_N=None))
# Ordered F0 root-only assembly: front placed first, then layers, then integral-pin back.
excluded={f'F0_{s}' for s in ('SKIN','RAIL_L','RAIL_R','ROOT_BACK')};installed={n:s for n,s in parts.items() if n not in excluded};sequence=[]
for name,shifts in [('F0_SKIN',[4,2,0]),('F0_RAIL_L',[4,2,0]),('F0_RAIL_R',[4,2,0]),('F0_ROOT_BACK',[5,3,1,0])]:
 samples=[]
 for x in shifts:
  assert not (ROOT/'runtime/STOP').exists()
  s=translate(parts[name],x,0,0);bb=bounds(s);hits=[]
  for n,t in installed.items():
   if overlap(bb,bounds(t)):
    v=common(s,t)
    if v>1e-8:hits.append(dict(part=n,intersection_mm3=v))
  samples.append(dict(shift_X_mm=x,hits=hits))
 sequence.append(dict(part=name,samples=samples));installed[name]=parts[name]
checks['ordered_assembly_samples']=all(not r['hits'] for s in sequence for r in s['samples'])
r=dict(status='BOUNDED_ROOT_CAPTURE_VERIFICATION_PASS' if all(checks.values()) else 'BOUNDED_ROOT_CAPTURE_VERIFICATION_FAIL',candidate=ref(src),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),checks=checks,meshes=meshes,stops=rows,distal_geometry=distal,unit_resultant_section_inventory=inventory,ordered_assembly_samples=sequence,actual_capacity_qualified=False,whole_system_release=False,limitations=['Rigid independent root fragments; no elastic loaded equilibrium/strain/creep or strength','Projected bearing/net areas are nominal geometry, not stress concentration/allowables or capacity','Back clamp and existing normal retaining bolts must be loaded and thread qualified','Distal geometry equality preserves prior sliding mechanism only; no finite loaded sliding or full Finger PASS','Ordered samples are not continuous assembly or tool/bolt installation proof','No dynamic/global energy, Stage1/Stage2 release or hardware measurement'])
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],failed=[k for k,v in checks.items() if not v])));raise SystemExit(0 if all(checks.values()) else 2)
