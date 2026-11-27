"""Actual83part P1 anchor: ordered assembly and necessary wrench transfer.
Uniform finite-face pressures and axial connectors are conditional witnesses,
not elastic contact, thread strength, installed preload, or bench fixation.
"""
import sys,json,shutil
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,translate,common,bounds,overlap,solid_count,volume
from primary_motor_bearing_wrenches import faces
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.BRepCheck import BRepCheck_Analyzer

def props(s,surface=False):
 g=GProp_GProps()
 (BRepGProp.SurfaceProperties_s if surface else BRepGProp.VolumeProperties_s)(s,g)
 p=g.CentreOfMass();return g.Mass(),np.array([p.X(),p.Y(),p.Z()])
def wrench(p,f):return np.r_[f,np.cross(np.array(p)*.001,f)]
def patch(a,b,ax,v,d,label,n):
 cells=[];other=[i for i in range(3) if i!=ax]
 for f in faces(a,ax,v):
  for g in faces(b,ax,v):
   s=BRepAlgoAPI_Common(f,g).Shape();area,_=props(s,True)
   if area<1e-8:continue
   bb=bounds(s);grids=[np.linspace(bb[k],bb[k+3],n+1) for k in other]
   for lo,hi in zip(grids[0][:-1],grids[0][1:]):
    for l2,h2 in zip(grids[1][:-1],grids[1][1:]):
     p=np.array(bb[:3]);sz=np.array(bb[3:])-p;p[ax]-=.01;sz[ax]=.02;p[other[0]]=lo;sz[other[0]]=hi-lo;p[other[1]]=l2;sz[other[1]]=h2-l2
     cell=BRepAlgoAPI_Common(s,box(*map(float,p),*map(float,sz))).Shape();ar,c=props(cell,True)
     if ar>1e-8:cells.append(dict(label=label,point_mm=c.tolist(),area_mm2=ar,direction=d))
 return cells
def solve(cells,connectors,W):
 meta=cells+connectors;A=np.array([wrench(r['point_mm'],r['direction']) for r in meta]).T
 ar=np.array([r['area_mm2'] for r in meta]);scale=np.array([1,1,1,100,100,100]);eq=np.c_[A*scale[:,None],np.zeros(6)];ub=np.c_[np.eye(len(meta)),-ar]
 r=linprog(np.r_[np.zeros(len(meta)),1.],A_eq=eq,b_eq=-W*scale,A_ub=ub,b_ub=np.zeros(len(meta)),bounds=(0,None),method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})
 row=dict(success=bool(r.success),solver_status=int(r.status),solver_message=r.message,external_wrench_N_Nm=W.tolist())
 if r.success:
  vals=r.x[:-1];res=A@vals+W;rays=[dict(m,force_N=float(v),pressure_MPa=float(v/m['area_mm2'])) for m,v in zip(meta,vals) if v>1e-12]
  row.update(minimax_uniform_patch_pressure_MPa=float(r.x[-1]),force_residual_N=float(np.max(abs(res[:3]))),moment_residual_Nm=float(np.max(abs(res[3:]))),rays=rays)
 return row
