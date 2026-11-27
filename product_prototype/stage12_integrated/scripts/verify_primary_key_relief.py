"""Reimported finite fixture assembly, bearing faces and necessary frictionless statics.
No fixation of old shared M5; all external boundary resultants remain explicit.
"""
import sys,json,shutil,itertools
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,translate,common,bounds,overlap,solid_count,volume
from mechanisms_stage1 import hex_axis
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_SOLID
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from scipy.optimize import linear_sum_assignment

def properties(s,surface=True):
 g=GProp_GProps()
 if surface:BRepGProp.SurfaceProperties_s(s,g)
 else:BRepGProp.VolumeProperties_s(s,g)
 p=g.CentreOfMass();return g.Mass(),[p.X(),p.Y(),p.Z()]

def face_patches(a,b,axis,value,divisions=1):
 def faces(s):
  it=TopExp_Explorer(s,TopAbs_FACE);out=[]
  while it.More():
   f=TopoDS.Face_s(it.Current());bb=bounds(f)
   if BRepAdaptor_Surface(f).GetType()==GeomAbs_Plane and abs(bb[axis]-value)<1e-5 and abs(bb[axis+3]-value)<1e-5:out.append(f)
   it.Next()
  return out
 pieces=[]
 for f in faces(a):
  for g in faces(b):
   c=BRepAlgoAPI_Common(f,g).Shape()
   if properties(c)[0]>1e-8:pieces.append(c)
 cells=[];axes=[i for i in range(3) if i!=axis]
 for piece in pieces:
  bb=bounds(piece);u,v=axes
  for u0,u1 in zip(np.linspace(bb[u],bb[u+3],divisions+1)[:-1],np.linspace(bb[u],bb[u+3],divisions+1)[1:]):
   for v0,v1 in zip(np.linspace(bb[v],bb[v+3],divisions+1)[:-1],np.linspace(bb[v],bb[v+3],divisions+1)[1:]):
    lo=np.array(bb[:3]);sz=np.array(bb[3:])-lo;lo[axis]=value-.01;sz[axis]=.02;lo[u]=u0;sz[u]=u1-u0;lo[v]=v0;sz[v]=v1-v0
    c=BRepAlgoAPI_Common(piece,box(*map(float,lo),*map(float,sz))).Shape();area,p=properties(c)
    if area>1e-8:cells.append(dict(area_mm2=area,centroid_mm=p))
 return dict(axis=axis,value_mm=value,area_mm2=sum(properties(c)[0] for c in pieces),cells=cells,cell_area_sum_mm2=sum(c['area_mm2'] for c in cells))

