"""Actual Vec3-only regression for isolated mixed-state BE specialization."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
from film_rigid_reference import SDK
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--source',required=True);a=p.parse_args();source=ROOT/'results'/('autonomous_film_'+a.source);meta=json.loads((source/'identity.json').read_text());prior=json.loads((source/'summary.json').read_text())
    if not meta.get('c2_closing') or prior['status']!='EXPERIMENTAL':raise ValueError('completed cold C2 source required')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result={};data={};binary=None
    for name in ('original','mixed'):
        case=out/name;case.mkdir();tree=ET.parse(source/'40/scene.scn');scene=tree.getroot()
        for e in scene.iter():
            for k,v in list(e.attrib.items()):
                if str(source/'40') in v:e.set(k,v.replace(str(source/'40'),str(case)))
        for e in list(scene):
            if e.tag=='NativeFreeBodyProbe' or (e.tag=='Node' and e.get('name')=='free_object'):scene.remove(e)
        for plugin in scene.findall('RequiredPlugin'):
            path=ROOT.__class__(plugin.get('pluginName',''))
            if path.name=='libReGripRigidImpactReference.so':
                if sha(path)!=meta['binary_sha256']:raise ValueError('mixed binary drift')
                binary=path
        ode=scene.find('ReGripRigidBE')
        if name=='original':ode.tag='ReGripBDFSolver'
        tree.write(case/'scene.scn');proc=guarded([SDK/'bin/runSofa-26.06.00','--noautoload','--tmp','-g','batch','-a','-n','40','--hideProgressBar',case/'scene.scn'],case/'process',60);result[name]=proc
        if proc['exit_code']!=0:continue
        rows=list(csv.DictReader((case/'displacement.csv').open()));energies=list(csv.DictReader((case/'film.csv').open()))
        if len(rows)!=40 or len(energies)!=40:raise ValueError('incomplete regression')
        data[name]=(np.array([np.fromstring(r['u'],sep=' ') for r in rows]),np.array([[float(r[k]) for k in ('time','U_shell','U_attachment','K','T_per_rail','tendon_work')] for r in energies]))
    errors={};status='FAIL'
    if len(data)==2:
        for i,name in enumerate(('state','energy_control')):
            x,y=data['original'][i],data['mixed'][i];absolute=float(np.max(np.abs(x-y)));scale=float(np.max(np.abs(x)));errors[name]=dict(maximum_absolute_error=absolute,relative_error=absolute/scale if scale else None)
        status='PASS' if all(v['maximum_absolute_error']<=1e-12 for v in errors.values()) else 'FAIL'
    write_json(out/'summary.json',dict(status=status,scope='actual unconstrained Vec3 cold C2 BE equivalence;NOT rigid contact/time/grasp gate',source_identity=meta,binary=str(binary),processes=result,errors=errors,criterion='max absolute difference <=1e-12 in each exported array'))
    print(json.dumps(dict(status=status,errors=errors)))
if __name__=='__main__':main()
