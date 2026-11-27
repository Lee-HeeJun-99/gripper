"""Bound actual128part P1 thread assembly, backlash and finite flank load maps.
Declared thread geometry is tested independently; no installed material capacity.
"""
import sys,json,math,shutil
import numpy as np
from scipy.optimize import brentq,linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common,overlap,translate,box,volume
from primary_nutseat46b import STATIONS
from validate_nutseat46c import rotate
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN,TopAbs_OUT
P=.8;K=P/(2*math.pi);RPE=4.456/2;RPI=4.605/2;CLEAR=(RPI-RPE)/math.sqrt(3)

def classification(shape,p):
    c=BRepClass3d_SolidClassifier(shape,gp_Pnt(*map(float,p)),1e-8)
    return 'IN' if c.State()==TopAbs_IN else 'OUT' if c.State()==TopAbs_OUT else 'ON_OR_UNKNOWN'

def main():
    assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated/primaryP1_thread49f_validation';out.mkdir();shutil.copyfile(__file__,out/'verifier.py')
    cp=ROOT/'cad/exports/primaryP1_thread49f/summary.json';d=json.loads(cp.read_text());assert all(sha(REPO/r['path'])==r['SHA256'] for r in d['part_references'].values());parts={n:read(REPO/r['path']) for n,r in d['part_references'].items()};bb={n:bounds(s) for n,s in parts.items()};poses=[];flanks=[];backlash=[];profiles=[];loads=[]
    for pre,i,x,y,zlo,zhi,parent in STATIONS:
        assert not(ROOT/'runtime/STOP').exists();bn=f'{pre}_BOLT_{i}';nn=f'{pre}_NUT_{i}';kn=f'{pre}_SOCKET_KEY_{i}';pn=f'{pre}_SPLIT_PIN_{i}';tip=zhi-6;bolt=parts[bn];nut=parts[nn]
        # Tightening precedes key/pin installation. Nut is held by actual cage.
        # Thread follows its RH screw symmetry dz=K*dtheta, not a smooth push.
        for dz in [6.5,6.,5.6,5.2,4.8,4.,3.2,2.4,1.6,.8,.4,.2,0.]:
            sh=translate(rotate(bolt,x,y,dz/K),0,0,dz);b=bounds(sh)
            hits=[dict(part_ID=n,common_mm3=v) for n,s in parts.items() if n not in ({bn,kn,pn}|({nn} if dz not in [3.2,0.] else set())) and overlap(b,bb[n]) and (v:=common(sh,s))>1e-8]
            poses.append(dict(bolt=bn,axial_dz_mm=dz,rotation_rad=dz/K,nut_BRep_pair_checked=dz in [3.2,0.],operation='RHboltfeed_nutheld_keypin_notyetinstalled',hits=hits))
        for sign in [-1,1]:
            levels=[]
            for tol in ([1e-9,1e-11] if pre=='BENCH_MOUNT' and i==0 else []):
                f=lambda z:common(translate(bolt,0,0,sign*z),nut)-tol
                fa,fb=f(0),f(.08)
                if fa*fb>=0:
                    levels.append(dict(volume_threshold_mm3=tol,axial_stop_mm=None,bracket_values_mm3=[fa,fb]));continue
                dd=brentq(f,0,.08,xtol=1e-11);levels.append(dict(volume_threshold_mm3=tol,axial_stop_mm=dd))
            before=common(translate(bolt,0,0,sign*.04),nut);after=common(translate(bolt,0,0,sign*.05),nut)
            backlash.append(dict(before_probe_dz_mm=sign*.04,before_probe_mm3=before,after_probe_dz_mm=sign*.05,after_probe_mm3=after,stop_method='measuredroot' if levels else 'before_after_actualBRepbracket',bolt=bn,nut=nn,sign=sign,levels=levels,independent_analytic_stop_mm=CLEAR,error_mm=None if not levels or levels[-1]['axial_stop_mm'] is None else abs(levels[-1]['axial_stop_mm']-CLEAR),threshold_change_mm=None if not levels or any(l['axial_stop_mm'] is None for l in levels) else abs(levels[0]['axial_stop_mm']-levels[1]['axial_stop_mm'])))
        # Independent radial/axial classification, including BOTH full flanks.
        # No points lie in head,tip,runout or declared nut end-chamfers.
        for j in range(6):
            a=2*math.pi*(3+(j+.37)/6);r=2.22+.2*((j%3)/2);center=tip+K*a
            for side in [-1,1]:
                ze=center+side*(P/4+(r-RPE)/math.sqrt(3));zi=center+side*(P/4+(r-RPI)/math.sqrt(3));xy=[x+r*math.cos(a),y+r*math.sin(a)]
                ep=[classification(bolt,xy+[ze+side*eps]) for eps in [-1e-4,1e-4]]
                ip=[classification(nut,xy+[zi+side*eps]) for eps in [-1e-4,1e-4]]
                flanks.append(dict(bolt=bn,nut=nn,theta_rad=a,radius_mm=r,side=side,bolt_across_groove=['OUT','IN'],actual_bolt=ep,nut_across_ridge=['IN','OUT'],actual_nut=ip))
        # Measure finite material changes against actual preceding pair.
        old=json.loads((ROOT/'cad/exports/primaryP1_profilepin48b/summary.json').read_text())
        profiles.append(dict(bolt=bn,nut=nn,major_diameter_mm=4.976,external_pitch_mm=4.456,declared_flat_root_mm=3.95,internal_minor_mm=4.334,internal_pitch_mm=4.605,bolt_volume_before_mm3=volume(read(REPO/old['part_references'][bn]['path'])),bolt_volume_after_mm3=volume(bolt),nut_volume_before_mm3=volume(read(REPO/old['part_references'][nn]['path'])),nut_volume_after_mm3=volume(nut),gross_nut_height_mm=4.7,declared_chamfer_each_mm=.433,complete_flank_axial_band_mm=4.7-2*.433,source_actual_effective_engagement_mm=None))
    # Actual finite helical flank patches, with constant normal pressure per
    # patch. Tensor Gauss integrates FORCE and MOMENT,not point load fiction.
    # Entire patches are contained in r[2.22,2.42],z[tip+1.8,tip+5.5].
    # Select complete2turnband avoiding both chamfers; these bounds are derived
    # from actual nut range and actual profile,not old ideal4.7mm pitchsurface.
    from numpy.polynomial.legendre import leggauss
    q,w=leggauss(4);patches=[];A=[]
    for turn in [3,4,5]:
        for j in range(16):
            alo=2*math.pi*(turn+j/16);ahi=2*math.pi*(turn+(j+1)/16);col=np.zeros(6);area=0.;zmin=1e9;zmax=-1e9
            for qr,wr in zip(q,w):
                r=2.32+.1*qr
                for qa,wa in zip(q,w):
                    a=(alo+ahi)/2+(ahi-alo)/2*qa;z=K*a-(P/4+(r-RPI)/math.sqrt(3));p=np.array([r*math.cos(a),r*math.sin(a),z-3.65]);er=np.array([math.cos(a),math.sin(a),0.]);et=np.array([-math.sin(a),math.cos(a),0.]);nraw=er/math.sqrt(3)-K/r*et+[0.,0.,1.];darea=r*np.linalg.norm(nraw)*.1*(ahi-alo)/2*wr*wa;n=nraw/np.linalg.norm(nraw);col+=np.r_[n,np.cross(p,n)]*darea;area+=darea;zmin=min(zmin,z);zmax=max(zmax,z)
            A.append(col);patches.append(dict(turn=turn,theta_range_rad=[alo,ahi],radius_range_mm=[2.22,2.42],local_z_range_mm=[zmin,zmax],area_mm2=area,wrench_per_MPa_N_Nmm=col.tolist()))
    A=np.array(A).T;target=np.array([0.,0.,1.,0.,0.,-K]);solution=linprog(np.array([p['area_mm2'] for p in patches]),A_eq=A,b_eq=target,bounds=(0,None),method='highs');assert solution.success
    # Independent screw virtual-work/null witness. No torque support -> fail.
    screw=np.array([0,0,K,0,0,1]);work=A.T@screw
    no_torque=linprog(np.ones(A.shape[1]),A_eq=A,b_eq=np.array([0.,0.,1.,0.,0.,0.]),bounds=(0,None),method='highs')
    for p,pressure in zip(patches,solution.x):p['conditional_pressure_MPa_per_1N_axial']=float(pressure)
    limits=['Unit1N axial load is a normalized physical traction map,NOT actual100goperatingload/preload/installedcapacity/equilibrium','Pressure optimization proves conditional finitepatch traction feasibility,NOT elastic pressuredistribution or source materialcapacity','Flat externalroot,tipchamfer,underheadrunout and nutchamfers are declared designgeometry,NOTsourceprofile/ISOconformity','Assembly13posesperbolt:allotherpartschecked;nutBRepcheckedonlyatdz3.2/0plusbacklashprobes,remainingnutposesrelyonRHscrewdesignsymmetry,notcontinuousCADcertificate','No sourceboltclass/pinformingminimum/ultimatehost/contactfriction/Finger/globalenergy qualification;all22remainUNQUALIFIED']
    checks=dict(all128hashes_bound=len(parts)==128,all_screw_assembly_poses_clear=all(not p['hits'] for p in poses),actual_both_flanks_match_independent_profiles=all(p['actual_bolt']==p['bolt_across_groove'] and p['actual_nut']==p['nut_across_ridge'] for p in flanks),both_sign_measured_backlash=all(p['before_probe_mm3']<1e-8 and p['after_probe_mm3']>1e-5 for p in backlash) and all(p['error_mm'] is not None and p['error_mm']<.001 and p['threshold_change_mm']<.001 for p in backlash if p['levels']),finite_patches_inside_full_nut_band=all(p['local_z_range_mm'][0]>1.3+.433 and p['local_z_range_mm'][1]<6-.433 for p in patches),finite_patch_unit_wrench_balance=bool(max(abs(A@solution.x-target))<1e-9),screw_null_work=bool(max(abs(work))<1e-10),unrestrained_screw_axial_transfer_fails=not no_torque.success)
    result=dict(status='ACTUAL_P1_FINITE_THREAD_ASSEMBLY_AND_UNIT_TRACTION_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_THREAD_VALIDATION_FAIL',candidate=ref(cp),verifier=ref(out/'verifier.py'),checks=checks,actual_parts=len(parts),assembly_poses=poses,measured_backlash=backlash,analytic_axial_clearance_each_side_mm=CLEAR,profile_classification=flanks,actual_material_and_engagement=profiles,finite_flank_patches=patches,conditional_unit_axial_wrench_N_Nmm=target.tolist(),conditional_unit_wrench_residual=float(max(abs(A@solution.x-target))),maximum_normalized_pressure_MPa_per_N=float(max(solution.x)),finite_contact_area_mm2=sum(p['area_mm2'] for p in patches),screw_null_virtual_work_error=float(max(abs(work))),free_axial_without_torque_feasible=bool(no_torque.success),accepted_physical_product_equilibria=0,source_actual_effective_engagement_mm=None,source_minimum_strength_MPa=None,installed_capacity_N=None,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=limits)
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],checks=checks,failedposes=[p for p in poses if p['hits']],failedprofiles=[p for p in flanks if p['actual_bolt']!=p['bolt_across_groove'] or p['actual_nut']!=p['nut_across_ridge']],clearance_mm=CLEAR,pressure=max(solution.x))));raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
