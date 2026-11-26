"""Documented full-tool reach bound, without asserting material removal rate."""
import argparse,json,math,shutil
from manufacturing_packet import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'config/RECEIVER_CUTTER_SOURCE.json';s=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 depth=2.1;clear=s['under_neck_length_mm']-depth;neck=s['neck_diameter_mm']/2;tool_bound=.35
 result=dict(status='CATALOGUE_TOOL_REACH_BOUND_PASS' if clear>0 and neck<=tool_bound and s['radius_mm']==.35 else 'FAIL',manufacturer_source=s,max_split_plane_depth_mm=depth,under_neck_to_split_plane_margin_mm=clear,actual_neck_radius_mm=neck,tested_conservative_cylinder_radius_mm=tool_bound,scope='Receiver halves machined SEPARATELY from their split faces: taper and4mm shank start at least1.9mm outside that half. Tested R0.35 cylinder contains0.33neck. Catalogue0.5mm is cutting-edge length; under-neck4mm is reach, not flute. Rough then3D ball contour; no cutting force/feeds/fixture/chatter/actual shop certification.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(result))
if __name__=='__main__':main()
