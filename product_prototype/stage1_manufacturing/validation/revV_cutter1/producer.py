"""Finite geometric ball-cutter access to actual split receiver pocket.
Tool is a required geometry, not an asserted stocked manufacturer product.
"""
import argparse,json,math,shutil
from incremental_stage1 import ROOT,read,common,sha
from build_stage1 import cyl,fuse
from mechanisms_stage1 import pitch_at
from receiver_fillet_stage1 import beta
from OCP.BRepPrimAPI import BRepPrimAPI_MakeSphere
from OCP.gp import gp_Pnt
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False);rows=[];joins=[]
 ni=read(ROOT/idx['parts']['F0_TIP_FACTORY_NIPPLE']['path'])
 for name,sign in [('SWIVEL_LOWER',-1),('SWIVEL_UPPER',1)]:
  actual=read(ROOT/idx['parts']['F0_'+name]['path']);s=pitch_at(actual,-beta(),(43,0,-92));joins.append(dict(part=name,factory_max_end_intersection_mm3=common(actual,ni)))
  for deg in range(0,181,15):
   t=math.radians(deg);x=43+1.75*math.cos(t);y=sign*1.75*math.sin(t)
   for z in (-81.85,-79.1,-76.35):
    tool=fuse(BRepPrimAPI_MakeSphere(gp_Pnt(x,y,z),.35).Shape(),cyl(.35,(x,y,z),6,(0,-sign,0)))
    v=common(s,tool);rows.append(dict(part=name,semicircle_deg=deg,tool_centre_mm=[x,y,z],retained_material_intersection_mm3=v))
 worst=max(r['retained_material_intersection_mm3'] for r in rows)
 result=dict(status='SAMPLED_RECEIVER_CUTTER_ACCESS_PASS' if worst<1e-7 and all(abs(r['factory_max_end_intersection_mm3'])<1e-7 for r in joins) else 'SAMPLED_RECEIVER_CUTTER_ACCESS_FAIL',case=a.case,required_tool_geometry=dict(ball_R_mm=.35,cutting_D_mm=.7,working_reach_min_mm=2.2,proposed_working_reach_mm=2.5,axis='normal to actual split plane; lower+Y/upper-Y',stock_or_machine_capability='NOT VERIFIED; select tool and inspect shop capability before fabrication'),samples=rows,factory_joins=joins,worst_retained_intersection_mm3=worst,input_sha256=sha(src),scope='78actual finite cutter positions at pocket floor and both rounded ends, bodies unassembled. NOT continuous toolpath generation, cutting-force/chatter/fixture/stocked-tool certification. Shared-contact0volume does not certify machine accuracy.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],samples=len(rows),worst_mm3=worst,joins=joins)))
if __name__=='__main__':main()
