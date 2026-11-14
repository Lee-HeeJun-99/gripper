"""Actual finite-rotation connector scenes, separate from uncoupled elastica tests."""
from integrated_trial import Config,run
from integrated_common import OUT,write_json

def main():
    out=OUT/'objective_connector';out.mkdir(parents=True,exist_ok=False);rows={}
    I=8*.4**3/12
    for name,c in [('small',Config(mode=2,k=100)),
                   ('moderate',Config(mode=2,k=1,load=0,moment=2*250*I*.1/100,duration=30,dt=.001)),
                   ('moderate_halfdt',Config(mode=2,k=1,load=0,moment=2*250*I*.1/100,duration=30,dt=.0005))]:
        rows[name]=run(out/name,c);write_json(out/'summary.json',rows)
        print(name,rows[name]['status'],rows[name].get('tip_deflection_mm'),rows[name].get('relative_residual'),flush=True)

if __name__=='__main__':main()
