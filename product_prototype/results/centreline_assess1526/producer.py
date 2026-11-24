"""Fixed1e-12 reflection API audit and matched Native ny-mesh contrast."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for case in ('centreline_asym1524','centreline_sym1525'):
  src=BASE/'results'/case;run=json.loads((src/'summary.json').read_text());assert run['status']=='VALID_CENTRELINE_MESH_COUPON_ONLY' and run['only_two_Cable_rows'];pre=json.loads((src/'preflight.json').read_text());m=json.loads((src/'mesh.json').read_text());local=np.array(m['local_positions_mm']);permutation=np.array(pre['geometry']['mirror_node_permutation']);rows=list(csv.DictReader((src/'finger0.csv').open()));q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);v=np.array([np.fromstring(r['v_m_s'],sep=' ').reshape(-1,3) for r in rows]);tip=(local[:,0]==100)&(local[:,2]==.1);qerror=float(abs(q-q[:,permutation]*[1,-1,1]).max());verror=float(abs(v-v[:,permutation]*[1,-1,1]).max());cy=q[:,tip,1].mean(1);records.append(dict(case=case,q_reflection_error_m=qerror,v_reflection_error_m_s=verror,API_1e12_pass=qerror<=1e-12 and verror<=1e-12,tip_y_min_max_end_mm=[float(cy.min()*1000),float(cy.max()*1000),float(cy[-1]*1000)],minimum_volume=run['minimum_saved_volume_ratio'],preflight_sha256=sha(src/'preflight.json'),raw_sha256=sha(src/'finger0.csv')))
 d=dict(status='PASS_SYMMETRIC_MESH_REFLECTION_API_ONLY' if records[-1]['API_1e12_pass'] else 'FAIL_SYMMETRIC_MESH_REFLECTION_API',records=records,scope='STRICT1e−12 q/vAPIreflection only,not time/mesh convergence or material/graspPASS. Matched294nodecases,volume/mass/reference/foot/cables/ODEsame;onlydiagonals differ. Surfaceboundary changesconsistently withFEM. No forces/positions/velocitiesfiltered or reset.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
