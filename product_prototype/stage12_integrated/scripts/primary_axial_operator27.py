"""New actual fivebody axial footprints through proven finite connector model."""
import sys,json,shutil,time
import numpy as np
from scipy.sparse import load_npz
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,ref,dump,sha
from primary_corotated_support import Support


def main():
    start=time.monotonic();assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    modelsrc=ROOT/'validation/integrated/primaryP1_fivebody_rebuild27/summary.json';ms=json.loads(modelsrc.read_text());patchsrc=ROOT/'validation/integrated/primaryP1_axial_rebuild27env/summary.json';ps=json.loads(patchsrc.read_text());names=['OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP','GROUND_PLATE','TEST_BASE'];rng=np.random.default_rng(2707);results=[]
    dump(out/'inputs.json',dict(candidate=ms['candidate'],fivebody=ref(modelsrc),fresh_axial_footprints=ref(patchsrc),producer=ref(out/'producer.py'),proven_connector=ref(ROOT/'scripts/primary_corotated_support.py'),port=ref(ROOT/'scripts/primary_finite_port.py'),load_meaning='Unit/multiple virtual axial forces and small geometry perturbations ONLY, no operating equilibrium or physical preload assigned.'))
    for mr,pr in zip(ms['results'],ps['results']):
        assert sha(REPO/mr['reference_model']['path'])==mr['reference_model']['SHA256'] and sha(REPO/pr['conditional_axial_D']['path'])==pr['conditional_axial_D']['SHA256']
        raw=np.load(REPO/mr['reference_model']['path']);a={k:raw[k] for k in raw.files};a['u_mm']=a.pop('reference_coordinates_mm');a['contact_label']=np.array([],dtype='U1');a['bolt_D']=load_npz(REPO/pr['conditional_axial_D']['path']).toarray();av=np.load(REPO/pr['availability']['path']);assert av['available'].all();a['bolt_k_N_mm']=av['k_N_mm'];model=Support(a,names);N=model.N;u=np.zeros(N);e0,g0=model.connectors(u)
        translation=np.array([.01,-.02,.03]);R=Rotation.from_rotvec([.001,-.0005,.0003]).as_matrix();rigid=model.rigid(u,R,translation);er,gr=model.connectors(rigid)
        direction=rng.normal(size=N)*.001;probe=rng.normal(size=N)*.0001;probe[-1]=direction[-1]=0.;eps=1e-3;forces=np.linspace(.1,1.4,14)
        extension,g=model.connectors(probe,forces);ep=model.connectors(probe+eps*direction,forces)[0];em=model.connectors(probe-eps*direction,forces)[0]
        virtual_error=abs(g@direction-forces@((ep-em)/(2*eps)))
        ext,elastic_g=model.connectors(probe);k=a['bolt_k_N_mm'];U=.5*np.sum(k*np.maximum(ext,0)**2);Up=.5*np.sum(k*np.maximum(ep,0)**2);Um=.5*np.sum(k*np.maximum(em,0)**2);energy_error=abs(elastic_g@direction-(Up-Um)/(2*eps))
        resultant=model.wrench(probe,g);common=model.rigid(probe,R,translation);transformed=model.connectors(common,forces)[0];objective_error=float(np.max(abs(extension-transformed)))
        rootY=np.zeros(N);b=model.bodies['F0_ROOT_BACK'];rootY[b['offset']+1:b['offset']+3*len(b['X']):3]=.001
        rootYext=model.connectors(rootY)[0]
        results.append(dict(mesh_level=mr['mesh_level'],branches=len(model.bolts),all_14_footprints_available=True,original_unfixed_coordinates=N,
            zero_reference_max_extension_mm=float(abs(e0).max()),zero_reference_max_connector_force_N=float(abs(g0).max()),common_finite_rigid_max_extension_mm=float(abs(er).max()),
            virtual_force_directional_work_error_Nmm=float(virtual_error),conditional_unilateral_energy_Nmm=float(U),conditional_energy_gradient_error_Nmm=float(energy_error),
            finite_objectivity_extension_error_mm=objective_error,internal_force_error_N=float(np.linalg.norm(resultant[:3])),internal_moment_error_Nm=float(np.linalg.norm(resultant[3:])),
            RootY_translation_axial_extension_mm=float(abs(rootYext).max()),no_lateral_tie=True,accepted_equilibrium=False))
    checks=dict(all14=all(r['branches']==14 for r in results),reference_and_rigid_modes=all(r['zero_reference_max_extension_mm']<1e-10 and r['zero_reference_max_connector_force_N']<1e-8 and r['common_finite_rigid_max_extension_mm']<1e-10 for r in results),
        original_virtualwork=all(r['virtual_force_directional_work_error_Nmm']<1e-8 and r['conditional_energy_gradient_error_Nmm']<1e-8 for r in results),
        objectivity_action_reaction=all(r['finite_objectivity_extension_error_mm']<1e-10 and r['internal_force_error_N']<1e-8 and r['internal_moment_error_Nm']<1e-10 for r in results),
        free_RootY_no_axial_tie=all(r['RootY_translation_axial_extension_mm']<1e-10 for r in results))
    dump(out/'summary.json',dict(status='ACTUAL_P1_NEW_MESH_14AXIAL_OPERATOR_VERIFIED' if all(checks.values()) else 'ACTUAL_P1_NEW_MESH_14AXIAL_OPERATOR_FAIL',candidate=ms['candidate'],inputs=ref(out/'inputs.json'),checks=checks,results=results,
        elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,
        limitations=['Conditional minor-core axial compliance and area-mean finite objective pullback. No thread/flank/core/engagement/material/bearing/preload capacity qualification.',
        'Virtual forces and small perturbations are derivative controls on actual assembly geometry, not measured/solved operating loads or strength.',
        'Remaining finite support/motorfront blocks, fresh coupled loads, physical Base anchor and full nonlinear contact/energy/convergence gates still required.']))
    print(json.dumps(dict(checks=checks,results=results)));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
