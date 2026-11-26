"""Independent local static state certification; never changes solver records.

Certificates are NOT global minima, execution PASS or whole Finger validation.
"""
import argparse,json,math,shutil
from baseline_registry import ROOT,REPO,ref,dump,sha

def key(row):return row['n'],round(row.get('angle_deg',row.get('fixture_angle_deg')),8)
def main():
    p=argparse.ArgumentParser();p.add_argument('--comparison',required=True);p.add_argument('--forces',nargs='+',required=True);p.add_argument('--geometry',nargs='+',required=True);p.add_argument('--tag',required=True);a=p.parse_args()
    source=ROOT/'validation/finger'/a.comparison/'summary.json';d=json.loads(source.read_text());out=ROOT/'validation/finger'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    origins={};certificates=[];force={};geometry={}
    for item in d['inputs']:
        path=REPO/item['result']['path']
        if sha(path)!=item['result']['SHA256']:raise ValueError('Stale original result')
        original=json.loads(path.read_text())
        if original['candidate']!=d['candidate']:raise ValueError('Candidate mismatch')
        for row in original['rows']:origins[key(row)]=item['result']
    for tags,kind,target in ((a.forces,'force',force),(a.geometry,'geometry',geometry)):
        for tag in tags:
            path=ROOT/'validation/finger'/tag/'summary.json';doc=json.loads(path.read_text());certificates.append(ref(path))
            if doc['status']!='PASS' or doc.get('product_release') is not False:raise ValueError('Not a bounded passing certificate')
            if kind=='geometry' and doc['tolerance_common_mm3']!=1e-8:raise ValueError('Geometry threshold changed')
            for row in doc['rows']:
                k=key(row)
                if k in target or row['status']!='PASS' or doc['source']!=origins.get(k):raise ValueError('Duplicate, failed or wrong-source certificate')
                if kind=='force':
                    values=[row['force_equivalent_N'],row['complementarity_relative']]
                    if not all(math.isfinite(x) for x in values) or row['maximum_N']!=1e-8 or row['complementarity_maximum']!=1e-7 or values[0]>=1e-8 or values[1]>=1e-7 or row['state_changed'] is not False:raise ValueError('Invalid force certificate')
                target[k]=ref(path)
    rows=[]
    for original in d['rows']:
        k=key(original)
        if k not in force or k not in geometry:raise ValueError('Missing independent state certificate')
        if not math.isfinite(original['axial_migration_m']) or original['continuous_min_gap_m'] < -1e-9:raise ValueError('Invalid/gap-violating state')
        rows.append(dict(original,status='PASS',original_optimizer_status=original['status'],independent_state_basis='LOCAL FRICTIONLESS KKT / ACTUAL ENVELOPE ONLY; NOT EXECUTION PASS',force_certificate=force[k],geometry_certificate=geometry[k],state_changed=False))
    if not rows:raise ValueError('Empty state certificate')
    by_angle={}
    for row in rows:by_angle.setdefault(round(row['fixture_angle_deg'],8),[]).append(row)
    refinements=[]
    for angle,group in by_angle.items():
        ordered=sorted(group,key=lambda r:r['n']);fine=ordered[-1]
        for coarse in ordered[:-1]:
            error=abs(coarse['axial_migration_m']-fine['axial_migration_m'])/max(abs(fine['axial_migration_m']),1e-12)
            refinements.append(dict(angle_deg=angle,coarse_n=coarse['n'],fine_n=fine['n'],migration_relative=error,maximum=.01,status='PASS' if error<.01 else 'FAIL'))
    result=dict(status='BOUNDED_LOCAL_STATES_CERTIFIED',scope='INDEPENDENT SAVED-STATE CERTIFICATES; ORIGINAL OPTIMIZER FAILS UNCHANGED',rows=rows,all_meshes_to_finest=refinements,all_meshes_converged=bool(refinements) and all(r['status']=='PASS' for r in refinements),source=ref(source),candidate=d['candidate'],PET_free_length_m=d['PET_free_length_m'],certificates=certificates,producer=ref(out/'producer.py'),whole_system_release=False,limitations=['KKT is local, not proof of unique/global stable equilibrium','Rigid prescribed rail, inextensible PET, zero friction, typical modulus','No actual flexible-Rail/friction/shell or Stage1/Stage2 system release'])
    dump(out/'summary.json',result);print(json.dumps(dict(status=result['status'],all_meshes_to_finest=refinements,all_meshes_converged=result['all_meshes_converged']),indent=2))
if __name__=='__main__':main()
