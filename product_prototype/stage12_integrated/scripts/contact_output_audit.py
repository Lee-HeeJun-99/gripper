"""Independent output-refinement check; energy convergence alone is insufficient."""
import argparse,json
from pathlib import Path
from baseline_registry import ROOT,ref,dump
def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--tag',required=True);a=p.parse_args();source=ROOT/'validation/finger'/a.input/'summary.json';d=json.loads(source.read_text());out=ROOT/'validation/convergence'/a.tag;out.mkdir(parents=True,exist_ok=False);rows=[]
    for angle in sorted(set(round(r['fixture_angle_deg'],8) for r in d['rows'])):
        values=sorted([r for r in d['rows'] if abs(r['fixture_angle_deg']-angle)<1e-8],key=lambda r:r['n']);coarse,fine=values[-2:]
        error=abs(coarse['axial_migration_m']-fine['axial_migration_m'])/max(abs(fine['axial_migration_m']),1e-12)
        rows.append(dict(angle_deg=angle,coarse_n=coarse['n'],fine_n=fine['n'],migration_refinement_relative=error,maximum=.01,status='PASS' if error<.01 else 'FAIL'))
    result=dict(status='PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL',scope='RELEVANT AXIAL MIGRATION OUTPUT, NOT ENERGY-ONLY CONVERGENCE',rows=rows,source=ref(source),producer=ref(Path(__file__)),whole_system_qualified=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
