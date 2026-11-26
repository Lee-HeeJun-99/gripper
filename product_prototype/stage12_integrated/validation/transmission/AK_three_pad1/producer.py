"""Separate finite external support candidate; never an adopted Palm fixation."""
import json, math, sys, shutil
from pathlib import Path
from baseline_registry import ROOT, REPO, S1, sha, ref, dump
sys.path.insert(0, str(S1/'scripts'))
from incremental_stage1 import read, cyl, common, export, bounds
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
import numpy as np

def main():
    assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/transmission/AK_three_pad1'
    out.mkdir(parents=True,exist_ok=False)
    shutil.copyfile(__file__,out/'producer.py')
    source=ROOT/'cad/exports/revAK_integral2/summary.json'
    parts=json.loads(source.read_text())['part_references']
    dump(out/'inputs.json',dict(candidate=ref(source),parts=parts,
        producer=ref(out/'producer.py'),dependencies=[ref(S1/'scripts'/n) for n in ('incremental_stage1.py','build_stage1.py')],
        design=dict(radius_mm=3,height_mm=6,center_radius_mm=25,angles_deg=[60,180,300],top_z_mm=-12),
        plan='One fixed candidate, no search: actual planar contact area and all-part interference; unit normal wrench basis and unilateral load cases. No friction or preload assumed.'))
    assert len(parts)==235
    for r in parts.values(): assert sha(REPO/r['path'])==r['SHA256']
    palm=read(REPO/parts['PALM']['path']); others={n:read(REPO/r['path']) for n,r in parts.items() if n!='PALM'}
    rows=[]
    for i,deg in enumerate((60,180,300)):
        assert not (ROOT/'runtime/STOP').exists()
        x,y=25*math.cos(math.radians(deg)),25*math.sin(math.radians(deg))
        pad=cyl(3,(x,y,-18),6);p=out/f'PAD_{i}.step';export(pad,p)
        probe=cyl(3,(x,y,-12.01),.02)
        area=mx=my=0.;it=TopExp_Explorer(palm,TopAbs_FACE)
        while it.More():
            face=TopoDS.Face_s(it.Current());b=bounds(face)
            if abs(b[2]+12)<1e-7 and abs(b[5]+12)<1e-7:
                cut=BRepAlgoAPI_Common(face,probe).Shape();g=GProp_GProps();BRepGProp.SurfaceProperties_s(cut,g)
                a=g.Mass();c=g.CentreOfMass();area+=a;mx+=a*c.X();my+=a*c.Y()
            it.Next()
        collisions=[dict(part=n,volume_mm3=common(pad,s)) for n,s in others.items()]
        rows.append(dict(pad=ref(p),center_mm=[x,y,-12],area_mm2=area,
            centroid_mm=[mx/area,my/area,-12] if area>1e-10 else None,
            palm_overlap_mm3=common(pad,palm),collisions=collisions))
    geometry_ok=all(r['area_mm2']>1e-6 and r['palm_overlap_mm3']<1e-7 and all(c['volume_mm3']<1e-7 for c in r['collisions']) for r in rows)
    W=np.array([[0,0,1,r['centroid_mm'][1],-r['centroid_mm'][0],0] for r in rows if r['centroid_mm']]).T
    cases=[]
    if W.shape==(6,3):
        A=W[[2,3,4],:]
        # Applied wrench; support must supply its negative. Moments in N mm.
        for label,load in [('center_compression',[0,0,-1,0,0,0]),('uplift',[0,0,1,0,0,0]),('lateral',[1,0,0,0,0,0]),('torsion',[0,0,0,0,0,1]),('eccentric_compression',[0,0,-1,0,40,0])]:
            load=np.array(load,dtype=float);reaction=np.linalg.solve(A,-load[[2,3,4]])
            residual=float(np.max(np.abs(W@reaction+load)))
            cases.append(dict(label=label,applied_wrench_N_Nmm=load.tolist(),normal_reactions_N=reaction.tolist(),residual=residual,
                feasible=bool(residual<1e-9 and min(reaction)>=-1e-10)))
    result=dict(status='FINITE_PAD_GEOMETRY_PASS_SUPPORT_INCOMPLETE' if geometry_ok else 'FINITE_PAD_DESIGN_GEOMETRY_FAIL',
        inputs=ref(out/'inputs.json'),producer=ref(out/'producer.py'),rows=rows,geometry_pass=geometry_ok,
        normal_wrench_matrix=W.tolist(),rank=int(np.linalg.matrix_rank(W)),cases=cases,whole_system_release=False,
        limitations=['Separate external candidate only, not AK/RevAA adoption or an installed fixture',
        'Normal-only rigid pad contact; uniform pressure basis is a subset of possible distributed pressure',
        'No tensile, lateral or torsional retention; unconnected pad bottoms have no qualified ground attachment',
        'No preload/friction/material/strength/compliance/global energy qualification; no full-Palm equilibrium solved'])
    dump(out/'summary.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
    raise SystemExit(0 if geometry_ok else 2)
if __name__=='__main__':main()
