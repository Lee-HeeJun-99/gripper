"""Independent tetra force reconstruction and fixed-floor work-adjoint contact audit."""
import sys,json,shutil,numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump
src=ROOT/'validation/integrated'/sys.argv[1];out=ROOT/'validation/integrated'/sys.argv[2];out.mkdir();shutil.copyfile(__file__,out/'producer.py');s=json.loads((src/'summary.json').read_text());assert sha(REPO/s['STEP']['path'])==s['STEP']['SHA256'];cad=json.loads((REPO/s['candidate']['path']).read_text());assert len(cad['part_references'])==83 and all(sha(REPO/q['path'])==q['SHA256'] for q in cad['part_references'].values())
quad=np.load(src/'quadrature.npz');B=quad['B'];C=quad['C'];qp=quad['points_mm'];weights=quad['weights_mm2'];E=s['E_ASSUMED_MPa'];nu=s['nu_ASSUMED'];mu=E/(2*(1+nu));la=E*nu/((1+nu)*(1-2*nu));rows=[]
for fp in sorted(src.glob('trial_*.npz')):
 assert not(ROOT/'runtime/STOP').exists()
 a=np.load(fp);p=a['points_mm'];t=a['tetra'];u=a['displacement_mm'];F=a['load_N'];r=a['reaction_N'];floor=a['floor_nodes'];previous=a['previous_displacement_mm'];q=a['quadrature_force_N'];frozen=a['frozen_normal_N'];off=np.setdiff1d(np.arange(len(p)),floor)
 XX=p[t[:,1:]]-p[t[:,0,None]];iv=np.linalg.inv(XX);vol=abs(np.linalg.det(XX))/6;grad=np.zeros((len(t),4,3));grad[:,1:]=iv.transpose(0,2,1);grad[:,0]=-grad[:,1:].sum(1);G=np.einsum('tai,taj->tij',u[t],grad);eps=(G+G.transpose(0,2,1))/2;sig=2*mu*eps+la*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);internal=np.zeros_like(F);ef=np.einsum('tij,taj,t->tai',sig,grad,vol)
 for j in range(4):np.add.at(internal,t[:,j],ef[:,j])
 calc=internal-F;pulled=np.zeros_like(F);pulled[floor]=B.T@q;uq=B@u[floor];delta=B@(u-previous)[floor];normal=q[:,2];T=q[:,:2];gap=uq[:,2];diss=-np.einsum('ij,ij->i',T,delta[:,:2]);support=.3*np.maximum(normal,0)*np.linalg.norm(delta[:,:2],axis=1);cone=.3*np.maximum(normal,0)-np.linalg.norm(T,axis=1);en=float(np.sum(.5*np.einsum('tij,tij->t',eps,sig)*vol));W=np.r_[(F+pulled).sum(0),np.cross(p,F+pulled).sum(0)];wrong=F.copy();wrong[0,0]+=.01
 row=dict(field=ref(fp),reaction_reconstruction_N=float(abs(calc-r).max()),adjoint_pullback_error_N=float(abs(calc-pulled).max()),off_floor_residual_N=float(abs(calc[off]).max()),force_moment_N_Nmm=W.tolist(),min_quadrature_gap_mm=float(gap.min()),min_whole_triangle_gap_mm=float(u[floor,2].min()),min_normal_N=float(normal.min()),min_cone_slack_N=float(cone.min()),normal_fixedpoint_N=float(abs(np.maximum(normal,0)-frozen).max()),complementarity_Nmm=float(abs(gap*normal).max()),max_dissipation_error_Nmm=float(abs(diss-support).max()),min_dissipation_Nmm=float(diss.min()),elastic_energy_Nmm=en,external_work_Nmm=float(np.sum(u*(F+calc))),quadrature_contact_work_Nmm=float(np.sum(uq*q)),nodal_contact_work_Nmm=float(np.sum(u*pulled)),perturbed_load_error_N=float(abs(internal-wrong-r).max()),increment_loss_Nmm=float(diss.sum()))
 row['quadrature_law']=bool(row['adjoint_pullback_error_N']<1e-7 and row['min_quadrature_gap_mm']>=-1e-9 and row['min_normal_N']>=-1e-7 and row['min_cone_slack_N']>=-1e-7 and row['normal_fixedpoint_N']<1e-7 and row['complementarity_Nmm']<1e-8 and row['max_dissipation_error_Nmm']<1e-9 and row['min_dissipation_Nmm']>=-1e-9)
 row['whole_triangle_nonpenetration']=row['min_whole_triangle_gap_mm']>=-1e-9
 rows.append(row)
# Negative control on actual floor interpolation: a hidden vertex mode can be
# invisible at all quadrature samples. This is NOT an equilibrium/load result.
_,sv,vh=np.linalg.svd(B,full_matrices=True);rank=int(np.sum(sv>1e-10));null=vh[rank:]
control=None
if len(null):
 v=null[0].copy();v*=1e-5/max(abs(v.min()),abs(v.max()))
 if abs(v.max())>abs(v.min()):v=-v
 control=dict(scope='actualB mathematical sampling negative control NOT equilibrium',rank=rank,floor_nodes=B.shape[1],quadrature_samples=B.shape[0],sample_gap_mm=float((B@v).min()),whole_triangle_vertex_gap_mm=float(v.min()),sample_pass=bool((B@v).min()>=-1e-9),whole_triangle_rejected=bool(v.min()<-1e-9))
checks=dict(actual83part_hashes=True,nonempty_actual_fields=bool(rows),all_original_nodal_forces=all(r['reaction_reconstruction_N']<1e-8 for r in rows),all_work_adjoint=all(abs(r['nodal_contact_work_Nmm']-r['quadrature_contact_work_Nmm'])<1e-10 for r in rows),all_local_elastic_halfwork=all(abs(r['external_work_Nmm']/2/r['elastic_energy_Nmm']-1)<1e-8 for r in rows),perturbed_load_rejected=all(r['perturbed_load_error_N']>.009 for r in rows),physical_quadrature_affine_geometry=bool(abs(B@p[floor]-qp).max()<1e-8),physical_1600mm2_area=abs(weights.sum()-1600)<1e-8)
dump(out/'fields.json',rows);dump(out/'summary.json',dict(status='ACTUAL_P1_FIXED_FLOOR_INDEPENDENT_RECONSTRUCTION' if all(checks.values()) else 'ACTUAL_P1_FIXED_FLOOR_AUDIT_FAIL',source=ref(src/'summary.json'),candidate=s['candidate'],producer=ref(out/'producer.py'),checks=checks,fields=ref(out/'fields.json'),undersampling_negative_control=control,last_field=rows[-1],whole_system_release=False,newly_qualified_system_gate_ids=[],scope='Independent actual tetra forces and Btranspose integrated contact reactions; all trial fields including failure. Reconstruction PASS is not contact/system qualification.'))
print(json.dumps(checks));raise SystemExit(0 if all(checks.values()) else 2)
