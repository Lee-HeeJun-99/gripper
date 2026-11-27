"""Independent imported STEP/mesh, section, rigid retention and insertion checks."""
import sys,json,shutil,math,itertools
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,common,translate,rotate,bounds,overlap,volume,solid_count,box
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'validation/finger/AX_wide_verify1';out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAX_wide_root1/summary.json';d=json.loads(src.read_text());parent=json.loads((REPO/d['parent']['path']).read_text())
assert sha(REPO/d['parent']['path'])==d['parent']['SHA256']
assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values())
dump(out/'inputs.json',dict(candidate=ref(src),parent=d['parent'],producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(ROOT/'scripts/baseline_registry.py')]))
parts={n:read(REPO/r['path']) for n,r in d['part_references'].items()};checks={'input_hashes':True,'part_count':len(parts)==254,'six_replacement_blanks':len(d['changed'])==6};meshes=[];sections=[];distal=[];stops=[]
for n in d['changed']:
 s=parts[n];checks[n+'_solid']=BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
 verts=[];edges={};oriented={};signed6=0
 for line in (ROOT/'cad/exports/revAX_wide_root1'/f'{n}.stl').read_text().splitlines():
  if line.strip().startswith('vertex'):verts.append(tuple(round(float(x),9) for x in line.split()[1:]))
 for j in range(0,len(verts),3):
  a,b,c=verts[j:j+3];signed6+=a[0]*(b[1]*c[2]-b[2]*c[1])+a[1]*(b[2]*c[0]-b[0]*c[2])+a[2]*(b[0]*c[1]-b[1]*c[0])
  for v,w in ((a,b),(b,c),(c,a)):
   k=tuple(sorted((v,w)));edges[k]=edges.get(k,0)+1;oriented[k]=oriented.get(k,0)+(1 if v<w else -1)
 ok=bool(edges) and all(v==2 for v in edges.values()) and all(v==0 for v in oriented.values()) and signed6>0
 checks[n+'_mesh']=ok;meshes.append(dict(part=n,triangles=len(verts)//3,closed_oriented_positive=ok,signed_mesh_volume_mm3=signed6/6))
 i=int(n[1]);s=rotate(s,-120*i);old=rotate(read(REPO/parent['part_references'][n]['path']),-120*i)
 clip=box(40,-25,-110,35,50,103)
 a=BRepAlgoAPI_Common(s,clip).Shape();b=BRepAlgoAPI_Common(old,clip).Shape();diff=abs(volume(a)+volume(b)-2*common(a,b))
 checks[n+'_distal_unchanged']=diff<1e-8;distal.append(dict(part=n,symmetric_difference_mm3=diff))
 # Independent center slices. .001mm finite slice has O(h^2) circle integration error;
 # compare exact integrated circular-hole chord, not an arbitrary tolerance relaxation.
 h=.001;r=1.05
 removed_section=(h/2*math.sqrt(r*r-h*h/4)+r*r*math.asin(h/(2*r)))*2/h
 expected=.2*(6-removed_section)
 sec=box(50.29,-20,1-h/2,.22,40,h)
 area=volume(BRepAlgoAPI_Common(s,sec).Shape())/h;oldarea=volume(BRepAlgoAPI_Common(old,sec).Shape())/h
 checks[n+'_net_section']=abs(area-expected)<1e-7 and area>4*oldarea
 # At z=-3 and10 the nominal shoulder reaches y=+/-13; pin edge at11.05.
 sections.append(dict(part=n,old_finite_slice_area_mm2=oldarea,new_finite_slice_area_mm2=area,expected_integrated_slice_mm2=expected,nominal_center_net_area_mm2=.78,area_ratio=area/oldarea,old_nominal_outer_ligament_mm=.45,new_nominal_outer_ligament_mm=1.95,nominal_bearing_area_mm2=.4,mean_net_MPa_per_N=1/area,mean_bearing_MPa_per_N=2.5,actual_load_N=None,allowable_MPa=None,stress_concentration=None,capacity_N=None,added_volume_mm3=volume(s)-volume(old)))
 back=rotate(parts[f'F{i}_ROOT_BACK'],-120*i);fragment=BRepAlgoAPI_Common(s,box(45,-25,-7,25,50,17)).Shape()
 for sign in (-1,1):
  before=common(translate(fragment,0,0,sign*.049),back);after=common(translate(fragment,0,0,sign*.051),back)
  checks[n+f'_stop_{sign}']=before<1e-8 and after>1e-8;stops.append(dict(part=n,sign=sign,before_mm3=before,after_mm3=after))
# Independently repeat changed/retained nominal exact intersection checks.
hits=[];pairs=0;bb={n:bounds(s) for n,s in parts.items()}
for n,m in itertools.combinations(parts,2):
 if n not in d['changed'] and m not in d['changed']:continue
 assert not (ROOT/'runtime/STOP').exists()
 if overlap(bb[n],bb[m]):
  pairs+=1;v=common(parts[n],parts[m])
  if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
checks['independent_nominal_context_clear']=not hits
# Root subassembly only, before mounting. Existing full installed-assembly FAIL retained.
sequence=[];installed={n:parts[n] for n in ['F0_ROOT_FRONT','F0_SKIN']}
for name,shifts in [('F0_RAIL_L',[4,2,0]),('F0_RAIL_R',[4,2,0]),('F0_ROOT_BACK',[5,3,1,0])]:
 samples=[]
 for x in shifts:
  s=translate(parts[name],x,0,0);bad=[]
  for n,t in installed.items():
   if overlap(bounds(s),bounds(t)):
    v=common(s,t)
    if v>1e-8:bad.append(dict(part=n,common_mm3=v))
  samples.append(dict(shift_X_mm=x,hits=bad))
 sequence.append(dict(part=name,samples=samples));installed[name]=parts[name]
checks['root_subassembly_samples']=all(not x['hits'] for y in sequence for x in y['samples'])
# Negative control must detect deliberately translated rail penetrating back clamp.
control=common(translate(parts['F0_RAIL_R'],.1,0,0),parts['F0_ROOT_BACK']);checks['misplaced_rail_control']=control>1e-8
r=dict(status='BOUNDED_WIDE_ROOT_VERIFICATION_PASS' if all(checks.values()) else 'BOUNDED_WIDE_ROOT_VERIFICATION_FAIL',candidate=ref(src),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),checks=checks,meshes=meshes,sections=sections,distal=distal,stops=stops,exact_intersection_pairs=pairs,interferences=hits,root_subassembly_samples=sequence,misplaced_rail_control_mm3=control,prior_full_installed_assembly_failure=ref(ROOT/'validation/finger/AO_root_verify1/summary.json'),actual_capacity_qualified=False,whole_system_release=False,limitations=['No elastic equilibrium, stress concentration, material minimum, creep/fatigue or strength/mesh convergence','Hole bearing area remains .4mm2; larger net section is not bearing qualification','Tab linear shoulder notch and clamp compliance/preload/thread load transfer require actual loaded analysis','Distal shape equality only; no loaded sliding/motion/CCD or full ordered assembly/tool proof','No system adoption, hardware, physical overload bound or global energy closure'])
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],failed=[k for k,v in checks.items() if not v],sections=sections)));raise SystemExit(0 if all(checks.values()) else 2)
