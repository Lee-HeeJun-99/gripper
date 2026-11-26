"""Finite manual clutch calibration fixture; NOT proof-rated or powered.

Input hub is held by a split keyed stand, not motor holding torque. Output
uses the actual Drum/Tendon interface. Motor is absent from this bench fixture.
"""
import argparse,json,sys,shutil,itertools
from baseline_registry import ROOT,S1,REPO,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,box,cyl,cut,fuse,export,common,volume,solid_count
from build_stage1 import compound
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.IFSelect import IFSelect_RetDone

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--outboard-fasteners',action='store_true');a=p.parse_args()
    out=ROOT/'hardware_test/fixtures'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports/revAF_layout6/summary.json';d=json.loads(source.read_text())
    cartridge={n:read(REPO/r['path']) for n,r in d['part_references'].items() if n.startswith(('F0_DRUM','F0_CLUTCH'))}
    made={}
    xs=(90,130) if a.outboard_fasteners else (100,120)
    for label,y in [('REAR',-13),('FRONT',-8.45)]:
        stand=box(86 if a.outboard_fasteners else 96,y,0,48 if a.outboard_fasteners else 28,4.45,36)
        # Actual nominal hub collar, asymmetric ear and bolt access envelope.
        # 0.10mm declared assembly gap, NOT an interference waiver.
        stand=cut(stand,cyl(7.1,(110,-13.1,20),9.3,(0,1,0)),box(112.15,-11.1,13.4,6,6.2,15.2))
        for x in xs:
            for z in (5,32):stand=cut(stand,cyl(2.2,(x,-13.1,z),9.3,(0,1,0)))
        made['STAND_'+label]=stand
    for x in xs:
        for z in (5,32):
            made[f'M4_BOLT_{x}_{z}']=fuse(cyl(1.99,(x,-15,z),13,(0,1,0)),cyl(3.5,(x,-19,z),4,(0,1,0)))
            # Threaded envelopes only, no claimed supplier/material strength.
            made[f'M4_NUT_{x}_{z}']=cut(box(x-3.5,-4,z-3.5,7,3.2,7),cyl(2.01,(x,-4.1,z),3.4,(0,1,0)))
    rows=[]
    for n,s in made.items():
        assert BRepCheck_Analyzer(s).IsValid() and solid_count(s)==1 and volume(s)>0
        export(s,out/n);rows.append(dict(part=n,STEP=ref(out/(n+'.step')),STL=ref(out/(n+'.stl')),volume_mm3=volume(s)))
    allparts={**cartridge,**made};hits=[]
    for n,m in itertools.combinations(allparts,2):
        if n not in made and m not in made:continue
        v=common(allparts[n],allparts[m])
        if abs(v)>1e-8:hits.append(dict(a=n,b=m,common_mm3=v))
    w=STEPControl_Writer();w.Transfer(compound(allparts.values()),STEPControl_AsIs);assert w.Write(str(out/'ASSEMBLY.step'))==IFSelect_RetDone
    result=dict(status='FIXTURE_NOMINAL_GEOMETRY_PASS' if not hits else 'FIXTURE_NOMINAL_GEOMETRY_FAIL',source=ref(source),producer=ref(out/'producer.py'),parts=rows,assembly=ref(out/'ASSEMBLY.step'),hits=hits,
        scope='Actual keyed split stand and M4 nominal fastener envelopes against actual F0 clutch cartridge only; not whole production assembly',outboard_fasteners=a.outboard_fasteners,
        force_reaction='Input hub asymmetric clamp ear reacts into stand, stand into an independently rated bench clamp; no motor holding torque assumed',
        test_requirements=dict(sensor_range_N=[0,5],desired_resolution_N=.001,nominal_tangent_radius_m=.01125,actually_authorized_test_load_N=None),
        unqualified=['Stand/key/clamp/bolt proof strength','Actual stand material and bench anchoring','Supplier M4 fastener/socket/thread model and tool access','Actual load cell and tendon end adapter','Temperature/rate/repeatability/drag calibration','Safe proof load and operating permission'],hardware_measured=False,powered_authorization=False,whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],parts=len(rows),hits=hits),indent=2))
if __name__=='__main__':main()
