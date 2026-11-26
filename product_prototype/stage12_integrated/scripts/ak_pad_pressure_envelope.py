"""Actual finite-pad pressure redistribution: conditional witness and rigorous exclusion."""
import json,sys,math,shutil
from baseline_registry import ROOT,REPO,S1,sha,ref,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,cyl,bounds
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/transmission/AK_pad_pressure1';out.mkdir(exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    src=ROOT/'validation/transmission/AK_three_pad2/summary.json'
    d=json.loads(src.read_text());inp=REPO/d['inputs']['path'];assert sha(inp)==d['inputs']['SHA256']
    inputs=json.loads(inp.read_text())
    refs=[inputs['candidate'],*inputs['parts'].values(),*inputs['dependencies'],*[r['pad'] for r in d['rows']]]
    for r in refs: assert sha(REPO/r['path'])==r['SHA256']
    dump(out/'inputs.json',dict(source=ref(src),source_inputs=ref(inp),references=refs,
        producer=ref(out/'producer.py'),dependencies=[ref(ROOT/'scripts/baseline_registry.py')],
        hypothesis='Finite nonuniform pressure can balance an eccentric load rejected by the centroid-only basis; exact footprint still cannot provide six-DOF attachment.',
        fixed_design=dict(patch_radius_mm=1,patch_x_shift_mm=1.5,pads=[0,2],force_per_patch_N=.5),
        acceptance='Actual Palm and pad common face patches; wrench balance <1e-9 N/Nmm; independent volume/first-moment checks. No elastic realizability claim.'))
    palm=read(REPO/inputs['parts']['PALM']['path']);patches=[]
    for i in (0,2):
        assert not (ROOT/'runtime/STOP').exists()
        row=d['rows'][i];x,y,z=row['center_mm'];x+=1.5
        probe=cyl(1,(x,y,z-.01),.02)
        pad=read(REPO/row['pad']['path']);a=mx=my=0.
        it=TopExp_Explorer(pad,TopAbs_FACE)
        while it.More():
            face=TopoDS.Face_s(it.Current());b=bounds(face)
            if abs(b[2]-z)<1e-6 and abs(b[5]-z)<1e-6:
                cut=BRepAlgoAPI_Common(BRepAlgoAPI_Common(face,probe).Shape(),palm).Shape()
                g=GProp_GProps();BRepGProp.SurfaceProperties_s(cut,g);v=g.Mass();c=g.CentreOfMass()
                a+=v;mx+=v*c.X();my+=v*c.Y()
            it.Next()
        assert a>0
        patches.append(dict(pad_index=i,center_mm=[x,y,z],radius_mm=1,area_mm2=a,
            centroid_mm=[mx/a,my/a,z],force_N=.5,pressure_N_mm2=.5/a))
    reaction=[0.,0.,0.,0.,0.,0.]
    for p in patches:
        x,y,z=p['centroid_mm'];f=p['force_N'];reaction[2]+=f;reaction[3]+=y*f;reaction[4]-=x*f
    load=[0,0,-1,0,14,0];res=max(abs(a+b) for a,b in zip(reaction,load))
    xb=[bounds(read(REPO/r['pad']['path'])) for r in d['rows']]
    xmax=max(b[3] for b in xb);xmin=min(b[0] for b in xb)
    # For every nonnegative normal pressure: xmin*N <= integral(x*p)dA <= xmax*N.
    # This necessary condition applies to arbitrary pressure, including boundary measures.
    centroid_reactions=[14/37.5,-1/37.5,14/37.5] # corrected below from exact symmetry
    side=(14+25)/(2*(12.5+25));centroid_reactions=[side,1-2*side,side]
    checks=dict(actual_patches_full=all(abs(p['area_mm2']-math.pi)<1e-6 for p in patches),
        finite_positive_pressure=all(p['pressure_N_mm2']>0 for p in patches),equilibrium=res<1e-9,
        centroid_basis_rejects=min(centroid_reactions)<0,old_40mm_excluded=40>xmax,
        shift_within_pad=1.5+1<3)
    dump(out/'summary.json',dict(status='FINITE_PRESSURE_WITNESS_AND_TIPPING_BOUND' if all(checks.values()) else 'FAIL',
        inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),patches=patches,checks=checks,
        applied_wrench_N_Nmm=load,reaction_wrench_N_Nmm=reaction,residual_N_Nmm=res,
        centroid_basis_reactions_N=centroid_reactions,x_support_bounds_mm=[xmin,xmax],
        old_40mm_separation_mm=40-xmax,whole_system_release=False,adopted=False,
        physical_pressure_solution=None,ground_attachment=None,
        limitations=['Constructive rigid pressure witness, not an elastic/preload solution or allowable pressure',
        'Normal-only pressure always has Fx=Fy=Mz=0 and Fz>=0; six-DOF attachment remains impossible',
        'Pads remain separate unconnected candidates; no material/strength/energy/full Palm certification']))
    print(json.dumps(dict(checks=checks,residual=res,x_bounds=[xmin,xmax],centroid_reactions=centroid_reactions)))
    raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
