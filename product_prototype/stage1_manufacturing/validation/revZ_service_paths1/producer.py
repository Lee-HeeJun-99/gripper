"""Exact STEP service cutsets and finite-part sampled extraction paths."""
import argparse,json,shutil,math
from incremental_stage1 import ROOT,read,bounds,overlap,common,sha
from build_stage1 import translate,compound
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case/'summary.json';idx=json.loads(src.read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 s={n:read(ROOT/v['path']) for n,v in idx['parts'].items() if not n.endswith('TENDON_WIRE')};bb={n:bounds(q) for n,q in s.items()};names=list(s)
 def starts(*p):return [n for n in names if n.startswith(tuple('F0_'+x for x in p))]
 coupling=starts('COUPLING');caps=starts('CAP_');nuts=starts('SHAFT_NUT','INNER_WASHER');right=starts('CAP_R','SHAFT_NUT_R','INNER_WASHER_R','BEARING_R','PEDESTAL_R')
 tipbody=starts('SWIVEL_LOWER','SWIVEL_UPPER','SWIVEL_BOLT','SWIVEL_NUT','TIP_FACTORY_NIPPLE')
 # Compression sleeve cannot pass through2.2mm fork eyes: withdraw it
 # WITH receiver/inner shims through the open fork, after removing axle.
 if idx['design_geometry'].get('receiver_preload_sleeve'):tipbody+=starts('SWIVEL_SLEEVE')+[n for n in starts('SWIVEL_SPACER') if n.endswith(('_L','_R'))]
 idler=starts('IDLER');rootfast=starts('ROOT_BOLT','ROOT_NUT');finger=starts('SKIN','RAIL','TERMINAL','SWIVEL','TIP_FACTORY_NIPPLE')
 specs=[]
 for label,d in [('L',-1),('R',1)]:
  specs.append((f'cap_{label}',starts('CAP_'+label)[:0]+[f'F0_CAP_{label}'],coupling+starts('CAP_'+label+'_BOLT'),(0,d,0),12))
  specs.append((f'bearing_{label}',[f'F0_BEARING_{label}'],coupling+caps+nuts,(0,d,0),14))
 specs += [('right_pedestal',[n for n in starts('PEDESTAL_R') if '_BOLT_' not in n and '_NUT_' not in n],right,(0,1,0),18),('drum_cup',['F0_DRUM_NIPPLE_CAP'],right+starts('DRUM_CAP_BOLT'),(0,1,0),14),('drum_nipple',['F0_DRUM_FACTORY_NIPPLE'],right+starts('DRUM_CAP_BOLT','DRUM_NIPPLE_CAP'),(0,1,0),12),('swivel_axle',['F0_SWIVEL_AXLE'],starts('SWIVEL_AXLE_NUT'),(0,-1,0),18),('swivel_receiver',tipbody,starts('SWIVEL_AXLE','SWIVEL_SPACER'),(0,0,1),20),('idler_module',[n for n in idler if not n.startswith(('F0_IDLER_BASE_BOLT','F0_IDLER_BASE_NUT'))],starts('IDLER_BASE_BOLT','IDLER_BASE_NUT'),(0,0,1),24),('root_front',['F0_ROOT_FRONT'],rootfast+idler,( -1,0,0),24),('finger_cartridge',finger,rootfast+idler+['F0_ROOT_FRONT'],(0,0,-1),32)]
 rows=[]
 for name,moving,cutset,d,L in specs:
  # Moving members belong to the extracted group, not obstacles. Every
  # other actual part remains present unless named in the service cutset.
  shape=compound([s[n] for n in moving]);hits=[]
  for mm in range(0,L+1,2):
   q=translate(shape,*(mm*v for v in d));b=bounds(q)
   for n,f in s.items():
    if n in moving or n in cutset or not overlap(b,bb[n]):continue
    vol=common(q,f)
    if vol>1e-7:hits.append(dict(travel_mm=mm,part=n,volume_mm3=vol))
  rows.append(dict(operation=name,moving=moving,removed_before_this_stage=cutset,direction=d,travel_mm=L,step_mm=2,hits=hits))
 result=dict(status='SAMPLED_SERVICE_PATH_PASS' if not any(r['hits'] for r in rows) else 'SAMPLED_SERVICE_PATH_FAIL',operations=rows,scope='Unpowered/rest/unloaded. De-tension then withdraw tip receiver toward idler (increases slack), open its split body and release finished tip. Flexible wire is NOT treated as a fixed REST rigid obstacle; manual peeling/unwinding from open rollers is not a simulated flexible service path. Actual rigid groups/nominal interfaces only, not insertion force/friction/continuous CCD. Reverse rigid sequences give nominal reassembly paths.',source_sha256=sha(src),stage1_release=False)
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(dict(status=result['status'],operations=len(rows),failed=[dict(operation=r['operation'],hits=r['hits'][:4]) for r in rows if r['hits']])))
if __name__=='__main__':main()
