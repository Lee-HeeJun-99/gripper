"""Bounded actual SOFA temporal energy diagnostic on a controlled plane unit."""
from birth_finish import wait_for
from birth_events import case
from birth_common import OUT,write_json
def main():
    wait_for(4,600)
    rows={}
    for steps in(2,4,8,16,32,64,128):
        rows[str(steps)]=case('birth_dt_'+str(steps),1.03,-.02,.02,steps=steps,dt=1./steps)
    write_json(OUT/'events_refined_summary.json',rows)
if __name__=='__main__':main()
