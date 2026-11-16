"""Same-input low-load attachment transient; predeclared step refinement at1s."""
import argparse,csv,json,subprocess,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--fine',action='store_true');a=p.parse_args();out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);case=out/'1';case.mkdir();steps=4160 if a.fine else 2080;dt=.000625 if a.fine else .00125
 profile=ROOT/'results/autonomous_film_20261116_rail_low6400_100/summary.json';r=json.loads(profile.read_text());estimate=r['stages']['physics']['runtime_s']/r['rows']*steps*1.3
 if r['status']!='PASS' or estimate>480:raise RuntimeError('profile budget')
 source=ROOT/'results/autonomous_film_20261116_rail_low3200_99/1/scene.scn';tree=ET.parse(source);root=tree.getroot();root.set('dt',str(dt));root.remove(root.find('DefaultAnimationLoop'));clock=ROOT/'build/autonomous_20261116_event_clock_a01/v1/libReGripEventStepClock.so';root.insert(0,ET.Element('RequiredPlugin',pluginName=str(clock)));root.insert(1,ET.Element('EventStepClockAnimationLoop',eventTimes='0 1 1.2',stepDivisors='1 8 8',filename=str(case/'clock.csv')))
 ode=root.find('ReGripBDFSolver');ode.set('profileFilename',str(case/'profile.csv'));root.find("Node[@name='assembly']/FilmRailTendon").set('filename',str(case/'journal.csv'));tree.write(case/'scene.scn')
 plugin=ROOT/'build/film_rail_20261116_rail_native95/libReGripFilmRailTendon.so';core=ROOT/'build/film_shell_20261116_trapezoid_reference69/libReGripFilmShell.so';identity=json.loads((ROOT/'results/autonomous_film_20261116_rail_native95/identity.json').read_text())
 if sha(plugin)!=identity['binary_sha256'] or sha(core)!=identity['integration_binary_sha256']:raise RuntimeError('binary drift')
 write_json(out/'identity.json',dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_sha256=sha(source),tool_sha256=sha(__file__),binary_sha256=sha(plugin),integration_binary_sha256=sha(core),clock_sha256=sha(clock),scene_sha256=sha(case/'scene.scn'),profile_sha256=sha(profile),projected_seconds=estimate,steps=steps,pre_dt=dt,post_dt=dt/8,Tmax=.0001,scheme='Trapezoidal theta=.5',scope='same physical input,refine only numerical1s derivative-change interval;no contact,not full-cycle qualification'))
 sdk=ROOT/'build/grasp_20261115/sofa_patched';process=guarded([sdk/'bin/graph_probe',sdk,case/'scene.scn',str(steps),'0',plugin],case/'process',480);rows=list(csv.DictReader((case/'journal.csv').open())) if (case/'journal.csv').exists() else [];status='PASS' if process['exit_code']==0 and len(rows)==steps and abs(float(rows[-1]['time'])-1.2)<1e-10 else 'FAIL';write_json(out/'summary.json',dict(status=status,rows=len(rows),process=process,scope='execution only;1–1.2s attachment transient,not full-cycle time certificate'))
if __name__=='__main__':main()
