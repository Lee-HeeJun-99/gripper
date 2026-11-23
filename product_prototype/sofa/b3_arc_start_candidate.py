"""One-variable manufactured curvature distribution candidate;CAD/REST only."""
import argparse,copy,json,subprocess
from pathlib import Path
import numpy as np
from mechanism_candidates import BASE,export,world
from analyse import sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/b3_alarm_window485/config.json';baseline=json.loads(src.read_text());candidate=copy.deepcopy(baseline);assert baseline['finger']['precurve']['start_mm']==70;candidate['finger']['precurve']['start_mm']=60;records={}
 for name,c in [('baseline70',baseline),('distributed60',candidate)]:
  report=export(name,c,out/name);q=np.array([world(c,[x,0,.1]) for x in np.linspace(0,100,101)]);records[name]=dict(initial_checks=report,width_mean_centre_tip_mm=q[-1].tolist(),manufactured_curvature_rad_per_mm=float(np.deg2rad(40)/(100-c['finger']['precurve']['start_mm'])),STL_hashes={f.name:sha(f) for f in (out/name).glob('*.stl')})
 d=dict(status='MANUFACTURED_GEOMETRY_CANDIDATE_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),hypothesis='100g early1.0–1.2s Skin support0.70645N<0.981N before iteration saturation. Distribute SAME40deg curvature over60–100mm to increase inward reach without increasing force/friction.',single_change='precurve.start_mm70→60;all other config values identical',source_config_sha256=sha(src),records=records,tip_change_mm=(np.array(records['distributed60']['width_mean_centre_tip_mm'])-records['baseline70']['width_mean_centre_tip_mm']).tolist(),physical_validation='NOT QUALIFIED',Holding='NOT RUN',Native='BLOCKED: full model time/mesh convergence and actual joint qualification fail;do not infer force capacity from REST geometry',scope='Parametric source+actualSTL+initial triangle/wire/conservative guide checks only;not complete assembly,motion,self-collision,pressure or grasp proof',next='Preserve static rejection if any;independent pressure/friction layer coupon next.');(out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(d,indent=2));print(json.dumps(d))
if __name__=='__main__':main()
