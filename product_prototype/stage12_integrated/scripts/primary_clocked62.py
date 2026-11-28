"""Same P1, individually clocked monolithic keeper plugs. Fit-to-measure proposal.
Angles are explicit design inputs, NOT measured installed setting or preload.
"""
import sys,json,math,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cut,fuse,canonical,export,bounds,common,overlap,volume,solid_count,translate
from build_stage1 import compound,rotate
from primary_captive59b import hexz
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def spin(s,x,y,a):return translate(rotate(translate(s,-x,-y,0),a),x,y,0)
def main():
 tag=sys.argv[1];out=ROOT/'cad/exports'/tag;out.mkdir();shutil.copyfile(__file__,out/'producer.py');cp=ROOT/'cad/exports/primaryP1_splitpin61g/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()};groups=json.loads((REPO/old['anchors']['path']).read_text())['groups'];angles=iter([17.,43.,11.,29.,37.,53.]);rows=[];settings=[]
 for g in groups:
  n=g['name'];keeper=parts[n]
  for y in g['ys']:
   a=next(angles);x=g['x'];z=g['headtop'];bn=next(n for n in parts if (n.startswith('F0_RF') and 'BOLT' in n if g['name'].startswith('ROOT') else n.startswith('MOTOR_CAP_BOLT')) and abs((bounds(parts[n])[0]+bounds(parts[n])[3])/2-x)<1e-6 and abs((bounds(parts[n])[1]+bounds(parts[n])[4])/2-y)<1e-6)
   # Remove only original projecting plug below continuous bridge, then replace
   # by independently clocked plug. Bridge/window/tongue/pin bore unchanged.
   keeper=cut(keeper,box(x-1.6,y-1.6,z-1.3,3.2,3.2,g['bridge_bottom_mm']-(z-1.3)))
   keeper=fuse(keeper,spin(hexz(x,y,z-1.25,2.4,g['bridge_bottom_mm']-z+1.55),x,y,a))
   parts[bn]=spin(parts[bn],x,y,a);export(parts[bn],out/bn);parts[bn]=read(out/(bn+'.step'));parent=refs[bn];refs[bn]=ref(out/(bn+'.step'));rows.append(dict(part_ID=bn,STEP=refs[bn],STL=ref(out/(bn+'.stl')),parent=parent,geometry_credit=False,change='Installed angular pose only; NOT a new standard fastener design',valid=bool(BRepCheck_Analyzer(parts[bn]).IsValid()),solids=solid_count(parts[bn])))
   settings.append(dict(bolt=bn,keeper=n,x=x,y=y,clock_angle_deg=a,axial_pose_change_mm=0,old_nearest_index_shift_mm=.5*min(a,60-a)/360,old_backoff_to_next_index_mm=.5*(60-a)/360,installed_preload_N=None,angle_input_is_measured=False))
  parts[n]=canonical(keeper);export(parts[n],out/n);parts[n]=read(out/(n+'.step'));parent=refs[n];refs[n]=ref(out/(n+'.step'));rows.append(dict(part_ID=n,STEP=refs[n],STL=ref(out/(n+'.stl')),parent=parent,geometry_credit=True,change='Two independently clocked integral hex plugs; original anchor/window/bridge retained',valid=bool(BRepCheck_Analyzer(parts[n]).IsValid()),solids=solid_count(parts[n]),volume_mm3=volume(parts[n])))
 bb={n:bounds(s) for n,s in parts.items()};queries=[]
 for n,m in itertools.combinations(parts,2):
  if not any(n==q['part_ID'] or m==q['part_ID'] for q in rows) or not overlap(bb[n],bb[m]):continue
  assert not(ROOT/'runtime/STOP').exists();queries.append(dict(pair=[n,m],intersection_mm3=common(parts[n],parts[m])))
 hits=[q for q in queries if q['intersection_mm3']>1e-8];w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
 bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=tag
 for q in bom['parts']:
  q['STEP']=refs[q['part_ID']]
  if any(q['part_ID']==r['part_ID'] and r['geometry_credit'] for r in rows):q['interface']='Custom monolithic keeper, individually clocked integral hex plugs. Measure final installed angles before machining; fit-to-measure manufacturing and strength UNQUALIFIED.'
 dump(out/'BOM.json',bom);dump(out/'setting_inputs.json',dict(settings=settings,source='Explicit synthetic design contrast, not hardware measurement',process='Set/preload six existing M3 fasteners; measure each angle and head height WITHOUT backing off; machine uniquely keyed keeper plugs at those angles; insert keeper then split pins. No automatic preload claim. Re-tightening requires remeasurement/replacement.',standard_parts='Same reviewed M3 fasteners and source-size proposed pins; custom keeper process not source-certified',failure_modes=['Measurement angular error exceeding hex clearance prevents insertion','Unknown actual installed head height may prevent1.25mm engagement','Manufacturing cutter radius/undercut/tool access and minimum ligament unresolved','No preload is measured or enforced by keeper; contact clearance retains free screw motion','Unique custom keeper not interchangeable after arbitrary bolt resetting']))
 d=dict(old);d.update(revision=tag,parent=ref(cp),producer=ref(out/'producer.py'),part_references=refs,part_bounds_mm=bb,changed=rows,unchanged_part_STEP_count=74,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),settings=ref(out/'setting_inputs.json'),interferences=hits,changed_pair_queries=queries,status='ACTUAL_P1_INDIVIDUALLY_CLOCKED_KEEPER_CLEAR_NOT_RELEASE' if not hits and all(q['valid'] and q['solids']==1 for q in rows) else 'ACTUAL_P1_CLOCKED_KEEPER_FAIL',design_change='Same83shape P1:3 real monolithic keepers have independently clocked plugs. Six bolt angular poses changed, zero new bolt-design credit. No bolt axial reset required by nominal keeper registration. Inputs are not measured preload/angles.',newly_qualified_system_gate_ids=[],capacity_qualified=False,whole_system_release=False)
 dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],hits=hits,changes=rows)));return 0 if not hits and all(q['valid'] and q['solids']==1 for q in rows) else 2
if __name__=='__main__':sys.exit(main())
