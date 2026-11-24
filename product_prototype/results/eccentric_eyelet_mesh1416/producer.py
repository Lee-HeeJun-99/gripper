"""Parametric finite eccentric-eyelet solid source; STL is not STEP qualification."""
import argparse,json,subprocess
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha

def solid(offset,segments=128):
    """Axis z; fixed OD3 and eccentric bore with 0.2x45deg chamfers."""
    z=np.array([-1.,-.8,.8,1.]);r=np.array([.8,.6,.6,.8]);theta=np.arange(segments)*2*np.pi/segments
    circle=np.column_stack([np.cos(theta),np.sin(theta),np.zeros(segments)])
    vertices=[]
    for height in z:vertices.extend((1.5*circle+[0,0,height]).tolist())
    for height,radius in zip(z,r):vertices.extend((radius*circle+offset+[0,0,height]).tolist())
    faces=[]
    def bridge(a,b,reverse=False):
        for k in range(segments):
            j=(k+1)%segments;pair=[[a+k,a+j,b+j],[a+k,b+j,b+k]]
            faces.extend([f[::-1] for f in pair] if reverse else pair)
    for k in range(3):bridge(k*segments,(k+1)*segments);bridge((4+k)*segments,(5+k)*segments,True)
    bridge(0,4*segments,True);bridge(3*segments,7*segments)
    mesh=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
    if mesh.volume<0:mesh.invert()
    return mesh

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    src=BASE/'results/eccentric_eyelet1415/summary.json';source=json.loads(src.read_text());records=[]
    analytic=np.pi*1.5**2*2-(np.pi*.6**2*1.6+2*np.pi*.2/3*(.6**2+.6*.8+.8**2))
    for row in source['records']:
        if 'trim_mm' not in row:continue
        eccentricity=float(np.linalg.norm(row['bore_centre_offset_mm']));mesh=solid(np.array([eccentricity,0,0]));name=f"route{row['route']}_guide{row['guide']}.stl";mesh.export(out/name)
        # Independent volume discretization factor for regular polygon rings.
        factor=128*np.sin(2*np.pi/128)/(2*np.pi);expected=analytic*factor
        records.append(dict(route=row['route'],guide=row['guide'],local_bore_offset_mm=[eccentricity,0,0],world_bore_offset_mm=row['bore_centre_offset_mm'],minimum_radial_wall_bound_mm=.7-eccentricity,watertight=bool(mesh.is_watertight),winding_consistent=bool(mesh.is_winding_consistent),volume_mm3=float(mesh.volume),analytic_volume_mm3=float(analytic),polygon_volume_error_mm3=float(mesh.volume-expected),relative_volume_discretization_error=float(abs(mesh.volume-analytic)/analytic),stl=name,sha256=sha(out/name)))
    good=all(r['watertight'] and r['winding_consistent'] and r['volume_mm3']>0 and abs(r['polygon_volume_error_mm3'])<1e-10 and r['minimum_radial_wall_bound_mm']>0 for r in records)
    result=dict(status='PASS_FINITE_SOLID_MESH_CONTRACT_ONLY' if good else 'FAIL_FINITE_SOLID_MESH_CONTRACT',part_count=len(records),records=records,units='mm',segments=128,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),source_sha256=sha(Path(__file__)),input_sha256=sha(src),STEP='NOT GENERATED',material=None,mass=None,tolerance=None,assembly_transform='Not applied: local z axis bore; local x points along world_bore_offset, zero eccentricity leaves x arbitrary. Source route/bisector required for assembly.',scope='20 independent through-eyelet STL solids only; terminal anchors absent. Not entire CAD assembly, structural strength, friction, Native force transmission or fabrication-ready. Legacy CAD/Native unchanged.')
    (out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(result['status'],len(records),min(r['minimum_radial_wall_bound_mm'] for r in records),max(abs(r['polygon_volume_error_mm3']) for r in records))
if __name__=='__main__':main()
