"""ONE quantitatively justified900s case, no physical tolerance/time-step changes."""
import json,math
from beam_common import OUT,write_json
from beam_grasp_trial import run
def main():
    profile=json.loads((OUT/'v2_profile/profile/summary.json').read_text());steps=profile['steps'][0]
    if profile['status']!='PASS' or steps['steps']!=8000:raise RuntimeError('measured profile missing')
    prediction=steps['wall']/8000*36000
    if prediction>750:raise RuntimeError('case does not fit bounded900s budget')
    write_json(OUT/'high_resolution_resource_plan.json',dict(measured_8000_steps_s=steps['wall'],predicted_36000_steps_s=prediction,wall_cap_s=900,default480_exception='user permits longer compute only with measured cause/resource basis;41-node240element rod and same SparseLU/contact math cost, no unbounded retry',maximum_trials=1,memory_cap_bytes=4*1024**3,physics_unchanged=dict(dt=.0005,duration=18,nodes=41,samples=32,history=.01,load=5e-6),no_physical_tolerance_relaxation=True))
    result=run('Tz_n41q32_profiled',nodes=41,samples=32,duration=18.,wall=900);write_json(OUT/'high_resolution_result.json',result)
if __name__=='__main__':main()
