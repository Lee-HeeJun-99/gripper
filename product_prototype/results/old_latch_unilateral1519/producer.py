"""Distinguish exact zero-tension slack from accepted geometric length violation.
Never revises old strict1e-12 equality FAIL or functional results.
"""
import argparse,csv,json
from pathlib import Path
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--cases',nargs='+',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);records=[]
 for case in a.cases:
  src=BASE/'results'/case;rows=[];hashes={};dt=.0025
  for i in range(3):
   path=src/f'latch{i}.csv';hashes[path.name]=sha(path)
   for r in csv.DictReader(path.open()):
    if not int(r['latched']):continue
    for j in range(2):
     gap=float(r[f'geometric{j}_m'])-float(r[f'target{j}_m']);force=float(r[f'force{j}_Ns'])/dt;rows.append(dict(time_s=float(r['time_s']),finger=i,cable=j,shortening_minus_command_m=gap,force_N=force,exact_zero_tension=force==0.,tension_gap_product_J=force*gap))
  worst=max(rows,key=lambda r:abs(r['shortening_minus_command_m']));active=[r for r in rows if r['force_N']!=0];slack=[r for r in rows if r['force_N']==0];records.append(dict(case=case,samples=len(rows),worst_absolute_equality=worst,maximum_positive_shortening_gap_m=max(r['shortening_minus_command_m'] for r in rows),maximum_forbidden_longer_path_m=max(0.,max(-r['shortening_minus_command_m'] for r in rows)),maximum_nonzero_tension_equality_error_m=max(abs(r['shortening_minus_command_m']) for r in active) if active else None,maximum_exact_zero_tension_positive_gap_m=max(r['shortening_minus_command_m'] for r in slack) if slack else None,exact_zero_tension_samples=len(slack),negative_tension_samples=sum(r['force_N']<0 for r in rows),maximum_absolute_tension_gap_product_J=max(abs(r['tension_gap_product_J']) for r in rows),raw_hashes=hashes))
 d=dict(status='ACCEPTED_UNILATERAL_CABLE_CLASSIFICATION_ONLY',records=records,scope='minForce0 physicalcable canbe shorterthanfixedspoollength at EXACTzero tension. e=actualshortening−command;negativee means pathlongerthancommand. Nonzero tensionrequireszero gap. No arbitraryforcefloor;strict1e−12 equalityFAILs/oldfunctionalverdictsunchanged. This isacceptedstategeometry,not observedNative stagecomplementarity or a repaired solver.',source_sha256=sha(Path(__file__)));(out/'summary.json').write_text(json.dumps(d,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(d,indent=2))
if __name__=='__main__':main()
