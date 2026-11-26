"""Independent solid-slice quadrature and wrench verification of actual pad pressure."""
import json,sys,shutil,math
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
import numpy as np

def measure(s):
    g=GProp_GProps();BRepGProp.VolumeProperties_s(s,g);c=g.CentreOfMass()
    return g.Mass(),np.array([c.X(),c.Y(),c.Z()])
def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/transmission/AK_pad_pressure_verify1';out.mkdir(exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'validation/transmission/AK_pad_pressure1/summary.json';d=json.loads(source.read_text())
    r=d['inputs'];assert sha(REPO/r['path'])==r['SHA256'];inp=json.loads((REPO/r['path']).read_text())
    for r in [inp['source'],inp['source_inputs'],inp['producer'],*inp['references'],*inp['dependencies']]:assert sha(REPO/r['path'])==r['SHA256']
    src=json.loads((REPO/inp['source']['path']).read_text())
    original=json.loads((REPO/inp['source_inputs']['path']).read_text())
    palm=read(REPO/original['parts']['PALM']['path']);rows=[];columns=[]
    for p in d['patches']:
        pad=read(REPO/src['rows'][p['pad_index']]['pad']['path'])
        x,y,z=p['center_mm']
        for h in (.001,.002):
            assert not (ROOT/'runtime/STOP').exists()
            for label,solid,z0 in [('pad',pad,z-h),('palm',palm,z)]:
                v,c=measure(BRepAlgoAPI_Common(solid,cyl(p['radius_mm'],(x,y,z0),h)).Shape())
                area=v/h;error=max(abs(c[:2]-np.array(p['centroid_mm'][:2])))
                rows.append(dict(pad_index=p['pad_index'],side=label,width_mm=h,area_mm2=area,centroid_error_mm=float(error),
                    matches=bool(abs(area-p['area_mm2'])<1e-5 and error<1e-6)))
        columns.append(np.r_[[0,0,p['force_N']],np.cross(p['centroid_mm'],[0,0,p['force_N']])])
    reaction=sum(columns);res=float(max(abs(reaction+np.array(d['applied_wrench_N_Nmm']))))
    # Independently recover cylinder radii from solid volumes and known finite height.
    extents=[]
    for row in src['rows']:
        v,c=measure(read(REPO/row['pad']['path']));radius=math.sqrt(v/(6*math.pi))
        assert abs(radius-3)<1e-6
        extents.append([float(c[0]-radius),float(c[0]+radius)])
    interval=[min(e[0] for e in extents),max(e[1] for e in extents)]
    # Deliberately impossible patch crosses actual pad edge; area check must reject it.
    row=src['rows'][0];x,y,z=row['center_mm'];h=.001
    badvol,_=measure(BRepAlgoAPI_Common(read(REPO/row['pad']['path']),cyl(1,(x+3.5,y,z-h),h)).Shape())
    badarea=badvol/h
    delta=np.array([.03,-.04,.02,.001,.002,-.003])
    direct=sum(p['force_N']*(delta[:3]+np.cross(delta[3:],p['centroid_mm']))[2] for p in d['patches'])
    work_error=abs(float(delta@reaction)-direct)
    # Barycentric solution independent of producer's symmetry formula.
    A=np.array([[1,r['centroid_mm'][1],-r['centroid_mm'][0]] for r in src['rows']]).T
    f=np.linalg.solve(A,-np.array(d['applied_wrench_N_Nmm'])[[2,3,4]])
    checks=dict(eight_actual_slices=len(rows)==8 and all(r['matches'] for r in rows),
        cross_product_equilibrium=res<1e-9,volume_derived_extent=bool(max(abs(np.array(interval)-d['x_support_bounds_mm']))<1e-6),
        outside_40mm_rejected=40>interval[1],centroid_only_negative=bool(min(f)<0),
        corrupted_patch_rejected=abs(badarea-math.pi)>1e-5,virtual_work=work_error<1e-12,
        finite_pressure_reconstructed=all(abs(p['pressure_N_mm2']*p['area_mm2']-p['force_N'])<1e-12 for p in d['patches']))
    ok=all(checks.values())
    dump(out/'summary.json',dict(status='INDEPENDENT_FINITE_PRESSURE_VERIFICATION_PASS' if ok else 'FAIL',source=ref(source),producer=ref(out/'producer.py'),
        checks=checks,rows=rows,equilibrium_residual_N_Nmm=res,x_extent_mm=interval,centroid_basis_N=f.tolist(),
        corrupt_patch_area_mm2=badarea,virtual_work_error_Nmm=work_error,whole_system_release=False,
        scope='Conditional rigid finite-pressure witness and footprint exclusion; no six-DOF support or elastic qualification'))
    print(json.dumps(dict(checks=checks,residual=res,corrupt_patch_area_mm2=badarea,x_extent_mm=interval)))
    raise SystemExit(0 if ok else 2)
if __name__=='__main__':main()
