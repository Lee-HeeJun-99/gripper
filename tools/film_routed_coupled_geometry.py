"""Read-only ACTUAL moving-sphere/film/wire geometry at recorded stages."""
import argparse,csv,json,shutil,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import mapping
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text())
 if m['status']!='PASS':raise ValueError('complete actual new-route contact model required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual geometry input changed')
 for f,d in m['source_hashes'].items():
  if sha(src/'sources'/f)!=d:raise ValueError('actual physical archive changed')
 first=list(csv.DictReader((src/'three.first_interval.csv').open()));states=list(csv.DictReader((src/'three.states.csv').open()));rows=list(csv.DictReader((src/'three.rows.csv').open()));samples=[('first_'+r['stage'],r['time'],r['q']) for r in first]+[('accepted_'+str(i+1),r['time'],r['q']) for i,r in enumerate(states)]
 if len(rows)%3:raise ValueError('incomplete three-row stage groups')
 for i in range(0,len(rows),3):
  group=rows[i:i+3]
  if any(r['stage_q']!=group[0]['stage_q'] or r['time']!=group[0]['time'] for r in group):raise ValueError('owned stage geometry differs')
  samples.append(('contact_stage_'+str(i//3),group[0]['time'],group[0]['stage_q']))
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';shutil.copytree(src/'sources/models',archive/'models');cpp=archive/'diagnostics/film_three_finger/RoutedGeometry.cpp';cpp.parent.mkdir(parents=True);text=(ROOT/'diagnostics/film_three_finger/RoutedGeometry.cpp').read_text();changes={'auto c=layout.mount[0].R.transpose()*(layout.bodyCenter-layout.mount[0].origin);Point center{c[0],c[1],c[2]};':'Point center{};', 'time_s,triangle_buffer_gap_mm':'time_s,finger,triangle_buffer_gap_mm','double t;in>>t;auto x=rest;':'double t;unsigned finger;Eigen::Vector3d global;in>>t>>finger>>global[0]>>global[1]>>global[2];if(finger>2)throw std::runtime_error("finger frame out of range");auto c=layout.mount[finger].R.transpose()*(global-layout.mount[finger].origin);center={c[0],c[1],c[2]};auto x=rest;',"out<<t<<','<<gap":"out<<t<<','<<finger<<','<<gap"}
 for old,new in changes.items():
  if text.count(old)!=1:raise ValueError('exact moving geometry specialization anchor differs')
  text=text.replace(old,new)
 cpp.write_text(text);P=mapping();nf=P.shape[1];names=[]
 with (out/'samples.txt').open('w') as f:
  f.write(str(3*len(samples))+'\n')
  for name,t,raw in samples:
   q=np.fromstring(raw,sep=' ')
   if q.size!=3*nf+6:raise ValueError('actual shared state dimension')
   for finger in range(3):f.write(t+' '+str(finger)+' '+' '.join(format(x,'.17g') for x in q[3*nf:3*nf+3])+' '+' '.join(format(x,'.17g') for x in P@q[finger*nf:(finger+1)*nf])+'\n');names.append(name)
 profile=ROOT/'results/autonomous_film_20261118_routed_geometry1251';cost=json.loads((profile/'summary.json').read_text());estimate=1.2*cost['process']['runtime_s']*(3*len(samples))/294+30
 if estimate>480:raise ValueError('geometry cost forecast>480s')
 compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'geometry'],out/'compile',120);run=guarded([out/'geometry',out/'samples.txt','4.5',out/'geometry.csv'],out/'process',480) if compile['exit_code']==0 else None;r=dict(status='FAIL',scope='postprocessed ACTUAL moving-sphere geometry at recorded accepted/stage states;NOT finite-thickness/wire contact/continuous CCD/grasp qualification',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},compile=compile,process=run,predicted_runtime_s=estimate,samples=3*len(samples),wire_radius=None,guide_body_clearance=None,contact_area=None,pressure=None)
 if run and run['exit_code']==0:
  values=list(csv.DictReader((out/'geometry.csv').open()));triangle=min(enumerate(values),key=lambda z:float(z[1]['triangle_buffer_gap_mm']));wire=min(enumerate(values),key=lambda z:float(z[1]['wire_centreline_physical_gap_mm']));r.update(status='PASS' if len(values)==len(names) else 'FAIL',minimum_triangle_buffer_gap_mm=float(triangle[1]['triangle_buffer_gap_mm']),minimum_wire_centreline_gap_mm=float(wire[1]['wire_centreline_physical_gap_mm']),triangle_minimum=dict(sample=names[triangle[0]],**triangle[1]),wire_minimum=dict(sample=names[wire[0]],**wire[1]),sampled_centreline_geometry_pass=float(triangle[1]['triangle_buffer_gap_mm'])>=-1e-10 and float(wire[1]['wire_centreline_physical_gap_mm'])>=0,binary_sha256=sha(out/'geometry'),raw_hashes={'geometry.csv':sha(out/'geometry.csv')})
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process')}))
if __name__=='__main__':main()
