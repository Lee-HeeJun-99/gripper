"""Independent actual P1 retention footprints, ordered fastener/tool insertion and weight."""
import sys,json,shutil,math
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,translate,common,bounds,overlap,volume,export,solid_count
from mechanisms_stage1 import hex_axis
from primary_motor_bearing_wrenches import patches,gravity
from OCP.BRepCheck import BRepCheck_Analyzer

def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py');assert not(ROOT/'runtime/STOP').exists()
 src=ROOT/'cad/exports/primaryP1_retention20/summary.json';oldsrc=ROOT/'cad/exports/primaryP1_framekey19/summary.json';cad=json.loads(src.read_text());old=json.loads(oldsrc.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());s={n:read(REPO/r['path']) for n,r in refs.items()};bb={n:bounds(q) for n,q in s.items()};rows=[];hits=[];comparisons=0
 def check(q,fixed):
  nonlocal comparisons
  local=[]
  for m in fixed:
   if overlap(bounds(q),bb[m]):
    comparisons+=1;v=common(s[m],q)
    if v>1e-8:local.append(dict(part=m,common_mm3=v))
  return local
 # Assemble Frame+Ground FIRST, before Finger,Drive and before TEST_BASE.
 fixed=['OPEN_FRAME','GROUND_PLATE'];stages=[];toolrows=[];delta=np.zeros(6);allareas=[]
 for i,(x,y) in enumerate([(-25,-28),(-25,14),(60,-28),(60,0)]):
  bn=f'GROUND_BOLT_{i}';nn=f'GROUND_NUT_{i}';b=s[bn];nut=s[nn]
  for n,sign in [(bn,-1),(nn,1)]:
   for d in (80,30,12,6,3,1,0):
    q=translate(s[n],0,0,sign*d);local=check(q,fixed);stages.append(dict(part=n,translation_mm=[0,0,sign*d],hits=local));hits+=local
   fixed.append(n)
  A=[];ds=[]
  for n,m,z,sgn,label in [(bn,'OPEN_FRAME',34,1,'head'),(nn,'GROUND_PLATE',46,-1,'nut')]:
   cells=patches(s[n],s[m],2,z,[0,0,sgn],label);area=sum(c['area_mm2'] for c in cells);A.append(area);vals=[common(translate(s[n],0,0,sgn*h),s[m])/h for h in (.001,.002)];ds.append(dict(label=label,area_mm2=area,overlap_derivatives_mm2=vals,relative_error=abs((2*vals[0]-vals[1])/area-1)))
  # Independent analytic area: intact hex8AF minus actual5.5dia plate hole; bolt head8.5dia.
  analytic=[math.pi*(4.25**2-2.75**2),math.sqrt(3)/2*8**2-math.pi*2.75**2]
  oldarea=sum(c['area_mm2'] for c in patches(read(REPO/old['part_references'][nn]['path']),s['GROUND_PLATE'],2,46,[0,0,-1],'oldnut'))
  oldbolt=read(REPO/old['part_references'][bn]['path']);oldnut=read(REPO/old['part_references'][nn]['path']);dg=gravity(b,7900)+gravity(nut,7900)-gravity(oldbolt,7900)-gravity(oldnut,7900);delta+=dg
  # Tool envelope:19mm wide/130long/4.2thick conservative straight corridor,
  #8.1AF ring opening. Dimensions from Bahco111M8,exact jaw/offsetCAD not provided.
  # Held stationary; rotate bolt with4AF driver before Finger is inserted.
  z=46.25;head=cyl(9.5,(x,y,z),4.2);handle=box(x,y-9.5,z,120.5,19,4.2);tool=fuse(head,handle)
  # Tool handle points outboard: -X for left pair,+X for right pair.
  from primary_module_design import tr
  angle=(math.pi/2 if i==1 else math.pi if x<0 else 0.);R=np.array([[math.cos(angle),-math.sin(angle),0],[math.sin(angle),math.cos(angle),0],[0,0,1.]])
  center=np.array([x,y,0.]);tool=tr(tool,R,center-R@center);tool=cut(tool,hex_axis((x,y,z-.01),(0,0,1),8.1,4.22))
  export(tool,out/('nut_hold_envelope_'+str(i)))
  localrows=[]
  for dz in (80,30,12,6,3,1,0):
   q=translate(tool,0,0,dz);local=check(q,fixed);localrows.append(dict(dz_mm=dz,hits=local));hits+=local
  toolrows.append(dict(station=i,tool='conditional19wide130long4.2thicknut_hold',poses=localrows))
  # L-key:29mmshortleg,74mmlongleg. Lateralapproachat3mmbelowsocket,
  # then3mmupwardengagement. LongstraightverticalbitwouldhitRootshelf.
  # Nominal geometric designenvelope only; Bahco1995M4dimensions,exactbendnotprovided.
  driver=fuse(hex_axis((x,y,2.4),(0,0,1),3.98,29),hex_axis((x-74,y,4.39),(1,0,0),3.98,74))
  export(driver,out/('driver_envelope_'+str(i)))
  localrows=[]
  shifts=[[-d,0,-3] for d in (160,80,40,20,10,3,1,0)]+[[0,0,d] for d in (-2,-1,0)]
  for shift in shifts:
   q=translate(driver,*shift);local=check(q,fixed);localrows.append(dict(translation_mm=shift,hits=local));hits+=local
  toolrows.append(dict(station=i,tool='conditional3.98AF_Lkey29short74long2.4engagement',poses=localrows))
  rows.append(dict(station=i,center_mm=[x,y],bolt_bounds_mm=bb[bn],nut_bounds_mm=bb[nn],grip_mm=12,tip_projection_mm=bb[bn][5]-bb[nn][5],projection_pitches=(bb[bn][5]-bb[nn][5])/.8,nominal_nut_height_mm=4.7,effective_thread_engagement_mm=None,full_thread_envelope_covers_nut=True,footprints_mm2=A,analytic_mm2=analytic,analytic_relative_error=max(abs(a/b-1) for a,b in zip(A,analytic)),derivatives=ds,old_nut_footprint_mm2=oldarea,geometry_mass_delta_kg=float(-dg[2]/9.80665),new_minor_core_diameter_mm=5-1.226869*.8,new_axial_compliance_length_mm=12+4.7/2,new_conditional_k_N_mm=200000*math.pi*(5-1.226869*.8)**2/4/(12+4.7/2),capacity_qualified=False))
 oldmass=json.loads((ROOT/'validation/integrated/primaryP1_framekey_witness2/summary.json').read_text());newmass=oldmass['conditional_mass_kg']-delta[2]/9.80665;newW=np.array(oldmass['updated_required_Base_wrench_N_Nm'])-delta
 checksd=dict(actual8hardware_single_valid=all(solid_count(s[n])==1 and BRepCheck_Analyzer(s[n]).IsValid() for n in refs if n.startswith(('GROUND_BOLT','GROUND_NUT'))),other70STEPrefs_unchanged=sum(refs[n]==old['part_references'][n] for n in refs)==70,positive_nominal_projection=all(r['tip_projection_mm']>0 for r in rows),footprint_analytic=max(r['analytic_relative_error'] for r in rows)<1e-6,independent_overlap_derivatives=max(d['relative_error'] for r in rows for d in r['derivatives'])<1e-6,ordered_sampled_hardware_and_tools_clear=not hits)
 dump(out/'inputs.json',dict(candidate=ref(src),parent=ref(oldsrc),source=ref(ROOT/'models/standard_drive/primary_retention_sources2/reviewed.json'),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/primary_motor_bearing_wrenches.py'),ref(S1/'scripts/incremental_stage1.py'),ref(S1/'scripts/mechanisms_stage1.py')],criteria=dict(intersection_mm3=1e-8,relative_area=1e-6),order='FrameintoGround->fourGroundbolt/nutpairs tightened beforeFinger/Drive andbeforeTestBase->Basefixture->Finger/Drive/Cap. ToolswithdrawbeforeBaseassembly.',scope='Nominal discrete poses and statedconditionaltoolenvelopes,NOTCCD/exactmanufacturerCAD/threadhelicalassembly/preload/torquecertificate.'))
 result=dict(status='ACTUAL_P1_INTERNAL_RETENTION_BOUNDED_WITNESS_PASS' if all(checksd.values()) else 'ACTUAL_P1_INTERNAL_RETENTION_WITNESS_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),inputs=ref(out/'inputs.json'),checks={k:bool(v) for k,v in checksd.items()},stations=rows,assembly_poses=stages,tool_poses=toolrows,hits=hits,exact_comparisons=comparisons,hardware_gravity_delta_N_Nm=delta.tolist(),conditional_mass_kg=float(newmass),required_external_Base_wrench_N_Nm=newW.tolist(),newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Smooth major thread envelopes +nominalprojection do NOT establish effectiveengagement/flankcapacity/preload/locking. A2boltclass/certificatelessA4nutpair notqualified.','Source dimension toolcorridors areconditional; exactjaw/offset/handle/rotation/physicalassembly notqualified. Toolheldwhileboltrotates; no fullnutrotation claimed.','Existing74040DOFresult belongs19; newnutfootprint/corelength14.35 instead14 invalidate directstress/reactiontransfer. Sourceallowables/mesh/time/globalenergy remainblocked.','Conditional7900kg/m3 hardwaredensity; sourcebolt4.01g/unit is informational and not substitutedforCADmass certificate. Weightupdate is exactgeometrycontrast,not totalmassverification.'])
 dump(out/'summary.json',result);print(dict(status=result['status'],checks=result['checks'],mass=newmass,required_base_wrench=newW.tolist(),hits=hits));raise SystemExit(0 if all(checksd.values()) else 2)
if __name__=='__main__':main()
