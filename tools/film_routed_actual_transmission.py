"""Read-only nonlinear tendon/attachment inventory from actual SOFA endpoints."""
import argparse,csv,json,os,shutil,subprocess,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_transmission_linear import mapping,shape
def prepare_transmission(cpp,lateral):
 text=(ROOT/'diagnostics/film_three_finger/RoutedTransmission.cpp').read_text()
 if lateral:text=text.replace('film_routed_tendon/Step.h','film_lateral_tendon/Step.h').replace('regrip_routed_tendon','regrip_lateral_tendon').replace('4.5','6.')
 cpp.write_text(text)
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--qualification');a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);m=json.loads((src/'summary.json').read_text())
 if m['status'] not in ('PASS','EXPERIMENTAL') or m['process']['exit_code'] or m['sofa_errors']:raise ValueError('completed actual required')
 if m['status']=='EXPERIMENTAL':
  qual=ROOT/'results'/('autonomous_film_'+a.qualification);qm=json.loads((qual/'summary.json').read_text())
  if qm['status']!='PASS' or qm['actual_summary_sha256']!=sha(src/'summary.json'):raise ValueError('actual API qualification required')
 for f,d in m['raw_hashes'].items():
  if sha(src/f)!=d:raise ValueError('actual raw changed')
 tokens=(src/'input.checkpoint').read_text().split();lateral=tokens[0] in ('REGRIP_LATERAL_PERSISTENT_V1','REGRIP_LATERAL_CONTROLLED_V1','REGRIP_LATERAL_FREE_V1','REGRIP_LATERAL_REST_FREE_V1','REGRIP_STATIONARY_CONTACT_V1','REGRIP_STATIONARY_FREE_V1','REGRIP_STATIONARY_GAUSS_FREE_V1')
 provider=src if lateral else ROOT/'results/autonomous_film_20261118_routed_resume1278';proof=json.loads((provider/'summary.json').read_text())
 for f,d in proof['source_hashes'].items():
  if sha(provider/'sources'/f)!=d:raise ValueError('physical source archive changed')
 P=mapping();n=3*P.shape[1]+6;tokens=(src/'input.checkpoint').read_text().split()
 if sha(src/'input.checkpoint')!=m['input_checkpoint_sha256'] or tokens[0] not in ('REGRIP_ROUTED_PERSISTENT_V1','REGRIP_LATERAL_PERSISTENT_V1','REGRIP_LATERAL_CONTROLLED_V1','REGRIP_LATERAL_FREE_V1','REGRIP_LATERAL_REST_FREE_V1','REGRIP_STATIONARY_CONTACT_V1','REGRIP_STATIONARY_FREE_V1','REGRIP_STATIONARY_GAUSS_FREE_V1'):raise ValueError('actual route-bound checkpoint required')
 pos=5+2*n+4+693+36
 for f in range(3):
  pairs=np.array(tokens[pos:pos+1386],float).reshape(693,2);pos+=1386;R=np.zeros_like(P)
  for row,(index,weight) in enumerate(pairs):
   if index>=0:R[row,int(index)]=weight
  if not np.array_equal(P,R):raise ValueError('actual root mapping differs')
 states=list(csv.DictReader((src/'three.states.csv').open()));fields=[list(csv.DictReader((src/f'film_{f}.csv').open())) for f in range(3)];contacts=list(csv.DictReader((src/'three.rows.csv').open()));rest=np.fromstring(ET.parse(src/'scene.scn').find('.//TriangleSetTopologyContainer').get('position'),sep=' ');samples=[];metrics=[];error=0.
 for i,s in enumerate(states):
  q=np.fromstring(s['q'],sep=' ');v=np.fromstring(s['v'],sep=' ');t=float(s['time'])
  for f in range(3):
   field=fields[f][i];x=np.fromstring(field['x'],sep=' ');u=P@q[f*649:(f+1)*649];vel=P@v[f*649:(f+1)*649];error=max(error,float(np.max(abs(x-rest-u))))
   if float(field['time'])!=t:raise ValueError('actual field clock differs')
   samples.append(' '.join((format(t,'.17g'),str(f),field['T_per_rail'],' '.join(format(z,'.17g') for z in u),' '.join(format(z,'.17g') for z in vel))))
   matching=[row for row in contacts if float(row['time'])==t and int(row['owner_finger'])==f]
   if matching:
    if any(not np.array_equal(np.fromstring(matching[0]['stage_'+k],sep=' '),np.fromstring(s[k],sep=' ')) for k in ('q','v')):raise ValueError('actual endpoint contact row identity differs')
    normal=float(matching[0]['force']);kind='actual owned contact row'
   else:
    # Zero is justified ONLY by the accepted checkpoint's explicitly empty
    # active set, never by absent CSV rows or a failed/incomplete process.
    snapshots=[cp for cp in src.glob('three.checkpoint_*.txt') if float(cp.read_text().split()[1])==t]
    if len(snapshots)!=1:raise ValueError('explicit accepted FREE checkpoint required')
    cp=snapshots[0];z=cp.read_text().split()
    if sha(cp)!=m['raw_hashes'][cp.name] or z[0] not in ('REGRIP_LATERAL_FREE_V1','REGRIP_STATIONARY_FREE_V1','REGRIP_STATIONARY_GAUSS_FREE_V1') or z[z.index('FREE_ACTIVE_COUNT')+1]!='0' or not np.array_equal(np.array(z[5:5+n],float),q) or not np.array_equal(np.array(z[5+n:5+2*n],float),v):raise ValueError('accepted FREE ownership/state differs')
    normal=0.;kind='explicit empty accepted active set;NOT missing-data fill'
   metrics.append(dict(time_s=t,finger=f,endpoint_normal_force_N=normal,normal_force_evidence=kind,object_vz_mm_s=float(v[-4]),**shape(u)))
 if error>1e-12:raise ValueError('actual field reconstruction differs')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copytree(provider/'sources/models',out/'sources/models');cpp=out/'sources/diagnostics/film_three_finger/RoutedTransmission.cpp';cpp.parent.mkdir(parents=True);prepare_transmission(cpp,lateral);(out/'samples.txt').write_text(str(len(samples))+'\n'+'\n'.join(samples)+'\n');sources={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()};compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'observer'],out/'compile',120);run=guarded([out/'observer',out/'samples.txt',out/'transmission.csv'],out/'process',480) if compile['exit_code']==0 else None
 r=dict(status='FAIL',scope='actual nonlinear endpoint force/power/shape inventory;NOT time/mesh/grasp or holding capacity',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),actual_summary_sha256=sha(src/'summary.json'),source_hashes=sources,compile=compile,process=run,actual_reconstruction_error_mm=error,root_reaction_work=None,contact_area=None,pressure=None,holding_load=None)
 if run and run['exit_code']==0:
  rows=list(csv.DictReader((out/'transmission.csv').open()))
  if len(rows)!=len(metrics):raise ValueError('incomplete force inventory')
  records=[dict(**{k:float(v) for k,v in row.items()},**{k:v for k,v in metric.items() if k not in row}) for row,metric in zip(rows,metrics)]
  with (out/'response.csv').open('w') as file:w=csv.DictWriter(file,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
  net=max(float(x['attachment_net_force_norm_N']) for x in rows);moment=max(float(x['attachment_net_moment_norm_Nmm']) for x in rows);direct=max(float(x['skin_direct_tendon_norm_N']) for x in rows);length_error=max(abs(float(row['cable_length_mm'])-float(fields[int(row['finger'])][i//3]['cable_length'])) for i,row in enumerate(rows))
  os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
  fig,axes=plt.subplots(2,2,figsize=(11,8));z=[x for x in records if x['finger']==0];time=[x['time_s']*1000 for x in z]
  for ax,keys in zip(axes.flat,(('rail75_tendon_Fz_N','skin75_attachment_Fz_N'),('skin75_mean_vz_mm_s','rail75_mean_vz_mm_s'),('skin_root_tip_total_angle_rad','left_root_tip_total_angle_rad'),('endpoint_normal_force_N','object_vz_mm_s'))):
   for k in keys:ax.plot(time,[x[k] for x in z],label=k)
   ax.set_xlabel('actual time [ms]');ax.legend(fontsize=7)
  axes.flat[-1].set_title('different units:force[N],velocity[mm/s]');fig.suptitle('ACTUAL routed3-finger saved endpoints;gravity0,NO friction\nDLL '+m['binary_sha256'][:12]+';NOT wrapping/holding/lift');fig.tight_layout();fig.savefig(out/'transmission.png',dpi=150);plt.close(fig)
  r.update(status='PASS' if net<1e-12 and moment<1e-12 and direct==0 and length_error<1e-12 else 'FAIL',samples=len(rows),binary_sha256=sha(out/'observer'),attachment_net_force_max_N=net,attachment_net_moment_max_Nmm=moment,skin_direct_tendon_force_max_N=direct,actual_field_cable_length_error_mm=length_error,endpoint=records[-3:],raw_hashes={f:sha(out/f) for f in ('samples.txt','transmission.csv','response.csv','transmission.png')})
 write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','process','endpoint')}))
if __name__=='__main__':main()
