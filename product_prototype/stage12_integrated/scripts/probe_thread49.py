"""Preserved actual first-pair occupancy diagnostic,not a release check."""
import json,sys,shutil
from baseline_registry import ROOT,REPO,ref,dump
from validate_thread49 import classification
from incremental_stage1 import read,common,translate
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated/primaryP1_thread49b_occupancy';out.mkdir();shutil.copyfile(__file__,out/'probe.py');cp=ROOT/'cad/exports/primaryP1_thread49b/summary.json';d=json.loads(cp.read_text());b=read(REPO/d['part_references']['BENCH_MOUNT_BOLT_0']['path']);n=read(REPO/d['part_references']['BENCH_MOUNT_NUT_0']['path'])
 rows=[dict(local_z_mm=z,bolt=classification(b,[-59+2.3,-58,54+z]),nut=classification(n,[-59+2.3,-58,54+z])) for z in [1.6+j*.02 for j in range(41)]]
 shifts=[dict(dz_mm=z,common_mm3=common(translate(b,0,0,z),n)) for z in [-.4,-.2,-.08,-.04,0,.04,.08,.2,.4]]
 dump(out/'summary.json',dict(status='ACTUAL_P1_THREAD_OCCUPANCY_DIAGNOSTIC_NOT_RELEASE',candidate=ref(cp),rows=rows,shifts=shifts));print(json.dumps(dict(rows=rows,shifts=shifts)))
if __name__=='__main__':main()
