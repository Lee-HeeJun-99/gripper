"""Actual native dimensions, axial load-path topology and conditional shim gap."""
import argparse,json,math,shutil
from incremental_stage1 import ROOT,read,bounds,sha
from fastener_joint_contract import cylinders,project_interval
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 parts={n:read(ROOT/v['path']) for n,v in idx['parts'].items() if n.startswith('F0_')};bb={n:bounds(s) for n,s in parts.items()}
 def width(n):return bb['F0_'+n][4]-bb['F0_'+n][1]
 updated=idx['design_geometry'].get('receiver_preload_sleeve',False)
 fork_faces=[project_interval(c,[0,1,0]) for c in cylinders(parts['F0_TERMINAL_FRONT']) if abs(c['r']-1.1)<1e-6 and abs(c['origin'][0]-43)<1e-6 and abs(c['origin'][2]+92)<1e-6];fork_faces.sort();assert len(fork_faces)==2,fork_faces;fork_gap=fork_faces[1][0]-fork_faces[0][1]
 if updated:
  journals=[project_interval(c,[0,1,0]) for c in cylinders(parts['F0_IDLER_AXLE']) if abs(c['r']-1.5)<1e-6 and 'FORWARD' in c['orientation']];assert len(journals)==1,journals;journal=journals[0]
  idler_gap=(journal[1]-journal[0])-width('IDLER')-width('IDLER_SPACER_L')-width('IDLER_SPACER_R')
  receiver_gap=width('SWIVEL_SLEEVE')-width('SWIVEL_LOWER')-width('SWIVEL_UPPER')-width('SWIVEL_SPACER_L')-width('SWIVEL_SPACER_R')
  runout=[]
  for n,expected in [('IDLER_AXLE',[-3,-2.5]),('SWIVEL_AXLE',[5,5.5])]:
   rr=[project_interval(c,[0,1,0]) for c in cylinders(parts['F0_'+n]) if abs(c['r']-.775)<1e-6];runout.append(dict(part=n,actual_relief_intervals_mm=rr,expected_mm=expected,verified=any(max(abs(x-y) for x,y in zip(t,expected))<1e-6 for t in rr)))
  contacts=dict(idler_shoulder_Y_mm=journal[0],actual_idler_journal_Y_mm=journal,actual_fork_bearing_faces_Y_mm=fork_faces,actual_fork_gap_mm=fork_gap,idler_shoulder_washer_Y_mm=[bb['F0_IDLER_SHOULDER_WASHER'][1],bb['F0_IDLER_SHOULDER_WASHER'][4]],idler_outer_washer_Y_mm=[bb['F0_IDLER_CLAMP_WASHER'][1],bb['F0_IDLER_CLAMP_WASHER'][4]],receiver_sleeve_Y_mm=[bb['F0_SWIVEL_SLEEVE'][1],bb['F0_SWIVEL_SLEEVE'][4]],receiver_outer_washer_Y_mm=[bb['F0_SWIVEL_SPACER_OUT'][1],bb['F0_SWIVEL_SPACER_OUT'][4]])
  axial_offset=.035/2+.005;groove_margin=.30-(.26+math.hypot(.03,axial_offset));port_margin=.39-.26-axial_offset
  passed=abs(idler_gap-.03)<1e-6 and abs(receiver_gap-.03)<1e-6 and abs(width('SWIVEL_SLEEVE')-fork_gap)<1e-6 and all(r['verified'] for r in runout) and abs(contacts['idler_shoulder_washer_Y_mm'][1]-journal[0])<1e-6 and abs(contacts['idler_outer_washer_Y_mm'][1]+5)<1e-6 and abs(contacts['receiver_outer_washer_Y_mm'][1]-5.5)<1e-6 and groove_margin>0 and port_margin>0
  status='METAL_PRELOAD_BYPASS_DESIGN_PASS' if passed else 'METAL_PRELOAD_BYPASS_DESIGN_FAIL'
 else:
  idler_gap=(bb['F0_IDLER_NUT'][1]-bb['F0_IDLER_SPACER_L'][1])-width('IDLER')-width('IDLER_SPACER_L')-width('IDLER_SPACER_R')
  receiver_gap=fork_gap-width('SWIVEL_LOWER')-width('SWIVEL_UPPER')-width('SWIVEL_SPACER_L')-width('SWIVEL_SPACER_R');runout=[];contacts=dict(actual_fork_bearing_faces_Y_mm=fork_faces,actual_fork_gap_mm=fork_gap);axial_offset=None;groove_margin=None;port_margin=None;status='ZERO_RUNNING_GAP_AND_PRELOAD_PATH_FAIL'
 result=dict(status=status,case=a.case,actual_native_nominal_idler_running_gap_mm=idler_gap,actual_native_nominal_receiver_running_gap_mm=receiver_gap,actual_reliefs=runout,metal_contact_planes=contacts,conditional_matched_gap_acceptance_mm=[.025,.035],conditional_groove_midplane_acceptance_mm=[-.005,.005],conditional_max_axial_offset_mm=axial_offset,conditional_maxwire_axial_groove_margin_mm=groove_margin,conditional_wire_port_margin_mm=port_margin,scope='Actual native nominal dimensions and specified metal path, NOT measured preload/friction/free-spin. Old0gap is geometric risk, NOT a fabricated seized-hardware result. New shim/sleeve lengths must be MATCHED to actual fork/body/journal dimensions and inspected after locking. Axial-groove bound assumes nominal radial geometry, not all combined manufacturing/FEM tolerances.',input_sha256=sha(src),hardware='NOT MEASURED',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(result))
if __name__=='__main__':main()
