"""Finite ground form-tool profile/reach for unassembled turned pulleys."""
import argparse,json,shutil
from incremental_stage1 import ROOT,read,sha,common
from build_stage1 import box,cyl,fuse,translate,export
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());assert idx['design_geometry'].get('broad_groove_floor_radius_mm')==10.93;out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False);rows=[]
 for n,x,z in [('F0_DRUM',80,20),('F0_IDLER',44,25)]:
  floor=z+10.93;tool=fuse(box(x-.5,-.45,floor,1,.90,8),box(x-.5,-.55,floor+.1,1,1.10,7.9))
  for y in (-.45,.45):tool=fuse(tool,cyl(.1,(x-.5,y,floor+.1),1,(1,0,0)))
  tool=fuse(tool,box(x-2.5,-2,floor+8,5,4,30));export(tool,out/(n+'_FORM_TOOL'));q=read(ROOT/idx['parts'][n]['path']);hits=[common(translate(tool,0,0,t),q) for t in (0,.1,.5,1,2,4,8,15)];deeper=common(translate(tool,0,0,-.02),q)
  rows.append(dict(part=n,retained_material_common_mm3=hits,deeper0_02_reference_cut_common_mm3=deeper,blade_width_mm=1.10,flat_width_mm=.90,corner_radius_mm=.10,tangential_blade_thickness_mm=1,neck_height_mm=8,shank_XY_mm=[5,4],minimum_shank_radial_clearance_mm=10.93+8-(17 if n=='F0_DRUM' else 12.5)))
 result=dict(status='BROAD_GROOVE_TOOL_GEOMETRY_PASS' if all(max(abs(v) for v in r['retained_material_common_mm3'])<1e-7 and r['deeper0_02_reference_cut_common_mm3']>1e-7 and r['minimum_shank_radial_clearance_mm']>0 for r in rows) else 'BROAD_GROOVE_TOOL_GEOMETRY_FAIL',case=a.case,checks=rows,input_sha256=sha(src),scope='Finite custom ground HSS/carbide form-tool envelope and eight radial approach samples on UNASSEMBLED turning stock/part. Shape provided for manufacture/profile inspection, NOT an asserted purchased SKU, measured tool stiffness/feeds/chatter/finish or actual machining. Ground flat>=0.900, cornerR<=0.100, inspect finished root21.850..21.860 at20+-1C; actual shop capability must be accepted before cutting.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],checks=rows)))
if __name__=='__main__':main()
