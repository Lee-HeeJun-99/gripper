"""Fresh actual P1 assembly identity and fixed Neumann-source geometry audit."""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,solid_count,volume,box
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from primary_motor_bearing_wrenches import faces

def moment(s):
 g=GProp_GProps();BRepGProp.SurfaceProperties_s(s,g);a=g.Mass();p=g.CentreOfMass();p=np.array([p.X(),p.Y(),p.Z()]);m=g.MatrixOfInertia();J=np.array([[m.Value(i+1,j+1) for j in range(3)] for i in range(3)]);return a,a*p,np.eye(3)*np.trace(J)/2-J+a*np.outer(p,p)
def main():
 out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'verifier.py');cp=ROOT/'cad/exports/primaryP1_anchor36b/summary.json';cad=json.loads(cp.read_text());parts={n:read(REPO/r['path']) for n,r in cad['part_references'].items()};identities=[dict(part_ID=n,hash_matches=sha(REPO/cad['part_references'][n]['path'])==cad['part_references'][n]['SHA256'],valid=bool(BRepCheck_Analyzer(s).IsValid()),solids=solid_count(s)) for n,s in parts.items()];sources=[];v=[]
 for tag in sys.argv[2:]:
  p=ROOT/'validation/integrated'/tag;d=json.loads((p/'summary.json').read_text());g=json.loads((REPO/d['geometry']['path']).read_text())
  for k,b in enumerate(d['body_results']):
   n=b['part'];F=[]
   if k==0:
    for x in faces(parts['TEST_BASE'],2,46):
     for y in faces(parts['GROUND_PLATE'],2,46):F.append(BRepAlgoAPI_Common(x,y).Shape())
   else:
    for x in faces(parts['BENCH_ANCHOR_RAIL'],2,66):
     for lo in (-64,96):F.append(BRepAlgoAPI_Common(x,box(lo,-64,65.99,10,109,.02)).Shape())
   ar=sum((moment(f)[0] for f in F));first=sum((moment(f)[1] for f in F),np.zeros(3));second=sum((moment(f)[2] for f in F),np.zeros((3,3)));qs=g['source_quadrature'][k];aq=sum(q['area_mm2'] for q in qs);fq=sum((q['area_mm2']*np.array(q['point_mm']) for q in qs),np.zeros(3));sq=sum((np.array(q['central_second_moment_mm4'])+q['area_mm2']*np.outer(q['point_mm'],q['point_mm']) for q in qs),np.zeros((3,3)))
   sources.append(dict(tag=tag,part=n,actual_source_area_mm2=ar,integrated_source_area_mm2=aq,relative_area_error=abs(aq/ar-1),centroid_max_error_mm=float(abs(fq/aq-first/ar).max()),raw_second_moment_relative=float(np.linalg.norm(sq-second)/np.linalg.norm(second)),actual_source_fixed_between_meshes=True,source_physical_external_support_qualified=False))
   a=np.load(REPO/b['fields']['path']);pts=a['points_mm'];t=a['tetra'];mv=float(np.abs(np.linalg.det(pts[t[:,1:]]-pts[t[:,0,None]])).sum()/6);cv=volume(parts[n]);v.append(dict(tag=tag,part=n,mesh_volume_mm3=mv,actual_CAD_volume_mm3=cv,relative_volume_error=abs(mv/cv-1),original1percent_volume=abs(mv/cv-1)<.01,nodes=len(pts),tetra=len(t)))
 bom=json.loads((REPO/cad['BOM']['path']).read_text());checks=dict(all85hash_valid_single=all(r['hash_matches'] and r['valid'] and r['solids']==1 for r in identities),assembly_hash=sha(REPO/cad['assembly']['path'])==cad['assembly']['SHA256'],aggregate85solids=solid_count(read(REPO/cad['assembly']['path']))==85,BOM_identity={r['part_ID']:r['STEP'] for r in bom['parts']}==cad['part_references'],all_fixed_source_moments=all(r['relative_area_error']<1e-8 and r['centroid_max_error_mm']<1e-6 and r['raw_second_moment_relative']<1e-8 for r in sources),volume1percent=all(r['original1percent_volume'] for r in v))
 dump(out/'summary.json',dict(status='ACTUAL_P1_FIXED_SOURCE_GEOMETRY_IDENTITY_PASS_LOCAL' if all(checks.values()) else 'ACTUAL_P1_SOURCE_GEOMETRY_OR_VOLUME_FAIL',candidate=ref(cp),verifier=ref(out/'verifier.py'),checks=checks,parts=identities,source_moments=sources,volumes=v,actual_CAD_changes=[],newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Fresh actual85part validity/identity,not a new assembly process or source-backed material/strength qualification. All original interference/order/tool evidence retained unchanged.','Exact fixed signed source moments confirm unchanged conditional source shape under mesh refinement;this is not a physical external fixture or operating load field.','Mesh volume agreement does not imply displacement/stress/contact/energy convergence.']))
 print(json.dumps(checks));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
