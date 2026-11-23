"""Changed hardware geometric mass coefficients; actual material/mass remainNULL."""
import argparse,json,subprocess,time
from pathlib import Path
import numpy as np
import trimesh
from manufacturing_assembly import BASE,sha

def tetra_moments(mesh):
 # Signed origin tetrahedra with a nearby reference for cancellation control.
 ref=mesh.vertices.mean(axis=0);tri=mesh.triangles-ref;a,b,c=tri[:,0],tri[:,1],tri[:,2];v=np.einsum('ij,ij->i',a,np.cross(b,c))/6;volume=v.sum()
 if not np.isfinite(volume) or volume<=0:raise ValueError('positive oriented solid required')
 sums=tri.sum(axis=1);centre=np.einsum('i,ij->j',v,sums)/(4*volume)
 second=np.einsum('i,ijk->jk',v,np.einsum('nki,nkj->nij',tri,tri)+np.einsum('ni,nj->nij',sums,sums))/20
 covariance=second/volume-np.outer(centre,centre);inertia=volume*(np.trace(covariance)*np.eye(3)-covariance)
 return float(volume),centre+ref,inertia

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);start=time.monotonic();src=BASE/'results/product_supplier_mount875/summary.json';parent=json.loads(src.read_text());records=[];hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),src)}
 for r in parent['records']:
  file=src.parent/(r['part']+'.stl')
  if sha(file)!=r['STL_sha256']:raise ValueError('saved STL identity changed')
  hashes[str(file.relative_to(BASE))]=sha(file);mesh=trimesh.load_mesh(file)
  if not mesh.is_volume or mesh.body_count!=1:raise ValueError('invalid saved CAD')
  volume,com,I=tetra_moments(mesh);error=float(np.linalg.norm(I-mesh.moment_inertia)/np.linalg.norm(I));com_error=float(np.linalg.norm(com-mesh.center_mass));eig=np.linalg.eigvalsh(I/volume)
  if error>1e-9 or com_error>1e-9 or eig.min()<=0:raise ValueError('independent CAD moments mismatch')
  records.append(dict(part=r['part'],volume_mm3=volume,COM_world_mm=com.tolist(),inertia_COM_per_mass_m2=(I/volume*1e-6).tolist(),principal_inertia_per_mass_m2=(eig*1e-6).tolist(),mass_per_density_m3=volume*1e-9,inertia_COM_per_density_m5=(I*1e-15).tolist(),independent_inertia_relative_error=error,independent_COM_error_mm=com_error,actual_material=None,actual_density_kg_m3=None,actual_mass_kg=None,actual_inertia_kg_m2=None,homogeneous_body_ASSUMPTION=True))
 result=dict(status='GEOMETRIC_MASS_COEFFICIENTS_ONLY_NOT_ACTUAL_MASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes=hashes,records=records,runtime_s=time.monotonic()-start,fabrication_ready=False,scope='Actual saved10changed CAD solids. Explicit signed-tetrahedron moments independently compared to trimesh mass_properties. Uniform-density geometric coefficients only;unknown material,joints,threads,process voids,tolerance and actual mass NOT substituted. No Native tensor or COM frame changed. Not hardware measurement or force/strength validation.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(dict(status=result['status'],parts=len(records),max_inertia_relative_error=max(r['independent_inertia_relative_error'] for r in records),runtime_s=result['runtime_s']),indent=2))
if __name__=='__main__':main()
