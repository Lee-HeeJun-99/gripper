"""Assess saved campaigns without changing original result JSONs."""
import argparse,csv,json
from curve_common import ROOT,write_json
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=ROOT/'results'/('autonomous_film_assess_'+a.tag);out.mkdir(exist_ok=False)
 def summary(tag):return json.loads((ROOT/'results'/('autonomous_film_20261116_'+tag)/'summary.json').read_text())
 def row(tag,key='1'):return summary(tag)['rows'][key]
 narrow=row('narrow06','4');wide=row('wide06','4');mesh=[row('wide06','1'),row('wide21'),row('wide41')]
 meshchecks=[]
 for i,j in ((0,1),(1,2),(0,2)):
  metrics={k:abs(mesh[i][k]-mesh[j][k])/abs(mesh[j][k])for k in ('tip_z','contact_area','normal_force','U')}
  meshchecks.append(dict(nodes=[(11,21,41)[i],(11,21,41)[j]],metrics=metrics,status='PASS'if all(v<=.01 for v in metrics.values())else'FAIL'))
 comparison=dict(scope='Two homogeneous rectangular SINGLE-film ROM coupons,not old3finger baseline or skin+rail assembly. Same solid volume/assumedE/nu/tipF/plane;different width/thickness. Density/inertia not a calibrated material.',narrow=narrow,wide=wide,area_ratio=wide['contact_area']/narrow['contact_area'],mean_pressure_ratio=(wide['normal_force']/wide['contact_area'])/(narrow['normal_force']/narrow['contact_area']),hold_force=None,grasp_success=None)
 result=dict(comparison=comparison,spatial=meshchecks,spatial_status='PASS'if all(v['status']=='PASS'for v in meshchecks)else'FAIL',root_boundary='Two fixed rows:effective clamp changes with mesh;not same continuum boundary!',static_dt='NOT A DYNAMIC TIME GATE;old static summaries time_status is reinterpreted here as partition repeatability,not altered.',full_grasp='BLOCKED',optuna='BLOCKED')
 write_json(out/'summary.json',result);print(json.dumps(result))
if __name__=='__main__':main()
