"""Finite actual AK root-material translation witnesses; no preload/strength solve.

Predeclared overlap threshold 1e-8 mm3 is a CAD numerical check, not a
physical clearance relaxation. Fixed root solids; each constituent moves
independently. Local cut at Z=-7 is not treated as a physical end stop.
"""
import json,sys
from baseline_registry import ROOT,REPO,S1,ref,dump,sha
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,box,translate,common,volume
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

def main():
    assert not (ROOT/'runtime/STOP').exists(), 'STOP requested'
    out=ROOT/'validation/finger/AK_root_retention1';out.mkdir(exist_ok=False,parents=True)
    source=ROOT/'cad/exports/revAK_integral2/summary.json';d=json.loads(source.read_text())
    moving=['F0_SKIN','F0_RAIL_L','F0_RAIL_R']
    fixed=['F0_ROOT_FRONT','F0_ROOT_BACK','F0_ROOT_BOLT_-16','F0_ROOT_BOLT_16','F0_ROOT_NUT_-16','F0_ROOT_NUT_16']
    shapes={};sources={}
    for n in moving+fixed:
        r=d['part_references'][n];p=REPO/r['path'];assert sha(p)==r['SHA256'];sources[n]=r;shapes[n]=read(p)
    rows=[]
    for name in moving:
        fragment=BRepAlgoAPI_Common(shapes[name],box(30,-30,-7,40,60,17)).Shape()
        assert volume(fragment)>0
        for dz in [0,-.01,-.1,-.5,.01,.1,.5]:
            assert not (ROOT/'runtime/STOP').exists(), 'STOP requested'
            moved=translate(fragment,0,0,dz);pairs=[]
            for other in fixed:
                ds=BRepExtrema_DistShapeShape(moved,shapes[other]);ds.Perform();assert ds.IsDone()
                pairs.append(dict(other=other,common_mm3=common(moved,shapes[other]),distance_mm=ds.Value()))
            rows.append(dict(part=name,dz_mm=dz,fragment_volume_mm3=volume(fragment),bounds_mm=bounds(moved),pairs=pairs,
                collision=any(p['common_mm3']>1e-8 for p in pairs)))
    nominal=all(not r['collision'] for r in rows if r['dz_mm']==0)
    witnesses=[dict(part=n,negative_clear_samples_mm=[r['dz_mm'] for r in rows if r['part']==n and r['dz_mm']<0 and not r['collision']],
        positive_clear_samples_mm=[r['dz_mm'] for r in rows if r['part']==n and r['dz_mm']>0 and not r['collision']]) for n in moving]
    result=dict(status='FINITE_ROOT_PROBE_COMPLETE' if nominal else 'NOMINAL_ROOT_COLLISION_FAIL',revision='revAK_integral2',
        source=ref(source),producer=ref(__import__('pathlib').Path(__file__)),inputs=sources,rows=rows,witnesses=witnesses,
        criteria=dict(nominal_overlap_mm3_max=1e-8,scope='finite sampled independent root-fragment axial translations against actual root clamps/fasteners'),
        nominal_no_overlap=nominal,whole_system_release=False,
        limitations=['No elastic deformation/preload/friction/force solution','Clear samples do not prove continuous escape or all assembly clearance',
        'Fragment cut is not a real free surface; moving entire root fragment is local kinematic screening only','No strength, safe load or assembled Finger PASS'])
    dump(out/'summary.json',result)
    print(json.dumps(dict(status=result['status'],witnesses=witnesses)))
if __name__=='__main__':main()
