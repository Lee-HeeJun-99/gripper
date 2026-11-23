"""Construction-specific manufacturer bend recommendation vs actual CAD design input."""
import argparse,json,subprocess
from pathlib import Path
from manufacturing_assembly import BASE,sha

def check(wire,ratio,barrel_radius):
 if min(wire['uncoated_diameter_mm'],ratio,barrel_radius)<=0:raise ValueError('positive dimensions required')
 required=wire['uncoated_diameter_mm']*ratio;actual=2*barrel_radius
 return dict(item=wire['item'],construction=wire['construction'],wire_diameter_mm=wire['uncoated_diameter_mm'],minimum_recommended_groove_root_diameter_mm=required,actual_groove_root_diameter_mm=actual,diameter_margin_mm=actual-required,status='MEETS_CATALOG_BEND_DIAMETER_ONLY' if actual>=required else 'FAIL_CATALOG_BEND_COMPATIBILITY',physical_fatigue_pass=False)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);cfgfile=BASE/'config/wire_bend_supplier_v40.json';cfg=json.loads(cfgfile.read_text());records=[check(w,cfg['minimum_recommended_B_over_uncoated_d'][w['construction']],cfg['current_geometry']['barrel_radius_mm']) for w in cfg['candidate_wires']]
 result=dict(status='SUPPLIER_COMPATIBILITY_AUDIT_NOT_PRODUCT_QUALIFICATION',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x.relative_to(BASE)):sha(x) for x in (Path(__file__),cfgfile,BASE/'cad/root_thrust_candidate.py')},records=records,current_CAD_wire_diameter_mm=.5,catalog_candidate_wire_diameter_mm=.45,source_urls=[cfg['pulley_source_url'],cfg['wire_source_url']],scope='NEW supplier-specific incompatibility screen,NOT a retroactive change to prior simulation or geometry PASS/FAIL. Uses actual V39 barrelR1.75 definition from root_thrust_candidate.wheel. Pitch radius2 and flangeOD6 must not substitute for groove-root diameter. No exact life,material,friction or exception data.',fabrication_ready=False)
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(records,indent=2))
if __name__=='__main__':main()