def wrench(p,f):return np.r_[f,np.cross(np.array(p)*.001,f)]
def statics(patches,external,mode):
 cols=[];meta=[]
 for name,patch in patches.items():
  if mode=='no_key' and name.startswith('key'):continue
  if mode=='no_bolts' and name.startswith('head'):continue
  for cell in patch['cells']:
   cols.append(wrench(cell['centroid_mm'],patch['normal_on_ground']))
   meta.append(dict(patch=name,centroid_mm=cell['centroid_mm'],area_mm2=cell['area_mm2'],normal_on_ground=patch['normal_on_ground']))
 A=np.array(cols).T;scale=np.array([1,1,1,100,100,100]);cost=np.ones(len(meta))
 r=linprog(cost,A_eq=scale[:,None]*A,b_eq=-scale*external,bounds=(0,None),method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
 row=dict(mode=mode,success=bool(r.success),solver_status=int(r.status),message=r.message)
 if r.success:
  active=[dict(m,normal_force_N=float(c),pressure_MPa=float(c/m['area_mm2'])) for m,c in zip(meta,r.x) if c>1e-12];res=A@r.x+external
  row.update(applied_wrench_N_Nm=external.tolist(),reaction_wrench_N_Nm=(A@r.x).tolist(),force_residual_N=float(np.linalg.norm(res[:3])),moment_residual_Nm=float(np.linalg.norm(res[3:])),minimum_total_reaction_objective_N=float(r.fun),bolt_axial_total_N=float(sum(x['normal_force_N'] for x in active if x['patch'].startswith('head'))),key_total_compression_N=float(sum(x['normal_force_N'] for x in active if x['patch'].startswith('key'))),active_uniform_tractions=active)
 return row

def main():
 tag=sys.argv[1];out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists()
 src=ROOT/'cad/exports/primaryP1_fixture15/summary.json';cad=json.loads(src.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values())
 s={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(v) for n,v in s.items()}
 dump(out/'inputs.json',dict(candidate=ref(src),producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/mechanisms_stage1.py'),ref(ROOT/'scripts/baseline_registry.py')],load_source=ref(ROOT/'validation/transmission/primaryP1_contact_transfer3/summary.json'),criteria=dict(intersection_mm3_max=1e-8,force_residual_N_max=1e-8,moment_residual_Nm_max=1e-10,mesh_relative_max=.01),scope='Actual nominal fixture; finite assembly samples and rigid necessary frictionless traction equilibrium. No FEM/contact uniqueness/preload/threads/source allowables or laboratory anchorage certificate.'))
 valid={n:bool(BRepCheck_Analyzer(q).IsValid() and solid_count(q)==1) for n,q in s.items()}
 # Reimported aggregate solid inventory matched by volume/centroid, not count only.
 ag=read(REPO/cad['assembly']['path']);it=TopExp_Explorer(ag,TopAbs_SOLID);actual=[]
 while it.More():
  vol,p=properties(it.Current(),False);actual.append([vol]+p);it.Next()
 expected=[]
 for q in s.values():v,p=properties(q,False);expected.append([v]+p)
 A=np.array(actual);E=np.array(expected);D=np.max(abs(A[:,None,:]-E[None,:,:])/(1e-7+1e-8*abs(E[None,:,:])),axis=2);ii,jj=linear_sum_assignment(D);identity=len(A)==len(E) and bool(np.max(D[ii,jj])<=1)
 final=[];pairs=0
 for n,m in itertools.combinations(s,2):
  if overlap(bb[n],bb[m]):
   pairs+=1;v=common(s[m],s[n])
   if v>1e-8:final.append(dict(a=n,b=m,common_mm3=v))
 # Attach completed P1 to base last. Bolt upward from below, nut downward from above.
 fixed=[n for n in s if n!='TEST_BASE' and not n.startswith('FIXTURE_')];rows=[];comparisons=0
 stages=[('base_vertical','TEST_BASE',[80,30,12,6,3,1,.2,0])]
 stages += [('bolt_from_below',n,[-80,-40,-20,-6,-1,0]) for n in s if n.startswith('FIXTURE_BOLT')]
 stages += [('nut_from_above',n,[30,12,6,1,0]) for n in s if n.startswith('FIXTURE_NUT')]
 for stage,n,poses in stages:
  for dz in poses:
   assert not(ROOT/'runtime/STOP').exists();q=translate(s[n],0,0,dz);hits=[]
   for m in fixed:
    if overlap(bounds(q),bb[m]):
     comparisons+=1;v=common(q,s[m])
     if v>1e-8:hits.append(dict(part=m,common_mm3=v))
   rows.append(dict(stage=stage,part=n,dz_mm=dz,hits=hits))
  fixed.append(n)
 tools=[]
 for j,(x,y) in enumerate([(-44,-30),(-44,10),(86,-30),(86,10)]):
  driver=hex_axis((x,y,0),(0,0,1),4,37.5)
  socket=cut(cyl(6,(x,y,66),35),hex_axis((x,y,65.99),(0,0,1),8.1,5),cyl(2.8,(x,y,70.8),30.3))
  for name,q,exclude in [('driver',driver,{f'FIXTURE_BOLT_{j}'}),('nut_socket',socket,{f'FIXTURE_NUT_{j}'})]:
   hits=[]
   for m in s:
    if m in exclude:continue
    if overlap(bounds(q),bb[m]):
     v=common(q,s[m])
     if v>1e-8:hits.append(dict(part=m,common_mm3=v))
   tools.append(dict(tool=name,station=j,hits=hits))
 # Base retains original RF holes and main drive service aperture.
 for y in (-16,16):
  q=cyl(1.5,(64,y,0),100);hits=[]
  for n in s:
   if n.startswith(('F0_RF','GROUND_BOLT','GROUND_NUT')):continue
   if overlap(bounds(q),bb[n]):
    v=common(q,s[n])
    if v>1e-8:hits.append(dict(part=n,common_mm3=v))
  tools.append(dict(tool='RF_driver',station=y,hits=hits))
 dump(out/'assembly.json',dict(rows=rows,tools=tools,comparisons=comparisons,order='Completed original P1 -> lower base from above -> raise four separate bolts -> lower nuts -> driver/socket tightening access. Thread rotation and continuous sweep unqualified.'))
 # Extract changed physical faces only; do not repeat old LP mesh trials.
 patches={}
 for name,axis,value in [('seat',2,46),('key_x_minus',0,-48),('key_x_plus',0,-40),('key_y_minus',1,-6),('key_y_plus',1,6)]:patches[name]=face_patches(s['GROUND_PLATE'],s['TEST_BASE'],axis,value,1)
 bearing=[]
 for j in range(4):bearing.append(dict(station=j,head=face_patches(s['GROUND_PLATE'],s[f'FIXTURE_BOLT_{j}'],2,40,1),nut=face_patches(s['TEST_BASE'],s[f'FIXTURE_NUT_{j}'],2,66,1)))
 checks=dict(all78single_valid=all(valid.values()),aggregate78identity=identity,final_interference_clear=not final,fixture_sampled_assembly_clear=all(not r['hits'] for r in rows),tools_clear=all(not r['hits'] for r in tools),finite_key_x24mm2=all(abs(patches[k]['area_mm2']-24)<1e-6 for k in ('key_x_minus','key_x_plus')),finite_key_y14_4mm2=all(abs(patches[k]['area_mm2']-14.4)<1e-6 for k in ('key_y_minus','key_y_plus')),fourfinitebearings=all(p['head']['area_mm2']>1 and p['nut']['area_mm2']>1 for p in bearing))
 dump(out/'patches.json',patches);r=dict(status='ACTUAL_P1_FILLETED_KEY_FIXTURE_ASSEMBLY_PASS' if all(checks.values()) else 'ACTUAL_P1_FILLETED_KEY_FIXTURE_ASSEMBLY_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),checks=checks,parts=len(s),final_exact_pairs=pairs,final_interferences=final,assembly=ref(out/'assembly.json'),patches=ref(out/'patches.json'),bearing=bearing,samples=len(rows),comparisons=comparisons,tools=len(tools),whole_system_release=False,newly_qualified_system_gate_ids=[],limitations=['Actual reimported78part inventory/nominal intersection/52sample fixture order/10tools only; no continuous CCD/tolerance or thread tightening','R0.5keyroot and0.6chamfer reduce finite contact area; actual compliance is separate evidence,not LP restatement','Material/process/source minima,local bearing/thread/preload,real physical Baseanchor/full3Finger/energy remain blocked'])
 dump(out/'summary.json',r);print(json.dumps(dict(status=r['status'],checks=checks,keyareas={k:v['area_mm2'] for k,v in patches.items()})));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
