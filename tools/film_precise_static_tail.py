"""Refine a failed static load interval from a fresh certified sparse-row seed."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
SEED=r'''std::ifstream seed(argv[3]);double seedT;seed>>seedT;std::vector<Point>saved(m.size());for(auto&p:saved)for(double&v:p)seed>>v;for(double&v:lambda)seed>>v;if(!seed||lambda.minCoeff()<0)throw std::runtime_error("complete nonnegative static seed required");x=map.pack(saved);if(map.expand(x)!=saved)throw std::runtime_error("static seed violates exact root map;NO projection");auto se=regrip_precise_tendon::parts(map,saved,seedT,6.);auto sg=problem.geometry(x,lambda);double seedForce=(-se.force-sg.C*lambda).norm(),seedGap=regrip_film_native::CoupledContactStep::gapError(sg.gap,lambda);std::ofstream witness(std::string(argv[2])+".seed.csv");witness<<std::setprecision(17)<<"T_N,force_residual_N,gap_error_mm,whole_triangle_gap_mm,owned_rows\n"<<seedT<<','<<seedForce<<','<<seedGap<<','<<sg.gap.minCoeff()<<','<<lambda.size()<<'\n';witness.flush();if(seedForce>1e-12||seedGap>1e-10||sg.gap.minCoeff()<-1e-10)throw std::runtime_error("fresh static seed fails original force/gap gates");
for(unsigned stage=0;stage<8;++stage){double T=stage==7?1e-4:seedT+(1e-4-seedT)*(stage+1)/8;
'''
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--provider',default='20261119_precise_static_full1756');p.add_argument('--unload',action='store_true');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.provider);m=json.loads((src/'summary.json').read_text())
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('compiled model changed')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('immutable completed static prefix changed')
 states=list(csv.DictReader((src/'contact.states.csv').open()));row=states[-1];stage=int(row['stage']);active=[r for r in csv.DictReader((src/'contact.rows.csv').open()) if int(r['stage'])==stage];forces=['0']*320
 for r in active:
  i=int(r['triangle'])
  if forces[i]!='0' or float(r['force_N'])<=0:raise ValueError('unique positive sparse owner rows required')
  forces[i]=r['force_N']
 count=64 if a.unload else 8;forecast=2*m['process']['runtime_s']*count/len(states)+20
 if forecast>480:raise ValueError('profiled static continuation forecast>480;NOT OS exhaustion')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(src/'sources',out/'sources');shutil.copy2(src/'public_mass.txt',out/'public_mass.txt');(out/'seed.txt').write_text(row['T_N']+' '+row['q']+' '+' '.join(forces)+'\n');cpp=out/'sources/diagnostics/film_three_finger/StaticContact.cpp';code=cpp.read_text();start=code.index('for(unsigned stage=0;stage<64;++stage){double T;');end=code.index('auto r=problem.solve(x,lambda,T,trace);',start);seed=SEED.replace('auto se=regrip_precise_tendon::parts(map,saved,seedT,6.);','auto se=problem.mechanical(map,saved,seedT);')
 if a.unload:seed=seed.replace('for(unsigned stage=0;stage<8;++stage){double T=stage==7?1e-4:seedT+(1e-4-seedT)*(stage+1)/8;','for(unsigned stage=0;stage<64;++stage){double T=stage==63?0:seedT*(1.-double(stage+1)/64);')
 cpp.write_text(code[:start]+seed+code[end:])
 r=dict(status='FAIL',scope='independent fixed-sphere STATIC continuation of8 smaller load increments ONLY;NOT dynamic checkpoint/resume/actual SOFA/wrapping/grasp',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_summary_sha256=sha(src/'summary.json'),source_full_load_status='original1756 FAIL preserved',source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},seed_sha256=sha(out/'seed.txt'),seed_source_stage=stage,seed_tension_N=float(row['T_N']),seed_row_ownership='320 topology IDs;sparse absent rows are EXACT zero by original owner format,not unknown measurements',force_gate_N=1e-12,gap_gate_mm=1e-10,maximum_tension_N=1e-4,contact_area=None,pressure=None,root_reaction_work=None,contact_multiplier_unit='N force;NOT impulse',no_old_three_finger_checkpoint=True)
 r.update(scope='independent fixed-sphere STATIC '+('64-stage unload toT0' if a.unload else '8-stage load-tail')+' with fresh validated seed ONLY;NOT dynamic checkpoint/resume/actual SOFA/wrapping/grasp',source_full_load_status=m['status']+' preserved',maximum_tension_N=float(row['T_N']) if a.unload else 1e-4,expected_stages=count,predicted_child_runtime_s=forecast)
 for key in ('thickness_envelope','mount_world_z_offset_mm','thickness_scope','profile_amplitude_mm','outboard_mm'):
  if key in m:r[key]=m[key]
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120)
 if r['compile']['exit_code']==0:
  r['binary_sha256']=sha(out/'reference');r['process']=guarded(['/usr/bin/time','-v','-o',out/'resource.txt',out/'reference',out/'public_mass.txt',out/'contact',out/'seed.txt'],out/'process',480)
  if (out/'contact.states.csv').exists():
   rows=list(csv.DictReader((out/'contact.states.csv').open()));r['completed_stages']=len(rows)
   if rows:r['endpoint']={k:float(v) for k,v in rows[-1].items() if k!='q'}
   r['status']='PASS' if r['process']['exit_code']==0 and len(rows)==count and all(float(x['residual_N'])<=1e-12 and float(x['gap_error_mm'])<=1e-10 and float(x['whole_triangle_gap_mm'])>=-1e-10 for x in rows) else 'FAIL'
 r['raw_hashes']={f.name:sha(f) for f in out.glob('*.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','raw_hashes')}))
if __name__=='__main__':main()
