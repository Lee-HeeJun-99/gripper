"""Actual AK collet specimen on integral D-shaft/flange reaction fixture.
Unpowered geometry preparation only; no safe load or capacity inferred.
"""
import argparse,json,sys,shutil,itertools
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,export,common,volume,solid_count
from build_stage1 import compound
from mechanisms_stage1 import hex_axis
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'hardware_test/fixtures'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports/revAK_integral2/summary.json';d=json.loads(source.read_text())
    specimen={n:read(REPO/d['part_references'][n]['path']) for n in ('F0_CLUTCH_INPUT_HUB','F0_CLUTCH_CLAMP_BOLT')}
    plate=box(90,-30,0,40,6,40)
    shaft=cut(cyl(2.494,(110,-20,20),34.5,(0,1,0)),box(111.906,-20,15,8,34.6,10))
    shaft=fuse(shaft,cyl(10,(110,-24,20),4,(0,1,0)))
    for x in (103,117):
        plate=cut(plate,cyl(2.2,(x,-30.1,20),6.2,(0,1,0)))
        shaft=cut(shaft,cyl(2.2,(x,-24.1,20),4.2,(0,1,0)))
    # Finite bench mounting holes; no fictitious fixed bench constraint.
    for x in (95,125):plate=cut(plate,cyl(2.2,(x,-30.1,5),6.2,(0,1,0)))
    made=dict(REACTION_PLATE=plate,INTEGRAL_D_SHAFT_FLANGE=shaft)
    for x in (103,117):
        bolt=fuse(cyl(1.99,(x,-30,20),14,(0,1,0)),cyl(3.5,(x,-34,20),4,(0,1,0)))
        bolt=cut(bolt,hex_axis((x,-34.1,20),(0,1,0),3,2.5))
        made[f'M4_BOLT_{x}']=bolt;made[f'M4_NUT_{x}']=cut(hex_axis((x,-20,20),(0,1,0),7,3.2),cyl(2.01,(x,-20.1,20),3.4,(0,1,0)))
    rows=[]
    for n,s in made.items():
        assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0,n
        export(s,out/n);rows.append(dict(part=n,STEP=ref(out/(n+'.step')),STL=ref(out/(n+'.stl')),volume_mm3=volume(s)))
    shapes={**specimen,**made};hits=[]
    for n,m in itertools.combinations(shapes,2):
        v=common(shapes[n],shapes[m])
        if abs(v)>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
    w=STEPControl_Writer();w.Transfer(compound(shapes.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
    result=dict(status='FIXTURE_NOMINAL_GEOMETRY_PASS' if not hits else 'FIXTURE_NOMINAL_GEOMETRY_FAIL',source=ref(source),producer=ref(out/'producer.py'),parts=rows,specimen_sources={n:d['part_references'][n] for n in specimen},assembly=ref(out/'ASSEMBLY.step'),hits=hits,
        scope='Actual AK hub/bolt mounted on nominal minimum-diameter/minimum-flat dummy shaft; geometry preparation only, not complete calibrated load rig',
        dimensions=dict(shaft_diameter_mm=4.988,D_flat_across_mm=4.4,shaft_tip_Y_mm=14.5,hub_engagement_mm=9.7,flat_normal='+X; fixture orientation defined, motor orientation must be separately verified'),
        reaction_path='Hub contact -> integral machined D-shaft/flange -> two M4 nominal envelopes -> plate -> separately rated bench attachment. No motor holding torque or motor bearing support assumed.',
        remaining=['Actual shaft/plate/fastener materials and proof load','Actual shaft finish/flat orientation/fit and strain measurement','Calibrated torque/axial load adapters and sensors','Guard, bench anchors, emergency stop and approved safe load','Combined axial/torque test with independent slip/displacement measurement'],hardware_measured=False,powered_authorization=False,whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],parts=len(rows),hits=hits)))
if __name__=='__main__':main()
