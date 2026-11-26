"""AO descendant with replaceable grooved drum nipple. Unrated rejected fuse candidate.
The continuous cable/swage bypass is explicitly checked; no force cap claimed.
"""
import sys,json,shutil,itertools
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,cut,export,common,bounds,overlap,solid_count,volume,rotate
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
assert not (ROOT/'runtime/STOP').exists()
out=ROOT/'cad/exports/revAP_tendon_fuse3';out.mkdir(parents=True,exist_ok=False)
shutil.copyfile(__file__,out/'producer.py')
src=ROOT/'cad/exports/revAO_root2/summary.json';d=json.loads(src.read_text());refs=dict(d['part_references'])
assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
dump(out/'inputs.json',dict(parent=ref(src),parts=refs,producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/build_stage1.py'),ref(ROOT/'scripts/baseline_registry.py')],predeclared=dict(interference_mm3_max=1e-8,area_error_mm2_max=1e-6,neck_outer_radius_mm=.5,bore_radius_mm=.25,neck_length_mm=1.,protection_requires='No continuous cable or bonded joint bypass across fractured neck; calibrated fracture and post-release energy still required')))
parts={n:read(REPO/r['path']) for n,r in refs.items()};changed=[];inventory=[]
# Existing head104..107, stem107..110, bore radius.25. No cable/shaft modification.
ring=cut(cyl(2,(108,0,8.75),1,(1,0,0)),cyl(.5,(107.9,0,8.75),1.2,(1,0,0)))
for i in range(3):
 n=f'F{i}_DRUM_FACTORY_NIPPLE';old=parts[n];s=cut(old,rotate(ring,120*i))
 assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
 export(s,out/n);parts[n]=s;refs[n]=ref(out/(n+'.step'));changed.append(n)
 inventory.append(dict(part=n,removed_mm3=volume(old)-volume(s)))
 # Enlarged outlet permits detached stem to pass; original AP2 recontact preserved.
 n=f'F{i}_DRUM';old=parts[n];s=cut(old,rotate(cyl(1.45,(110,0,8.75),10,(1,0,0)),120*i))
 assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
 export(s,out/n);parts[n]=s;refs[n]=ref(out/(n+'.step'));changed.append(n)
 inventory.append(dict(part=n,removed_mm3=volume(old)-volume(s)))
hits=[];count=0;bb={n:bounds(s) for n,s in parts.items()}
for n,m in itertools.combinations(parts,2):
 if n not in changed and m not in changed:continue
 assert not (ROOT/'runtime/STOP').exists()
 if overlap(bb[n],bb[m]):
  count+=1;v=common(parts[n],parts[m])
  if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
dump(out/'BOM.json',dict(revision=out.name,parts=[dict(part_ID=n,STEP=r,changed=n in changed,material_status='UNQUALIFIED',source_status='CUSTOM_UNRATED_GROOVED_NIPPLE_NOT_SUPPLIER_PART' if n in changed else 'RETAINED_PARENT') for n,r in sorted(refs.items())],manufacture='Custom nipple with sharp annular relief x108..109 local frame, OD1mm ID.5mm; no supplier rating carried over. Drum outlet enlarged to radius1.45mm at x110..120 for fragment escape. Not authorized for manufacture or use.'))
r=dict(status='UNRATED_FUSE_GEOMETRY_PASS' if not hits else 'FUSE_INTERFERENCE_FAIL',revision=out.name,parent=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),parts=len(parts),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inventory=inventory,interferences=hits,exact_intersection_pairs=count,invalidated=['Nipple supplier applicability, swage/cable anchorage and manufacture','Fracture force scatter, fatigue, creep, notch stress and debris','Wire motion, fracture escape, residual inertia and continuing drive work','Same-revision Stage1 and Stage2 gates'],actual_capacity_qualified=False,whole_system_release=False)
dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],hits=hits)));raise SystemExit(2 if hits else 0)
