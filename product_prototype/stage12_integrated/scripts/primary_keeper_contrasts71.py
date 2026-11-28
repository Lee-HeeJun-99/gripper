"""All actual keeper scalar pairs, and exact same-mesh Neumann gauge contrast.
Rigid projection is explicitly a local Neumann quotient, never an operatingmotion.
"""
import sys,json,shutil,itertools,numpy as np
from baseline_registry import ROOT,REPO,ref,sha,dump
out=ROOT/'validation/integrated'/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py');states=[];rows=[]
for tag in sys.argv[2:]:
 sp=ROOT/'validation/integrated'/tag/'summary.json';s=json.loads(sp.read_text());fp=REPO/s['field']['path'];assert sha(fp)==s['field']['SHA256'];a=np.load(fp);p,t,u=a['points_mm'],a['tetra'],a['displacement_mm'];vol=abs(np.linalg.det(p[t[:,1:]]-p[t[:,0,None]]))/6;center=np.sum(vol[:,None]*p[t].mean(1),axis=0)/vol.sum();R=np.zeros((len(p),3,6))
 for j,e in enumerate(np.eye(3)):R[:,:,j]=e;R[:,:,j+3]=np.cross(e,p-center)
 Rt=R[t];ut=u[t];rs=Rt.sum(1);us=ut.sum(1);gram=np.einsum('tai,taj,t->ij',rs,rs,vol)/20+np.einsum('tnai,tnaj,t->ij',Rt,Rt,vol)/20;rhs=np.einsum('tai,ta,t->i',rs,us,vol)/20+np.einsum('tnai,tna,t->i',Rt,ut,vol)/20;coeff=np.linalg.solve(gram,rhs);uc=u-np.einsum('nai,i->na',R,coeff)
 def norm(v):
  vv=v[t];return float(np.sqrt(np.sum(vol[:,None]*(vv.sum(1)**2+np.sum(vv**2,axis=1)))/(20*vol.sum())))
 rows.append(dict(source=ref(sp),nodes=len(p),tetra=len(t),h_mm=s['h_mm'],energy_Nmm=s['static_energy_Nmm'],raw_volume_RMS_mm=norm(u),Neumann_quotient_RMS_mm=norm(uc),removed_rigid_coefficients=coeff.tolist(),physical_host_force_N=s['explicit_host_force_on_each_bolt_N'],all_node_local_checks=all(s['checks'].values()),whole_surface_accepted=False));states.append((p,t,u,uc,norm))
pairs=[]
for i,j in itertools.combinations(range(len(rows)),2):
 a,b=rows[i],rows[j];pa,ta,ua,uca,_=states[i];pb,tb,ub,ucb,_=states[j];same=np.array_equal(pa,pb) and np.array_equal(ta,tb);v=None;quotient=None
 if same:
  vol=abs(np.linalg.det(pa[ta[:,1:]]-pa[ta[:,0,None]]))/6
  def nn(x):
   z=x[ta];return float(np.sqrt(np.sum(vol[:,None]*(z.sum(1)**2+np.sum(z*z,axis=1)))/(20*vol.sum())))
  v=nn(ua-ub);quotient=nn(uca-ucb)
 metrics={k:dict(first_denominator=abs(a[k]-b[k])/abs(a[k]),second_denominator=abs(a[k]-b[k])/abs(b[k])) for k in ['energy_Nmm','raw_volume_RMS_mm','Neumann_quotient_RMS_mm']};pairs.append(dict(first=a['source'],second=b['source'],same_mesh=same,all_scalar_differences=metrics,same_mesh_raw_vector_RMS_mm=v,same_mesh_quotient_vector_RMS_mm=quotient,full_crossmesh_vector_metric=None if not same else quotient,crossmesh_vector_not_computed=not same,physical_original_spatial_gate_qualified=False,reason='Node references fail whole clipped interface. Raw Neumann rigidgauges differ; quotient is explicit elastic diagnostic only. Scalar agreement or quotient must not certify actual operatingmotion or globalmeshgate.'))
dump(out/'summary.json',dict(status='ACTUAL_P1_KEEPER_ALLPAIR_LOCAL_SCALARS_AND_NEUMANN_GAUGES_NOT_SPATIAL_PASS',producer=ref(out/'producer.py'),candidate=s['candidate'],rows=rows,pairs=pairs,accepted83body_physical_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False));print(json.dumps(dict(rows=rows,pairs=pairs)))
