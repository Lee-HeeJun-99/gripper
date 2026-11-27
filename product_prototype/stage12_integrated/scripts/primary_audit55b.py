"""Independent sameP1 final77part physical geometry audit.
Exact volume provenance and continuous clearance of ONLY newlyadded webs;
full oldbody trajectories remain finite sampled elsewhere.
"""
import json,sys,shutil,math,os,time
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,bounds,volume,common,solid_count,translate,overlap,canonical
from OCP.BRepCheck import BRepCheck_Analyzer
from primary_anchor_contact38 import common_faces,surface_moment
out=ROOT/'validation/integrated/primaryP1_audit55b';out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_integral55c/summary.json';cad=json.loads(cp.read_text());oldp=REPO/cad['parent']['path'];old=json.loads(oldp.read_text());refs=cad['part_references'];assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*refs.values(),cad['assembly'],cad['BOM']]);parts={n:read(REPO/r['path']) for n,r in refs.items()};s=parts['BENCH_SUPPORT'];constituents=['BENCH_SUPPORT','BENCH_ANCHOR_RAIL','TEST_BASE','GROUND_PLATE','OPEN_FRAME'];base=read(REPO/old['part_references'][constituents[0]]['path']);contain=[]
def journal(row):
 with (out/'journal.jsonl').open('a') as f:f.write(json.dumps(row)+'\n');f.flush();os.fsync(f.fileno())
for n in constituents:
 assert not(ROOT/'runtime/STOP').exists();a=read(REPO/old['part_references'][n]['path']);av=volume(a);journal(dict(state='START',operation='exact_parent_material_containment',part=n));cv=common(s,a);remainder=cut(a,s);remain_solid=solid_count(remainder);remain_vol=volume(remainder);contain.append(dict(part=n,parent_volume_mm3=av,retained_common_volume_mm3=cv,lost_volume_mm3=av-cv,actual_parent_minus_new_solids=remain_solid,actual_parent_minus_new_volume_mm3=remain_vol));journal(dict(state='COMPLETE',**contain[-1]))
 if n!=constituents[0]:base=fuse(base,a)
base=canonical(base);added=cut(s,base);addedV=volume(added);webs=[];sections=[];covered=0
for x,y in [(-59,-58),(101,-58),(-59,39),(101,39)]:
 x0,x1=(x-7,x+4.8) if x<0 else (x-4.8,x+7);web=cut(box(x0,y-5,60,x1-x0,10,14),cyl(2.75,(x,y,59),16));v=common(added,web);covered+=v;webs.append(dict(center_xy_mm=[x,y],bounds_mm=bounds(web),added_volume_mm3=v));slab=box(x0,y-5,67.9995,x1-x0,10,.001);area=common(s,slab)/.001;sections.append(dict(center_mm=[x,y,68],exact_bounded_section_area_mm2=area,minimum_added_annular_rectangle_area_mm2=118-math.pi*2.75**2,minimum_nominal_bore_ligament_mm=2.05))
# All candidate assembly stages taken from freshlyexecuted77part verifier.
pd=ROOT/'validation/integrated/primaryP1_product55/summary.json';product=json.loads(pd.read_text());assert product['candidate']==ref(cp);ad=REPO/product['assembly']['path'];assembly=json.loads(ad.read_text());continuous=[]
for stage,ids in [('finger_lift_slide_lower',assembly['partition']['finger']),('drive_vertical',assembly['partition']['drive']),('cap_vertical',['MOTOR_CAP'])]:
 shifts=np.array([r['shift_mm'] for r in assembly['stages'] if r['stage']==stage]);low=np.min([np.array(bounds(parts[n]))[:3] for n in ids],axis=0)+shifts.min(0);high=np.max([np.array(bounds(parts[n]))[3:] for n in ids],axis=0)+shifts.max(0);swept=np.r_[low,high];clear=[]
 for w in webs:
  b=np.array(w['bounds_mm']);sep=np.maximum(low-b[3:],b[:3]-high);axis=int(np.argmax(sep));clear.append(dict(web_xy_mm=w['center_xy_mm'],separating_axis=axis,continuous_interval_clearance_mm=float(sep[axis]),clear=bool(sep[axis]>1e-8)))
 continuous.append(dict(stage=stage,moving_actual_part_IDs=ids,full_piecewise_linear_translation_AABB_mm=swept.tolist(),newweb_clearances=clear))
