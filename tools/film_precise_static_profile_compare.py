"""Fresh same-load constrained-state/force/centreline-clearance audit and plots."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import shape
CPP=r'''#include "../../models/film_rail_aspect/Design.h"
#include "../../models/film_precise_static/SphereEquilibrium.h"
#include "../../models/film_precise_static/Profiled.h"
#include "../../models/film_three_finger/FrameLayout.h"
#include "../../models/film_sphere_contact/ClosestPrimitiveValue.h"
#include <fstream>
#include <iostream>
#include <iomanip>
int main(int argc,char**argv){try{using namespace regrip_precise_static;auto m=regrip_rail_aspect::design(.1);auto mass=publicMass(argv[2]);std::vector<Point>zero(m.size());auto map=mechanics(m,zero,zero,.0001,0,mass);regrip_three_finger::Layout layout;Eigen::Vector3d center=layout.mount[0].R.transpose()*(layout.bodyCenter+Eigen::Vector3d(0,0,.0001)-layout.mount[0].origin);std::ifstream in(argv[1]);unsigned cases;in>>cases;std::ofstream nodes(std::string(argv[3])+".nodes.csv"),guides(std::string(argv[3])+".guides.csv"),fixture(std::string(argv[3])+".fixture.csv");nodes<<std::setprecision(17)<<"amplitude,node,x,y,z\n";guides<<std::setprecision(17)<<"amplitude,rail,station,x,y,z\n";fixture<<std::setprecision(17)<<"cx,cy,cz,buffer_radius,actual_radius\n"<<center[0]<<','<<center[1]<<','<<center[2]<<','<<layout.bufferRadius<<','<<layout.bodyRadius<<'\n';std::cout<<std::setprecision(17)<<"amplitude,T_N,force_residual_N,whole_triangle_gap_mm,max_attachment_gap_mm,wire_centreline_buffer_gap_mm,resultant_normal_force_N,radial_contact_moment_Nmm,hypothetical_symmetric3_vertical_reaction_N\n";
for(unsigned sample=0;sample<cases;++sample){double amplitude,T;in>>amplitude>>T;std::vector<Point>q(m.size());for(auto&p:q)for(double&x:p)in>>x;Eigen::VectorXd lambda(320);for(double&x:lambda)in>>x;if(!in)throw std::runtime_error("complete selected state/owned force rows required");auto packed=map.pack(q);if(map.expand(packed)!=q)throw std::runtime_error("exact root map differs");SphereEquilibrium problem(map,{center[0],center[1],center[2]},layout.bufferRadius);auto g=problem.geometry(packed,lambda,false);auto e=regrip_precise_static_profile::parts(map,q,T,amplitude);double residual=(-e.force-g.C*lambda).norm();auto rest=m.rest();for(unsigned i=0;i<q.size();++i){auto p=add(rest[i],q[i]);nodes<<amplitude<<','<<i<<','<<p[0]<<','<<p[1]<<','<<p[2]<<'\n';}double attachment=0;regrip_precise_attachment::attachments(m,q,[&](const Element&e){attachment=std::max(attachment,std::sqrt(2*e.energy.v/m.bondK));});double wire=1e99;
for(unsigned part:{1u,2u}){std::vector<Point>points;for(unsigned k=0;k<5;++k){unsigned i=(m.nx-1)*k/4;Assembly::Local local(m.guideIds(part,i),rest); // replace with actual nodal geometry before guide query
 auto actual=rest;for(unsigned j=0;j<q.size();++j)actual[j]=add(actual[j],q[j]);Assembly::Local current(m.guideIds(part,i),actual);auto p=regrip_profiled_tendon::guide(m,current,part,i,amplitude);Point value{p[0].v,p[1].v,p[2].v};points.push_back(value);guides<<amplitude<<','<<part<<','<<k<<','<<value[0]<<','<<value[1]<<','<<value[2]<<'\n';}for(unsigned k=0;k<4;++k)wire=std::min(wire,regrip_film_sphere_value::ClosestPrimitiveValue::evaluate({points[k],points[k+1]},{center[0],center[1],center[2]},layout.bufferRadius).gap.v);}
Eigen::Vector3d force=Eigen::Vector3d::Zero(),moment=force;for(int row=0;row<lambda.size();++row)if(lambda(row)>0){auto tri=problem.triangles[row];std::vector<Point>p;for(unsigned id:tri)p.push_back(add(rest[id],q[id]));auto geo=regrip_film_sphere::ClosestPrimitive::evaluate(p,{center[0],center[1],center[2]},layout.bufferRadius);Eigen::Vector3d point(geo.point[0].v,geo.point[1].v,geo.point[2].v),F=lambda(row)*(point-center).normalized();force+=F;moment+=(point-center).cross(-F);}Eigen::Vector3d hypothetical=Eigen::Vector3d::Zero();for(unsigned f=0;f<3;++f)hypothetical-=layout.mount[f].R*force;
std::cout<<amplitude<<','<<T<<','<<residual<<','<<g.gap.minCoeff()<<','<<attachment<<','<<wire<<','<<force.norm()<<','<<moment.norm()<<','<<hypothetical.z()<<'\n';}return 0;}catch(const std::exception&e){std::cerr<<e.what()<<'\n';return 1;}}
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--wide-case');p.add_argument('--reuse-observer');a=p.parse_args();names=('20261119_precise_static_full1756','20261119_precise_static_profile05_1761','20261119_precise_static_profile45_1762')+((a.wide_case,) if a.wide_case else ());parents=[ROOT/'results'/('autonomous_film_'+n) for n in names];meta=[json.loads((p/'summary.json').read_text()) for p in parents];sets=[]
 for parent,m in zip(parents,meta):
  for f,d in m['raw_hashes'].items():
   if sha(parent/f)!=d:raise ValueError('immutable static raw changed')
  sets.append({int(x['stage']):x for x in csv.DictReader((parent/'contact.states.csv').open())})
 stage=max(set.intersection(*(set(x) for x in sets)));selected=[x[stage] for x in sets]
 if len({x['T_N'] for x in selected})!=1:raise ValueError('same original load required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(parents[-1]/'sources/models',out/'sources/models');cpp=out/'sources/diagnostics/film_three_finger/ProfileCompare.cpp';cpp.parent.mkdir(parents=True)
 code=CPP
 if a.wide_case:
  code=code.replace('amplitude,node,x','amplitude,outboard,node,x').replace('amplitude,rail,station','amplitude,outboard,rail,station').replace('amplitude,T_N,force','amplitude,outboard,T_N,force').replace('double amplitude,T;in>>amplitude>>T;','double amplitude,outboard,T;in>>amplitude>>outboard>>T;').replace('parts(map,q,T,amplitude)','parts(map,q,T,amplitude,outboard)').replace('regrip_profiled_tendon::guide(m,current,part,i,amplitude)','regrip_precise_static_profile::guide(m,current,part,i,amplitude,outboard)').replace("nodes<<amplitude<<','<<i","nodes<<amplitude<<','<<outboard<<','<<i").replace("guides<<amplitude<<','<<part","guides<<amplitude<<','<<outboard<<','<<part").replace("std::cout<<amplitude<<','<<T","std::cout<<amplitude<<','<<outboard<<','<<T")
 cpp.write_text(code);shutil.copy2(parents[-1]/'public_mass.txt',out/'public_mass.txt');text=[];metrics=[];variants=[]
 for amplitude,parent,row,m in zip((0,.5,4.5)+((4.5,) if a.wide_case else ()),parents,selected,meta):
  outboard=m.get('outboard_mm',6.);variants.append((amplitude,outboard))
  forces=['0']*320
  for value in csv.DictReader((parent/'contact.rows.csv').open()):
   if int(value['stage'])==stage:forces[int(value['triangle'])]=value['force_N']
  text.append(str(amplitude)+' '+(str(outboard)+' ' if a.wide_case else '')+row['T_N']+' '+row['q']+' '+' '.join(forces));rest=8*np.sqrt(625+amplitude**2);metrics.append(dict(amplitude_mm=amplitude,outboard_mm=outboard,T_N=float(row['T_N']),rest_cable_length_mm=float(rest),shortening_mm=float(rest)-float(row['cable_length_mm']),**shape(np.fromstring(row['q'],sep=' ')),**{k:float(row[k]) for k in ('U_skin','U_rails','U_attachment','active_force_rows')}))
 (out/'states.txt').write_text(str(len(parents))+'\n'+'\n'.join(text)+'\n');r=dict(status='FAIL',scope='fresh independent same-T/core-volume STATIC constrained profile comparison ONLY;NOT actual SOFA/wrapping/holding/free3-finger/lift',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_summary_hashes={n:sha(p/'summary.json') for n,p in zip(names,parents)},source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},selected_stage=stage,source_full_load_status={n:m['status'] for n,m in zip(names,meta)},matched_work=False,guide_hardware_volume=None,contact_area=None,pressure=None,holding_capacity=None,metrics=metrics,gravity_comparison='3 rotated copies of FIXED-object reaction is a conditional scale calculation,NOT actual3-finger/free-body load capacity;100g weight=.981N')
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'observer'],out/'compile',120)
 if r['compile']['exit_code']==0:
  r['binary_sha256']=sha(out/'observer')
  if a.reuse_observer:
   old=ROOT/'results'/('autonomous_film_'+a.reuse_observer);proof=json.loads((old/'process/result.json').read_text())
   if proof['exit_code']!=0 or sha(old/'observer')!=r['binary_sha256'] or sha(old/'states.txt')!=sha(out/'states.txt'):raise ValueError('completed identical binary/input observation required;NOT silently rerun')
   for name in ('nodes','guides','fixture'):shutil.copy2(old/('geometry.'+name+'.csv'),out/('geometry.'+name+'.csv'))
   folder=out/'process';folder.mkdir();shutil.copy2(old/'process/stdout.log',folder/'stdout.log');r['process']=dict(exit_code=0,reused_immutable_observation=str(old),result_sha256=sha(old/'process/result.json'),new_physics_process='NOT RUN')
  else:r['process']=guarded([out/'observer',out/'states.txt',out/'public_mass.txt',out/'geometry'],out/'process',120)
  if r['process']['exit_code']==0:
   fresh=[{k:float(v) for k,v in row.items()} for row in csv.DictReader((out/'process/stdout.log').open())];r['fresh_metrics']=fresh;r['status']='COMPARISON_ONLY' if all(x['force_residual_N']<=1e-12 and x['whole_triangle_gap_mm']>=-1e-10 for x in fresh) else 'FAIL';r['wire_centreline_status']='FAIL' if any(x['wire_centreline_buffer_gap_mm']<0 for x in fresh) else 'CLEAR_CENTRELINES_ONLY;finite wire/guide clearance NOT qualified'
   nodes=list(csv.DictReader((out/'geometry.nodes.csv').open()));fixture=next(csv.DictReader((out/'geometry.fixture.csv').open()));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
   fig,axes=plt.subplots(1,2,figsize=(12,5));c=(float(fixture['cx']),float(fixture['cz']));angles=np.linspace(0,2*np.pi,500);axes[0].plot(c[0]+float(fixture['buffer_radius'])*np.cos(angles),c[1]+float(fixture['buffer_radius'])*np.sin(angles),'k--',label='fixed buffer sphere cross-section')
   for amplitude,outboard in variants:
    p=np.array([[float(x[k]) for k in ('x','y','z')] for x in nodes if float(x['amplitude'])==amplitude and (not a.wide_case or float(x['outboard'])==outboard)]);skin=p[:105].reshape(21,5,3).mean(axis=1);label='profile '+str(amplitude)+' / lateral '+str(outboard)+'mm';axes[0].plot(skin[:,0],skin[:,2],label=label);axes[1].plot(np.linspace(0,100,21),skin[:,2],label=label)
    with (out/('profile_'+str(amplitude)+'_outboard_'+str(outboard)+'.obj')).open('w') as f:
     f.write('# INDEPENDENT STATIC FEM; NOT SOFA or wrapping qualification; no displacement scaling\n')
     for point in p:f.write('v '+' '.join(format(v,'.17g') for v in point)+'\n')
     for offset,ny in ((0,5),(105,3),(168,3)):
      for i in range(20):
       for j in range(ny-1):
        ia=offset+i*ny+j+1;ib=ia+ny;ic=ia+1;id_=ib+1;f.write(f'f {ia} {ib} {ic}\nf {ib} {id_} {ic}\n')
   axes[0].set(xlabel='Actual local x [mm]',ylabel='Actual local z [mm]',xlim=(0,105),ylim=(-35,10));axes[0].set_aspect('equal',adjustable='box');axes[1].set(xlabel='Material coordinate [mm]',ylabel='Width-mean z [mm]')
   for ax in axes:ax.legend();ax.grid(alpha=.3)
   fig.suptitle('Independent constrained static FEM —same'+format(float(selected[0]['T_N'])*1e6,'.2f')+'uN/core volume;actual stored coordinates\nProjection only;3D whole-triangle gap audited separately;NOT SOFA/wrapping/holding');fig.tight_layout();fig.savefig(out/'static_constrained_profiles.png',dpi=150);plt.close(fig)
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.is_file()};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('metrics','fresh_metrics','source_hashes','raw_hashes','compile','process')}))
if __name__=='__main__':main()
