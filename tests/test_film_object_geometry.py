import math,sys,unittest
from collections import Counter
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from film_object_geometry import cylinder_y
class CylinderGeometry(unittest.TestCase):
 def test_closed_oriented_faceted_volume(self):
  import numpy as np
  for n in (32,64,128):
   center=np.array([75.,12.,-8.2]);points,faces=cylinder_y(center,8,40,n);q=np.array(points)-center;directed=Counter();volume=0
   for a,b,c in faces:
    for i,j in ((a,b),(b,c),(c,a)):directed[i,j]+=1
    normal=np.cross(q[b]-q[a],q[c]-q[a]);self.assertGreater(np.linalg.norm(normal),0)
    volume+=np.dot(q[a],np.cross(q[b],q[c]))/6
   for (a,b),count in directed.items():self.assertEqual(count,1);self.assertEqual(directed[b,a],1)
   expected=n/2*8**2*math.sin(2*math.pi/n)*40
   self.assertLess(abs(volume-expected)/expected,1e-14)
   self.assertLess(np.max(abs(np.linalg.norm(q[:2*n,[0,2]],axis=1)-8)),1e-13)
if __name__=='__main__':unittest.main()
