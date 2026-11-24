"""Place finite parts in immutable initial route frames; not Native dynamics."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    src=BASE/'results/eccentric_eyelet_mesh1416/summary.json';parts=json.loads(src.read_text());routes=json.loads((BASE/'results/four_route_gate1408/summary.json').read_text())['routes'];gate=json.loads((BASE/'results/eccentric_eyelet1415/summary.json').read_text());records=[];combined=[]
    for part in parts['records']:
        j,k=part['route'],part['guide'];q=np.array(routes[j]['route_mm']);point=q[k+1];u=point-q[k];u/=np.linalg.norm(u);v=q[k+2]-point;v/=np.linalg.norm(v);axis=u+v;axis/=np.linalg.norm(axis);offset=np.array(part['world_bore_offset_mm']);ecc=np.linalg.norm(offset)
        x=offset/ecc if ecc>1e-12 else np.array([0.,1,0]);x-=axis*(x@axis);x/=np.linalg.norm(x);y=np.cross(axis,x);rotation=np.column_stack([x,y,axis]);assert abs(np.linalg.det(rotation)-1)<1e-12
        local=trimesh.load(src.parent/part['stl'],force='mesh',process=False);world=local.copy();world.vertices=local.vertices@rotation.T+point;filename=part['stl'];world.export(out/filename);roundtrip=trimesh.load(out/filename,force='mesh',process=True)
        # Triangle arrays avoid vertex reindexing performed by STL readers.
        expected=world.triangles;loaded=trimesh.load(out/filename,force='mesh',process=False).triangles;error=float(np.linalg.norm(expected-loaded,axis=2).max())
        outer=world.vertices[:0] # Explicit geometry contract uses local ring vertices below, not an AABB centre.
        radial=(local.vertices[:,0]**2+local.vertices[:,1]**2)**.5
        mask=np.isclose(radial,1.5,atol=1e-6);outer_centre=world.vertices[mask].mean(0);centre_error=float(np.linalg.norm(outer_centre-point))
        arcrow=next(r for r in gate['records'] if r.get('route')==j and r.get('guide')==k and 'trim_mm'in r)
        # Inscribed hole polygon differs by at most bore-R sagitta; outer
        # polygons remove solid, so cannot introduce new wire-solid interference.
        discretization=.8*(1-np.cos(np.pi/128));budget=arcrow['swept_wire_solid_clearance_lower_bound_mm']-discretization-error
        records.append(dict(route=j,guide=k,position_mm=point.tolist(),rotation_columns=rotation.tolist(),outer_centre_error_mm=centre_error,stl_roundtrip_max_error_mm=error,finite_mesh_clearance_lower_bound_mm=float(budget),watertight=bool(roundtrip.is_watertight),winding_consistent=bool(roundtrip.is_winding_consistent),stl=filename,sha256=sha(out/filename)));combined.append(world)
    trimesh.util.concatenate(combined).export(out/'initial_eyelets.stl')
    good=all(r['watertight'] and r['winding_consistent'] and r['outer_centre_error_mm']<1e-6 and r['finite_mesh_clearance_lower_bound_mm']>0 for r in records)
    result=dict(status='PASS_INITIAL_PART_PLACEMENT_ONLY' if good else 'FAIL_INITIAL_PART_PLACEMENT',records=records,part_count=len(records),minimum_finite_mesh_clearance_lower_bound_mm=min(r['finite_mesh_clearance_lower_bound_mm'] for r in records),maximum_STL_roundtrip_error_mm=max(r['stl_roundtrip_max_error_mm'] for r in records),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),input_sha256=sha(src),scope='20 static through-eyelets on single-finger four routes. Full surface support/eyelet unions, terminals,3finger swept motion,wire friction/equilibrium,mass,joints and Native path NOT QUALIFIED. Existing300partCAD and Native states unchanged.',Native='NOT RUN',STEP='NOT GENERATED')
    (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(result['status'],result['minimum_finite_mesh_clearance_lower_bound_mm'],result['maximum_STL_roundtrip_error_mm'])
if __name__=='__main__':main()
