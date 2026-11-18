"""Public dt changes must not imply time resets or differing observation clocks."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from film_transmission_plan_run import make_plan
for duration in (.0002,.0008,.0016,.05):
 plans=[make_plan(duration,r) for r in (1,2,4)]
 assert plans[0][1]==plans[1][1]==plans[2][1]
 for ends,epochs in plans:
  assert ends[-1]==duration and all(e in ends for e in epochs)
  previous=0.
  for end in ends:
   h=end-previous
   assert h>0 and previous+h==end
   previous=end
assert [len(make_plan(.05,r)[0]) for r in (1,2,4)]==[278,556,1112]
assert len(make_plan(.0002,1)[0])==8
assert [len(make_plan(.05,r,1,True)[0]) for r in (1,2,4)]==[294,588,1176]
for startup in (1,2,4,8):
 for graded in (False,True):
  plans=[make_plan(.0032,r,startup,graded) for r in (1,2,4)]
  assert plans[0][1]==plans[1][1]==plans[2][1]
print('PASS explicit plan counts,exact accumulated epochs and representable next-dt updates;NOT physics/time certificate')
