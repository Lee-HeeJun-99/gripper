"""Preserved actual first-pair occupancy diagnostic,not a release check."""
import json,sys,shutil
from baseline_registry import ROOT,REPO,ref,dump
from validate_thread49 import classification
from incremental_stage1 import read,common,translate
def main():
 assert not(ROOT/'runtime/STOP').exists();out=ROOT/'validation/integrated/primaryP1_thread49c_boolean';out.mkdir();shutil.copyfile(__file__,out/'probe.py');cp=ROOT/'cad/exports/primaryP1_thread49c/summary.json';d=json.loads(cp.read_text());b=read(REPO/d['part_references']['BENCH_MOUNT_BOLT_0']['path']);n=read(REPO/d['part_references']['BENCH_MOUNT_NUT_0']['path'])
 from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
 from incremental_stage1 import box,volume,solid_count
 from OCP.BRepCheck import BRepCheck_Analyzer
 import io
 extras=[]
 for label,a,c in [('pair',b,n),('boltinprobe',b,box(-56.71,-58.01,55.99,.02,.02,.02)),('nutinprobe',n,box(-56.71,-58.01,55.99,.02,.02,.02))]:
  op=BRepAlgoAPI_Common(a,c);buf=io.BytesIO();op.DumpErrors(buf);extras.append(dict(label=label,done=op.IsDone(),errors=op.HasErrors(),error_text=buf.getvalue().decode(),volume_mm3=volume(op.Shape()),solids=solid_count(op.Shape()),valid=bool(BRepCheck_Analyzer(op.Shape()).IsValid())))
 rows=[dict(local_z_mm=z,bolt=classification(b,[-59+2.3,-58,54+z]),nut=classification(n,[-59+2.3,-58,54+z])) for z in [1.6+j*.02 for j in range(41)]]
 shifts=[dict(dz_mm=z,common_mm3=common(translate(b,0,0,z),n)) for z in [-.4,-.2,-.08,-.04,0,.04,.08,.2,.4]]
 dump(out/'summary.json',dict(status='ACTUAL_P1_THREAD_OCCUPANCY_DIAGNOSTIC_NOT_RELEASE',candidate=ref(cp),rows=rows,shifts=shifts,boolean=extras));print(json.dumps(dict(rows=rows,shifts=shifts,boolean=extras)))
if __name__=='__main__':main()
