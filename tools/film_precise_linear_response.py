"""New-model rest Jacobian and continuous linear response vs actual nonlinear SOFA."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,csv,json,shutil,subprocess,sys
from pathlib import Path
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import mapping,shape
CPP=r'''#include "../../models/film_precise_attachment/Force.h"
#include "../../models/film_rail_aspect/Design.h"
#include <iostream>
#include <iomanip>
int main(int argc,char**argv){try{using namespace regrip_transmission;auto m=regrip_rail_aspect::design(.1);auto mass=publicMass(argv[1]);std::vector<Point>zero(m.size());auto map=mechanics(m,zero,zero,.000025,0,mass);auto a=regrip_precise_attachment::parts(map,zero,0,6.),b=regrip_precise_attachment::parts(map,zero,1,6.);if(a.force.norm()!=0)throw std::runtime_error("stress-free precise rest must be exact");auto M=filmMass(map);std::cout<<std::setprecision(17)<<map.freeSize<<'\n';for(int i=0;i<M.rows();++i)std::cout<<M(i,i)<<' ';std::cout<<'\n';for(double x:b.force-a.force)std::cout<<x<<' ';std::cout<<'\n';for(int i=0;i<a.stiffness.rows();++i)for(int j=0;j<a.stiffness.cols();++j)std::cout<<a.stiffness(i,j)<<' ';std::cout<<'\n';}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def worker(out):
 from scipy.sparse import bmat,csr_matrix,eye
 from scipy.sparse.linalg import expm_multiply
 d=np.fromstring((out/'matrix/process/stdout.log').read_text(),sep=' ');n=int(d[0]);M=d[1:1+n];B=d[1+n:1+2*n];K=d[1+2*n:].reshape(n,n);P=mapping();inv=1/np.sqrt(M);Kh=inv[:,None]*K*inv[None,:];gamma=np.sqrt(np.max(np.sum(abs(Kh),axis=1)));A=bmat([[None,gamma*eye(n)],[-csr_matrix(Kh/gamma),-2*eye(n)]],format='csr');actual=list(csv.DictReader((out/'actual.csv').open()));rows=[];references=[];passed=True
 for index in (7,19,39):
  row=actual[index];h=float(row['time']);co=np.array([0,0,0,10*(h/.01)**3,-15*(h/.01)**4,6*(h/.01)**5]);forcing=np.zeros((2*n,6));forcing[n:,:]=(inv*B)[:,None]*.0001*co;clock=np.zeros((6,6))
  for j in range(1,6):clock[j,j-1]=j
  scale=h*.0001*(h/.01)**3*np.linalg.norm(inv*B);L=bmat([[h*A,csr_matrix(h*forcing/scale)],[None,csr_matrix(clock)]],format='csr');initial=np.zeros(2*n+6);initial[2*n]=scale
  def flow(parts):
   state=initial.copy()
   for _ in range(parts):state=expm_multiply(L/parts,state,traceA=float(L.diagonal().sum())/parts)
   return dict(q=P@(inv*state[:n]/gamma),v=P@(inv*state[n:2*n]))
  one,four=flow(1),flow(4);error={};difference={}
  for key in ('q','v'):
   measured=np.fromstring(row[key],sep=' ')
   for label,region in (('all',slice(None)),('Skin',slice(0,315)),('Rails',slice(315,None))):
    error[label+'_'+key]=float(np.linalg.norm(one[key][region]-four[key][region])/max(np.linalg.norm(one[key][region]),np.linalg.norm(four[key][region])));difference[label+'_'+key]=float(np.linalg.norm(measured[region]-one[key][region])/max(np.linalg.norm(measured[region]),np.linalg.norm(one[key][region])))
  s,t=shape(one['q']),shape(four['q'])
  for key in s:
   magnitude=max(abs(s[key]),abs(t[key]));error[key]=abs(s[key]-t[key])/magnitude if magnitude else None
  passed=passed and all(v is not None and v<=1e-8 for v in error.values());rows.append(dict(time_s=h,reference_flow_split_relative=error,actual_nonlinear_vs_continuous_rest_linear_relative=difference,actual_shape=shape(np.fromstring(row['q'],sep=' ')),linear_shape=s));references.append(dict(time_s=h,q=' '.join(map(str,one['q'])),v=' '.join(map(str,one['v']))))
 with (out/'linear_states.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(references[0]));w.writeheader();w.writerows(references)
 write_json(out/'worker.json',dict(status='EXPERIMENTAL' if passed else 'FAIL',reference_flow_split_gate='PASS' if passed else 'FAIL',direct_Skin_tendon_gradient_norm=float(np.linalg.norm(B[:295])),direct_Rail_tendon_gradient_norm=float(np.linalg.norm(B[295:])),instantaneous_Skin_acceleration_sensitivity_norm=float(np.linalg.norm((B/M)[:295])),results=rows,scope='new-model rest Jacobian continuous linear response vs actual nonlinear SOFA ONLY;NOT linear model as nonlinear truth',warning='linear/nonlinear differences are conditional mechanical-model differences,not automatically solver error or wrapping performance'))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag');p.add_argument('--reuse-matrix');p.add_argument('--worker');a=p.parse_args()
 if a.worker:worker(Path(a.worker));return
 if not a.tag:raise ValueError('unique tag required')
 parent=ROOT/'results/autonomous_film_20261119_precise_window_actual1702';m=json.loads((parent/'summary.json').read_text())
 if m['status']!='PASS':raise ValueError('qualified actual1ms required')
 for f,d in m['source_hashes'].items():
  if sha(parent/'sources'/f)!=d:raise ValueError('compiled physical source changed')
 if sha(parent/'actual.csv')!=m['raw_hashes']['actual.csv']:raise ValueError('immutable actual state required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(parent/'sources',archive);cpp=archive/'tests/PreciseMatrix.cpp';cpp.write_text(CPP.replace('../../models/','../models/'));shutil.copy2(parent/'actual.csv',out/'actual.csv');mass=ROOT/'results/autonomous_film_20261119_rail_aspect_peak1652/public_mass.txt'
 if a.reuse_matrix:
  previous=ROOT/'results'/('autonomous_film_'+a.reuse_matrix)
  if {str(f.relative_to(previous/'sources')):sha(f) for f in (previous/'sources').rglob('*') if f.is_file()}!={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()} or json.loads((previous/'compile/result.json').read_text())['exit_code']!=0:raise ValueError('ALL matrix sources and completed compile required')
  shutil.copy2(previous/'matrix_observer',out/'matrix_observer');compile=dict(exit_code=0,ALL_sources_EXACT=True,reused_binary_sha256=sha(out/'matrix_observer'))
 else:compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'matrix_observer'],out/'compile',120)
 r=dict(status='FAIL',actual_summary_sha256=sha(parent/'summary.json'),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile)
 if compile['exit_code']==0:
  r['matrix_binary_sha256']=sha(out/'matrix_observer');(out/'matrix').mkdir();matrix=guarded([out/'matrix_observer',mass],out/'matrix/process',120);r['matrix_process']=matrix
  if matrix['exit_code']==0:
   run=guarded([sys.executable,__file__,'--worker',out],out/'process',180);r['process']=run
   if run['exit_code']==0:r.update(json.loads((out/'worker.json').read_text()))
 r['raw_hashes']={str(f.relative_to(out)):sha(f) for f in out.rglob('*') if f.is_file() and f.suffix in ('.csv','.log')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','raw_hashes','compile','process','matrix_process','results')}))
if __name__=='__main__':main()
