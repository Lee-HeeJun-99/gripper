"""Evaluate response AND unsmoothed stress without hiding clamp-edge growth."""
import argparse,json,shutil
import numpy as np
from baseline_registry import ROOT,REPO,ref,dump,sha
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args()
    out=ROOT/'validation/convergence'/a.tag;out.mkdir(parents=True,exist_ok=False);shutil.copyfile(__file__,out/'producer.py')
    inputs=[];rows=[]
    for tag in ('AI_tab_h3b','AI_tab_h2','AI_tab_h1p5'):
        src=ROOT/'validation/transmission'/tag/'summary.json';d=json.loads(src.read_text());inputs.append(ref(src));assert d['status']=='LOCAL_UNIT_LOAD_PASS'
        field=REPO/d['field']['path'];assert sha(field)==d['field']['SHA256'];f=np.load(field)
        k=int(np.argmax(f['vm_Pa']));centroid=f['points_m'][f['tetra'][k]].mean(axis=0)
        rows.append(dict(h_mm=d['h_mm'],compliance_m_N=d['compliance_m_N'],energy_J=d['energy_J'],peak_vm_Pa=d['peak_unsmoothed_vm_Pa'],peak_element_centroid_m=centroid.tolist(),distance_from_clamped_cut_mm=float(abs(centroid[0]-.105)*1000),source=d['source'],STEP=d['STEP'],material=d['material']))
    assert all(r['source']==rows[0]['source'] and r['STEP']==rows[0]['STEP'] and r['material']==rows[0]['material'] for r in rows)
    coarse,fine=rows[-2:];response=abs(coarse['compliance_m_N']/fine['compliance_m_N']-1);stress=abs(coarse['peak_vm_Pa']/fine['peak_vm_Pa']-1)
    result=dict(status='LOCAL_STRESS_CONVERGENCE_FAIL' if stress>=.01 else 'LOCAL_CONVERGENCE_PASS',scope='Actual local tab, same geometry/material and finite load; not whole-Palm strength',rows=rows,inputs=inputs,producer=ref(out/'producer.py'),criterion_relative_max=.01,response_relative=response,response_converged=response<.01,unsmoothed_peak_stress_relative=stress,stress_converged=stress<.01,
        interpretation='Response convergence does NOT certify stress/strength. Peak location relative to artificial clamped cut is reported, not deleted. Whole-Palm support/contact analysis is the physical followup, not a blind finer-mesh sweep.',
        assembly_note='Finest level uses the same P2 law/degree2 quadrature summed in8000-element blocks, a memory strategy already used by Stage2 shaft FEM.',whole_system_release=False)
    dump(out/'summary.json',result);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