def main():
 tag=sys.argv[1];out=ROOT/'validation/integrated'/tag;out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists()
 cp=ROOT/'cad/exports/primaryP1_anchor36/summary.json';cad=json.loads(cp.read_text());refs=cad['part_references'];s={n:read(REPO/r['path']) for n,r in refs.items()};base=s['TEST_BASE'];rail=s['BENCH_ANCHOR_RAIL'];old=json.loads((ROOT/'cad/exports/primaryP1_ycapture24/summary.json').read_text())
 assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());mass=[]
 for n,shape in s.items():
  V,c=props(shape);rho=1400 if n=='F0_SKIN' else 2700 if n in ('OPEN_FRAME','MOTOR_CAP','TEST_BASE','F0_SPOOL','F0_DRUM_NIPPLE_CAP','BENCH_ANCHOR_RAIL') else 7900
  m=.0095 if n=='F0_MICRO_MOTOR' else .0028 if n=='F0_STOCK_HUB' else V*1e-9*rho
  mass.append(dict(part_ID=n,STEP=refs[n],volume_mm3=V,centroid_mm=c.tolist(),conditional_density_kg_m3=None if n in ('F0_MICRO_MOTOR','F0_STOCK_HUB') else rho,mass_kg=m,gravity_wrench_N_Nm=wrench(c,[0,0,-9.80665*m]).tolist()))
 loadp=ROOT/'validation/transmission/primaryP1_gravity_cat_demand_ports2/summary.json';l=json.loads(loadp.read_text())['rows'][0]
 contact=np.array(l['full_product_external_wrench_about_origin_N_Nm'])-np.array(l['deformed_gravity_wrench_N_Nm'])
 total=sum((np.array(r['gravity_wrench_N_Nm']) for r in mass),np.zeros(6));up=sum((np.array(r['gravity_wrench_N_Nm']) for r in mass if r['part_ID']!='BENCH_ANCHOR_RAIL'),np.zeros(6));W=up+contact
 # Only new upper joint tested: upstream Root/Finger/clamps remain unqualified.
 # Whole83part CAD nominal gravity is fresh. Contact-only historical resultant
 # is explicitly frozen; this is NOT a re-solved100g operating equilibrium.
 connectors=[];bearings=[]
 for i,x in enumerate((-44,86)):
  h=patch(base,s[f'ANCHOR_BOLT_{i}'],2,60,[0,0,1],f'head{i}',1);nut=patch(rail,s[f'ANCHOR_NUT_{i}'],2,74,[0,0,-1],f'nut{i}',1)
  ah=sum(r['area_mm2'] for r in h);an=sum(r['area_mm2'] for r in nut);bearings.append(dict(station=i,head_area_mm2=ah,nut_area_mm2=an))
  connectors.append(dict(label=f'bolt{i}',point_mm=[x,34,60],direction=[0,0,1],area_mm2=min(ah,an),head_area_mm2=ah,nut_area_mm2=an,thread_flank_implemented=False))
 definitions=[(2,66,[0,0,-1],'topseat'),(0,-50,[-1,0,0],'key0_xmin'),(0,-38,[1,0,0],'key0_xmax'),(1,28,[0,-1,0],'key_ymin'),(1,40,[0,1,0],'key_ymax')]
 levels=[];patchsets={};witnesses={}
 loads={'conditional_frozen_contact_plus_nominal_gravity':W,'nominal_upstream_gravity_only':up}
 for k in range(6):
  for sign in (-1,1):
   w=np.zeros(6);w[k]=sign*(1 if k<3 else .001);loads[f'sensitivity_{k}_{sign}']=w
 for n in (2,4,8):
  assert not(ROOT/'runtime/STOP').exists();cells=[]
  for ax,v,d,label in definitions:cells+=patch(base,rail,ax,v,d,label,n)
  patchsets[str(n)]=cells;sol={name:solve(cells,connectors,w) for name,w in loads.items()};witnesses[str(n)]=sol
  levels.append(dict(divisions=n,cells=len(cells),areas_mm2={label:sum(c['area_mm2'] for c in cells if c['label']==label) for *_,label in definitions},solutions={name:{k:v for k,v in row.items() if k!='rays'} for name,row in sol.items()}))
 fine=patchsets['8'];withoutkey=solve([r for r in fine if r['label']=='topseat'],connectors,loads['sensitivity_0_1']);withoutbolts=solve(fine,[],loads['nominal_upstream_gravity_only'])
 # Physical clearance counterexample: enlarge the key pocket, don't silently
 # apply nominal contact pressures at open gaps. Never written over old CAD.
 gaprail=rail
 for i,x in enumerate((-44,86)):
  half=6 if i==0 else 6.2;gaprail=cut(gaprail,box(x-half-.02,27.98,65.9,2*half+.04,12.04,3.3))
 gapcells=[]
 for ax,v,d,label in definitions:gapcells+=patch(base,gaprail,ax,v,d,label,2)
 gapcase=solve(gapcells,connectors,loads['sensitivity_0_1'])
 # Finite part assembly poses, full old primary retained. No collision inferred
 # from output code: exact BRep common is inspected at every recorded pose.
 assembly=[]
 def hits(shape,others):
  b=bounds(shape);return [dict(part_ID=n,common_mm3=v) for n in others if overlap(b,bounds(s[n])) and (v:=common(shape,s[n]))>1e-8]
 fixed=[n for n in s if n!='BENCH_ANCHOR_RAIL' and not n.startswith('ANCHOR_')]
 for dz in (25,10,3.2,1,.2,0):assembly.append(dict(stage='rail_lowering',dz_mm=dz,interferences=hits(translate(rail,0,0,dz),fixed)))
 for i in range(2):
  for dz in (-25,-10,-2,0):assembly.append(dict(stage=f'bolt{i}_up',dz_mm=dz,interferences=hits(translate(s[f'ANCHOR_BOLT_{i}'],0,0,dz),fixed+['BENCH_ANCHOR_RAIL'])))
  for dz in (25,10,2,0):assembly.append(dict(stage=f'nut{i}_down',dz_mm=dz,interferences=hits(translate(s[f'ANCHOR_NUT_{i}'],0,0,dz),fixed+['BENCH_ANCHOR_RAIL'])))
 tools=[]
 for i,x in enumerate((-44,86)):
  for label,shape in [('4AF_driver_enclosure',cyl(2.5,(x,34,20),37.5)),('8AF_openhead_enclosure',cyl(9.5,(x,34,74),4.7))]:
   tools.append(dict(station=i,tool=label,interferences=hits(shape,[n for n in s if n not in (f'ANCHOR_BOLT_{i}',f'ANCHOR_NUT_{i}')]),scope='Conservative axisymmetric bounding corridor,not exact jaw/handle/torque or swept threaded engagement. Existing reviewed Bahco19mm width/4.2mm thickness;4.7mm thickness encloses it.'))
 # Positive roof clearance checked by overlap after lifting key into roof.
 roof=[dict(dz_mm=dz,common_mm3=common(translate(base,0,0,dz),rail)) for dz in (0,.19,.21)]
 mesh=[]
 for a,b in zip(levels,levels[1:]):
  changes={name:abs(b['solutions'][name]['minimax_uniform_patch_pressure_MPa']/a['solutions'][name]['minimax_uniform_patch_pressure_MPa']-1) for name in loads if a['solutions'][name]['success'] and b['solutions'][name]['success']}
  mesh.append(dict(divisions=[a['divisions'],b['divisions']],relative_pressure_bound_changes=changes,original1percent=all(v<.01 for v in changes.values())))
 checks=dict(all83STEP_hashes=True,all83valid_single=all(BRepCheck_Analyzer(x).IsValid() and solid_count(x)==1 for x in s.values()),aggregate83solids=solid_count(read(REPO/cad['assembly']['path']))==83,unchanged77_original_refs=sum(refs.get(n)==r for n,r in old['part_references'].items())==77,actual_BOM_matches={r['part_ID']:r['STEP'] for r in json.loads((REPO/cad['BOM']['path']).read_text())['parts']}==refs,assembly_sample_poses_clear=all(not r['interferences'] for r in assembly),tool_enclosures_clear=all(not r['interferences'] for r in tools),all14cases_all3patchlevels_feasible=all(r['success'] for level in witnesses.values() for r in level.values()),force_original1e_minus8=all(r.get('force_residual_N',1)<1e-8 for level in witnesses.values() for r in level.values()),moment_original1e_minus10=all(r.get('moment_residual_Nm',1)<1e-10 for level in witnesses.values() for r in level.values()),key_omission_rejected=not withoutkey['success'],bolt_omission_rejected=not withoutbolts['success'],open_gap_key_pressure_rejected=not gapcase['success'],roof_gap_counterexample_detected=roof[1]['common_mm3']<1e-8 and roof[2]['common_mm3']>1e-8)
 dump(out/'patches.json',dict(levels=patchsets,connectors=connectors));dump(out/'tractions.json',witnesses);dump(out/'mass.json',dict(parts=mass,total_mass_kg=sum(r['mass_kg'] for r in mass),total_gravity_wrench_N_Nm=total.tolist(),upstream_gravity_wrench_N_Nm=up.tolist(),conditional_frozen_contact_wrench_N_Nm=contact.tolist(),required_external_rail_wrench_N_Nm=(-(total+contact)).tolist()))
 dump(out/'inputs.json',dict(candidate=ref(cp),load_source=ref(loadp),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/primary_motor_bearing_wrenches.py'),ref(S1/'scripts/incremental_stage1.py')],criteria=dict(force_N=1e-8,moment_Nm=1e-10,mesh_relative=.01),conditional_density_scope='Reuses primary_full_mass_v2 densities and manufacturer nominal motor/hub masses;not material or mass minimum. Nominal CAD centroids,no deformed-body update.',standard_sources=ref(ROOT/'models/standard_drive/primary_retention_sources2/reviewed.json')))
 dump(out/'summary.json',dict(status='ACTUAL_P1_ANCHOR_CONDITIONAL_RIGID_WITNESS_COMPLETE' if all(checks.values()) else 'ACTUAL_P1_ANCHOR_VALIDATION_FAIL',candidate=ref(cp),inputs=ref(out/'inputs.json'),checks=checks,actual_parts=83,actual_changed_parts=6,conditional_mass_kg=sum(r['mass_kg'] for r in mass),bearings=bearings,levels=levels,mesh_contrasts=mesh,assembly=assembly,tool_access=tools,roof_clearance_controls=roof,negative_controls=dict(without_keys=withoutkey,without_axial_connectors=withoutbolts,actual_02mm_gap=gapcase),patches=ref(out/'patches.json'),tractions=ref(out/'tractions.json'),mass=ref(out/'mass.json'),accepted_elastic_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,hardware='NOT_MEASURED',limitations=['Actual whole assembly and actual newfinite faces,not a coupon. Necessary positive uniform patch pressure witness plus axial connector;NOT real elastic distribution/preload/threadflank/installed anchorage or strength.','Historical100g contact-only resultant is frozen;new nominal CAD gravity recomputed. No new coupled100g Finger/support/sourcefield equilibrium. Unit1N and1Nmm sixmode sensitivities are NOT sixDOF grasp closure or product rated loads.','Minimax uniform-patch pressure mesh convergence is ONLY LP discretization,not elastic/contact/Beam mesh1percent qualification.','Nominal exact key fit is not toleranced. Explicit0.02mm gap removes shear at unchangedpose. Roof clearance0.2mm and reliefs are nominal.','Finite83part primary now ends at BENCH_ANCHOR_RAIL;external rail-to-bench attachment/material/preload/finite support remain UNQUALIFIED. No hidden fixedDOFs.','All prior78part/sourcefield and mesh/time/globalenergy failures preserved. No fullsame-revision3Finger release. Assembly checks sampled finite poses and enclosing local tool corridors,not complete continuous threaded/process certification.']))
 print(json.dumps(dict(checks=checks,levels=levels,mesh_contrasts=mesh,roof=roof)));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
