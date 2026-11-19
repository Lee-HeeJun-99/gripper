"""Independent geometric audit of NEW thickness-aware accepted static states."""
import argparse,csv,json,shutil,subprocess,os
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_precise_static_thickness_audit import CPP
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text())
 if m['status']!='PASS' or not m.get('thickness_envelope'):raise ValueError('completed thickness model required')
 for key in ('source_hashes','raw_hashes'):
  for f,d in m[key].items():
   if sha(src/('sources' if key=='source_hashes' else '')/f)!=d:raise ValueError('immutable source/raw changed')
 rows=list(csv.DictReader((src/'contact.states.csv').open()));out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(src/'sources/models',out/'sources/models');cpp=out/'sources/diagnostics/film_three_finger/EnvelopeClearance.cpp';cpp.parent.mkdir(parents=True)
 code=CPP.replace('Eigen::Vector3d(0,0,.0001)','Eigen::Vector3d(0,0,'+str(m['mount_world_z_offset_mm'])+')')
 amp=m.get('profile_amplitude_mm',0);lat=m.get('outboard_mm',6)
 if amp==0 and lat==6:code=code.replace('film_precise_static/Profiled.h','film_lateral_tendon/Route.h').replace('regrip_precise_static_profile::guide(m,local,part,i,4.5,8.)','regrip_lateral_tendon::guide(m,local,part,i,6.)')
 else:code=code.replace('part,i,4.5,8.)','part,i,'+str(amp)+','+str(lat)+')')
 cpp.write_text(code);(out/'states.txt').write_text(str(len(rows))+'\n'+'\n'.join(' '.join((r['stage'],r['T_N'],r['q'])) for r in rows)+'\n')
 r=dict(status='FAIL',scope='independent audit of all committed STATIC load states;NOT SOFA/contact area/pressure/continuous path/wrapping',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_summary_sha256=sha(src/'summary.json'),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},mount_world_z_offset_mm=m['mount_world_z_offset_mm'],profile_amplitude_mm=amp,outboard_mm=lat,wire_radius_measured=None,root_work=None)
 r['compile']=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'observer'],out/'compile',120)
 if r['compile']['exit_code']==0:
  r['binary_sha256']=sha(out/'observer');r['process']=guarded([out/'observer',out/'states.txt'],out/'process',120)
  if r['process']['exit_code']==0:
   shutil.copy2(out/'process/stdout.log',out/'clearance.csv');values=list(csv.DictReader((out/'clearance.csv').open()));minimum={k:min(float(x[k]) for x in values) for k in values[0] if k not in ('stage','T_N')};r.update(minimum_gaps_mm=minimum,sampled_states=len(values),status='PASS_SAMPLED_GEOMETRY' if min(minimum.values())>=0 and len(values)==len(rows) else 'FAIL',wire_scope='zero-radius centreline only;finite measured wire/guide/self-collision NOT qualified')
   os.environ.setdefault('MPLCONFIGDIR','/tmp/regrip-matplotlib');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
   fig,ax=plt.subplots();T=[float(x['T_N'])*1e6 for x in values]
   for key in ('Skin_envelope_gap_mm','Rail_envelope_gap_mm','wire_centreline_actual_sphere_gap_mm'):ax.plot(T,[float(x[key]) for x in values],label=key)
   ax.axhline(0,color='k',lw=.6);ax.set(xlabel='Prescribed tension per rail [uN]',ylabel='Gap to actual R30 sphere [mm]',title='Independent static accepted states — NOT SOFA/grasp');ax.legend(fontsize=6);fig.tight_layout();fig.savefig(out/'clearance.png');plt.close(fig)
 r['raw_hashes']={f.name:sha(f) for f in out.glob('*.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k!='source_hashes'}))
if __name__=='__main__':main()
