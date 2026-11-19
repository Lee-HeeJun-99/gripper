"""Publish native alternative diagnostics and verify old immutable evidence.

No simulation, tolerance changes, or physical PASS synthesis takes place here.
Raw paths remain in place; hashes and exact producer snapshots are published.
"""
import argparse,json,shutil,subprocess
from pathlib import Path
import numpy as np
from native_bending_coupon import BASE,ROOT,sha
from observer_identity import compiled_observer

CASES=['native_loaded_sections407','native_shell_loaded408','native_shell_graph409',
       'native_shell_graph_fine411','native_shell_graph_cross412','native_shell_cg_trace413',
       'native_shell_cg_plan414','native_bending_matrix_paths415','native_shell_pcg416',
       'native_shell_pcg_refine417','native_shell_pcg_half418','native_shell_precurve_rest419',
       'native_shell_tensor_probe420','native_shell_assess421','native_rectangular_beam422',
       'native_rectangular_rest423','native_rectangular_graph424','native_section_translation425',
       'native_rigid_tangent427','native_rigid_tangent429','native_rectangular_budget430',
       'native_beam_reference432','native_rectangular_geometric433','native_rectangular_ramp434',
       'native_rectangular_ramp435','native_beam_linear_reference436','native_beam_reference_api437',
       'native_beam_reference_precision439','native_beam_precision_assess440',
       'native_beam_private_force442','native_rectangular_ls_zero443','native_beam_second_order444',
       'native_rectangular_small_load445','native_beam_private_assess446','native_beam_reinforce447',
       'native_rectangular_centered448','native_rectangular_centered_refine449','native_rectangular_centered_half450',
       'native_beam_accepted452','native_beam_centered_assess453',
       'native_beam_refined_diagnostic454','native_beam_ulp_probe455','native_beam_units457',
       'native_beam_loaded_fd459','native_beam_loaded_regression460','native_beam_mode_fd462',
       'native_beam_mode_fd464','native_beam_mode_ladder465','native_beam_fd_assess466']

