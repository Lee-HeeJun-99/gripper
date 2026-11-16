"""Derived BE-startup/BDF2 G-energy inventory, not a fitted numerical loss."""
import argparse,csv,json,struct,subprocess,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);base=ROOT/'results'/('autonomous_film_'+a.case);summary=json.loads((base/'summary.json').read_text());identity=json.loads((base/'identity.json').read_text())
 if summary['status']!='PASS' or 'order="2" theta="1"' not in (base/'1/scene.scn').read_text():raise RuntimeError('complete uniform BDF2 assembly required')
 rows=list(csv.DictReader((base/'1/journal.csv').open()));x=np.array([np.fromstring(r['x'],sep=' ').reshape(-1,3) for r in rows]);n=x.shape[1];nx=n//11;rest=[]
 for offset,ny,width,thickness,y,z in identity['layout']:
  rest.extend([[100*i/(nx-1),y+width*j/(ny-1),z] for i in range(nx) for j in range(ny)])
 u=np.concatenate([np.zeros_like(x[:1]),x-np.array(rest)]);time=np.r_[0.,[float(r['time']) for r in rows]];h=time[1];v=np.zeros_like(u);v[1]=(u[1]-u[0])/h
 for i in range(2,len(u)):v[i]=(1.5*u[i]-2*u[i-1]+.5*u[i-2])/h
 speed_error=float(max(abs(np.max(np.linalg.norm(v[1:],axis=2),axis=1)-np.array([float(r['max_speed']) for r in rows]))))
 if speed_error>1e-7:raise RuntimeError('actual kinematics mismatch '+str(speed_error))
 tension=np.r_[0.,[float(r['T_per_rail']) for r in rows]]
 with (out/'states.bin').open('xb') as f:
  f.write(struct.pack('QQ',n,len(time)))
  for i,t in enumerate(time):f.write(struct.pack('dd',t,tension[i]));f.write(np.concatenate([u[i],v[i]],axis=1).astype(np.float64).tobytes())
 source=ROOT/'diagnostics/film_rail_tendon/BDFEnergyAudit.cpp';shutil.copy2(source,out/source.name);stages={};stages['compile']=logged(['g++','-std=c++17','-O2','-ffp-contract=off',source,'-o',out/'audit'],out/'compile',180)
 if stages['compile']['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stages=stages));return
 stages['audit']=logged([out/'audit',out/'states.bin'],out/'audit_process',480)
 if stages['audit']['exit_code']:write_json(out/'summary.json',dict(status='FAIL',stages=stages));return
 audit=list(csv.DictReader((out/'audit_process/stdout.log').open()));arrays={k:np.array([float(r[k]) for r in audit]) for k in audit[0]};scale=float(max(abs(np.cumsum(arrays['tendon_path_work']))));error=float(max(abs(np.cumsum(arrays['identity_residual']))));U=np.array([float(r['U_shell'])+float(r['U_attachment']) for r in rows]);K=np.array([float(r['K']) for r in rows]);totals={k:float(sum(v)) for k,v in arrays.items() if k not in ('time','U','K')}
 write_json(out/'summary.json',dict(status='PASS' if error/scale<=.001 else 'FAIL',scope='accepted actual SOFA states plus independent force reconstruction;no-object BDF2 discrete identity only',source_sha256=sha(source),tool_sha256=sha(__file__),binary_sha256=sha(out/'audit'),input_journal_sha256=sha(base/'1/journal.csv'),stages=stages,totals=totals,maximum_cumulative_unexplained=error,relative_to_peak_work=error/scale,maximum_speed_error=speed_error,U_error=float(max(abs(U-arrays['U']))),K_error=float(max(abs(K-arrays['K']))),definitions=dict(G='G_K=.25*m*(|v_n|²+|2v_n-v_prev|²);inventory=Delta(G_K-K)',difference='BDF2 loss=.25*m*|v_n-2v_prev+v_prevprev|²;BE startup=.5*m*|dv|²',identity='Delta(K+U)=W_path-D+(W_endpoint-W_path)-Q_elastic-loss-Delta(G_K-K)+unexplained',elastic='Q=h*gradU_n.v_n-DeltaU;not arbitrary heat',damping='2*h*m*|v_n|²;endpoint quadrature',initialization='BE startup uses physical K and own difference identity;BDF2 inventory starts with two actual prior velocities'),global_energy='BLOCKED',missing=['object/contact/friction','pressure/vacuum','layer friction','guide friction','self-collision']))
 print(json.dumps(dict(relative_identity_error=error/scale,totals=totals)))
if __name__=='__main__':main()
