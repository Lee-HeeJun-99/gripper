"""New cap and nut-tool service checks, exact retained STEP obstacles."""
import argparse,json,shutil
from incremental_stage1 import ROOT,read,overlap,bounds,common,sha,hex_y
from build_stage1 import box,cyl,cut,fuse,translate,export
def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--tag',required=True);a=p.parse_args();src=ROOT/'cad/exports'/a.case
 d=json.loads((src/'summary.json').read_text());out=ROOT/'validation'/a.tag;out.mkdir(exist_ok=False)
 s={n:read(ROOT/v['path']) for n,v in d['parts'].items()};b={n:bounds(x) for n,x in s.items()}
 cutset=[n for n in s if n.startswith('F0_COUPLING') or n.startswith('F0_CAP_L_BOLT') or n.startswith('F0_CAP_R_BOLT')]
 rows=[]
 for label,sign in [('L',-1),('R',1)]:
  name='F0_CAP_'+label
  for mm in range(13):
   cap=translate(s[name],0,sign*mm,0);bb=bounds(cap)
   for n,q in s.items():
    if n==name or n in cutset or not overlap(bb,b[n]):continue
    v=common(cap,q)
    if v>1e-7:rows.append(dict(moving=name,travel_mm=mm,obstacle=n,volume_mm3=v))
 # Actual machined thin8AF spanner, not an assumed infinite access ray.
 tools=[]
 for label,y in [('L',-5.6),('R',20.1)]:
  tool=fuse(cyl(7,(80,y,20),1.5,(0,1,0)),box(77,y,25,6,1.5,50))
  tool=cut(tool,hex_y(8,y-.1,1.7),box(80,y-.1,16,10,1.7,8))
  export(tool,out/('THIN_8AF_SPANNER_'+label));hits=[];bb=bounds(tool)
  for n,q in s.items():
   if n=='F0_SHAFT_NUT_'+label or n in cutset or not overlap(bb,b[n]):continue
   v=common(tool,q)
   if v>1e-7:hits.append(dict(part=n,volume_mm3=v))
  tools.append(dict(side=label,hits=hits,part='custom1.5mm steel thin8AF spanner, not certified torque tool'))
 result=dict(status='CAP_AND_NUT_SERVICE_GEOMETRY_PASS' if not rows and not any(t['hits'] for t in tools) else 'SERVICE_GEOMETRY_FAIL',cap_slide_collision_samples=rows,cap_service_cutset=cutset,cap_straight_samples=13,travel_mm=12,tool_checks=tools,continuous_CCD=False,thread_engagement_mm=dict(cap_screws=3,coupler_screws=3.85,shaft_nuts=2.7),assembly_order=['drum on central shaft; insert pin and both threaded retaining plugs','offer empty pedestals from each journal end; bolt pedestals to Palm','insert bearings from OUTSIDE onto journal/seat; never pass OD16 through ID13 shoulder','install inner washers/thin nuts/locking compound; verify bearing fit and selected endplay','install outside caps and their screws; service left cap with coupling removed','install two coupling jaws and their four screws LAST'],scope='Nominal solid service paths and explicit assembly construction; no insertion force, preload, wrench strength or hardware execution')
 (out/'summary.json').write_text(json.dumps(result,indent=2));shutil.copyfile(__file__,out/'producer.py');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
