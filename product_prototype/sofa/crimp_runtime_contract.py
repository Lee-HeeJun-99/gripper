"""Measured startup-amortized resource forecast; never a physical validation."""
import argparse,json,xml.etree.ElementTree as ET
from pathlib import Path
from analyse import BASE,sha

def canonical(path,folder):
 root=ET.parse(path).getroot()
 for e in root.iter():
  if e.get('filename'):e.set('filename',e.get('filename').replace(str(folder),'CASE'))
 return ET.tostring(root)

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();short=BASE/'results/crimp_contact1898';long=BASE/'results/crimp_withdrawal1899';s=json.loads((short/'summary.json').read_text());l=json.loads((long/'summary.json').read_text());assert all(d['status']=='VALID_UNBRACED_OBJECT_CONTACT_PREFIX_ONLY' for d in [s,l]);assert canonical(short/'scene.scn',short)==canonical(long/'scene.scn',long),'Only run duration may differ';files=[];mismatch=[]
 for f in short.glob('*.csv'):
  other=long/f.name;data=f.read_bytes();ok=other.read_bytes().startswith(data);files.append(dict(file=f.name,prefix_sha256=sha(f),prefix_identical=ok))
  if not ok:mismatch.append(f.name)
 assert not mismatch,mismatch
 ts=json.loads((short/'preflight.json').read_text())['duration_s'];tl=json.loads((long/'preflight.json').read_text())['duration_s'];slope=(l['process']['runtime_s']-s['process']['runtime_s'])/(tl-ts);startup=s['process']['runtime_s']-slope*ts;assert slope>0 and startup>=0;raw=startup+slope*2.;bounded=raw*1.3;d=dict(status='PASS_BOUNDED_RUNTIME_ESTIMATE_ONLY' if bounded<420 else 'BLOCKED_RUNTIME_FORECAST',short_case=short.name,long_case=long.name,identical_scene_except_output_paths=True,identical_actual_prefix_files=files,observed_runtime_s=[s['process']['runtime_s'],l['process']['runtime_s']],observed_duration_s=[ts,tl],affine_fixed_cost_s=startup,affine_cost_per_simulation_second=slope,full2s_forecast_s=raw,safety_factor=1.3,full2s_with_margin_s=bounded,child_limit_s=420,source_sha256=sha(Path(__file__)),input_sha256={str(f.relative_to(BASE)):sha(f) for f in [short/'summary.json',long/'summary.json',short/'scene.scn',long/'scene.scn']},scope='Two actual identical-prefix runs separate startup/closing cost from subsequent motion. Resource estimate NOT runtime guarantee, physics/PASS or tolerance relaxation. Full run still hard420s/4GiB and preserve timeout evidence. No state checkpoint restart or physics/output removal.');out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps({k:v for k,v in d.items() if k not in ['input_sha256','identical_actual_prefix_files']},indent=2))
if __name__=='__main__':main()
