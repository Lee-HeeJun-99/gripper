"""Additional bounded cold-start checks; unique output directories required."""
from concurrent.futures import ThreadPoolExecutor
from integrated_trial import Config
from stabilization_trials import run
from stabilization_common import OUT,write_json

def main():
    cases=[('free',Config(layers=8,k=0)),('k1',Config(layers=8,k=1)),('k10',Config(layers=8,k=10)),('repeat',Config(layers=8,k=100)),('quarterdt',Config(layers=8,k=100,dt=.000125))]
    with ThreadPoolExecutor(2) as pool:
        results=dict(zip([n for n,c in cases],pool.map(lambda item:run('compensated_followup/'+item[0],item[1],compensated=True),cases)))
    write_json(OUT/'compensated_followup/summary.json',results)

if __name__=='__main__':main()
