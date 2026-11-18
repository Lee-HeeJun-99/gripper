"""Read-only limited optimization decision;do NOT add unrelated speedups."""
import argparse,json,shutil
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();names=('20261118_precise_cache_serial1343','20261118_precise_cache_reverse1348');direct=ROOT/'results/autonomous_film_20261118_precise_cache_derivatives1345';d=json.loads((direct/'summary.json').read_text());build=ROOT/'results/autonomous_film_20261118_precise_cache_build1340';b=json.loads((build/'summary.json').read_text())
 if d['status']!='PASS' or d['force_H_gap_J_contact_H_max_abs']!=0 or not d['query_purity'] or d['cache_build_summary_sha256']!=sha(build/'summary.json') or sha(direct/'test')!=d['binary_sha256']:raise ValueError('direct force/H/geometry parity required')
 pairs=[];orders=set()
 for name in names:
  src=ROOT/'results'/('autonomous_film_'+name);m=json.loads((src/'summary.json').read_text())
  if m['status']!='PASS' or m['cache_build_summary_sha256']!=sha(build/'summary.json') or not all(m['physical_csv_byte_exact'].values()) or not all(m['original_known_actual_csv_byte_exact'].values()):raise ValueError('same-source completed exact actual benchmark required')
  for variant,hashes in m['raw_hashes'].items():
   for file,digest in hashes.items():
    if sha(src/variant/file)!=digest:raise ValueError('actual optimization raw changed')
  for row in m['checkpoints']:
   for variant in ('baseline','cached'):
    if sha(src/variant/row['name'])!=row[variant+'_sha256']:raise ValueError('physical checkpoint evidence changed')
  order=tuple(v['variant'] for v in m['variants']);orders.add(order);pairs.append(dict(case=name,summary_sha256=sha(src/'summary.json'),execution_order=order,baseline_runtime_s=m['baseline_runtime_s'],cached_runtime_s=m['cached_runtime_s'],observed_reduction_fraction=m['observed_runtime_reduction_fraction']))
 if orders!={('baseline','cached'),('cached','baseline')}:raise ValueError('two opposite serial orders required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');result=dict(status='PASS' if all(x['observed_reduction_fraction']>0 for x in pairs) else 'FAIL',scope='limited opt-in query-local arithmetic reuse on tested actual coupon ONLY;NOT a universal engine speed factor',cache_build_summary_sha256=sha(build/'summary.json'),direct_derivative_summary_sha256=sha(direct/'summary.json'),binary_sha256=b['binary_sha256'],force_H_gap_J_contact_H_exact=True,physical_CSV_byte_exact=True,pairs=pairs,adoption='separate OPT-IN research owner;qualified Edge/Release modules NOT automatically replaced',baseline_already_has_journal_row_reuse=True,combined_speedup=None,whole_cycle_speedup=None,legacy_sampled_work='byte parity does NOT restore/certify its private origin',physics_force_tolerance_or_precision_changed=False);write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
