"""Abort ONLY an owned Native child after nonfinite accepted-state observation."""
import csv,json,os,signal,threading
from pathlib import Path
import numpy as np
from native_bending_coupon import guarded

def finite_guard(command,directory,timeout=420,state_file=None):
 command=list(map(str,command));directory=Path(directory);state_file=Path(state_file) if state_file else directory.parent/'wheel.csv'
 if not state_file.resolve().is_relative_to(directory.parent.resolve()):raise ValueError('state monitor must belong to this trial')
 if not 0<timeout<=420:raise ValueError('leave finalization margin below outer480s')
 done=threading.Event();observation={};error={}
 def watch():
  while not done.wait(.05):
   if not state_file.is_file() or not(directory/'process.json').is_file():continue
   try:
    rows=list(csv.DictReader(state_file.open()))
    for row in rows:
     if row.get('rigid_q') and row.get('rigid_v') and not np.isfinite(np.fromstring(row['rigid_q']+' '+row['rigid_v'],sep=' ')).all():
      process=json.loads((directory/'process.json').read_text())
      if process['command']!=command:error['reason']='refuse_to_signal_unowned_command';return
      observation.update(reason='actual_nonfinite_accepted_state',first_time_s=float(row['time_s']))
      try:os.killpg(process['pid'],signal.SIGTERM)
      except ProcessLookupError:pass
      return
   except (OSError,json.JSONDecodeError):continue
 watcher=threading.Thread(target=watch,daemon=True);watcher.start()
 try:result=guarded(command,directory,timeout)
 finally:done.set();watcher.join()
 result=dict(result,nonfinite_observation=observation,finite_guard_error=error,internal_limit_s=timeout)
 # Preserve guarded's own result.json;this is a separate observation record.
 (directory/'finite_guard.json').write_text(json.dumps(dict(observation=observation,error=error,internal_limit_s=timeout,scope='Launchcontrolonly,noq/v/force/SDK/tolerancealteration'),indent=2))
 return result
