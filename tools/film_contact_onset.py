"""Read-only first-impact diagnosis using actual nodal impulses, not candidate count.

The mass-only stopping impulse is a comparison scale, NOT the solution of the
elastic coupled problem. Frozen-plane chord time is NOT continuous collision
detection. Existing pointwise-force/time FAIL gates are not modified here.
"""
import argparse
import csv
import json
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT, sha, write_json


def inspect(tag):
    path=ROOT/'results'/('autonomous_film_'+tag)
    summary=json.loads((path/'summary.json').read_text())
    if summary.get('status')!='PASS' or not summary.get('finite'):
        raise RuntimeError('complete finite physical run required')
    source=path/'1'
    tree=ET.parse(source/'scene.scn')
    observer=tree.find('FilmNativeObserver')
    if observer.get('objectShape','sphere')!='sphere':
        raise RuntimeError('analytic plane-target reconstruction is sphere-only')
    center=np.fromstring(tree.find("Node[@name='fixed']/MechanicalObject").get('position'),sep=' ')
    radius=float(observer.get('radius'))+.01 # scene contactDistance must match
    if float(tree.find('MinProximityIntersection').get('contactDistance'))!=.01:
        raise RuntimeError('contact distance not derived')
    rows=list(csv.DictReader((source/'contact_rows.csv').open()))
    contacts=list(csv.DictReader((source/'contact.csv').open()))
    velocities=list(csv.DictReader((source/'momentum.csv').open()))
    if len(contacts)!=summary['rows'] or len(contacts)!=len(velocities):
        raise RuntimeError('incomplete journals')
    groups={}
    for row in rows:groups.setdefault(float(row['time']),[]).append(row)
    first=next((i for i,c in enumerate(contacts) if groups.get(float(c['time']))),None)
    if first is None:return dict(case=tag,status='NO_LOAD',inertial_stopping_impulse=None)
    contact=contacts[first];velocity=velocities[first];time=float(contact['time'])
    active=groups[time]
    if len(active)!=1:
        return dict(case=tag,status='NOT MEASURED',reason='multiple active rows;do not infer individual Jacobians from total impulse',time=time)
    row=active[0];lam=float(row['lambda_impulse']);force=np.array([float(row[k]) for k in ('force_x','force_y','force_z')]);normal=force/np.linalg.norm(force)
    impulse=np.fromstring(velocity['contact_impulse'],sep=' ').reshape(-1,3)
    weights=impulse@normal/lam
    if np.min(weights)<-1e-12 or abs(weights.sum()-1)>1e-10 or np.linalg.norm(impulse-lam*weights[:,None]*normal)>1e-18:
        raise RuntimeError('single-direction nodal Jacobian reconstruction failed')
    points={k:weights@np.fromstring(contact[k],sep=' ').reshape(-1,3) for k in ('begin_positions','free_positions','positions')}
    gaps={k:float(normal@(point-center)-radius) for k,point in points.items()}
    speeds={k:float(normal@(weights@np.fromstring(velocity[k],sep=' ').reshape(-1,3))) for k in ('v_begin','v_free','v_accepted')}
    h=float(contact['dt']);alpha=None
    if gaps['begin_positions']>=0 and gaps['free_positions']<0:
        alpha=gaps['begin_positions']/(gaps['begin_positions']-gaps['free_positions'])
    mass=np.fromstring(tree.find("Node[@name='assembly']/DiagonalMass").get('vertexMass'),sep=' ')
    # A contact on a constrained/mapped root cannot use a diagonal mass formula.
    nx=int(tree.find("Node[@name='assembly']/FilmRailTendon").get('nx'))
    root=np.zeros(len(mass),dtype=bool)
    for start,width in ((0,5),(5*nx,3),(8*nx,3)):root[start:start+3*width]=True
    effective_mass=None if np.any(abs(weights[root])>1e-14) else 1/float(np.sum(weights*weights/mass))
    return dict(case=tag,status='EXPERIMENTAL',time=time,dt=h,normal=normal.tolist(),gaps_mm=gaps,
                normal_speeds_mm_s=speeds,frozen_plane_chord_fraction=alpha,
                physical_ccd_time=None,actual_impulse=lam,actual_step_mean_force=lam/h,
                diagonal_mass_effective_mass=effective_mass,
                inertial_stopping_impulse=None if effective_mass is None else effective_mass*max(-speeds['v_begin'],0),
                interpretation='mass-only scale excludes elasticity/damping/ongoing tendon force;not a predicted physical impulse',
                inputs={name:sha(source/name) for name in ('scene.scn','contact_rows.csv','contact.csv','momentum.csv')})


def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args()
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False)
    results=[inspect(tag) for tag in a.cases]
    write_json(out/'summary.json',dict(status='EXPERIMENTAL',results=results,script_sha256=sha(__file__),
        time_gate='UNCHANGED: this diagnostic does not approve convergence',friction='NOT RUN'))
    print(json.dumps(results))


if __name__=='__main__':main()
