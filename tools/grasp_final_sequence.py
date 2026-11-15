"""Same6 directions,24s: only post-release observation is extended (load6..14)."""
from concurrent.futures import ThreadPoolExecutor,as_completed
from dataclasses import replace
from grasp_common import OUT,write_json
from grasp_trial import Config,run

def main():
    c=replace(Config(),duration=24,rayleigh_mass=2.);rows={}
    write_json(OUT/'release_criteria.json',dict(declared_before_runs=True,contact_open='final contact count=0',finger_speed_mm_s=1e-5,finger_angular_speed_rad_s=1e-5,finger_translation_from_rest_mm=1e-4,finger_rotation_from_rest_rad=1e-5,rationale='research recovery resolution:1ppm of100mm; same existing equilibrium speed thresholds, no object-position reset or initial-pose requirement',hold_conditions='same dt/material/mu/tension/pressure/load6..14 and damping for all6; only observation after wireOFF16 extends from18 to24s'))
    with ThreadPoolExecutor(2) as pool:
        tasks={pool.submit(run,'final_sphere_'+axis+sign,replace(c,axis=i,load=s*1e-6)):axis+sign for i,axis in enumerate('xyz') for sign,s in [('plus',1),('minus',-1)]}
        for task in as_completed(tasks):
            name=tasks[task]
            try:rows[name]=task.result()
            except Exception as e:rows[name]=dict(status='FAIL',failure_reason=repr(e))
            write_json(OUT/'final_sequence.json',rows)

if __name__=='__main__':main()
