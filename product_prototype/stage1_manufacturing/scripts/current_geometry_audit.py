"""Actual latest part topology/mesh and finite heel tool audit."""
import argparse,json,shutil,math
import trimesh
from incremental_stage1 import ROOT,read,sha,common
from build_stage1 import cyl,export
from mechanisms_stage1 import pitch_at
from receiver_fillet_stage1 import beta
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';j=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False);rows=[];tools=[]
 for n,v in j['parts'].items():
  f=ROOT/v['path'];q=read(f);ex=TopExp_Explorer(q,TopAbs_SOLID);count=0
  while ex.More():count+=1;ex.Next()
  m=trimesh.load(f.with_suffix('.stl'),force='mesh');rows.append(dict(part=n,actual_STEP_SHA256=sha(f),indexed_SHA256=v['sha256'],BRep_valid=BRepCheck_Analyzer(q).IsValid(),solid_count=count,STL_closed=m.is_watertight,STL_winding=m.is_winding_consistent,STL_positive_volume_mm3=float(m.volume),actual_STL_SHA256=sha(f.with_suffix('.stl'))))
 for n,start,end in [('F0_SWIVEL_LOWER',-10,-2.5),('F0_SWIVEL_UPPER',2.5,10)]:
  q=pitch_at(read(ROOT/j['parts'][n]['path']),-beta(),(43,0,-92));hits=[]
  for x in (37,37.5,38,38.5):
   for z in (-91.5,-91,-90.5,-90,-89.5):
    cutter=cyl(.5,(x,start,z),end-start,(0,1,0));v=common(q,cutter);hits.append(v)
  export(pitch_at(cutter,beta(),(43,0,-92)),out/(n+'_HEEL_CUTTER'))
  tools.append(dict(part=n,actual_cutter_D_mm=1,axis_Y_range_mm=[start,end],positions=len(hits),max_retained_material_common_mm3=max(hits)))
 minima=dict(pivot_web_mm=(43-.05)-3.05/2-(39+.10),bolt_web_mm=(-86.5-.05)-2.25/2-(-89+.10),half_remaining_mm=2.99-(.5+.1))
 ok=all(r['actual_STEP_SHA256']==r['indexed_SHA256'] and r['BRep_valid'] and r['solid_count']==1 and r['STL_closed'] and r['STL_winding'] and r['STL_positive_volume_mm3']>0 for r in rows) and all(r['max_retained_material_common_mm3']<1e-7 for r in tools) and min(minima.values())>0
 result=dict(status='CURRENT_GEOMETRY_AND_HEEL_TOOL_PASS' if ok else 'CURRENT_GEOMETRY_AND_HEEL_TOOL_FAIL',case=a.case,parts=rows,heel_tools=tools,conditional_selected_web_minima_mm=minima,input_sha256=sha(src),scope='Actual304native BRep valid/single solids and closed positive STLs; finite1mm cutter at20positions per half. Selected protected-interface web intervals only, NOT exhaustive minimum-wall/offset/FEM/physical process capability or cutting forces. Actual dimensions remain NOT MEASURED.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],parts=len(rows),tool_checks=tools,minima=minima)))
if __name__=='__main__':main()
