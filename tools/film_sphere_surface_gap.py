"""Actual deformed triangle/sphere gap, distinct from vertex gap and area."""
import argparse,csv,json,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_surface_distance import point_triangles
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args()
    source=ROOT/'results'/('autonomous_film_'+a.case)/'1';s=json.loads((source.parent/'summary.json').read_text())
    if s.get('status')!='PASS' or not s.get('finite'):raise RuntimeError('completed finite trial only')
    tree=ET.parse(source/'scene.scn');observer=tree.find('FilmNativeObserver')
    if observer.get('objectShape','sphere')!='sphere':raise ValueError('sphere-only geometry audit')
    center=np.fromstring(tree.find("Node[@name='fixed']/MechanicalObject").get('position'),sep=' ');radius=float(observer.get('radius'));buffer=float(tree.find('MinProximityIntersection').get('contactDistance'))
    indices=np.fromstring(tree.find("Node[@name='assembly']/Node[@name='actual']/TriangleSetTopologyContainer").get('triangles'),sep=' ',dtype=int).reshape(-1,3)
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);records=[]
    for row in csv.DictReader((source/'contact.csv').open()):
        q=np.fromstring(row['positions'],sep=' ').reshape(-1,3);distance,closest,degenerate=point_triangles(center,q[indices]);i=int(distance.argmin())
        records.append(dict(time=float(row['time']),minimum_mid_surface_gap_mm=float(distance[i]-radius),minimum_buffered_mid_surface_gap_mm=float(distance[i]-radius-buffer),closest_triangle=i,degenerate_triangles=degenerate,closest_x=float(closest[i,0]),closest_y=float(closest[i,1]),closest_z=float(closest[i,2])))
    with (out/'gaps.csv').open('x') as stream:
        w=csv.DictWriter(stream,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    result=dict(status='EXPERIMENTAL',scope='closest point on actual planar FE triangles;NOT contact area/pressure/finite-thickness certification',
        minimum_mid_surface_gap_mm=min(r['minimum_mid_surface_gap_mm'] for r in records),minimum_buffered_mid_surface_gap_mm=min(r['minimum_buffered_mid_surface_gap_mm'] for r in records),
        maximum_degenerate_triangles=max(r['degenerate_triangles'] for r in records),inputs={name:sha(source/name) for name in ('scene.scn','contact.csv')},
        script_sha256=sha(__file__),geometry_source_sha256=sha(ROOT/'tools/film_surface_distance.py'),finite_thickness_gap=None,contact_area=None)
    write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
