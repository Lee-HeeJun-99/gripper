"""Record front/back geometry at a completed whole-triangle gap violation."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--gap-case',required=True);a=p.parse_args()
    source=ROOT/'results'/('autonomous_film_'+a.case);gap=ROOT/'results'/('autonomous_film_'+a.gap_case)
    if json.loads((source/'summary.json').read_text()).get('status')!='PASS':raise ValueError('complete trajectory only')
    gs=json.loads((gap/'summary.json').read_text())
    if gs['inputs']['contact.csv']!=sha(source/'1/contact.csv'):raise ValueError('gap oracle does not belong to this trajectory')
    target=min(csv.DictReader((gap/'gaps.csv').open()),key=lambda r:float(r['minimum_buffered_mid_surface_gap_mm']));time=float(target['time']);rows=csv.DictReader((source/'1/contact.csv').open());row=next(r for r in rows if float(r['time'])==time)
    tree=ET.parse(source/'1/scene.scn');actual=tree.find("Node[@name='assembly']/Node[@name='actual']");triangles=np.fromstring(actual.find('TriangleSetTopologyContainer').get('triangles'),sep=' ',dtype=int).reshape(-1,3);indices=triangles[int(target['closest_triangle'])];center=np.fromstring(tree.find("Node[@name='fixed']/MechanicalObject").get('position'),sep=' ');stages={}
    for key in ('begin_positions','free_positions','positions'):
        tri=np.fromstring(row[key],sep=' ').reshape(-1,3)[indices];normal=np.cross(tri[1]-tri[0],tri[2]-tri[0]);norm=float(np.linalg.norm(normal))
        if norm==0:raise ValueError('degenerate triangle;front side not defined')
        signed=float(np.dot(center-tri[0],normal/norm));stages[key]=dict(signed_front_distance_mm=signed,side='front' if signed>0 else 'back' if signed<0 else 'coplanar')
    sdk=Path(json.loads((source/'identity.json').read_text())['sdk']);headers={}
    for name in ('Triangle','Line','Point'):
        path=sdk/'include/Sofa.Component.Collision.Geometry/sofa/component/collision/geometry'/(name+'CollisionModel.inl')
        if path.exists():headers[str(path)]=dict(sha256=sha(path),default_declaration=[line.strip() for line in path.read_text().splitlines() if 'd_bothSide(initData' in line])
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    result=dict(status='EXPERIMENTAL',scope='candidate-culling hypothesis geometry;NOT detector branch trace or physical certification',case=a.case,gap_case=a.gap_case,time=time,triangle_indices=indices.tolist(),gap_record=target,stages=stages,explicit_collision_parameters={n.tag:dict(n.attrib) for n in actual if n.tag in ('TriangleCollisionModel','LineCollisionModel','PointCollisionModel')},sdk_headers=headers,inputs={name:sha(source/'1'/name) for name in ('scene.scn','contact.csv')},script_sha256=sha(__file__),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    write_json(out/'summary.json',result);print(json.dumps(dict(time=time,triangle=indices.tolist(),stages=stages)))
if __name__=='__main__':main()
