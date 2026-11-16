"""Mesh numerical checks and actual SOFA load;NOT shell/grasp verification."""
import argparse,json,math
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
def main():
 p=argparse.ArgumentParser();p.add_argument('--version',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
 out=ROOT/'results'/('autonomous_design_'+a.tag);out.mkdir(exist_ok=False);summary={}
 sdk=ROOT/'build/grasp_20261115/sofa_patched'
 for name in ('film_contact','selective_jamming'):
  folder=ROOT/'designs'/name/a.version;vertices=[];faces=[]
  for line in(folder/'rest.obj').read_text().splitlines():
   s=line.split()
   if s and s[0]=='v':vertices.append(list(map(float,s[1:])))
   if s and s[0]=='f':faces.append([int(x)-1 for x in s[1:]])
  area=0
  for f in faces:
   x,y,z=[vertices[i]for i in f];u=[y[j]-x[j]for j in range(3)];v=[z[j]-x[j]for j in range(3)];w=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];tri=.5*math.sqrt(sum(t*t for t in w))
   if tri<=0:raise ValueError('degenerate triangle')
   area+=tri
  if len(vertices)!=315 or len(faces)!=480 or abs(area-6300)>1e-6:raise ValueError('mesh geometry invariant')
  stage=logged([sdk/'bin/graph_probe',sdk,folder/'geometry.scn','1','0'],out/name,120)
  log=(out/name/'stdout.log').read_text()+(out/name/'stderr.log').read_text()
  summary[name]=dict(status='PASS'if stage['exit_code']==0 and '[ERROR]'not in log else'FAIL',scope='SOFA geometry loading ONLY,1animation step without mechanical integrator',vertices=len(vertices),triangles=len(faces),undeformed_surface_area_mm2=area,mesh_sha256=sha(folder/'rest.obj'),scene_sha256=sha(folder/'geometry.scn'),process=stage)
 write_json(out/'summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
