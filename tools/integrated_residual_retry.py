"""Strict residual re-execution/extension; no load or tolerance relaxation."""
from integrated_trial import Config,run
from integrated_common import OUT,write_json

def main():
    out=OUT/'strict_residual_retry';out.mkdir(parents=True,exist_ok=False);rows={}
    for name,c in [('small_tension_18s',Config(k=0,load=0,normal_k=.001,cable_tension=1e-6,duration=18)),
                   ('length_control_18s',Config(k=0,load=0,normal_k=.001,cable_k=.01,shortening=.0001,duration=18)),
                   ('wire_pressure_18s',Config(mode=1,k=1,pressure=1e-8,normal_k=.001,load=0,cable_tension=1e-5,duration=18))]:
        rows[name]=run(out/name,c);write_json(out/'summary.json',rows)

if __name__=='__main__':main()