def main():
    p=argparse.ArgumentParser();p.add_argument('--name',required=True)
    p.add_argument('--prior',default='evidence_native_elastic_v7');a=p.parse_args()
    out=BASE/'reports'/a.name;out.mkdir(exist_ok=False)
    previous=BASE/'reports'/a.prior/'manifest.json'
    old=json.loads(previous.read_text());checked=0;mismatches=[]
    for name,digest in old['files'].items():
        immutable=name.startswith('product_prototype/results/') or name.startswith('product_prototype/reports/evidence_') or any(name.startswith('product_prototype/'+x) for x in ('cad/build_','meshes/','drawings/','sofa/scenes/'))
        if not immutable:continue
        checked+=1;f=ROOT/name
        if not f.is_file() or sha(f)!=digest:mismatches.append(name)
    manifest=dict(scope='Native diagnostics only;NOT B3/grasp/fabrication qualification',
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        prior_manifest_sha256=sha(previous),prior_immutable_audit=dict(checked=checked,mismatches=mismatches),
        cases={},files={})
    if mismatches:raise ValueError('Prior immutable evidence changed; do not rewrite baseline')
    for case in CASES:
        folder=BASE/'results'/case;summary=folder/'summary.json'
        if not summary.is_file():raise ValueError('Missing completed summary: '+case)
        shutil.copy2(summary,out/(case+'.json'));manifest['cases'][case]=dict(raw=str(folder.relative_to(ROOT)),summary_sha256=sha(summary))
        for f in folder.rglob('*'):
            if f.is_file():manifest['files'][str(f.relative_to(ROOT))]=sha(f)
    manifest['exclusions']={'native_rectangular_ramp434':'Unused keyTimes/keyForces;zero load;not loaded bending evidence. Original summary/Raw retained.',
                            'native_rigid_tangent427':'Wrong scalar matrix API;not native tangent discrepancy evidence.'}
    for identifier in ('400','406','410','428','431','438','441','451','456','458','463'):
        binary,source=compiled_observer(identifier)
        for f in (binary,source):manifest['files'][str(f.relative_to(ROOT))]=sha(f)
    rejected_binary=BASE/'cad/build_rigid_observer426/libReGripElasticObserver.so'
    manifest['files'][str(rejected_binary.relative_to(ROOT))]=sha(rejected_binary)
    failed_observer=BASE/'cad/build_mode_observer461/libReGripElasticObserver.so'
    manifest['files'][str(failed_observer.relative_to(ROOT))]=sha(failed_observer)
    sdk=Path('/home/ubuntu/SOFA/v26.06.00')
    for f in [sdk/'bin/runSofa-26.06.00',sdk/'plugins/BeamAdapter/lib/libBeamAdapter.so',
              sdk/'include/Sofa.Component.SolidMechanics.Spring/sofa/component/solidmechanics/spring/FastTriangularBendingSprings.inl']:
        if f.is_file():manifest['files'][str(f)]=sha(f)
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    loaded=json.loads((BASE/'results/native_loaded_sections407/summary.json').read_text())['records']
    fig,ax=plt.subplots(1,2,figsize=(10,4))
    x=np.arange(len(loaded))
    ax[0].semilogy(x,[r['private_linear_residual_N'] for r in loaded],'o-',label='private K u-F')
    ax[0].semilogy(x,[r['private_represented_linear_residual_N'] for r in loaded],'s-',label='K ((q0+u)-q0)-F')
    ax[0].axhline(1e-12,color='k',linestyle='--',label='unchanged force gate')
    ax[0].set_xticks(x,[r['component'] for r in loaded],rotation=12)
    ax[0].set_ylabel('Residual norm [N]');ax[0].set_title('407: PRIVATE reference, not accepted state');ax[0].legend(fontsize=7)
    records=[]
    for case in ('native_shell_pcg416','native_shell_pcg_refine417'):
        records.extend(json.loads((BASE/'results'/case/'summary.json').read_text())['records'])
    for ny in (3,5):
        rows=sorted([r for r in records if r['ny']==ny and 'tip_m' in r],key=lambda r:r['nx'])
        ax[1].plot([r['nx'] for r in rows],[r['tip_m']*1e3 for r in rows],'o-',label=f'width nodes {ny}')
    ax[1].set_xlabel('Length nodes');ax[1].set_ylabel('Actual static tip displacement [mm]')
    ax[1].set_title('416/417: native shell, mesh FAIL');ax[1].legend()
    fig.suptitle('Installed SOFA v26.06.00; 1 microN; not B3 or grasp certification',fontsize=10)
    fig.tight_layout();fig.savefig(out/'native_diagnostics.png',dpi=160);plt.close(fig)
    reference=json.loads((BASE/'results/native_beam_reference_precision439/summary.json').read_text())
    measured=[r for r in reference['records'] if r['observed']]
    fig,axis=plt.subplots(figsize=(7,4))
    axis.bar(['flat / straight=true','flat / geometric rest','curved / geometric rest'],[r['initial_free_force_norm_N'] for r in measured])
    axis.axhline(1e-12,color='k',linestyle='--',label='unchanged absolute force gate')
    axis.set_ylabel('Actual initial native free-force norm [N]');axis.set_title('439: initial native reference only, NOT loaded B3')
    axis.legend(fontsize=8);fig.tight_layout();fig.savefig(out/'native_reference_inventory.png',dpi=160);plt.close(fig)
    shutil.copy2(BASE/'results/native_beam_private_assess446/PRIVATE_reference_force_scaling.png',out/'PRIVATE_reference_force_scaling.png')
    shutil.copy2(BASE/'results/native_beam_centered_assess453/actual_native_static_profiles.png',out/'actual_native_static_profiles.png')
    for name in ('native_loaded_section.py','native_shell_coupon.py','native_shell_assess.py',
                 'native_bending_matrix_paths.py','native_beamadapter_coupon.py','observer_identity.py',
                 'native_matrix_assess.py','native_alternatives_evidence.py','native_rigid_tangent.py',
                 'native_beam_reference_inventory.py','native_beam_reference_assess.py',
                 'native_beam_private_force.py','native_beam_private_assess.py','native_beam_accepted.py','native_beam_centered_assess.py',
                 'native_beam_refined_diagnostic.py','native_beam_ulp_probe.py','native_beam_unit_scale.py','native_beam_loaded_fd.py',
                 'native_beam_mode_fd.py','native_beam_fd_assess.py'):
        f=BASE/'sofa'/name;shutil.copy2(f,out/name)
    for f in out.iterdir():
        if f.is_file():manifest['files'][str(f.relative_to(ROOT))]=sha(f)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(dict(output=str(out),prior_checked=checked,mismatches=mismatches,cases=len(CASES),files=len(manifest['files']))))

if __name__=='__main__':main()