# Actual criticalinterface faces preserveRootseat/Motorlands/toolbores exactly.
interfaces=[]
for n,ax,value in [('F0_ROOT_BACK',2,-7),('F0_ROOT_BACK',0,68),('F0_MICRO_MOTOR',2,14),('F0_MICRO_MOTOR',0,-5),('F0_MICRO_MOTOR',0,5),('EXTERNAL_BENCH_PLATE',2,-130)]:
 a=parts[n];ff=common_faces(s,a,ax,value);area=sum(surface_moment(f)[0] for f in ff);parentn='BENCH_SUPPORT' if n=='EXTERNAL_BENCH_PLATE' else 'OPEN_FRAME';parent=read(REPO/old['part_references'][parentn]['path']);oldff=common_faces(parent,a,ax,value);oldarea=sum(surface_moment(f)[0] for f in oldff);interfaces.append(dict(part=n,axis=ax,value_mm=value,actual_interface_area_mm2=area,parent_interface_area_mm2=oldarea,area_difference_mm2=area-oldarea))
# Entire finalmodule lowers onto plate onlyafter build;eachmovingpart queried.
placed=[]
for dz in [20.,10.,5.,1.,.2,0.]:
 for n,a in parts.items():
  if n=='EXTERNAL_BENCH_PLATE' or n.startswith('BENCH_THROUGH_'):continue
  b=translate(a,0,0,dz)
  if not overlap(bounds(b),bounds(parts['EXTERNAL_BENCH_PLATE'])):continue
  journal(dict(state='START',operation='full_module_onto_host',part=n,dz_mm=dz));v=common(parts['EXTERNAL_BENCH_PLATE'],b);r=dict(state='COMPLETE',part=n,dz_mm=dz,intersection_mm3=v);placed.append(r);journal(r)
checks=dict(actual77parts=len(parts)==77,onecontinuousgroundsolid=solid_count(s)==1 and BRepCheck_Analyzer(s).IsValid(),all77partSTEPsvalidsingle=all(solid_count(a)==1 and BRepCheck_Analyzer(a).IsValid() for a in parts.values()),assembly77solids=solid_count(read(REPO/cad['assembly']['path']))==77,all76retainedSTEPhashes=sum(refs.get(n)==r for n,r in old['part_references'].items())==76,BOMexact={r['part_ID']:r['STEP'] for r in json.loads((REPO/cad['BOM']['path']).read_text())['parts']}==refs,all_original_ground_material_preserved=all(r['actual_parent_minus_new_solids']==0 and abs(r['actual_parent_minus_new_volume_mm3'])<1e-8 for r in contain),added_material_only_four_realwebs=abs(covered-addedV)<1e-5,positive_material_sections=all(r['exact_bounded_section_area_mm2']>=r['minimum_added_annular_rectangle_area_mm2']-1e-6 for r in sections),continuous_newweb_clearance_allthree_stages=all(c['clear'] for r in continuous for c in r['newweb_clearances']),critical_interface_faces_preserved=all(r['actual_interface_area_mm2']>0 and abs(r['area_difference_mm2'])<1e-7 for r in interfaces),fullmodule_hostapproach_finite_clear=all(abs(r['intersection_mm3'])<1e-8 for r in placed),fresh_actual_product_assembly=bool(product['checks']['sampled_ordered_assembly_clear']))
dump(out/'summary.json',dict(status='ACTUAL_P1_77PART_INTEGRAL_MATERIAL_AND_ADDEDWEB_CONTINUOUS_CLEARANCE_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_INTEGRAL_GEOMETRY_PROVENANCE_OR_CLEARANCE_FAIL',candidate=ref(cp),producer=ref(out/'producer.py'),parent=ref(oldp),journal=ref(out/'journal.jsonl'),fresh_product=ref(pd),checks={k:bool(v) for k,v in checks.items()},actual_parts=77,unchanged_part_STEP_count=76,parent_material_containment=contain,new_material_volume_mm3=addedV,covered_added_material_volume_mm3=covered,newwebs=webs,actual_sections=sections,continuous_newweb_clearance=continuous,actual_interfaces=interfaces,finite_wholemodule_host_approach=placed,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Continuousbound appliesONLYnewwebmaterials versus threepiecewise-linearassemblystages;originalbodyshapeCCD/fulltools/threads stillnotcertified','Finalsame-revision3Finger notbuilt;preservedattachmentgeometry/jamming/PETslide isdesignintent,not operatingperformance','Source-backedmotor/hub/throughparts retained;materialminimum/manufactureprocess/hostconstraints/operating/protectedpeak/mesh/time/globalenergy unqualified']))
print(json.dumps(dict(checks={k:bool(v) for k,v in checks.items()},added_volume_mm3=addedV,covered=covered,sections=sections,interfaces=interfaces)),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
