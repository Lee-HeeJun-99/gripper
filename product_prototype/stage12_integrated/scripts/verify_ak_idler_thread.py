"""Independent continuous coaxial envelope exclusion, not sampled-motion proof."""
import json,sys,math
from pathlib import Path
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,rotate,box,cyl,common,cut,volume
p=ROOT/'validation/transmission/AK_idler_thread1/summary.json';d=json.loads(p.read_text())
assert not (ROOT/'runtime/STOP').exists()
for r in [d['candidate'],d['producer'],d['feature_reader']]:assert sha(REPO/r['path'])==r['SHA256']
rows=[]
for row in d['rows']:
    i=row['sector'];parts=row['parts']
    for r in parts.values():assert sha(REPO/r['path'])==r['SHA256']
    axle=rotate(read(REPO/parts[f'F{i}_IDLER_AXLE']['path']),-120*i)
    nut=rotate(read(REPO/parts[f'F{i}_IDLER_NUT']['path']),-120*i)
    # Every nut position dy in [-1,0] lies within this Y slab. Exclude all
    # axle material outside radius1.5 in it; nut has no material inside it.
    slab=box(34,-9,15,20,3.5,20)
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
    clipped=BRepAlgoAPI_Common(axle,slab).Shape()
    gauge=cyl(1.5,(44,-10,25),5,(0,1,0))
    outside=abs(volume(cut(clipped,gauge)));nut_inside=abs(common(nut,gauge))
    b=row['nut_bounds_mm'];contain=b[1]-1>=-9-1e-7 and b[4]<=-5.5+1e-7
    area=math.pi*row['neck']['r']**2
    rows.append(dict(sector=i,axle_outside_radius_mm3=outside,nut_inside_radius_mm3=nut_inside,swept_Y_slab_contains=contain,neck_area_recomputed_mm2=area,passed=outside<=1e-8 and nut_inside<=1e-8 and contain and abs(area-row['neck_area_mm2'])<1e-12))
passed=len(rows)==3 and all(r['passed'] for r in rows)
out=ROOT/'validation/transmission/AK_idler_thread_verify1';out.mkdir(exist_ok=False)
dump(out/'summary.json',dict(status='CONTINUOUS_NOMINAL_ENVELOPE_EXCLUSION_VERIFIED' if passed else 'FAIL',source=ref(p),producer=ref(Path(__file__)),rows=rows,scope='Continuous axial nut translation [-1,0]mm against nominal axle only. Circular cylindrical contact normals have zero axial component; friction and manufactured helices are not represented.',whole_system_release=False))
print(json.dumps(dict(passed=passed,rows=rows)));raise SystemExit(0 if passed else 2)
