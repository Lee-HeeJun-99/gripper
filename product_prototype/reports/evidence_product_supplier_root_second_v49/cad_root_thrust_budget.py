"""Separated-factor endplay/side-gap budget;not a manufacturing fit approval."""
import argparse,json,subprocess
from pathlib import Path
from manufacturing_assembly import BASE,sha

def budget(span,wheel,groove,wire,misalignment,errors):
 if min(span,wheel,groove,wire)<=0 or misalignment<0 or any(x<0 for x in errors.values()):raise ValueError('invalid dimensional bounds')
 gap=span-wheel;variation=errors.get('fork_span',0)+errors.get('wheel_width',0)
 side=(groove-errors.get('groove_width',0)-wire-errors.get('wire_diameter',0))/2
 minimum=gap-variation;wander=(gap+variation)/2;margin=side-wander-misalignment
 return dict(minimum_axial_clearance_mm=minimum,maximum_centered_wander_mm=wander,available_wire_side_mm=side,old_motion_misalignment_mm=misalignment,strict_alignment_margin_mm=margin,conditional_nonbinding_and_alignment=minimum>0 and margin>0)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);cfgfile=BASE/'config/root_thrust_v37.json';motionfile=BASE/'results/product_root_motion793/summary.json';cfg=json.loads(cfgfile.read_text());motion=json.loads(motionfile.read_text());mis=max(r['worst']['axial_bound_mm'] for r in motion['records'])-cfg['wire_diameter']/2;records=[]
 for name,lands,wide in [('baseline',False,False),('lands_only',True,False),('wide_only',False,True),('combined',True,True)]:
  span=cfg['land_fork_span'] if lands else cfg['old_fork_span'];groove=cfg['new_groove_width'] if wide else cfg['old_groove_width']
  for case,errors in [('nominal',{}),('ASSUMED_NOT_MEASURED',cfg['ASSUMED_symmetric_tolerance_bounds'])]:records.append(dict(candidate=name,condition=case,**budget(span,cfg['wheel_width'],groove,cfg['wire_diameter'],mis,errors)))
 d=dict(status='CONDITIONAL_ROOT_STACK_FACTORIAL_NOT_QUALIFICATION',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x.relative_to(BASE)):sha(x) for x in (Path(__file__),cfgfile,motionfile)},records=records,actual_endplay_mm=None,actual_process_capability_mm=None,scope='Four-factorial geometric hypotheses keep pitchR2/OD6/wireD0.5 andOLD793motion. Worst axialwander added conservatively toOLDmisalignment. Assumederrors are illustrative,not shop/ISO/supplier/physical data. No friction/load-deflection/wear/pullout certification;old770FAIL preserved.',fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
