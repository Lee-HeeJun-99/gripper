"""Publish bounded native elastic diagnostics with immutable Raw hashes and figures."""
import argparse,json,shutil,subprocess
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from native_bending_coupon import BASE,ROOT,sha
from native_elastic_audit import CASES

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=BASE/'reports'/a.tag;out.mkdir(exist_ok=False)
    cases=CASES+['native_elastic_audit395','native_pure_bending396','native_hexa_inventory397',
                'native_pure_bending_thin398','native_hexa_thin_inventory399',
                'native_matrix_assess401','native_matrix_assess402','native_static_large403']
    files={};processes=[]
    for name in cases:
        folder=BASE/'results'/name
        summary=folder/'summary.json'
        if summary.exists():shutil.copy2(summary,out/f'{name}.json')
        for f in folder.rglob('*'):
            if f.is_file():files[str(f.relative_to(ROOT))]=sha(f)
        for f in folder.glob('*/process/result.json'):
            process=json.loads(f.read_text());processes.append(dict(path=str(f.relative_to(ROOT)),
                status=process['process_status'],runtime_s=process['runtime_s']))
    inputs={};pairs=[];prediction=[];fig,ax=plt.subplots(figsize=(8,5))
    for name,thickness in [('native_pure_bending396',.01),('native_pure_bending_thin398',.005)]:
        data=json.loads((BASE/'results'/name/'summary.json').read_text());inputs[name]=sha(BASE/'results'/name/'summary.json')
        for model in ('tetra','hexa'):
            for cross in (3,5):
                rows=[r for r in data['records'] if r['model']==model and r['cross']==cross and 'tip_m' in r]
                if not rows:continue
                ax.plot([r['nx'] for r in rows],[100*r['relative_field_error'] for r in rows],'-o',label=f'{model}, h={thickness*1000:g}mm,cross{cross}')
                for i,x in enumerate(rows):
                    if model=='hexa' and cross==3:
                        dx=.1/(x['nx']-1);ratio=1/(1+.5*(dx/thickness)**2)
                        prediction.append(dict(case=name,nx=x['nx'],restricted_Q1_kinematic_tip_m=data['exact_tip_m']*ratio,
                                               actual_tip_m=x['tip_m'],difference_m=abs(x['tip_m']-data['exact_tip_m']*ratio)))
                    for y in rows[i+1:]:
                        error=abs(x['tip_m']-y['tip_m'])/max(abs(x['tip_m']),abs(y['tip_m']))
                        pairs.append(dict(case=name,model=model,cross=cross,nx=[x['nx'],y['nx']],relative=error,
                                          gate=.01,status='PASS_PAIR_ONLY' if error<=.01 else 'FAIL_MESH_GATE'))
    ax.axhline(1,color='gray',linestyle='--',label='1% field-error reference line (not all-pair approval)')
    ax.set(xlabel='Longitudinal nodes',ylabel='Actual full-field error against exact linear solution [%]',
           title='Native pure bending; ν=0, E=1MPa, κ=.01/m\nStraight reference coupons only; B3 NOT certified')
    ax.legend(fontsize=6,ncol=2);fig.tight_layout();fig.savefig(out/'actual_pure_bending.png',dpi=170);fig.savefig(out/'actual_pure_bending.svg');plt.close(fig)
    prior=json.loads((BASE/'results/native_elastic_audit395/summary.json').read_text())
    result=dict(scope='Published native elastic diagnostics; NOT B3/grasp/fabrication qualification',
                source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                source_sha256=sha(Path(__file__)),prior_immutable_audit=prior['prior_immutable'],
                prior_audit_sha256=sha(BASE/'results/native_elastic_audit395/summary.json'),
                sdk_identities=prior['sdk_identities'],axial_patch=prior['axial_patch'],
                inputs=inputs,mesh_pairs=pairs,restricted_kinematic_prediction=prediction,
                native_processes=processes,files=files,
                failed_harness='383 CSV field-size limit: raw retained; no summary/completion;fixed prospectively384',
                physical_gate='FAIL_MESH_AND_TIME_PRESERVED; NO B3 PROMOTION')
    observer=BASE/'cad/build_elastic_observer400/libReGripElasticObserver.so'
    result['native_observer_binary_sha256']=sha(observer)
    result['files'][str(observer.relative_to(ROOT))]=sha(observer)
    result['observer_scope']='Read-only initial native K/force queries;solid tetra/hexa two-step q/v difference0;not general internal-history purity'
    for f in out.glob('*'):
        if f.is_file():result['files'][str(f.relative_to(ROOT))]=sha(f)
    (out/'producer.py').write_bytes(Path(__file__).read_bytes())
    result['files'][str((out/'producer.py').relative_to(ROOT))]=sha(out/'producer.py')
    (out/'manifest.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(dict(output=str(out),processes=len(processes),max_native_child_runtime_s=max(x['runtime_s'] for x in processes),raw_files=len(files),prior=prior['prior_immutable'],mesh_pair_failures=sum(x['status']=='FAIL_MESH_GATE' for x in pairs)),indent=2))

if __name__=='__main__':main()
