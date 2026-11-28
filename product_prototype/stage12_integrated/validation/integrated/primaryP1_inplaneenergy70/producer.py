"""Independent exact nested strain-energy and virtual-work contrasts on actual plate.
No continuum bound, source-minimum capacity or global-energy certificate.
"""
import sys,json,shutil,numpy as np
from baseline_registry import ROOT,REPO,ref,dump
V=ROOT/'validation/integrated';src=V/sys.argv[1];out=V/sys.argv[2];out.mkdir();shutil.copyfile(__file__,out/'producer.py');s=json.loads((src/'summary.json').read_text());rows=[]
for row in s['rows']:
 assert not (ROOT/'runtime/STOP').exists()
 cs=REPO/row['coarse']['path'];fs=REPO/row['fine']['path'];a=np.load(cs.parent/'field.npz');b=np.load(fs.parent/'field.npz');mp=np.load(REPO/row['parent_map']['path']);parent=mp['fine_to_coarse_tetra'];bc=mp['coarse_barycentric_at_fine_vertices'];p,t,u=b['points_mm'],b['tetra'],b['displacement_mm'];c=np.einsum('tai,tij->taj',bc,a['displacement_mm'][a['tetra'][parent]]);f=u[t];e=f-c;dx=p[t[:,1:]]-p[t[:,0,None]];vol=abs(np.linalg.det(dx))/6;iv=np.linalg.inv(dx);grad=np.concatenate([-iv.sum(2)[:,None,:],iv.transpose(0,2,1)],axis=1)
 E=200000.;nu=.3;mu=E/(2*(1+nu));la=E*nu/((1+nu)*(1-2*nu))
 def strain(v):
  G=np.einsum('tai,taj->tij',v,grad);return (G+G.transpose(0,2,1))/2
 def stress(v):return 2*mu*v+la*np.trace(v,axis1=1,axis2=2)[:,None,None]*np.eye(3)
 def bil(x,y):return float(np.sum(np.einsum('tij,tij->t',x,stress(y))*vol))
 ef,ec,ee=map(strain,[f,c,e]);Uf,Uc,Ue=[.5*bil(x,x) for x in [ef,ec,ee]]
 # Continuity of prolongation is checked at every fine node, including duplicates.
 cn=np.zeros_like(u);count=np.zeros(len(p))
 for j in range(4):np.add.at(cn,t[:,j],c[:,j]);np.add.at(count,t[:,j],1)
 cn/=count[:,None];continuity=float(abs(c-cn[t]).max());assert continuity<1e-11
 en=u-cn;F=b['load_N'];R=b['reaction_N'];work=float(np.sum(en*(F+R)));weak=bil(ee,ef);workerr=abs(work-weak);assert workerr<1e-9
 fsd=json.loads(fs.read_text());csd=json.loads(cs.read_text());assert abs(Uf/fsd['static_energy_Nmm']-1)<1e-8 and abs(Uc/csd['static_energy_Nmm']-1)<1e-8
 internal=np.zeros_like(u);eforce=np.einsum('tij,taj,t->tai',stress(ef),grad,vol)
 for j in range(4):np.add.at(internal,t[:,j],eforce[:,j])
 residual=float(abs(internal-F-R).max());wrong=F.copy();wrong[0,0]+=.01;negative=float(abs(internal-wrong-R).max());assert residual<1e-7 and negative>.009
 rows.append(dict(coarse=row['coarse'],fine=row['fine'],parent_map=row['parent_map'],fine_energy_Nmm=Uf,coarse_energy_Nmm=Uc,difference_strain_energy_Nmm=Ue,relative_energy_norm_fine=(Ue/Uf)**.5,relative_energy_norm_coarse=(Ue/Uc)**.5,energy_relative_both=[abs(Uf/Uc-1),abs(Uc/Uf-1)],prolongation_continuity_error_mm=continuity,fine_original_nodal_residual_N=residual,altered_load_rejected_N=negative,difference_virtual_work_Nmm=work,independent_strain_virtual_work_Nmm=weak,virtual_work_error_Nmm=workerr,fullvolume_displacement_original1percent=row['original1percent_both_directions'],both_local=row['both_full_load_local']))
dump(out/'summary.json',dict(status='ACTUAL_P1_EXACT_NESTED_STRAIN_AND_VIRTUAL_WORK_CONTRAST',candidate=s['candidate'],source=ref(src/'summary.json'),producer=ref(out/'producer.py'),rows=rows,newly_qualified_system_gate_ids=[],whole_system_release=False,scope='Every original tetra and every nodal force restored. Same fixed polyhedral domain, material and frozen loads. Difference energy norm is diagnostic, not substituted for original displacement/energy convergence. Frictional contact changes prevent assuming simple nested compliance bounds. Not global energy, dt or strength.'))
print(json.dumps(rows))
