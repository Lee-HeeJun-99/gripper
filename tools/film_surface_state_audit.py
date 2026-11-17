"""Audit actual ForceField/owner state and row inventories, not global energy."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
def rows(path):return list(csv.DictReader(path.open()))
def vector(text):return list(map(float,text.split()))
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args()
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');results={};hashes={}
    for name in a.cases:
        path=ROOT/'results'/('autonomous_film_'+name);summary=json.loads((path/'summary.json').read_text());identity=json.loads((path/'identity.json').read_text())
        if summary['status']!='PASS' or not identity.get('owner_ode'):raise ValueError('completed sole ODE input required')
        accepted=rows(path/'event.csv.states.csv');field=rows(path/'displacement.csv');events=rows(path/'event.csv.surface.csv');constraints=rows(path/'event.csv.constraints.csv')
        exact=len(accepted)==len(field) and all(float(s['time'])==float(f['time']) and vector(s['local_displacement'])==vector(f['u']) for s,f in zip(accepted,field))
        inventory={};seen=set();row_status=True
        for r in constraints:
            owner=(r['time'],r['step_owner'],r['row_owner']);row_status &= owner not in seen;seen.add(owner)
            stage=int(r['stage']);key=(float(r['time']),stage);inventory[key]=inventory.get(key,0)+float(r['impulse'])
            row_status &= float(r['impulse'])>=0 and stage in (1,2)
            row_status &= abs(sum(float(r[k]) for k in ('b0','b1','b2'))-1)<=1e-12
            row_status &= abs(sum(float(r[k])**2 for k in ('nx','ny','nz'))-1)<=1e-12
            if stage==2:row_status &= float(r['normal_after'])>=-1e-10
        max_inventory_error=0
        for s in accepted:
            for stage,key in ((1,'constraint_impulse'),(2,'projection_impulse')):
                maximum=abs(inventory.get((float(s['time']),stage),0)-float(s[key]));max_inventory_error=max(max_inventory_error,maximum)
                # Summation of rows follows the same order as the C++ sum;
                # retain any measured rounding difference separately.
                row_status &= maximum<=1e-20
        impact_status=all(float(r['impulse'])>=0 and float(r['post_normal'])>=-1e-10 and float(r['impact_loss'])>=0 for r in events)
        results[name]=dict(status='PASS' if exact and row_status and impact_status else 'FAIL',forcefield_displacement_exact=exact,owned_rows=len(constraints),unique_row_ids=len(seen),maximum_impulse_inventory_error=max_inventory_error,impact_rows=len(events),impact_conditions=impact_status,scope='recording/state ownership gates only;NOT energy or time qualification')
        for file in ('identity.json','summary.json','event.csv.states.csv','event.csv.surface.csv','event.csv.constraints.csv','displacement.csv'):hashes[str((path/file).relative_to(ROOT))]=sha(path/file)
    write_json(out/'summary.json',dict(status='PASS' if all(r['status']=='PASS' for r in results.values()) else 'FAIL',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),scope='limited actual state/row audit;NOT full physics/grasp',cases=results,source_hashes=hashes))
    print(json.dumps(results))
if __name__=='__main__':main()
