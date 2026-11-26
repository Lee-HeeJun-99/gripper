"""Conservative fastener exterior witnesses, NEVER manufacturing parts.
Stock length plus declared seat displacement; no operating CAD is overwritten.
"""
import argparse,json,math,shutil
import numpy as np
from incremental_stage1 import ROOT,read,bounds,overlap,common,sha,canonical,export
from build_stage1 import cyl,fuse,rotate,volume,solid_count
from OCP.BRepCheck import BRepCheck_Analyzer
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--joints',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());jp=ROOT/'validation'/a.joints/'summary.json';j=json.loads(jp.read_text());assert j['case']==a.case and j['input_sha256']==sha(src);out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 actual={n:read(ROOT/v['path']) for n,v in idx['parts'].items()};modified=dict(actual);manifest={};rules=[];std={4:.24,6:.24,8:.29,10:.29,12:.35,14:.35,16:.35,18:.35,20:.42,50:.50}
 for row in j['rows']:
  n=row['screw']
  if n not in actual or 'SWIVEL_BOLT_' in n:continue
  base=actual[n];u=np.array(row['shank_axis']);bb=bounds(base);c=np.array([(bb[k]+bb[k+3])/2 for k in range(3)]);r=row['nominal_shank_D_mm']/2;segments=row.get('evaluated_material_intervals_mm',[row['actual_shank_interval_mm']]);span=[min(t[0] for t in segments),max(t[1] for t in segments)]
  if 'PLUG' in n:
   # Set-screw working end stays against pin; increased length extends OUT.
   direction=np.array([-1.,0,0]) if n.endswith('_L') else np.array([1.,0,0]);tip=bb[0] if n.endswith('_L') else bb[3];c[0]=tip;extra=.24;extension=cyl(r,tuple(c-.02*direction),extra+.02,tuple(direction));new=fuse(base,extension);basis='ISO4026M2x4 drawing length acceptance+-0.24; working end fixed, outer end growth; not a claimed DIN912 tolerance for set screw'
  else:
   side=row['head_side'];assert side in (-1,1),n;direction=-side*u;tip=span[0] if side==1 else span[1];c+=u*(tip-np.dot(c,u))
   if 'AXLE' in n:extra=.05;basis='Custom drawing end-position acceptance+-0.05, NOT stock screw'
   elif n.startswith(('F0_TERMINAL_FLUSH_BOLT','F0_CAP_L_BOLT')):extra=.60;basis='CSK drawing length acceptance0.30 + permitted recess0.20 + seat datum0.10; not catalogue claim'
   else:extra=std[round(row['actual_shank_interval_mm'][1]-row['actual_shank_interval_mm'][0])]+.10;basis='DIN912 manufacturer maximum length + declared seat-datum0.10; other bodies nominal'
   new=fuse(base,cyl(r,tuple(c-.02*direction),extra+.02,tuple(direction)))
  new=canonical(new);assert BRepCheck_Analyzer(new).IsValid() and solid_count(new)==1,n;assert volume(new)>volume(base),n
  rules.append(dict(part=n,extra_tip_or_outer_end_mm=extra,direction=direction.tolist(),basis=basis))
  for i in range(3):
   name=n.replace('F0_',f'F{i}_',1);s=rotate(new,120*i);export(s,out/name);f=out/(name+'.step');manifest[name]=dict(path=str(f.relative_to(ROOT)),sha256=sha(f),STL_sha256=sha(f.with_suffix('.stl')),actual_manufacturing_part_SHA256=idx['parts'][name]['sha256']);modified[name]=s
 bs={n:bounds(s) for n,s in modified.items()};names=list(modified);hits=[];changed=set(manifest)
 for i,n in enumerate(names):
  for m in names[i+1:]:
   if not ({n,m}&changed) or not overlap(bs[n],bs[m]):continue
   v=common(modified[n],modified[m])
   if v>1e-7:hits.append(dict(a=n,b=m,volume_mm3=v))
 result=dict(status='STOCK_MAX_EXTERIOR_ENVELOPES_CLEAR' if not hits else 'STOCK_MAX_EXTERIOR_ENVELOPES_FAIL',case=a.case,case_SHA256=sha(src),variants=manifest,rules=rules,static_hits=hits,manufacturing_parts=False,scope='Finite conservative fastener exterior witnesses only; original operating CAD untouched. Matched swivel screws use separate retainer envelope. Other component dimensions nominal; NOT all-combined tolerances, helical threads, strength or actual purchased stock. Never use these as manufacturing/BOM parts.',stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],variants=len(manifest),static_hits=hits[:8])))
if __name__=='__main__':main()
