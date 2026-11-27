"""Same-revision five actual elastic bodies and independent port/gravity loads.

Reuses proven Support.elastic, NOT historical displacement/contact/load fields.
Contact and connector completion is explicitly required before any solve.
"""
import sys,json,shutil,time
import numpy as np
from scipy.spatial.transform import Rotation
from baseline_registry import ROOT,REPO,ref,dump,sha
from finite_face_union27 import boundary
from primary_corotated_support import Support
from primary_finite_port import ObjectiveRootPort,motor_pullback


def main():
    start=time.monotonic();assert not (ROOT/'runtime/STOP').exists()
    out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir(exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    cadpath=ROOT/'cad/exports/primaryP1_ycapture24/summary.json';cad=json.loads(cadpath.read_text())
    histpath=ROOT/'validation/integrated/primaryP1_reclosure3/summary.json';hist=json.loads(histpath.read_text());oldcad=json.loads((REPO/hist['candidate']['path']).read_text())
    assert sha(REPO/hist['field']['path'])==hist['field']['SHA256'];old=np.load(REPO/hist['field']['path'])
    names=['OPEN_FRAME','F0_ROOT_BACK','MOTOR_CAP','GROUND_PLATE','TEST_BASE']
    assert all(cad['part_references'][n]==oldcad['part_references'][n] for n in names[2:])
    assert all(sha(REPO/r['path'])==r['SHA256'] for r in cad['part_references'].values())
    loadpath=ROOT/'validation/transmission/primaryP1_gravity_cat_demand_ports2/summary.json';loads=json.loads(loadpath.read_text())['rows'][0]
    dump(out/'inputs.json',dict(candidate=ref(cadpath),parts={n:cad['part_references'][n] for n in names},
        historical_geometry_material_only=dict(source=ref(histpath),field=hist['field'],unchanged_parts=names[2:]),
        new_geometry={str(l):ref(ROOT/f'validation/integrated/primaryP1_ycapture_mesh{l}/summary.json') for l in [2,3]},
        conditional_original_operating_ports=ref(loadpath),producer=ref(out/'producer.py'),dependencies=[ref(ROOT/f'scripts/{n}.py') for n in ['primary_corotated_support','primary_finite_port','finite_face_union27']],
        excluded_historical_fields=['u_mm','contact_force_N','contact_gaps_mm','bolt_force_N','applied_force_N','stresses','sourcefield','old_offsets'],
        solve_authorized_by_this_descriptor=False))
    results=[];rng=np.random.default_rng(2706)
    for level in [2,3]:
        ms=json.loads((ROOT/f'validation/integrated/primaryP1_ycapture_mesh{level}/summary.json').read_text());new=np.load(REPO/ms['mesh']['path']);a={};offset=0
        for name in names:
            mesh=new if name in names[:2] else old
            for suffix in ['points_mm','tetra']:a[name+'_'+suffix]=mesh[name+'_'+suffix]
            for suffix in ['E_MPa','nu','rho_kg_m3']:a[name+'_'+suffix]=old[name+'_'+suffix]
            a[name+'_offset']=np.array(offset);offset+=3*len(a[name+'_points_mm'])
        a['motor_offset']=np.array(offset);offset+=6;a['upstream_freeY_offset']=np.array(offset);offset+=1
        # These zeros are reference coordinates, explicitly NOT a solved sourcefield.
        a['u_mm']=np.zeros(offset);a['contact_label']=np.array([],dtype='U1');a['bolt_D']=np.empty((0,offset))
        model=Support(a,names);u=np.zeros(offset)
        zeroE,zeroG,zeroRows=model.elastic(u);rigid=u.copy();translation=np.array([.01,-.02,.03]);R=Rotation.from_rotvec([.0003,-.0002,.0001]).as_matrix()
        for name,b in model.bodies.items():
            o=b['offset'];rigid[o:o+3*len(b['X'])]=(b['X']@R.T+translation-b['X']).ravel()
        rigidE,rigidG,rigidRows=model.elastic(rigid)
        # Nonzero actual-geometry strain field: directional energy derivative of proven FEM.
        affine=u.copy();direction=u.copy()
        for name,b in model.bodies.items():
            o=b['offset'];affine[o:o+3*len(b['X'])]=(b['X']@np.diag([1e-6,-2e-6,1e-6])).ravel()
            direction[o:o+3*len(b['X'])]=(b['X']@np.diag([-1e-6,1e-6,2e-6])).ravel()
        E,G,_=model.elastic(affine);eps=1e-3;plus=model.elastic(affine+eps*direction)[0];minus=model.elastic(affine-eps*direction)[0];derivative_error=abs((plus-minus)/(2*eps)-G@direction)
        fgravity=np.zeros(offset);bodyrows=[]
        for name,b in model.bodies.items():
            mass=b['w']*b['rho']*1e-9;fg=np.zeros_like(b['X']);fg[:,2]=-mass*9.80665;model.scatter(fgravity,name,fg)
            bodyrows.append(dict(part=name,nodes=len(b['X']),tetra=len(b['t']),conditional_E_MPa=float(a[name+'_E_MPa']),conditional_nu=float(a[name+'_nu']),conditional_density_kg_m3=b['rho'],
                tetra_volume_mm3=float(b['V'].sum()),conditional_tetra_mass_kg=float(mass.sum()),gravity_force_N=fg.sum(axis=0).tolist(),gravity_moment_Nm=np.cross(b['X']*.001,fg).sum(axis=0).tolist(),
                material_minimum_qualified=False))
        # Rebuild actual new Root face quadrature; no old port weights or loads copied.
        b=model.bodies['F0_ROOT_BACK'];p=b['X'];bf=boundary(p,b['t']);face=bf[np.all(abs(p[bf,0]-50.5)<1e-7,axis=1)];assert len(face)>0
        area=np.linalg.norm(np.cross(p[face[:,1]]-p[face[:,0]],p[face[:,2]]-p[face[:,0]]),axis=1)/2;w=np.zeros(len(p))
        for j in range(3):np.add.at(w,face[:,j],area/3)
        ids=np.flatnonzero(w);port=ObjectiveRootPort(p[ids],w[ids]);W=np.array(loads['Root_force_couple_XYZ_N_Nm']);W[3:]+=np.cross(loads['Root_reference_m'],W[:3]);ff=port.pullback(np.zeros((len(ids),3)),W)
        mapped=np.r_[ff.sum(axis=0),np.cross(p[ids]*.001,ff).sum(axis=0)];fport=np.zeros(offset);fp=np.zeros_like(p);fp[ids]=ff;model.scatter(fport,'F0_ROOT_BACK',fp)
        MW=np.array(loads['Motor_force_couple_XYZ_N_Nm']);MW[3:]+=np.cross(loads['Motor_reference_m'],MW[:3]);fport[int(a['motor_offset']):int(a['motor_offset'])+6]=motor_pullback(np.zeros(6),MW)
        rigidvel=np.tile([.002,-.003,.001],(len(ids),1))+np.cross(np.tile([.0001,-.0002,.0003],(len(ids),1)),p[ids])
        # Exact cotangent/finite port work independent of old FE displacement.
        analytic=np.sum(ff*rigidvel);eps=1e-3;poseplus=port.pose(eps*rigidvel);poseminus=port.pose(-eps*rigidvel)
        from scipy.spatial.transform import Rotation as Rot
        dc=(poseplus[1]-poseminus[1])/(2*eps);omega=Rot.from_matrix(poseplus[0]@poseminus[0].T).as_rotvec()/(2*eps)
        expected=W[:3]@dc+1000*(W[3:]-np.cross(port.center*.001,W[:3]))@omega
        # No Base counterload is assembled: physical anchor and remaining hardware sources absent.
        saved={k:v for k,v in a.items() if k not in ['u_mm','contact_label','bolt_D']};saved['reference_coordinates_mm']=u;saved['conditional_gravity_N']=fgravity;saved['conditional_original_port_loads_N']=fport;saved['Root_port_weights_mm2']=w
        np.savez_compressed(out/f'h{level}_fivebody_reference.npz',**saved)
        results.append(dict(mesh_level=level,physical_coordinates=offset,independent_body_rigid_modes=36,upstream_freeY_scalar_present=True,
            body_geometry=bodyrows,new_root_port_nodes=len(ids),new_root_port_area_mm2=float(area.sum()),root_force_error_N=float(np.linalg.norm(mapped[:3]-W[:3])),root_moment_error_Nm=float(np.linalg.norm(mapped[3:]-W[3:])),
            root_port_work_error_Nmm=float(abs(analytic-expected)),zero_reference_elastic_energy_Nmm=zeroE,max_zero_reference_force_N=float(abs(zeroG).max()),
            common_finite_rigid_rotation_elastic_energy_Nmm=rigidE,affine_elastic_energy_Nmm=E,energy_directional_derivative_error_Nmm=derivative_error,
            conditional_original_Root_wrench_N_Nm=W.tolist(),conditional_original_Motor_wrench_N_Nm=MW.tolist(),
            fivebody_gravity_wrench_N_Nm=model.wrench(u,fgravity).tolist(),partial_external_wrench_N_Nm=model.wrench(u,fgravity+fport).tolist(),
            applied_Base_counterload=False,all_physical_nodes_unfixed=True,old_sourcefield_transferred=False,
            full_coupled_model_ready=False,missing=['Remaining finite support/motorfront contact blocks','14 physical axial branches with new-mesh area owners','Fresh coupled Finger/string source and freeY equation','Exact remaining hardware gravity/physical Base anchor','Finite step transaction/contact pressure and all physical acceptance checks'],
            reference_model=ref(out/f'h{level}_fivebody_reference.npz')))
    checks=dict(source_and_same_revision_geometry=True,new_root_port_load_resultants=all(r['root_force_error_N']<1e-8 and r['root_moment_error_Nm']<1e-10 and r['root_port_work_error_Nmm']<1e-8 for r in results),
        proven_elastic_operator=all(abs(r['zero_reference_elastic_energy_Nmm'])<1e-10 and r['max_zero_reference_force_N']<1e-8 and r['common_finite_rigid_rotation_elastic_energy_Nmm']<1e-8 and r['energy_directional_derivative_error_Nmm']<1e-8 for r in results),
        unfixed_geometry_no_old_solution=all(r['all_physical_nodes_unfixed'] and not r['old_sourcefield_transferred'] and not r['applied_Base_counterload'] for r in results))
    dump(out/'summary.json',dict(status='ACTUAL_P1_FIVEBODY_GEOMETRY_ELASTICITY_PORT_REBUILD_VERIFIED_NOT_EQUILIBRIUM' if all(checks.values()) else 'ACTUAL_P1_FIVEBODY_REFERENCE_REBUILD_FAIL',candidate=ref(cadpath),inputs=ref(out/'inputs.json'),checks=checks,results=results,
        elapsed_s=time.monotonic()-start,newly_qualified_system_gate_ids=[],accepted_equilibria=0,whole_system_release=False,
        limitations=['Reference model blocks only; partial physical external sources explicitly not balanced and never solved.',
        'Inherited isotropic constants/densities are conditional, not source-backed minima/allowables. Three unchanged meshes reused only after exact CAD identity; changed Root/Frame meshes are new.',
        'Conditional original operating ports independently pulled back to new Root face. Not current coupled Finger/string loads or newly certified operating demand.',
        'No material/strength, mesh1%/time.1%, complete energy, physical Base anchor or full3Finger qualification.']))
    print(json.dumps(dict(checks=checks,results=results)));return 0 if all(checks.values()) else 2

if __name__=='__main__':sys.exit(main())
