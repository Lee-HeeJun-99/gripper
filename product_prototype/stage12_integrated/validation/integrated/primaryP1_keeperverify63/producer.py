"""Independent saved tetra fields: affine coordinates/virtual work/volume RMS.
No assembly of producer stiffness; reject a removed physical nodal load.
"""
import sys,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');rows=[]
for tag in sys.argv[2:]:
 sp=ROOT/'validation/integrated'/tag/'summary.json';d=json.loads(sp.read_text());f=REPO/d['field']['path'];assert sha(f)==d['field']['SHA256'] and sha(REPO/d['STEP']['path'])==d['STEP']['SHA256'];a=np.load(f);p=a['points_mm'];t=a['tetra'];u=a['displacement_mm'];load=a['load_N'];xyz=p[t];mat=np.concatenate([np.ones((*xyz.shape[:2],1)),xyz],axis=2);iv=np.linalg.inv(mat);grad=iv[:,1:,:].transpose(0,2,1);V=abs(np.linalg.det(mat))/6;G=np.einsum('tai,taj->tij',u[t],grad);eps=.5*(G+G.transpose(0,2,1));E=d['E_ASSUMED_MPa'];nu=d['nu_ASSUMED'];mu=E/(2*(1+nu));la=E*nu/((1+nu)*(1-2*nu));sig=2*mu*eps+la*np.trace(eps,axis1=1,axis2=2)[:,None,None]*np.eye(3);forces=np.einsum('tij,taj,t->tai',sig,grad,V);internal=np.zeros_like(u)
 for j in range(4):np.add.at(internal,t[:,j],forces[:,j])
 residual=np.max(abs(internal-load));energy=float(np.sum(np.einsum('tij,tij->t',eps,sig)*V)/2);rms=float(np.sqrt(np.sum(V[:,None]*(np.sum(u[t],axis=1)**2+np.sum(u[t]**2,axis=1)))/(20*V.sum())));force=load.sum(0);moment=np.cross(p,load).sum(0);bad=load.copy();idx=np.unravel_index(np.argmax(abs(load)),load.shape);bad[idx]+=1e-4;negative=np.max(abs(internal-bad))>1e-8
 checks=dict(original_allDOF_force=residual<1e-8,independent_energy=abs(energy/d['static_energy_Nmm']-1)<1e-8,independent_volume_RMS=abs(rms/d['volume_RMS_displacement_mm']-1)<1e-10,halfwork=abs(float(np.sum(load*u))/2/energy-1)<1e-8,force=np.max(abs(force))<1e-8,moment=np.max(abs(moment))<1e-8,perturbed_load_rejected=bool(negative))
 rows.append(dict(source=ref(sp),field=ref(f),checks={k:bool(v) for k,v in checks.items()},independent_original_residual_N=float(residual),energy_Nmm=energy,volume_RMS_displacement_mm=rms))
checks=all(all(r['checks'].values()) for r in rows)
dump(out/'summary.json',dict(status='ACTUAL_KEEPER_SAVED_FIELD_INDEPENDENT_CHECK_PASS_NOT_CONTACT' if checks else 'ACTUAL_KEEPER_SAVED_FIELD_CHECK_FAIL',producer=ref(out/'producer.py'),rows=rows,newly_qualified_system_gate_ids=[],whole_system_release=False));print(json.dumps(rows));raise SystemExit(0 if checks else 2)
