"""Source-aware minimum-stock length/full-nut overlap design bounds."""
import argparse,json,shutil
from manufacturing_packet import ROOT
def overlap(a,b):return max(0,min(a[1],b[1])-max(a[0],b[0]))
def main():
 p=argparse.ArgumentParser();p.add_argument('--joints',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'validation'/a.joints/'summary.json';j=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False);rows=[]
 std={4:.24,6:.24,8:.29,10:.29,12:.35,14:.35,16:.35,18:.35,20:.42,50:.50}
 for r in j['rows']:
  n=r['screw']
  if 'BOLT' not in n or 'SWIVEL_BOLT' in n:continue
  span=r['actual_shank_interval_mm'];length=span[1]-span[0];csk=n.startswith(('F0_TERMINAL_FLUSH_BOLT','F0_CAP_L_BOLT'));nominal=10 if 'TERMINAL_FLUSH' in n else 6 if n.startswith('F0_CAP_L_BOLT') else round(length)
  delta=.30 if csk else std[nominal];basis='DRAWING procurement acceptance+-0.30, NOT a claimed DIN7991 catalogue tolerance' if csk else 'Bollhoff DIN912/A2 manufacturer length limits, selected nominal length'
  grip=.25 if n.startswith(('F0_ROOT_BOLT','F0_TERMINAL_FLUSH_BOLT')) else .20 if any(m['kind']=='nut' for m in r['partners']) else .10
  side=r['head_side'];assert side in (-1,1);short=[span[0]+delta,span[1]] if side==1 else [span[0],span[1]-delta]
  for m in r['partners']:
   if m['kind']=='nut':
    nt=[v-side*grip for v in m['axial_interval_mm']];eng=overlap(short,nt);margin=(nt[0]-short[0]) if side==1 else (short[1]-nt[1]);ok=margin>=0 and eng>=m['nut_axial_extent_mm']-1e-6
    rows.append(dict(screw=n,partner=m['part'],kind='full_nut_at_shortest_stock_and_max_grip',nominal_L_mm=nominal,stock_minus_mm=delta,extra_grip_mm=grip,minimum_full_nut_tip_margin_mm=margin,full_nut=ok,basis=basis))
   else:rows.append(dict(screw=n,partner=m['part'],kind='positive_tapped_overlap_only_NOT_strength',minimum_axial_overlap_design_mm=m['engagement_mm']-delta-grip,full_nut=m['engagement_mm']>delta+grip,basis=basis))
 motor=dict(stock_M3x6_mm=[5.76,6.24],plate_mm=[2.9,3.1],minimum_thread_depth_mm=4.5,engagement_design_mm=[5.76-3.1,6.24-2.9],minimum_bottom_margin_mm=4.5-(6.24-2.9),scope='Source-standard length bound corrects earlier S-transfer assumption2.8..3.2; actual bounds2.66..3.34. Old raw not modified.')
 long=dict(M3x50_source_nominal_thread_b_mm=18,required_incoming_fully_formed_tip_thread_span_min_mm=8,maximum_design_nut_span_from_tip_mm=6.7,scope='Manufacturer b18 reference plus incoming8mm design inspection, NOT measured supplier thread. Do not assume every50mm shank is fully threaded.')
 result=dict(status='STOCK_LENGTH_ENGAGEMENT_DESIGN_PASS' if rows and all(r['full_nut'] for r in rows) and motor['minimum_bottom_margin_mm']>0 and long['required_incoming_fully_formed_tip_thread_span_min_mm']>long['maximum_design_nut_span_from_tip_mm'] else 'STOCK_LENGTH_ENGAGEMENT_DESIGN_FAIL',case=j['case'],checks=rows,motor_mount=motor,long_screw=long,source_url='https://uk.misumi-ec.com/pdf/ds/AAU1/AAU1_DIN_912_Edelstahl_A2_data_sheet_en1.pdf',scope='Conditional manufactured stack/length bounds and full-nut geometry. CSK procurement acceptance explicit. Custom axles, matched screws/fine nuts use drawing-specific runout/gap contracts. Does NOT check all tail-to-foreign collisions, certify strength/preload or replace actual inspection.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],checks=len(rows),minimum_nut_tip_margin_mm=min(r['minimum_full_nut_tip_margin_mm'] for r in rows if 'minimum_full_nut_tip_margin_mm' in r),motor_bottom_margin_mm=motor['minimum_bottom_margin_mm'],failed=[r for r in rows if not r['full_nut']])))
if __name__=='__main__':main()
