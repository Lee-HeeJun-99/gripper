"""Independent frozen-tangent modal participation from an ACTUAL event state."""
import argparse,csv,json,shutil,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);p.add_argument('--event',type=int,default=1);a=p.parse_args()
    source=ROOT/'results'/('autonomous_film_'+a.case);scene=ET.parse(source/'scene.scn');events=list(csv.DictReader((source/'event.csv.event_states.csv').open()));event=next(r for r in events if int(r['event_id'])==a.event)
    before=list(map(float,event['pre_velocity'].split()));after=list(map(float,event['post_velocity'].split()));jump=[y-x for x,y in zip(before,after)]
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');archive=out/'sources';archive.mkdir()
    for directory in ('models/film_impact','models/film_native_contact','models/film_rail_tendon','models/film_shell','models/film_sphere_contact'):
        dest=archive/directory;dest.mkdir(parents=True)
        for f in (ROOT/directory).glob('*.h'):shutil.copy2(f,dest/f.name)
    cpp=archive/'diagnostics/film_impact/ImpactModes.cpp';cpp.parent.mkdir(parents=True);shutil.copy2(ROOT/'diagnostics/film_impact/ImpactModes.cpp',cpp)
    field=scene.find("Node[@name='assembly']/FilmRailTendon");mass=scene.find('.//DiagonalMass').get('vertexMass').split()
    values=[field.get('nx'),field.get('guideIntervals','4'),field.get('guideOffset'),field.get('bondStiffness'),str(int(field.get('rootGuideSecondOrder','0') in ('1','true'))),scene.getroot().get('dt'),event['event_time'],event['event_tension'],str(len(mass)),' '.join(mass),event['event_displacement'],' '.join(map(repr,jump))]
    (out/'input.txt').write_text('\n'.join(values)+'\n');binary=out/'probe'
    compile_result=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',binary],out/'compile',120)
    run=guarded([binary,out/'input.txt',out/'modes.csv'],out/'run',120) if compile_result['exit_code']==0 else None
    result=dict(status='PASS' if run and run['exit_code']==0 else 'FAIL',scope='independent frozen tangent modal diagnostic from actual SOFA event;NOT nonlinear dynamics/energy qualification',case=a.case,event=a.event,event_time=float(event['event_time']),compile=compile_result,run=run,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(archive)):sha(f) for f in archive.rglob('*') if f.is_file()},input_sha256=sha(out/'input.txt'),actual_event_state_sha256=sha(source/'event.csv.event_states.csv'),energy_note='0.5 deltaV^T M deltaV modal metric;NOT physical impact heat or kinetic-energy change')
    if binary.exists():result['binary_sha256']=sha(binary)
    if run and run['exit_code']==0:
        rows=list(csv.DictReader((out/'modes.csv').open()));total=sum(float(r['jump_metric_energy']) for r in rows)
        result.update(negative_modes=sum(float(r['eigenvalue'])<0 for r in rows),maximum_omega=max(float(r['omega']) for r in rows if r['omega']!='null'),jump_metric=total)
        result['participation_fractions']={str(limit):sum(float(r['jump_metric_energy']) for r in rows if r['omega_dt']!='null' and float(r['omega_dt'])>limit)/total for limit in (.1,1,3.141592653589793)}
    write_json(out/'summary.json',result);print(json.dumps({k:v for k,v in result.items() if k in ('status','maximum_omega','negative_modes','participation_fractions')}))
if __name__=='__main__':main()
