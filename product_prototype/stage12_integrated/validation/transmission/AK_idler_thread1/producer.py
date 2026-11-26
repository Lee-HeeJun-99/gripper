"""Actual AK idler nominal-envelope axial load-transfer identifiability audit."""
import json,sys,shutil,math
from pathlib import Path
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,rotate,common,bounds
from fastener_joint_contract import cylinders,project_interval
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.gp import gp_Trsf,gp_Vec

def moved(s,x,y):
    t=gp_Trsf();t.SetTranslation(gp_Vec(x,y,0));return BRepBuilderAPI_Transform(s,t,True).Shape()
def main():
    assert not (ROOT/'runtime/STOP').exists(),'STOP'
    out=ROOT/'validation/transmission/AK_idler_thread1';out.mkdir(exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'cad/exports/revAK_integral2/summary.json';d=json.loads(src.read_text());inputs=d['part_references']
    assert len(inputs)==235
    for r in inputs.values():assert sha(REPO/r['path'])==r['SHA256']
    rows=[]
    for i in range(3):
        names=[f'F{i}_IDLER_{s}' for s in ('AXLE','NUT','CLAMP_WASHER','BRACKET')]
        ss={n:rotate(read(REPO/inputs[n]['path']),-120*i) for n in names}
        axle,nut=ss[names[0]],ss[names[1]]
        ac,nc=cylinders(axle),cylinders(nut)
        inner=[c for c in nc if abs(c['r']-1.5)<1e-7]
        neck=[c for c in ac if abs(c['r']-1.19)<1e-7]
        thread=[c for c in ac if abs(c['r']-1.5)<1e-7 and project_interval(c,[0,1,0])[1]<-3.49]
        assert len(inner)==len(neck)==len(thread)==1
        overlaps=[dict(dy_mm=y,overlap_mm3=common(axle,moved(nut,0,y))) for y in (0,-.01,-.1,-.5,-1)]
        control=common(axle,moved(nut,.05,0))
        rows.append(dict(sector=i,parts={n:inputs[n] for n in names},nut_bounds_mm=bounds(nut),nut_bore=inner[0],thread_envelope=thread[0],neck=neck[0],axial_states=overlaps,radial_control_overlap_mm3=control,
            neck_area_mm2=math.pi*1.19**2,nominal_major_area_mm2=math.pi*1.5**2))
    checks=dict(all_15_axial_states_no_overlap=all(v['overlap_mm3']<=1e-8 for r in rows for v in r['axial_states']),all_radial_controls_rejected=all(r['radial_control_overlap_mm3']>1e-8 for r in rows))
    result=dict(status='NOMINAL_THREAD_AXIAL_TRANSFER_UNMODELED' if all(checks.values()) else 'GEOMETRY_ANALYSIS_FAIL',candidate=ref(src),producer=ref(out/'producer.py'),feature_reader=ref(S1/'scripts/fastener_joint_contract.py'),rows=rows,checks=checks,whole_system_release=False,
        conclusion='Smooth nominal M3 cylinders do not establish axial thread engagement or preload. This is a CAD representation limitation, not evidence that a manufactured M3 thread has zero capacity.',
        missing=['Actual thread minor/root profile and tolerances','Material minimums and notch/fatigue basis','Preload and stripping/contact proof','Protected maximum load and loaded free-spin'],
        strength_capacity_N=None,physical_thread_failure=False)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,controls=[r['radial_control_overlap_mm3'] for r in rows])))
    raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
