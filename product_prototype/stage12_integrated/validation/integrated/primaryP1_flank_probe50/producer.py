"""Independent closest-surface and occupancy audit of failed actual P1 flank site."""
import sys,json,math,shutil
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read
from validate_thread49f import classification
from OCP.gp import gp_Pnt
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

def main():
 out=ROOT/'validation/integrated/primaryP1_flank_probe50';out.mkdir();shutil.copyfile(__file__,out/'producer.py');src=ROOT/'validation/integrated/primaryP1_flank50/summary.json';d=json.loads(src.read_text());cp=REPO/d['candidate']['path'];assert sha(cp)==d['candidate']['SHA256'];r=d['actual_pair']['nut'];assert sha(REPO/r['path'])==r['SHA256'];n=read(REPO/r['path']);failed=[r for r in d['classification'] if r['nut_across']!=r['expected_nut']];rows=[]
 for fail in failed:
  xx,yy,z=fail['point_mm'];x=-59.;y=-58.;radius=math.hypot(xx-x,yy-y);theta=math.atan2(yy-y,xx-x)
  for da in [-.01,-.001,0,.001,.01]:
   p=[x+radius*math.cos(theta+da),y+radius*math.sin(theta+da),z+.8/(2*math.pi)*da];dist=BRepExtrema_DistShapeShape(BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex(),n);dist.Perform();assert dist.IsDone();closest=dist.PointOnShape2(1);probes=[]
   for dz in [-.01,-.001,-.0001,0,.0001,.001,.01]:probes.append(dict(dz_mm=dz,state=classification(n,[p[0],p[1],p[2]+dz])))
   rows.append(dict(delta_theta_rad=da,point_mm=p,distance_to_actual_surface_mm=dist.Value(),closest_surface_mm=[closest.X(),closest.Y(),closest.Z()],probes=probes))
 dump(out/'summary.json',dict(status='ACTUAL_P1_FLANK_BINDING_DISCREPANCY_PRESERVED',candidate=ref(cp),producer=ref(out/'producer.py'),failed_map=ref(src),failed_sites=failed,actual_nut=r,rows=rows,whole_system_release=False,newly_qualified_system_gate_ids=[],accepted_product_equilibria=0,note='Diagnostic only. Original analytic finite-patch traction map remains FAIL;no pressure/capacity approval or tolerance relaxation. Require trimmed actual-face integration and independent virtual work before installed torque/loadsplit.'))
 print(json.dumps(rows),flush=True)
if __name__=='__main__':main()
