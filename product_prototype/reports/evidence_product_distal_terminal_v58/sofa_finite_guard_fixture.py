"""SOFTWARE TEST CHILD ONLY. Outputs are NOT simulated/measured physical states."""
import argparse,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--nonfinite',action='store_true');a=p.parse_args()
a.output.write_text('time_s,rigid_q,rigid_v\n0.001,"'+('nan' if a.nonfinite else '0')+' 0 0 0 0 0 1","0 0 0 0 0 0"\n')
if a.nonfinite:time.sleep(60)
