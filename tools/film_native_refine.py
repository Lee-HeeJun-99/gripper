"""Bounded same-binary time refinement of a COMPLETED native contact trial.

Only dt and output locations change. This does not restore a partial checkpoint,
alter the physical control law, rebuild a kernel,or approve convergence.
"""
import argparse,csv,json,math,shutil,subprocess,xml.etree.ElementTree as ET
from pathlib import Path
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded

def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args()
    if not a.tag.replace('_','').isalnum() or not a.case.replace('_','').isalnum():raise ValueError('campaign name')
    source=ROOT/'results'/('autonomous_film_'+a.case);reference=json.loads((source/'summary.json').read_text())
    if reference.get('status')!='PASS' or not reference.get('finite'):raise ValueError('complete finite source required')
    command=json.loads((source/'1/process/command.json').read_text());previous_steps=int(command[command.index('-n')+1]);steps=2*previous_steps
    estimate=reference['stages']['physics']['runtime_s']*2*1.5
    if steps>1600 or estimate>480:raise ValueError('measured refinement projection exceeds bounded1600-step/480s policy')
    identity=json.loads((source/'identity.json').read_text());tree=ET.parse(source/'1/scene.scn');root=tree.getroot()
    if identity.get('accepted_integrator')!='BE' or root.find('FilmNativeCoupledCorrection') is None:raise ValueError('qualified coupled BE source only')
    expected={}
    for name,component in (('core','ReGripFilmShell'),('assembly','ReGripFilmRailTendon'),('observer','ReGripFilmNativeObserver')):
        matches=[Path(n.get('pluginName')) for n in root.findall('RequiredPlugin') if n.get('pluginName','').endswith('/lib'+component+'.so')]
        if len(matches)!=1 or sha(matches[0])!=identity[name+'_sha256']:raise RuntimeError('immutable binary identity drift:'+name)
        expected[str(matches[0])]=sha(matches[0])
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);case=out/'1';case.mkdir();shutil.copytree(source/'sources',out/'sources')
    for node in root.iter():
        for key,value in list(node.attrib.items()):node.set(key,value.replace(str(source/'1'),str(case)))
    root.set('dt',str(float(root.get('dt'))/2));tree.write(case/'scene.scn')
    # Verify the only physical/numerical scene change is dt. Output addresses
    # are normalized back before byte comparison of the parsed XML tree.
    check=ET.parse(case/'scene.scn')
    for node in check.getroot().iter():
        for key,value in list(node.attrib.items()):node.set(key,value.replace(str(case),str(source/'1')))
    check.getroot().set('dt',ET.parse(source/'1/scene.scn').getroot().get('dt'))
    if ET.tostring(check.getroot())!=ET.tostring(ET.parse(source/'1/scene.scn').getroot()):raise RuntimeError('unexpected scene change')
    command[command.index('-n')+1]=str(steps);command[-1]=str(case/'scene.scn')
    identity.update(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=__import__('sys').argv,
        scene_sha256=sha(case/'scene.scn'),reuse_binary_source_case=a.case,reuse_identity_sha256=sha(source/'identity.json'),
        same_binary_time_refinement=2,compiled_source_note='Copied immutable source archive;NO new compilation',
        refinement_script_sha256=sha(__file__),coupled_budget=dict(projected_seconds=estimate,profile=a.case,margin=1.5,hard_seconds=480))
    write_json(out/'identity.json',identity)
    if any(sha(Path(path))!=value for path,value in expected.items()):raise RuntimeError('prelaunch binary drift')
    process=guarded(command,case/'process',480)
    rows=list(csv.DictReader((case/'journal.csv').open())) if (case/'journal.csv').exists() else []
    finite=bool(rows) and all(math.isfinite(float(value)) for row in rows for key,value in row.items() if key!='x') and all(math.isfinite(float(value)) for row in rows for value in row['x'].split())
    log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
    ok=process['exit_code']==0 and len(rows)==steps and finite and not any(s in log for s in ('[ERROR]','Unused Attribute','Newton-Raphson method failed to converge'))
    result=dict(status='PASS' if ok else 'FAIL',scope='same-binary execution only;time convergence NOT approved',finite=finite,stages=dict(physics=process),rows=len(rows),last={k:v for k,v in rows[-1].items() if k!='x'} if rows else None)
    write_json(out/'summary.json',result);print(json.dumps({k:result[k] for k in ('status','finite','rows')}))

if __name__=='__main__':main()
