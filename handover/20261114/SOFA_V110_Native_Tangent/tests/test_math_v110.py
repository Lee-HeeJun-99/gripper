"""Independent numerical validation of linearized tangential shear law.
Does NOT compile or execute SOFA plugin.
"""
import numpy as np
h=.4;k=.1
b=np.array([-1.,-h/2,1.,-h/2]);K=k*np.outer(b,b)
def E(q):return .5*k*(b@q)**2
def F(q):return -k*b*(b@q)
rng=np.random.default_rng(11)
for i in range(100):
 q=rng.normal(scale=.001,size=4)
 fd=np.array([(E(q+1e-6*np.eye(4)[j])-E(q-1e-6*np.eye(4)[j]))/(2e-6) for j in range(4)])
 assert np.allclose(F(q),-fd,rtol=1e-8,atol=1e-13)
 for j in range(4):
  d=np.eye(4)[j]*1e-6
  assert np.allclose(F(q+d)-F(q-d),-2*K@d,rtol=1e-8,atol=1e-13)
assert np.linalg.eigvalsh(K).min()>-1e-12
print('PASS: conservative force, analytical 4x4 stiffness, PSD energy, 100 random checks')
