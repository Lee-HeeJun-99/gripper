"""Reflection contrast from actual Native no-object coupons;not a grasp PASS."""
import argparse,csv,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def read(p):return list(csv.DictReader(p.open()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);folders=[BASE/'results'/name for name in ('mirror_control1521','mirror_reflected1522')];data=[];xml=[];local=np.array(json.loads((folders[0]/'mesh.json').read_text())['local_positions_mm']);permutation=np.array(json.loads((folders[0]/'preflight.json').read_text())['mirror_node_permutation']);tip=(local[:,0]==100)&(local[:,2]==.1);clocks=[];records=[]
 for folder in folders:
  run=json.loads((folder/'summary.json').read_text());assert run['status']=='VALID_NOOBJECT_MIRROR_COUPON_ONLY' and run['only_two_Cable_rows'];rows=read(folder/'finger0.csv');clocks.append([float(r['time_s']) for r in rows]);q=np.array([np.fromstring(r['q_m'],sep=' ').reshape(-1,3) for r in rows]);v=np.array([np.fromstring(r['v_m_s'],sep=' ').reshape(-1,3) for r in rows]);data.append((q,v));root=ET.parse(folder/'scene.scn').getroot();q0=np.fromstring(root.find("Node[@name='finger0']/MechanicalObject").get('position'),sep=' ').reshape(-1,3);displacement=q-q0;twist=(displacement[:,tip,0][:,-1]-displacement[:,tip,0][:,0]);cy=displacement[:,tip,1].mean(1);records.append(dict(case=folder.name,tip_lateral_min_max_end_mm=[float(cy.min()*1000),float(cy.max()*1000),float(cy[-1]*1000)],tip_crosswidth_normal_difference_end_mm=float(twist[-1]*1000),minimum_volume=run['minimum_saved_volume_ratio'],raw_sha256=sha(folder/'finger0.csv')));root.find("Node[@name='finger0']/MeshTopology").attrib.pop('tetrahedra')
  for node in root.iter():
   for k,val in list(node.attrib.items()):node.set(k,val.replace(str(folder),'__OUTPUT__'))
  xml.append(ET.tostring(root))
 assert clocks[0]==clocks[1] and xml[0]==xml[1];q0,v0=data[0];q1,v1=data[1];rq=q0[:,permutation]*[1,-1,1];rv=v0[:,permutation]*[1,-1,1];d=dict(status='ACTUAL_NOOBJECT_TET_REFLECTION_CONTRAST_ONLY',records=records,normalized_Scene_equal_except_tetrahedra=True,only_two_Cable_rows_both=True,maximum_actual_unreflected_q_difference_m=float(abs(q1-q0).max()),maximum_reflected_q_prediction_error_m=float(abs(q1-rq).max()),maximum_reflected_v_prediction_error_m_s=float(abs(v1-rv).max()),scope='Samephysicalreference/mass/foot/guide/cable/BC/ODE;onlytetconnectivity reflected. If lateral/twist signsreverse while reflectedpredictionmatches,this isolatesdiscretization handedness inthis no-object case,not a unique fullcontactspin cause. No newmesh/grasp/time/physicalPASS.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
