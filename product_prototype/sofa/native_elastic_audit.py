"""Read-only Raw audit, exact axial patch comparison and measured static plots."""
import argparse,csv,json,re,subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from native_bending_coupon import BASE,ROOT,sha

CASES=['native_solid_baseline380','native_static_conditioning381','native_solid_halfload382',
       'native_solid_cross5_383','native_solid_cross5_384','native_solid_assess385','native_hexa_fine386',
       'native_beam_probe387','native_beam_small388','native_traction_cross3_389',
       'native_traction_cross5_390','native_traction_assess391','native_bending_components392',
       'native_axial_patch393','native_static_eigen394']

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    csv.field_size_limit(64*1024*1024)
    out=BASE/'results'/a.tag;out.mkdir(exist_ok=False)
    patch=BASE/'results/native_axial_patch393';meta=json.loads((patch/'summary.json').read_text());checks=[]
    for record in meta['records']:
        d=patch/f"{record['model']}_{record['nx']}";scene=ET.parse(d/'scene.scn')
        q=np.fromstring(scene.find('.//MechanicalObject').get('position'),sep=' ').reshape(-1,3)
        expected=q.copy();expected[:,0]+=meta['force_N']*q[:,0]/(meta['E_Pa']*.01*.01)
        rows=list(csv.DictReader((d/'states.csv').open()))
        error=max(float(np.max(abs(np.fromstring(row['q'],sep=' ').reshape(-1,3)-expected))) for row in rows)
        checks.append(dict(model=record['model'],nx=record['nx'],all_nodes_all_static_outputs_error_m=error,
                           gate_m=1e-12,status='PASS_AXIAL_PATCH_ONLY' if record['status']=='COMPLETED_STATIC_DIAGNOSTIC' and error<=1e-12 else 'FAIL'))
    prior_path=BASE/'reports/evidence_native_mechanism_v5/manifest.json'
    prior=json.loads(prior_path.read_text());mismatches=[];count=0
    for name,digest in prior['files'].items():
        if not (name.startswith('product_prototype/results/') or any(name.startswith('product_prototype/'+part) for part in ('meshes/','drawings/','cad/build_','sofa/scenes/'))):continue
        count+=1;path=ROOT/name
        if not path.is_file() or sha(path)!=digest:mismatches.append(name)
    files={};cases={}
    for name in CASES:
        folder=BASE/'results'/name
        for path in folder.rglob('*'):
            if path.is_file():files[str(path.relative_to(ROOT))]=sha(path)
        summary=folder/'summary.json'
        cases[name]=dict(summary_sha256=sha(summary) if summary.exists() else None,
                         completion='HAS_SUMMARY' if summary.exists() else 'HARNESS_CSV_FIELD_LIMIT_FAILURE_NOT_COMPLETED')
    sdk=Path('/home/ubuntu/SOFA/v26.06.00')
    identities={str(path):sha(path) for path in [sdk/'bin/runSofa-26.06.00']+list((sdk/'lib').glob('libSofa.Component.SolidMechanics.FEM.Elastic.so*')) if path.is_file()}
    fig,ax=plt.subplots(figsize=(8,5))
    for name in ('native_traction_cross3_389','native_traction_cross5_390'):
        data=json.loads((BASE/'results'/name/'summary.json').read_text())
        for model in ('tetra','hexa'):
            rows=[r for r in data['records'] if r['model']==model and 'tip_m' in r]
            ax.plot([r['nx'] for r in rows],[r['tip_m']*1000 for r in rows],'-o',label=f"{model}; cross={data['cross_nodes']}")
    ax.axhline(.4,color='gray',linestyle='--',label='Euler beam approximation, not exact 3-D')
    ax.set(xlabel='Longitudinal nodes',ylabel='Actual native static mean tip displacement [mm]',
           title='Straight 100×10×10 mm beam; 1mN; E=1MPa, ν=.3\nNative small FEM/StaticSolver; mesh gate NOT passed')
    ax.legend(fontsize=8);fig.tight_layout();fig.savefig(out/'actual_static_mesh.png',dpi=160);fig.savefig(out/'actual_static_mesh.svg');plt.close(fig)
    result=dict(scope='Native validation diagnostics only; B3 functional results preserved but NOT certified',
                source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                source_sha256=sha(Path(__file__)),sdk_identities=identities,
                prior_immutable=dict(manifest_sha256=sha(prior_path),checked=count,mismatches=mismatches,
                                     status='PASS_BYTE_PRESERVATION_ONLY' if not mismatches else 'FAIL'),
                axial_patch=checks,cases=cases,files=files,
                b3_time_gate='FAIL_PRESERVED',b3_mesh_gate='FAIL_PRESERVED',
                root_reaction_work=None,native_strain_energy=None,physical_fabrication='NOT_QUALIFIED')
    (out/'producer.py').write_bytes(Path(__file__).read_bytes())
    (out/'summary.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(dict(axial_patch=checks,prior=result['prior_immutable'],raw_files=len(files)),indent=2))
    if mismatches:raise SystemExit('Immutable evidence mismatch')

if __name__=='__main__':main()
