"""Analysis-only unit-conditioned wrapper for trimesh closest_point.
Does not change the library tolerance,SOFA,contact forces or any physical state.
Rejects degenerate triangles rather than adding a denominator floor.
"""
import argparse,inspect,json
from pathlib import Path
import numpy as np
import trimesh
from analyse import BASE,sha
def closest(triangles,points):
 t=np.asarray(triangles,dtype=float);p=np.asarray(points,dtype=float)
 if t.shape!=(len(p),3,3) or p.shape!=(len(p),3):raise ValueError('invalid triangle/point shape')
 a=t[:,0];e1=t[:,1]-a;e2=t[:,2]-a;scale=np.maximum.reduce([np.linalg.norm(e1,axis=1),np.linalg.norm(e2,axis=1),np.linalg.norm(t[:,2]-t[:,1],axis=1)])
 if np.any(scale<=0) or np.any(np.linalg.norm(np.cross(e1,e2),axis=1)==0) or not np.all(np.isfinite(t)) or not np.all(np.isfinite(p)):raise ValueError('degenerate or undefined analysis geometry')
 normalized=(t-a[:,None,:])/scale[:,None,None];q=(p-a)/scale[:,None];result=trimesh.triangles.closest_point(normalized,q)
 return a+result*scale[:,None]
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 cases=[([.3,.3,.2],[.3,.3,0]),([.7,.3,0],[.7,.3,0]),([-.2,.3,0],[0,.3,0]),([1,1,0],[.5,.5,0]),([-.1,-.1,.1],[0,0,0])]
 for size in (1.,1e-3,1e-6):
  for origin in (np.zeros(3),np.array([.1,-.03,.08])):
   tri=origin+size*np.array([[0,0,0],[1,0,0],[0,1,0]])
   for point,reference in cases:
    q=origin+size*np.array(point);expected=origin+size*np.array(reference);raw=trimesh.triangles.closest_point(tri[None,:],q[None,:])[0];actual=closest(tri[None,:],q[None,:])[0];error=float(np.linalg.norm(actual-expected));records.append(dict(size_m=size,origin_m=origin.tolist(),expected_m=expected.tolist(),raw_coordinate_error_m=float(np.linalg.norm(raw-expected)),conditioned_coordinate_error_m=error,coordinate_error_divided_by_exact_size=error/size))
 rejected=False
 try:closest(np.zeros((1,3,3)),np.zeros((1,3)))
 except ValueError:rejected=True
 source=Path(inspect.getfile(trimesh.triangles));result=dict(status='PASS_ANALYSIS_WRAPPER_REFERENCES_ONLY' if rejected and max(r['coordinate_error_divided_by_exact_size'] for r in records)<1e-9 else 'FAIL_ANALYSIS_REFERENCE',scope='Analytic triangle projections at m/mm/um scales. Same inputs/outputs SI,internal nondimensionalization only. Not a SOFA solver,physical tolerance relaxation or Native time/energy PASS.',source_sha256=sha(Path(__file__)),library_source_path=str(source),library_source_sha256=sha(source),library_version=trimesh.__version__,library_zero_tolerance_unchanged=trimesh.constants.tol.zero,degenerate_rejected=rejected,records=records)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='records'},indent=2))
if __name__=='__main__':main()
