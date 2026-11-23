import argparse,csv,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/contact_gap_probe1212';st=list(csv.DictReader((src/'probe.states.csv').open()));rows=list(csv.DictReader((src/'probe.rows.csv').open()));js=list(csv.DictReader((src/'probe.J.csv').open()));records=[]
 for r in st:
  if r['phase']!='build_end':continue
  t=float(r['time_s']);rr=[x for x in rows if x['phase']=='build_end' and abs(float(x['time_s'])-t)<1e-14 and int(x['row'])%3==0];jj=[x for x in js if x['phase']=='build_end' and abs(float(x['time_s'])-t)<1e-14 and int(x['row'])%3==0];q=np.fromstring(r['q'],sep=' ');fq=np.fromstring(r['free_q'],sep=' ');records.append(dict(time_s=t,previous_lower_face_z_m=float(q[2]-.0001),free_lower_face_z_m=float(fq[2]-.0001),normal_row_dFree=[float(x['dFree']) for x in rr],normal_row_parent_translation_J=[np.fromstring(x['values'],sep=' ')[:3].tolist() for x in jj]))
 control={}
 for case in ('layer_surface_slip1213','layer_surface_friction1214'):
  file=BASE/'results'/case/'rigid.csv';rr=list(csv.DictReader(file.open()));last=rr[-1];I=np.fromstring(last['object_impulse_Ns_Nms'],sep=' ')[:3];control[case]=dict(final_x_m=float(np.fromstring(last['rigid_q'],sep=' ')[0]),final_contact_force_N=(I/.0002).tolist(),qualification='Contact support restored but mu0 lateral locking invalidates friction control;not PASS')
 d=dict(status='CONTACT_NORMAL_DEGENERACY_DIAGNOSTIC_ONLY',rows=records,surface_normal_controls=control,physical_validation='NOT QUALIFIED',scope='Normal grouping uses actual mu.3 response three-row layout. At coincidence all normal rows become horizontal;later reverseZ. Policy contrast is not universal SOFA bug or verified friction repair.',input_hashes={str(f.relative_to(BASE)):sha(f) for f in (src/'probe.states.csv',src/'probe.rows.csv',src/'probe.J.csv',Path(__file__))});(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(dict(status=d['status'],controls=control)))
if __name__=='__main__':main()
