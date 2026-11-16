"""Accepted versus begin-stage net moment for the EXACT frictionless sphere law.

Radial normal traction has zero moment about a sphere center. A frozen plane
surrogate need not have this property at its accepted geometry. This is NOT
a measurement of fixed reactions or whole-system angular balance.
"""
import argparse
import csv
import json
import xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args()
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);cases={}
    for case in a.cases:
        source=ROOT/'results'/('autonomous_film_'+case)/'1';summary=json.loads((source.parent/'summary.json').read_text())
        if summary.get('status')!='PASS' or not summary.get('finite'):raise RuntimeError('complete finite execution required')
        tree=ET.parse(source/'scene.scn');observer=tree.find('FilmNativeObserver')
        if observer.get('objectShape','sphere')!='sphere':raise RuntimeError('zero normal-traction torque is sphere-only;not a faceted cylinder identity')
        center=np.fromstring(tree.find("Node[@name='fixed']/MechanicalObject").get('position'),sep=' ');radius=float(observer.get('radius'));records=[]
        for row in csv.DictReader((source/'contact.csv').open()):
            if int(row['unmatched_jacobian_rows']):raise RuntimeError('incomplete force reconstruction')
            scalar_force=float(np.sum(np.fromstring(row['lambda_impulse'],sep=' ')))/float(row['dt'])
            if scalar_force==0:continue
            F=np.fromstring(row['body_force'],sep=' ');sample=dict(time=float(row['time']),scalar_normal_force=scalar_force)
            for stage in ('begin','free','accepted'):
                torque=np.fromstring(row['body_moment_'+stage],sep=' ')-np.cross(center,F)
                sample[stage+'_absolute_moment']=float(np.linalg.norm(torque))
                sample[stage+'_relative_radial_law_defect']=float(np.linalg.norm(torque)/(radius*scalar_force))
            records.append(sample)
        maximum=max((r['accepted_relative_radial_law_defect'] for r in records),default=None)
        cases[case]=dict(status='NOT RUN' if maximum is None else 'PASS' if maximum<=.001 else 'FAIL',
            scope='net moment diagnostic against exact sphere radial law;NOT global angular balance',
            maximum_accepted_relative_defect=maximum,
            maximum_begin_relative_defect=max((r['begin_relative_radial_law_defect'] for r in records),default=None),
            maximum_accepted_absolute_moment=max((r['accepted_absolute_moment'] for r in records),default=None),
            records=records,inputs={name:sha(source/name) for name in ('contact.csv','scene.scn')},fixed_reaction=None)
    write_json(out/'summary.json',dict(status='EXPERIMENTAL',diagnostic_relative_threshold=.001,
        exact_law='sphere frictionless normal traction is radial;torque about sphere center vanishes',
        no_load_relative_error=None,script_sha256=sha(__file__),cases=cases))
    print(json.dumps({name:{k:v for k,v in value.items() if k.startswith('maximum') or k=='status'} for name,value in cases.items()}))

if __name__=='__main__':main()
