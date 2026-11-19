"""Fresh force/tangent/sensitivity witness of a completed lower-load static state."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import shape
CPP=r'''#include "../../models/film_rail_aspect/Design.h"
#include "../../models/film_precise_tendon/Force.h"
#include <Eigen/Eigenvalues>
#include <fstream>
#include <iostream>
#include <iomanip>
int main(int argc,char**argv){try{using namespace regrip_transmission;auto m=regrip_rail_aspect::design(.1);std::vector<Point>q(m.size()),zero(m.size());double T;std::ifstream input(argv[1]);input>>T;for(auto&p:q)for(double&v:p)input>>v;if(!input||!(T>0&&T<=.0001))throw std::runtime_error("bounded archived lower-load state required");auto map=mechanics(m,q,zero,.0001,T,publicMass(argv[2]));auto e=regrip_precise_tendon::parts(map,q,T,6.);auto B=regrip_precise_tendon::parts(map,q,1.,6.).tendon;Eigen::SelfAdjointEigenSolver<Eigen::MatrixXd>spectrum(e.stiffness);if(spectrum.info()!=Eigen::Success)throw std::runtime_error("actual tangent eigensolve failed");Eigen::VectorXd dq=e.stiffness.fullPivLu().solve(B);double residual=(e.stiffness*dq-B).norm();Eigen::VectorXd direction=dq.normalized();double eps=1e-6;auto x=map.pack(q);auto plus=regrip_precise_tendon::parts(map,map.expand(x+eps*direction),T,6.);auto minus=regrip_precise_tendon::parts(map,map.expand(x-eps*direction),T,6.);auto fd=(plus.force-minus.force)/(2*eps);auto predicted=-e.stiffness*direction;
std::ofstream out(argv[3]);out<<std::setprecision(17)<<"T_N,force_residual_N,min_tangent_eigenvalue_N_mm,max_tangent_eigenvalue_N_mm,tangent_asymmetry_N_mm,Skin_direct_tendon_sensitivity,Rail_direct_tendon_sensitivity,static_sensitivity_solve_residual,force_directional_FD_relative\n"<<T<<','<<e.force.norm()<<','<<spectrum.eigenvalues().minCoeff()<<','<<spectrum.eigenvalues().maxCoeff()<<','<<(e.stiffness-e.stiffness.transpose()).cwiseAbs().maxCoeff()<<','<<B.head(295).norm()<<','<<B.tail(354).norm()<<','<<residual<<','<<(fd-predicted).norm()/predicted.norm()<<'\n';std::ofstream sensitivity(std::string(argv[3])+".sensitivity.csv");sensitivity<<std::setprecision(17)<<"dq_dT\n\"";for(double v:dq)sensitivity<<v<<' ';sensitivity<<"\"\n";return 0;
}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'results/autonomous_film_20261119_precise_static_geometric1730';m=json.loads((src/'summary.json').read_text())
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('compiled source changed')
 raw=src/'0.1/equilibrium.states.csv'
 if sha(raw)!=m['raw_hashes']['0.1/equilibrium.states.csv']:raise ValueError('immutable partial branch changed')
 selected=[x for x in csv.DictReader(raw.open()) if x['stage']=='43']
 if len(selected)!=1:raise ValueError('explicit completed lower-load stage required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(src/'sources/models',out/'sources/models');cpp=out/'sources/diagnostics/film_three_finger/StaticWitness.cpp';cpp.parent.mkdir(parents=True);cpp.write_text(CPP);row=selected[0];(out/'state.txt').write_text(row['T']+' '+row['q']+'\n');shutil.copy2(src/'public_mass.txt',out/'public_mass.txt')
 r=dict(status='FAIL',scope='fresh independent lower-load free static tangent/transmission witness ONLY;NOT full load continuation/contact/wrapping/dynamic stability/actual SOFA',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_summary_sha256=sha(src/'summary.json'),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},full_load_status='FAIL preserved',contact_area=None,pressure=None,holding_capacity=None,shape=shape(np.fromstring(row['q'],sep=' ')))
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120)
 if r['compile']['exit_code']==0:
  r['binary_sha256']=sha(out/'reference');r['process']=guarded([out/'reference',out/'state.txt',out/'public_mass.txt',out/'witness.csv'],out/'process',120)
  if r['process']['exit_code']==0:
   r['metrics']={k:float(v) for k,v in next(csv.DictReader((out/'witness.csv').open())).items()};r['status']='PASS' if r['metrics']['force_residual_N']<=1e-12 and r['metrics']['force_directional_FD_relative']<=1e-5 else 'FAIL'
 r['raw_hashes']={f.name:sha(f) for f in out.glob('*.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','shape')}))
if __name__=='__main__':main()
