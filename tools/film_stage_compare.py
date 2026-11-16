"""Replay one short scene against preserved pre/post-fix binaries, exclusively."""
import csv,json
from curve_common import ROOT,sha,write_json
from closure_validation_suite import logged
from film_stage_assess import assess

def main():
    out=ROOT/'results/autonomous_film_20261116_stage_compare01';out.mkdir(exist_ok=False)
    sdk=ROOT/'build/grasp_20261115/sofa_patched'
    source=ROOT/'results/autonomous_film_20261116_stage02/1/scene.scn'
    results={}
    for name,tag in [('before','20261116_stage01'),('after','20261116_stage02')]:
        case=out/name;case.mkdir()
        scene=source.read_text().replace(str(source.parent/'journal.csv'),str(case/'journal.csv'))
        (case/'scene.scn').write_text(scene)
        binary=ROOT/'build'/('film_shell_'+tag)/'libReGripFilmShell.so'
        result=logged([sdk/'bin/graph_probe',sdk,case/'scene.scn','4','0',binary],case/'process',480)
        result.update(binary_sha256=sha(binary),scene_sha256=sha(case/'scene.scn'))
        trace=case/'journal.csv.stages.csv'
        if trace.exists():result['first_corrections']=assess(trace,1e-6,10,5)
        journal=case/'journal.csv'
        if journal.exists():
            rows=list(csv.DictReader(journal.open()));result['completed_steps']=len(rows)
            if rows:result['last_tip']=float(rows[-1]['tip_z'])
        results[name]=result
    write_json(out/'summary.json',results);print(json.dumps(results,indent=2))

if __name__=='__main__':main()
