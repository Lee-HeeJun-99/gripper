"""Audit only what the in-engine contact-owner journal actually observes."""
import csv,math,json
from collections import Counter
from birth_common import OUT,write_json
def audit(path):
    rows=list(csv.DictReader(path.open()));counts=Counter((r['step'],r['stage'])for r in rows)
    unknown=('unknown_pressure_work','unknown_stiffness_damping','unknown_total_closure')
    known=[k for k in rows[0] if k not in unknown+('stage',)]
    finite=all(math.isfinite(float(r[k])) for r in rows for k in known)
    missing_stay_unknown=all(r[k]=='null' for r in rows for k in unknown)
    pre=[r for r in rows if r['stage']=='pre_commit'];post=[r for r in rows if r['stage']=='post_commit']
    one_commit=len(pre)==len(post) and all(counts[(r['step'],'pre_commit')]==counts[(r['step'],'post_commit')]==1 for r in pre)
    split_error=max(abs(float(r['contact_U'])-float(r['contact_normal_U'])-float(r['contact_tangent_U']))for r in rows)
    plastic=[float(r['contact_plastic_D'])for r in post];loss=[float(r['detachment_loss'])for r in post]
    nonnegative=all(v>=-1e-25 for v in plastic+loss)
    monotone=all(b>=a-1e-25 for a,b in zip(plastic,plastic[1:])) and all(b>=a-1e-25 for a,b in zip(loss,loss[1:]))
    return dict(partial_journal_status='PASS' if finite and missing_stay_unknown and one_commit and nonnegative and monotone and split_error<1e-16 else 'FAIL',global_energy_status='BLOCKED',rows=len(rows),steps=len(pre),finite_known_columns=finite,unknown_columns_preserved=missing_stay_unknown,one_pre_post_per_commit=one_commit,nonnegative_loss=nonnegative,monotone_loss=monotone,maximum_contact_energy_split_error=split_error,final_plastic_D=plastic[-1] if plastic else None,final_detachment_loss=loss[-1] if loss else None,reason='No global transaction or complete pressure/Rayleigh stiffness/external work accounting; force method queries are not necessarily solver stages')
def main():
    result={}
    for path in sorted((OUT/'grasp').glob('*/energy_journal.csv')):
        if not(path.parent/'metrics.json').exists():continue
        try:result[path.parent.name]=audit(path)
        except (ValueError,KeyError,IndexError)as e:result[path.parent.name]=dict(partial_journal_status='FAIL',reason=str(e))
    controlled={}
    for path in sorted((OUT/'events').glob('*/journal.csv')):
        m=path.parent/'metrics.json'
        if not m.exists()or json.loads(m.read_text()).get('expected_rejection'):continue
        rows=list(csv.DictReader(path.open()));begin=[r for r in rows if r['stage']=='begin'];post=[r for r in rows if r['stage']=='post_commit']
        if not begin or not post:continue
        first,last=begin[0],post[-1]
        def total(r):return sum(float(r[k])for k in('beam_U','layer_U','contact_U','kinetic_K'))
        defect=total(last)-total(first)+float(last['contact_plastic_D'])-float(first['contact_plastic_D'])+float(last['detachment_loss'])-float(first['detachment_loss'])
        controlled[path.parent.name]=dict(status='EXPERIMENTAL',steps=len(post),initial_K_plus_U=total(first),final_K_plus_U=total(last),observed_energy_defect=defect,scope='actual controlled plane unit: only contact, mass, fixed zero-velocity object; gravity/external load/actuator/damping absent, fixed constraint work zero. Defect is OBSERVED, not defined to be numerical dissipation; dt1 is not baseline dt.')
    write_json(OUT/'controlled_event_energy.json',controlled)
    write_json(OUT/'energy_audit.json',result);print(json.dumps(result,indent=2));print('controlled event energies',controlled)
if __name__=='__main__':main()
