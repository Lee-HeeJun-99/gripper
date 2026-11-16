"""Independent accepted-row pullback audit. Not pressure or fixed-root reaction."""
import argparse,csv,json
import numpy as np
from curve_common import ROOT,sha,write_json
from film_surface_distance import point_triangles

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args()
    source=ROOT/'results'/('autonomous_film_'+a.case)/'1'
    status=json.loads((source.parent/'summary.json').read_text())
    if status.get('status')!='PASS' or not status.get('finite'):raise ValueError('complete finite case required')
    import xml.etree.ElementTree as ET
    scene=ET.parse(source/'scene.scn');owner=scene.find('FilmNativeCoupledCorrection')
    if owner is None or owner.get('candidateComplete')!='1':raise ValueError('independent owned rows required')
    center=np.fromstring(scene.find("Node[@name='fixed']/MechanicalObject").get('position'),sep=' ')
    radius=8+float(owner.get('contactDistance'))
    contacts={r['time']:r for r in csv.DictReader((source/'contact.csv').open())}
    momentum={r['time']:r for r in csv.DictReader((source/'momentum.csv').open())}
    errors=dict(gap=0.,normal=0.,barycentric_point=0.,radial_moment=0.,nodal_impulse=0.)
    accumulated={};count=0;added=0
    path=source/'coupled.csv.owned_rows.csv'
    for row in csv.DictReader(path.open()):
        q=np.fromstring(contacts[row['time']]['positions'],sep=' ').reshape(-1,3)
        support=np.fromstring(row['support'],sep=' ',dtype=int);J=np.fromstring(row['jacobian'],sep=' ').reshape(-1,3)
        normal=np.fromstring(row['normal'],sep=' ');point=np.fromstring(row['point'],sep=' ');lam=float(row['lambda_impulse'])
        if lam<0 or len(support)!=len(J) or not np.isfinite(J).all():raise ValueError('invalid owned row')
        distance=np.linalg.norm(point-center);errors['gap']=max(errors['gap'],abs(distance-radius-float(row['gap'])))
        errors['normal']=max(errors['normal'],float(np.linalg.norm(J.sum(axis=0)-normal)))
        weights=J@normal;errors['barycentric_point']=max(errors['barycentric_point'],float(np.linalg.norm(weights@q[support]-point)))
        errors['radial_moment']=max(errors['radial_moment'],float(np.linalg.norm(np.cross(q[support]-center,J).sum(axis=0))))
        if row['time'] not in accumulated:accumulated[row['time']]=np.zeros_like(q)
        np.add.at(accumulated[row['time']],support,lam*J);count+=1;added+=int(row['triangle'])>=0
    for time,row in momentum.items():
        actual=np.fromstring(row['contact_impulse'],sep=' ').reshape(-1,3)
        expected=accumulated.get(time,np.zeros_like(actual))
        errors['nodal_impulse']=max(errors['nodal_impulse'],float(np.linalg.norm(actual-expected)))
    passed=errors['gap']<1e-10 and errors['normal']<1e-10 and errors['barycentric_point']<1e-9 and errors['radial_moment']<1e-9 and errors['nodal_impulse']<1e-14
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    result=dict(status=('PASS' if passed else 'FAIL') if count else 'NOT RUN',scope='independent owned-row geometry and impulse pullback only;empty rows do NOT test contact;NOT whole-time convergence,area,pressure or reaction measurement',errors=errors,rows=count,added_triangle_row_records=added,
        source_commit=__import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),inputs={str(f.name):sha(f) for f in (path,source/'contact.csv',source/'momentum.csv',source/'scene.scn')},script_sha256=sha(__file__))
    write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
