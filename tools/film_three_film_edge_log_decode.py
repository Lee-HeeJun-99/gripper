"""Lossless decoding ONLY of a diagnosed logging-escape bug;Raw immutable."""
import argparse,csv,io,json,shutil
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--case',required=True);a=p.parse_args();src=ROOT/'results'/('autonomous_film_'+a.case);meta=json.loads((src/'summary.json').read_text());raw=src/'transfer.continuation.csv'
 if meta['status']!='PASS' or sha(raw)!=meta['raw_hashes'][raw.name]:raise ValueError('completed immutable diagnostic payload required')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');text=raw.read_text();decoded=text.replace('\\n','\n').replace('\\"','"').replace('"23662','"\n');lines=decoded.splitlines();inverse=lines[0]+'\\n'+''.join(line.replace(',"',',\\"')+'23662' for line in lines[1:])
 if inverse!=text:raise ValueError('decoding not byte-reversible:do not repair numerical data')
 rows=list(csv.DictReader(io.StringIO(decoded)))
 if len(rows)!=meta['continuation_steps'] or any(len(np.fromstring(r[k],sep=' '))!=1953 or not np.isfinite(np.fromstring(r[k],sep=' ')).all() for r in rows for k in ('q','v')):raise ValueError('malformed decoded numerical payload')
 if any(float(r['minimum_gap'])< -1e-10 or float(r['momentum'])>1e-17 or float(r['normal_velocity'])>1e-10 for r in rows):raise ValueError('original physical gate failed')
 (out/'decoded.csv').write_text(decoded);result=dict(status='PASS',scope='read-only byte-reversible logging-format normalization of SAME independent numeric run;NOT new physics/SOFA',case=a.case,parent_summary_sha256=sha(src/'summary.json'),raw_sha256=sha(raw),decoded_sha256=sha(out/'decoded.csv'),rows=len(rows),inverse_byte_exact=True,numerical_values_changed=False,original_problem='literal escaped newline/opening quote and C++ multi-character newline marker23662;current driver fixed;future primitive build uses -Werror=multichar',qualification='original1057 states were not valid CSV;use this hash-bound decoded artifact for numeric comparisons,never overwrite raw');write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
