"""Actual P1 eight installed thread pairs; declared 6g/6H design geometry.
Not supplier CAD, ISO conformity, certified root form, or installed capacity.
"""
import sys,json,math,shutil,itertools
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,box,cut,fuse,canonical,export,bounds,common,overlap,solid_count,volume,translate
from build_stage1 import compound
from OCP.gp import gp_Ax3,gp_Pnt,gp_Dir,gp_Pnt2d
from OCP.Geom import Geom_CylindricalSurface
from OCP.GCE2d import GCE2d_MakeSegment
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakePolygon
from OCP.BRepLib import BRepLib
from OCP.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
from primary_nutseat46b import STATIONS
P=.8;K=P/(2*math.pi)
EXT=dict(major=4.976,pitch=4.456,minor=3.95)
INT=dict(major=5.12,pitch=4.605,minor=4.334)

def ridge(rmin,rmax,rpitch,z0,height):
    # Cross section lies in a radial/axial plane. Frenet transport of a
    # circular cylindrical helix is exactly rotation about Z + axial advance.
    # Material is within +/- [P/4+(r-rpitch)/sqrt(3)] for INTERNAL ridges.
    surf=Geom_CylindricalSurface(gp_Ax3(gp_Pnt(0,0,z0),gp_Dir(0,0,1)),rpitch)
    line=GCE2d_MakeSegment(gp_Pnt2d(0,0),gp_Pnt2d(height/K,height)).Value()
    ed=BRepBuilderAPI_MakeEdge(line,surf).Edge();BRepLib.BuildCurves3d_s(ed)
    spine=BRepBuilderAPI_MakeWire(ed).Wire()
    w=BRepBuilderAPI_MakePolygon()
    # Width grows radially outward: generic internal ridge. External uses
    # the same helix as a groove cutting tool, so complementary flanks match.
    for r,sgn in [(rmin,-1),(rmax,-1),(rmax,1),(rmin,1)]:
        w.Add(gp_Pnt(r,0,z0+sgn*(P/4+(r-rpitch)/math.sqrt(3))))
    w.Close();pipe=BRepOffsetAPI_MakePipeShell(spine);pipe.SetMode(True);pipe.Add(w.Wire(),False,False);pipe.Build();assert pipe.IsDone();assert pipe.MakeSolid()
    return pipe.Shape()

def local_pair(oldbolt,oldnut,x,y,seat,nutlow):
    # Local datum Z=bolt tip. Full shank is20mm, original head/socket retained.
    b=translate(oldbolt,-x,-y,-(seat-20));n=translate(oldnut,-x,-y,-(seat-20))
    # Source-limit external major; actual reduced shank, not a display overlay.
    b=cut(b,cut(cyl(2.51,(0,0,-.01),20.01),cyl(EXT['major']/2,(0,0,-.02),20.03)))
    # Groove phase zero; external ridge is centred half a pitch away.
    tool=ridge(EXT['minor']/2,2.6,EXT['pitch']/2,-P,21.6)
    b=canonical(cut(b,tool))
    # Replace old major-bore nut by a physically connected inner ridge.
    # Nut nominal source envelope retains8AF/4.7mm; no invented strength.
    zlo=nutlow-(seat-20);zhi=zlo+4.7
    inside=ridge(INT['minor']/2,INT['major']/2,INT['pitch']/2,-P,8.)
    inside=translate(inside,0,0,math.floor(zlo/P)*P)
    inside=__import__('OCP.BRepAlgoAPI',fromlist=['BRepAlgoAPI_Common']).BRepAlgoAPI_Common(inside,box(-3,-3,zlo,6,6,4.7)).Shape()
    # Old nut bore is2.5; ridge extends to2.56 with positive radial attachment.
    n=canonical(fuse(n,inside))
    return b,n

def main():
    assert not(ROOT/'runtime/STOP').exists();tag=sys.argv[1] if len(sys.argv)>1 else 'primaryP1_thread49';out=ROOT/'cad/exports'/tag;out.mkdir();shutil.copyfile(__file__,out/'producer.py')
    cp=ROOT/'cad/exports/primaryP1_profilepin48b/summary.json';old=json.loads(cp.read_text());refs=dict(old['part_references']);assert all(sha(REPO/r['path'])==r['SHA256'] for r in refs.values());parts={n:read(REPO/r['path']) for n,r in refs.items()}
    pre,i,x,y,zlo,zhi,parent=STATIONS[0];b,n=local_pair(parts[f'{pre}_BOLT_{i}'],parts[f'{pre}_NUT_{i}'],x,y,zhi+14,zlo)
    changed=[]
    for pre,i,x,y,zlo,zhi,parent in STATIONS:
        assert not(ROOT/'runtime/STOP').exists()
        for name,s in [(f'{pre}_BOLT_{i}',b),(f'{pre}_NUT_{i}',n)]:
            s=translate(s,x,y,zhi-6);export(s,out/name);parts[name]=read(out/(name+'.step'));refs[name]=ref(out/(name+'.step'));changed.append(dict(part_ID=name,STEP=refs[name],STL=ref(out/(name+'.stl')),valid=bool(BRepCheck_Analyzer(parts[name]).IsValid()),solids=solid_count(parts[name]),volume_mm3=volume(parts[name]),parent=old['part_references'][name]))
    bb={n:bounds(s) for n,s in parts.items()};hits=[];pairs=0
    for a,b in itertools.combinations(parts,2):
        assert not(ROOT/'runtime/STOP').exists()
        if overlap(bb[a],bb[b]):
            pairs+=1;v=common(parts[a],parts[b])
            if v>1e-8:hits.append(dict(a=a,b=b,common_mm3=v))
    w=STEPControl_Writer();w.Transfer(compound(parts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
    bom=json.loads((REPO/old['BOM']['path']).read_text());bom['revision']=tag
    for c in changed:
        r=next(r for r in bom['parts'] if r['part_ID']==c['part_ID']);r.update(STEP=c['STEP'],interface='Actual right-hand .8mm helical finite flanks;design-limit dimensions,not source-certified thread;runout/chamfer/root/material unqualified')
    dump(out/'BOM.json',bom);dump(out/'inputs.json',dict(parent=ref(cp),producer=ref(out/'producer.py'),external_design_mm=EXT,internal_design_mm=INT,pitch_mm=P,source=ref(ROOT/'models/standard_drive/primary_thread_sources49/reviewed.json'),chamfers_and_runout_qualified=False,material_and_capacity_qualified=False))
    good=not hits and all(c['valid'] and c['solids']==1 for c in changed)
    d=dict(old);d.update(revision=tag,status='ACTUAL_P1_HELICAL_THREAD_GEOMETRY_PASS_NOT_RELEASE' if good else 'ACTUAL_P1_HELICAL_THREAD_GEOMETRY_FAIL',parent=ref(cp),part_references=refs,changed=changed,assembly=ref(out/'ASSEMBLY.step'),BOM=ref(out/'BOM.json'),inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),part_bounds_mm=bb,interferences=hits,exact_pairs=pairs,design_change='Same128partP1:8installedM5x20bolts/8ISO4032nuts gain finite helical load flanks;112otherparts unchanged',not_qualified=old['not_qualified']+['Recreated thread design,not supplier/ISOcertificate;root/runout/chamfers/material/installedcapacity unqualified'])
    dump(out/'summary.json',d);print(json.dumps(dict(status=d['status'],hits=hits,invalid=[c for c in changed if not c['valid'] or c['solids']!=1])));raise SystemExit(0 if good else 2)
if __name__=='__main__':main()
