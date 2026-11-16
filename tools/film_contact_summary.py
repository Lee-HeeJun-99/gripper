"""Evidence-backed checkpoint: scoped successes and retained physical failures."""
import argparse,csv,json,subprocess
import numpy as np
from curve_common import ROOT,sha,write_json
def main():
    p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--assembly-cases',nargs=3,default=['20261116_rail_low_coarse88','20261116_rail_low84','20261116_rail_low_fine89']);a=p.parse_args()
    if not a.tag.replace('_','').isalnum():raise ValueError('tag')
    out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);inputs={}
    def base(tag):return ROOT/'results'/('autonomous_film_'+tag)
    def read(tag):
        root=base(tag);summary=json.loads((root/'summary.json').read_text());inputs[str((root/'summary.json').relative_to(ROOT))]=sha(root/'summary.json');path=root/'1/journal.csv';inputs[str(path.relative_to(ROOT))]=sha(path)
        records=list(csv.DictReader(path.open()));return summary,records
    groups={'original':{11:'20261116_original_root11_65',21:'20261116_original_root21_66',41:'20261116_original_root41_67',81:'20261116_original_root81_68'},'cubic':{11:'20261116_cubic_root11_62',21:'20261116_cubic_root21_63',41:'20261116_cubic_root41_64'}}
    spatial={}
    for name,cases in groups.items():
        rows={}
        for nx,tag in cases.items():
            summary,records=read(tag)
            if summary.get('status',summary.get('process_status'))!='PASS':raise RuntimeError('incomplete spatial case')
            row=records[-1];rows[nx]={key:float(row[key]) for key in ('tip_z','U','contact_area','normal_force','free_force','max_speed')};rows[nx]['relative_static_force_residual']=float(row['free_force'])/(1e-6/np.sqrt(5))
        pairs={f'{i}:{j}':{key:dict(relative=abs(rows[i][key]-rows[j][key])/abs(rows[j][key]),status='PASS' if abs(rows[i][key]-rows[j][key])/abs(rows[j][key])<=.01 else 'FAIL') for key in ('tip_z','U','contact_area','normal_force')} for k,i in enumerate(cases) for j in list(cases)[k+1:]}
        spatial[name]=dict(endpoints=rows,pairs=pairs,scope='20s endpoint only,not full dynamic mesh or width qualification')
    names=a.assembly_cases;data={}
    for name in names:
        summary,records=read(name)
        if summary['status']!='PASS':raise RuntimeError('failed low-load control')
        data[name]={key:np.array([float(r[key]) for r in records]) for key in records[0] if key!='x'}
        data[name]['cable_displacement']=data[name]['cable_length']-200
    coupled={}
    for lo,hi in ((0,1),(1,2),(2,4),(0,4)):
        selected={name:{key:value[(d['time']>=lo-1e-12)&(d['time']<=hi+1e-12)] for key,value in d.items()} for name,d in data.items()};pairs={}
        for n,i in enumerate(names):
            for j in names[n+1:]:
                first,second=selected[i],selected[j];metrics={}
                for key in ('skin_tip_z','left_tip_z','right_tip_z','U_shell','U_attachment','K','tendon_work','cable_displacement'):
                    fine=np.interp(first['time'],second['time'],second[key]);absolute=float(max(abs(first[key]-fine)));scale=float(max(abs(fine)));relative=absolute/scale if scale else (0. if absolute==0 else None)
                    metrics[key]=dict(absolute=absolute,relative=relative,status='PASS' if relative is not None and relative<=.001 else 'FAIL')
                pairs[i+':'+j]=metrics
        coupled[f'{lo}:{hi}']=pairs
    recovery_summary,recovery=read('20261116_rail_recovery90');tip=np.array([float(r['skin_tip_z']) for r in recovery]);peak=float(max(abs(tip)));end=float(tip[-1]);recover=1-abs(end)/peak
    original=base('20261116_trapezoid_window3280_71')/'1/journal.csv';repeated=base('20261116_trapezoid_repeat77')/'1/journal.csv'
    repeat_exact=sha(original)==sha(repeated);inputs[str(original.relative_to(ROOT))]=sha(original);inputs[str(repeated.relative_to(ROOT))]=sha(repeated)
    result=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),tool_sha256=sha(__file__),inputs=inputs,spatial=spatial,assembly_time_comparisons=coupled,
        assembly_time_status='PASS' if all(v['status']=='PASS' for phase in coupled.values() for pair in phase.values() for v in pair.values()) else 'FAIL',
        low_load_recovery=dict(peak_tip_mm=peak,tip_at8s_mm=end,recovered_fraction=recover,velocity_at8s=float(recovery[-1]['max_speed']),scope='model low-load no-object elastic recovery,not a grasp release gate'),
        coupon_repeat_bitwise_equal=repeat_exact,nominal_tension_status='FAIL:original T=.001 trapezoid and BDF2 controls both fail;not overridden by lower T=.0001 success',
        global_energy='BLOCKED',single_finger_wrapping='NOT RUN',three_finger_grasp='NOT RUN',grasp_optimization='BLOCKED',physical_measurements=None)
    write_json(out/'summary.json',result);print(json.dumps(dict(assembly_time_status=result['assembly_time_status'],recovery=result['low_load_recovery'],repeat_exact=repeat_exact),indent=2))
if __name__=='__main__':main()
