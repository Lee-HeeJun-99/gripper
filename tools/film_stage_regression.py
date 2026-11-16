"""Short actual-SOFA no-load/no-contact and passive-trace purity regressions."""
import csv,json,xml.etree.ElementTree as ET
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged

def main():
    out=ROOT/'results/autonomous_film_20261116_stage_regression01';out.mkdir(exist_ok=False)
    sdk=ROOT/'build/grasp_20261115/sofa_patched'
    source=ROOT/'results/autonomous_film_20261116_exact_stage12/1/scene.scn'
    binary=ROOT/'build/film_shell_20261116_exact_stage12/libReGripFilmShell.so'
    results={};journals={}
    for name in ('trace_on','trace_off','unloaded','no_contact'):
        case=out/name;case.mkdir();tree=ET.fromstring(source.read_text());field=tree.find('FilmShell')
        field.set('filename',str(case/'journal.csv'));field.set('matrixProbe','1' if name=='trace_on' else '0')
        if name in ('unloaded','no_contact'):
            field.attrib.pop('plane',None);field.attrib.pop('contactStiffness',None)
        if name=='unloaded':
            field.set('observedTipForce','0');tree.find('LinearForceField').set('forces','0 0 0 0 0 0 0 0 0')
        ET.ElementTree(tree).write(case/'scene.scn',encoding='unicode')
        process=logged([sdk/'bin/graph_probe',sdk,case/'scene.scn','4','0',binary],case/'process',480)
        rows=list(csv.DictReader((case/'journal.csv').open())) if (case/'journal.csv').exists() else []
        journals[name]=rows
        log=(case/'process/stdout.log').read_text()+(case/'process/stderr.log').read_text()
        results[name]=dict(process=process,records=len(rows),scene_sha256=sha(case/'scene.scn'),
            status='PASS' if process['exit_code']==0 and len(rows)==4 and '[ERROR]' not in log and 'failed to converge' not in log else 'FAIL')
    results['query_purity']=dict(status='PASS' if journals['trace_on']==journals['trace_off'] else 'FAIL',definition='Every recorded CSV value identical with passive tracing enabled/disabled')
    results['unloaded_rest']=dict(status='PASS' if len(journals['unloaded'])==4 and all(float(r['U'])==float(r['max_speed'])==float(r['tip_z'])==0 for r in journals['unloaded']) else 'FAIL')
    write_json(out/'summary.json',dict(binary_sha256=sha(binary),results=results,full_grasp='NOT RUN'))
    print(json.dumps({k:v['status'] for k,v in results.items()}))

if __name__=='__main__':main()
