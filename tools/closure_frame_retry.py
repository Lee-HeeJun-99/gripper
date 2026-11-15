"""One bounded high-resolution retry, original timed-out artifacts unchanged."""
from dataclasses import replace
from closure_frame_trial import Config,run
from closure_frame_common import OUT,write_json
def main():
    c=Config(nodes=41,samples=32,axis=5,load=5e-6,duration=18.)
    write_json(OUT/'retry_plan.json',dict(config=vars(c),reason='one independent initialized q32 retry; same physics/dt/480s cap, original timeout remains FAIL; no automatic retries',maximum_children=1))
    result=run('retry_n41q32',c,480);write_json(OUT/'retry_result.json',result)
if __name__=='__main__':main()
