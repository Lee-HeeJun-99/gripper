"""Isolate tiny Rail→Skin constitutive VALUE from solver/time integration."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
CPP=r'''#include "../../models/film_transmission/Kernel.h"
#include <iostream>
#include <iomanip>
int main(int argc,char**argv){try{using namespace regrip_transmission;auto m=model();std::cout<<std::setprecision(17)<<"mode,delta_mm,Skin_Fz_N,Rail_Fz_N,expected_Skin_Fz_N,AD_dSkinFz_dLeftRailTranslation_N_mm\n";for(unsigned mode=0;mode<2;++mode)for(double delta:{0.,1e-10,1e-14,1e-18,1e-24,1e-30}){std::vector<Point>u(m.size());for(unsigned part=0;part<3;++part)if(mode==1||part==1)for(unsigned i=0;i<m.parts[part].nx*m.parts[part].ny;++i)u[m.parts[part].offset+i][2]=delta;double skin=0,rail=0,jac=0;m.elements(u,0,[&](const Element&e){if(e.kind!=1)return;for(unsigned a=0;a<3*e.ids.size();++a){if(a%3!=2)continue;if(e.ids[a/3]<105){skin-=e.energy.g[a];for(unsigned b=0;b<3*e.ids.size();++b)if(b%3==2&&e.ids[b/3]>=105&&e.ids[b/3]<168)jac-=e.energy.h[N*a+b];}else rail-=e.energy.g[a];}});std::cout<<(mode?"rigid_all_parts":"relative_left_rail")<<','<<delta<<','<<skin<<','<<rail<<','<<(mode?0:5*m.bondK*delta)<<','<<jac<<'\n';} }catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--precise',action='store_true');a=p.parse_args();provider=ROOT/'results/autonomous_film_20261119_rail_aspect_api1654';pm=json.loads((provider/'summary.json').read_text())
 if pm['status']!='PASS':raise ValueError('qualified actual model source required')
 for f,d in pm['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('compiled physical source changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(provider/'sources/models',archive/'models');diag=archive/'diagnostics/film_three_finger';diag.mkdir(parents=True);cpp=diag/'AttachmentValue.cpp';code=CPP
 if a.precise:
  shutil.copytree(ROOT/'models/film_precise_attachment',archive/'models/film_precise_attachment');code=code.replace('#include "../../models/film_transmission/Kernel.h"','#include "../../models/film_transmission/Kernel.h"\n#include "../../models/film_precise_attachment/Elements.h"').replace('m.elements(u,0,[&]','regrip_precise_attachment::attachments(m,u,[&]')
 cpp.write_text(code);compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'probe'],out/'compile',120);run=guarded([out/'probe'],out/'process',60) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='independent unprojected attachment constitutive value/Jacobian/rigid-translation test ONLY;NO solver/time/SOFA dynamic/grasp',variant='reference-exact displacement-frame attachment' if a.precise else 'legacy global-coordinate attachment',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_model_summary_sha256=sha(provider/'summary.json'),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,bond_k_N_mm=.001,actuation_T_N=0,contact='NONE',physical_parameters='unchanged100mm/24mm/.05mmSkin/.1mmRail/E250MPa,nu0,5attachments per rail',reference='uniform left-rail translation dz,flat unchanged normal:sum SkinFz=5*k*dz;rigid translation all parts:SkinFz=0',precision_gate_relative=.001,original_absolute_API_FD_gates='preserved;this probes additional tiny-signal value range',selected_model=None)
 if run and run['exit_code']==0:
  rows=list(csv.DictReader((out/'process/stdout.log').open()));records=[]
  for x in rows:
   row={k:float(v) if k!='mode' else v for k,v in x.items()};delta=row['delta_mm'];scale=(5 if row['mode']=='relative_left_rail' else 10)*.001*delta;row['normalized_constitutive_value_error']=abs(row['Skin_Fz_N']-row['expected_Skin_Fz_N'])/scale if scale else None;records.append(row)
  with (out/'precision.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
  worst=max(x['normalized_constitutive_value_error'] for x in records if x['normalized_constitutive_value_error'] is not None);r.update(status='PASS' if worst<=.001 else 'FAIL',observer_completed=True,maximum_normalized_error=worst,metrics=records,binary_sha256=sha(out/'probe'),raw_hashes={'precision.csv':sha(out/'precision.csv')},failure_reason='relative Rail shift / rigid translation lost in value evaluation below coordinate ULP;AD Jacobian may remain nonzero' if worst>.001 else None)
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','metrics')}))
if __name__=='__main__':main()
