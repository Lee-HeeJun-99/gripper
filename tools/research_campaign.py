"""Finite information-seeking campaign, four physics children maximum."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from research_common import OUT,write_json
from autonomous_trial import run
def main():
    plan=[('base',dict(history=.01,duration=24)),('h_half',dict(history=.005)),('h_quarter',dict(history=.0025)),('h_eighth',dict(history=.00125))]
    write_json(OUT/'history_plan.json',dict(cases=plan,profiles=dict(coarse_4s_wall=31.1597585179843,fine_4s_wall=49.55616708798334),prediction_fine_18s=223.00275189592503,wall_limit=480,memory_limit=4294967296,max_children=4,hypothesis='remove interpolation/return mismatch, compare actual committed material-point plastic'))
    results={}
    with ThreadPoolExecutor(4)as pool:
        futures={pool.submit(run,name,**kw):name for name,kw in plan}
        for f in as_completed(futures):
            name=futures[f]
            try:r=f.result();results[name]=dict(status=r['status'],process=r['process'])
            except Exception as e:results[name]=dict(status='FAIL',reason=repr(e))
            write_json(OUT/'history_completed.json',results)
    print(results)
if __name__=='__main__':main()
