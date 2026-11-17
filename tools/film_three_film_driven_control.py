"""Actual applied C2 input audit and scale-one state-derived observables."""
import argparse,csv,json,os,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'identity.json').read_text())
 if json.loads((src/'summary.json').read_text())['status']!='PASS' or not meta['actual_solver'].startswith('ThreeFilmDrivenODE'):raise ValueError('completed actual driven owner required')
 ref=ROOT/'results'/('autonomous_film_'+meta['reference']);reference=list(csv.DictReader((ref/'states.csv').open()));states=list(csv.DictReader((src/'three.states.csv').open()));scene=ET.parse(src/'scene.scn');rest=np.fromstring(scene.find('.//TriangleSetTopologyContainer').get('position'),sep=' ').reshape(-1,3)
 error=0.;measurements=[];last_work=0.
 for f in range(3):
  rows=list(csv.DictReader((src/('film_'+str(f)+'.csv')).open()));field=scene.find('Node[@name="finger'+str(f)+'"]//FilmRailTendon')
  if len(rows)!=meta['steps'] or len(reference)!=meta['steps']:raise ValueError('incomplete input audit')
  if any(float(field.get(k))!=v for k,v in dict(maximumTension=.0001,rampTime=.01,releaseBegin=.02,releaseEnd=.03,c2Control=1).items()):raise ValueError('actual control XML differs')
  for r,expected in zip(rows,reference):
   error=max(error,abs(float(r['T_per_rail'])-float(expected['tension'])));x=np.fromstring(r['x'],sep=' ').reshape(-1,3)
   measurements.append(dict(finger=f,time=float(r['time']),tension_N=float(r['T_per_rail']),cable_length_mm=float(r['cable_length']),field_tendon_work_Nmm=float(r['tendon_work']),tip_local_z_mm=float(x[102,2]-rest[102,2]),mid_local_z_mm=float(x[52,2]-rest[52,2])))
  last_work+=float(rows[-1]['tendon_work'])
 final=np.fromstring(states[-1]['q'],sep=' ');initial=np.fromstring(next(csv.DictReader((src/'three.rows.csv').open()))['stage_q'],sep=' ')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py')
 with (out/'observed.csv').open('w') as stream:w=csv.DictWriter(stream,fieldnames=measurements[0]);w.writeheader();w.writerows(measurements)
 os.environ.setdefault('MPLCONFIGDIR',str(out/'matplotlib_cache'));import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,3,figsize=(13,4))
 for f in range(3):
  r=[x for x in measurements if x['finger']==f];t=[x['time'] for x in r]
  for ax,key in zip(axes,('tension_N','tip_local_z_mm','field_tendon_work_Nmm')):ax.plot(t,[x[key] for x in r],label='finger'+str(f));ax.set_ylabel(key);ax.set_xlabel('actual time [s]');ax.grid();ax.legend()
 fig.suptitle('Actual SOFA C2 10ms already-touching pilot;NOT wrapping/lift/grasp\n'+meta['source_commit'][:8]+' DLL '+meta['binary_sha256'][:12]);fig.tight_layout();fig.savefig(out/'actual_control.png',dpi=160);plt.close(fig)
 result=dict(status='PASS' if error<=1e-18 else 'FAIL',scope='actual accepted field C2 input vs independent existing ControlProfile;NOT stage tangent,time convergence or energy certification',case=a.case,max_absolute_tension_error_N=error,final_body_translation_mm=(final[-6:-3]-initial[-6:-3]).tolist(),field_sampled_tendon_work_Nmm=last_work,work_note='actual field sampling inventory,NOT independently quadrature-qualified energy/work',raw_hashes={name:sha(src/name) for name in ('identity.json','scene.scn','three.states.csv','three.rows.csv','film_0.csv','film_1.csv','film_2.csv')})
 write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
