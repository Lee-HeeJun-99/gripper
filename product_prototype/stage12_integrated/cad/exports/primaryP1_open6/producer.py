"""One primary split/open-frame Stage2 specimen. Nominal interfaces, no release."""
import argparse,json,math,shutil,sys,itertools
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,translate,export,common,bounds,overlap,solid_count,volume,canonical
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.gp import gp_Pnt,gp_Dir,gp_Ax2,gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def Ry(a):
 c,s=math.cos(a),math.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def tr(s,r,d):
 t=gp_Trsf();t.SetValues(*map(float,np.column_stack((r,d)).ravel()));return BRepBuilderAPI_Transform(s,t,True).Shape()
def route(deg):
 a=math.radians(deg);r=Ry(a);base=np.array([50.,0,-100.])
 end=base if not a else np.array([50-88/a*(1-math.cos(a))-5*math.sin(a),0,-7-88/a*math.sin(a)-5*math.cos(a)])
 shift=end-r@base;P=r@np.array([43.,0,-92.])+shift;C=np.array([0.,0,20.]);u=(P-C)/np.linalg.norm(P-C);k=11.25/np.linalg.norm(P-C)
 n=k*u+math.sqrt(1-k*k)*np.array([-u[2],0,u[0]]);Q=C+11.25*n;t=(Q-P)/np.linalg.norm(Q-P);E=P+16*t
 phi=math.atan2(n[2],n[0]);return dict(P=P,Q=Q,E=E,t=t,b=math.atan2(t[0],t[2]),phi=phi,free=11.25*(phi+math.pi/2)+np.linalg.norm(Q-E),r=r,shift=shift)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();assert not (ROOT/'runtime/STOP').exists()
 out=ROOT/'cad/exports'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
 ax=ROOT/'cad/exports/revAX_wide_root1/summary.json';av=ROOT/'cad/exports/revAV_micro_interface1/summary.json';A=json.loads(ax.read_text());V=json.loads(av.read_text())
 ao=ROOT/'cad/exports/revAO_root2/summary.json';AO=json.loads(ao.read_text())
 deps=[ax,av,ao,S1/'scripts/bend_aware_stage1.py',ROOT/'models/standard_drive/batch6_sources1/reviewed.json',ROOT/'models/materials/primary_material_contract1.json',S1/'scripts/incremental_stage1.py',S1/'scripts/build_stage1.py',ROOT/'scripts/baseline_registry.py']
 # Reuse full actual Finger incl. replaceable terminal and root, exclude optional dock and old drive/Palm.
 excludes=('IDLER','CLUTCH','DRUM','MOTOR','AXIAL','MF0','MF1','TENDON_WIRE','CASSETTE','JAMMING_DOCK')
 refs={n:r for n,r in A['part_references'].items() if n.startswith('F0_') and not any(k in n for k in excludes)}
 assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
 parts={n:read(REPO/r['path']) for n,r in refs.items()};new={};g=route(0);oldb=-(math.atan2(117,1)-math.acos(11.25/math.hypot(117,1)))
 for n in list(parts):
  if n.startswith(('F0_SWIVEL_LOWER','F0_SWIVEL_UPPER','F0_SWIVEL_BOLT','F0_SWIVEL_NUT','F0_TIP_FACTORY_NIPPLE')):
   rr=Ry(g['b']-oldb);new[n]=tr(parts[n],rr,g['P']-rr@np.array([43.,0,-92.]));parts.pop(n);refs.pop(n)
 for n,r in V['part_references'].items():
  if n.startswith('F0_'):new[n]=translate(read(REPO/r['path']),-110,-1.5,0)
 # Open right-side C frame. Root underside mounting shelf follows actual RF datums.
 frame=fuse(box(54,-23,-12,20,46,5),box(68,-23,-12,6,46,52))
 frame=fuse(frame,box(-32,-42,34,106,65,6))
 cradle=box(-9,-36.5,11,18,29,9)
 cavity=box(-5.05,-35.2,13.95,10.1,25.7,12.1)
 cradle=cut(cradle,cavity,cyl(2.1,(0,-9.6,20),2.2,(0,1,0)))
 frame=fuse(frame,box(-9,-39.5,11,18,3.1,29));frame=fuse(frame,cradle)
 cap=cut(box(-9,-36.4,20,18,28.9,9),cavity,cyl(2.1,(0,-9.6,20),2.2,(0,1,0)))
 # Move root mounting outside the transverse clamp screw envelope; finite tabs.
 rootback=fuse(parts.pop('F0_ROOT_BACK'),box(60,-20,-7,8,40,4));refs.pop('F0_ROOT_BACK')
 for y in (-16,16):
  rootback=cut(rootback,cyl(1.7,(64,y,-7.1),4.2),cyl(2.9,(64,y,-3),14))
 new['F0_ROOT_BACK']=canonical(rootback)
 for n in list(parts):
  if n.startswith('F0_RF'):
   new[n]=translate(parts.pop(n),5,0,0);refs.pop(n)
 for y in (-16,16):frame=cut(frame,cyl(1.7,(64,y,-13),7))
 for x in (-7,7):
  for y in (-29.5,-13.5):
   frame=cut(frame,cyl(1.65,(x,y,10),25),cyl(2.9,(x,y,33.9),6.2));cap=cut(cap,cyl(1.65,(x,y,19.9),9.2))
   new[f'MOTOR_CAP_BOLT_{x}_{y}']=fuse(cyl(1.5,(x,y,7),22),cyl(2.75,(x,y,29),3))
   new[f'MOTOR_CAP_NUT_{x}_{y}']=cut(cyl(3.175,(x,y,8.6),2.4),cyl(1.5,(x,y,8.5),2.6))
 plate=box(-32,-42,40,106,65,6)
 for j,(x,y) in enumerate([(-25,-28),(-25,14),(60,-28),(60,0)]):
  frame=cut(frame,cyl(2.75,(x,y,33.9),6.2));plate=cut(plate,cyl(2.75,(x,y,39.9),6.2))
  new[f'GROUND_BOLT_{j}']=fuse(cyl(2.5,(x,y,34),16),cyl(4.25,(x,y,29),5))
  new[f'GROUND_NUT_{j}']=cut(cyl(4.62,(x,y,46),4),cyl(2.5,(x,y,45.9),4.2))
 # Through service window admits complete drive vertically and allows cap tools.
 frame=cut(frame,box(-18,-36.7,33.9,36,44.7,12.2))
 plate=cut(plate,box(-18,-36.7,39.9,36,44.7,6.2))
 for y in (-16,16):
  frame=cut(frame,cyl(3,(64,y,33.9),6.2));plate=cut(plate,cyl(3,(64,y,39.9),6.2))
 new.update(OPEN_FRAME=canonical(frame),MOTOR_CAP=canonical(cap),GROUND_PLATE=plate)
 # Reuse the source-backed tangent factory-nipple drum/pocket/cap, not a sharp tail bend.
 drum=translate(read(REPO/AO['part_references']['F0_DRUM']['path']),-110,0,0)
 drum=fuse(drum,cyl(4.15,(0,-2.5,20),7,(0,1,0)))
 drum=cut(drum,cyl(1.6,(0,-2.6,20),7.2,(0,1,0)))
 # Four stock1996 M3 interfaces retain2mm drum back web; counterbores admit heads/tools.
 for j in range(4):
  ang=math.pi/4+j*math.pi/2;x=6.35*math.cos(ang);z=20+6.35*math.sin(ang)
  drum=cut(drum,cyl(1.65,(x,-2.6,z),2.2,(0,1,0)),cyl(2.9,(x,-.5,z),5.1,(0,1,0)))
 new['F0_SPOOL']=canonical(drum)
 for n,r in AO['part_references'].items():
  if n.startswith(('F0_DRUM_NIPPLE_CAP','F0_DRUM_FACTORY_NIPPLE','F0_DRUM_CAP_BOLT')):new[n]=translate(read(REPO/r['path']),-110,0,0)
 # One straight tangent factory end, then11.25mm-radius wrap. No internal90degree bend.
 ax2=gp_Ax2(gp_Pnt(0,0,20),gp_Dir(0,-1,0),gp_Dir(0,0,-1))
 arc=BRepPrimAPI_MakeTorus(ax2,11.25,.25,g['phi']+math.pi/2).Shape();d=g['E']-g['Q'];lead=cyl(.25,tuple(g['Q']),float(np.linalg.norm(d)),tuple(d/np.linalg.norm(d)))
 new['F0_TENDON_WIRE']=fuse(fuse(arc,lead),cyl(.25,(-6,0,8.75),6,(1,0,0)))
 dump(out/'inputs.json',dict(producer=ref(out/'producer.py'),dependencies=[ref(p) for p in deps],reused=refs,source_AX_parts=A['part_references'],source_AV_parts=V['part_references'],tolerances=dict(intersection_mm3_max=1e-8),design='ONE primary F0 module; open root shelf, motor shifted110mm inwards, split rectangular clamp, bolted finite ground plate. Not AO adoption.'))
 rows=[]
 for n,s in new.items():
  assert not (ROOT/'runtime/STOP').exists();valid=BRepCheck_Analyzer(s).IsValid();count=solid_count(s)
  export(s,out/n);parts[n]=s;refs[n]=ref(out/(n+'.step'));rows.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),valid=bool(valid),solids=count,volume_mm3=volume(s)))
 bb={n:bounds(s) for n,s in parts.items()};hits=[];pairs=0
 for n,m in itertools.combinations(parts,2):
  assert not (ROOT/'runtime/STOP').exists()
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(parts[n],parts[m])
   if v>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
 w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 dump(out/'BOM.json',dict(revision=a.tag,parts=[dict(part_ID=n,STEP=r,material='See primary_material_contract1; UNQUALIFIED minimum',interface='nominal smooth fastener envelopes; thread load capacity NOT qualified' if 'BOLT' in n or 'NUT' in n else 'finite CAD') for n,r in sorted(refs.items())],optional_extension='Original3Finger/cartridge/jamming preserved in AX/AO immutable models; this is one replaceable module, not final3Finger BOM'))
 r=dict(status='PRIMARY_NOMINAL_INTERFERENCE_FAIL' if hits or any(not x['valid'] or x['solids']!=1 for x in rows) else 'PRIMARY_NOMINAL_GEOMETRY_SCREEN_PASS',revision=a.tag,primary=True,parts=len(parts),part_references=refs,changed=rows,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),interferences=hits,exact_pairs=pairs,part_bounds_mm=bb,route={k:v.tolist() if isinstance(v,np.ndarray) else v for k,v in g.items()},load_path=['motor rectangular gearbox faces -> split cradle -> OPEN_FRAME -> four M5 -> finite GROUND_PLATE','Motor D shaft -> stock1996 set-screw hub -> four M3 -> spool -> factory-head nipple -> tendon -> original tip nipple/swivel -> terminal -> two AX Rails/PET -> pinned ROOT_BACK -> two RF bolts -> OPEN_FRAME -> Ground'],capacity_qualified=False,whole_system_release=False,hardware='NOT_MEASURED',not_qualified=['standard hub setscrew rating and actual radial-hole position','motor body extent vs terminals and axial clamp retention','all bolt thread core/engagement/preload and material minima','factory terminal pullout/pocket wall/cap strength; unused historical drum crossbores unqualified','motor shaft bearing radial/axial capacity','actual finite coupled Finger/contact and global energy','swept assembly/tool and full Stage1','physical overload and all22system gates'])
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],parts=len(parts),hits=hits)));raise SystemExit(2 if r['status'].endswith('FAIL') else 0)
if __name__=='__main__':main()
