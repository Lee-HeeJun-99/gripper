"""New-state modal error projection;reuses,does not rerun old campaigns."""
import argparse,csv,json,shutil,xml.etree.ElementTree as ET
import numpy as np
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
from film_guarded_process import guarded
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs=2,required=True);p.add_argument('--time',type=float,required=True);a=p.parse_args()
    roots=[ROOT/'results'/('autonomous_film_'+name) for name in a.cases];snapshots=[];fields=[];inputs={}
    for directory in roots:
        summary=json.loads((directory/'summary.json').read_text())
        if summary.get('status')!='PASS' or not summary.get('finite'):raise ValueError('complete finite trajectories only')
        rows=list(csv.DictReader((directory/'1/journal.csv').open()));row=min(rows,key=lambda r:abs(float(r['time'])-a.time))
        if abs(float(row['time'])-a.time)>1e-10:raise ValueError('physical time must exactly coincide;no row-index or interpolation substitution')
        snapshots.append(row);tree=ET.parse(directory/'1/scene.scn');fields.append(tree.find("Node[@name='assembly']/FilmRailTendon"));inputs[str(directory.relative_to(ROOT))]={name:sha(directory/'1'/name) for name in ('journal.csv','scene.scn')}
    # Same XML control and same physical time are mandatory. Printed endpoint
    # tensions can differ by a few ULPs because accumulated time differs.
    if fields[0].attrib!={k:v.replace(str(roots[1]/'1'),str(roots[0]/'1')) for k,v in fields[1].attrib.items()} or not np.isclose(float(snapshots[0]['T_per_rail']),float(snapshots[1]['T_per_rail']),rtol=32*np.finfo(float).eps,atol=0):raise ValueError('different assembly/control inputs')
    for relative in ('film_rail_tendon/Kernel.h','film_shell/Kernel.h','film_shell/AD.h','film_shell/PlaneContact.h','film_native_contact/CoupledPlaneStep.h'):
        for root in roots:
            if sha(ROOT/'models'/relative)!=sha(root/'sources'/relative):raise ValueError('compiled modal kernel mismatch:'+relative)
    field=fields[1]
    if field.get('rootGuideSecondOrder','0') not in ('0','false'):raise ValueError('root guide variant not qualified')
    tree=ET.parse(roots[1]/'1/scene.scn');mass=tree.find("Node[@name='assembly']/DiagonalMass").get('vertexMass');q=[np.fromstring(s['x'],sep=' ') for s in snapshots]
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);state=out/'state.txt'
    with state.open('x') as stream:
        stream.write(' '.join([field.get('nx'),field.get('guideIntervals','4'),field.get('guideOffset'),field.get('bondStiffness'),snapshots[1]['T_per_rail']])+'\n'+mass+'\n'+snapshots[1]['x']+'\n'+' '.join(format(v,'.17g') for v in q[0]-q[1])+'\n')
    source=ROOT/'diagnostics/film_rail_tendon/CurrentModes.cpp';shutil.copyfile(source,out/'CurrentModes.cpp');stages={};stages['compile']=logged(['g++','-std=c++17','-O2','-ffp-contract=off','-I/usr/include/eigen3',source,'-o',out/'modes'],out/'compile',180)
    if stages['compile']['exit_code']:raise RuntimeError('modal compile failed')
    stages['reference']=guarded([out/'modes',state],out/'reference',60)
    if stages['reference']['exit_code']:raise RuntimeError('modal reference failed')
    records=[{k:float(v) for k,v in r.items()} for r in csv.DictReader((out/'reference/stdout.log').open())];ranked=sorted(records,key=lambda r:abs(r['quadratic_error_projection']),reverse=True)
    result=dict(status='EXPERIMENTAL',scope='independent instantaneous FULL stored/generator tangent incl tendon;NOT modal dynamics or energy certification',time=a.time,cases=a.cases,negative_eigenvalues=sum(r['eigenvalue']<0 for r in records),dominant_error_modes=ranked[:12],inputs=inputs,source_sha256=sha(source),binary_sha256=sha(out/'modes'),stages=stages,coordinate_note='world snapshots minus rest;NOT near-rest force reconstruction',contact_tangent_included=False)
    write_json(out/'summary.json',result);print(json.dumps(dict(negative_eigenvalues=result['negative_eigenvalues'],dominant_error_modes=ranked[:4])))
if __name__=='__main__':main()
