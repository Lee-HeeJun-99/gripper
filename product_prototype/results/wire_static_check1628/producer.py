"""Check frozen QP stationarity without pretending tiny positive f are active contacts."""
import argparse,json
from pathlib import Path
import numpy as np
from analyse import BASE,sha
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);src=BASE/'results/wire_constraint_residual1621';data=np.load(src/'native_problem.npz');W=data['W'];d=data['dFree'];diag=np.diag(W);assert np.all(diag>0);records=[]
 for label,f in [('Native',data['f']),('SLSQP_reference',data['reference_f'])]:
  w=W@f+d;error=float(abs(np.minimum(diag*f,w)).max());records.append(dict(model=label,maximum_diagonal_scaled_NCP_residual=error,maximum_negative_w=float(max(0,-w.min())),maximum_complementarity_product=float(abs(w*f).max()),strict_1e12_component_check=error<=1e-12))
 result=dict(status='FROZEN_STATIC_REFERENCE_STATIONARITY_INVENTORY_ONLY',records=records,scope='min(diagW*f,w) vanishes iff nonnegative complementarity withpositiveWdiagonal. Noactivefthreshold/artificialerrorfloor. SLSQPsuccess/objective isNOTKKTorphysicalPASS. Allcomputedonexisting1621data,noNative/optimizerrerun; no correctedmultipliersinstalled.',source_sha256=sha(Path(__file__)),input_sha256=sha(src/'native_problem.npz'));(out/'summary.json').write_text(json.dumps(result,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
if __name__=='__main__':main()
