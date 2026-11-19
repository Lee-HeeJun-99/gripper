"""No physics-Gate floors:input-law and actual response-group layout regressions."""
import csv,unittest
import numpy as np
from analyse import BASE
from native_response_blocks import friction_blocks
def read(path):
 with path.open() as stream:return list(csv.DictReader(stream))
class NativeInertiaTest(unittest.TestCase):
 def test_stock_trapezoidal_held_input_no_change(self):
  # Installed scheme changed,but B=K=0 held-input system is unchanged here.
  for variant in (0,1):
   for i in (0,1):
    a=read(BASE/f'results/b3_inertia_input_100ms613/{variant}/guide{i}.csv');b=read(BASE/f'results/b3_inertia_input_trap618/{variant}/guide{i}.csv');self.assertEqual(len(a),40);self.assertEqual(len(b),40)
    for x,y in zip(a,b):
     for key in ('rigid_q','rigid_v','object_impulse_Ns_Nms'):np.testing.assert_array_equal(np.fromstring(x[key],sep=' '),np.fromstring(y[key],sep=' '))
 def test_all_contacts_in_response_group(self):
  rows=read(BASE/'results/b3_inertia_input_contact600/0/response0.csv');actual=[r for r in rows if float(r['time_s'])==.0075];self.assertEqual(friction_blocks(rows,.0075,{int(r['row_id']) for r in actual}),[0,3,6,9,12])
 def test_nonzero_group_origin(self):
  rows=[dict(time_s='1',constraint_path='/a',first_row='2',row_id=str(i)) for i in range(2,8)];self.assertEqual(friction_blocks(rows,1,set(range(2,8))),[2,5])
 def test_incomplete_group_rejected(self):
  rows=[dict(time_s='1',constraint_path='/a',first_row='0',row_id='0')]
  with self.assertRaises(ValueError):friction_blocks(rows,1,{0})
 def test_unowned_row_rejected(self):
  with self.assertRaises(ValueError):friction_blocks([],1,{0,1,2})
 def test_sampled_input_law_and_power(self):
  for case in ('b3_inertia_input_free593','b3_inertia_input_contact600','b3_inertia_input_contact_half601','b3_inertia_input_contact_quarter602'):
   for i in (0,1):
    for r in read(BASE/f'results/{case}/0/inertia_input{i}.csv'):
     w=np.fromstring(r['omega_world_rad_s'],sep=' ');L=np.fromstring(r['angular_momentum_Nms'],sep=' ');tau=np.fromstring(r['applied_torque_Nm'],sep=' ');expected=-np.cross(w,L);self.assertLessEqual(np.linalg.norm(tau-expected),32*np.finfo(float).eps*np.linalg.norm(w)*np.linalg.norm(L))
     # Cross-product subtraction can cancel. Its roundoff scales with |w||L|,
     # NOT with the much smaller RESULT |tau|;then dot with w adds |w|.
     self.assertLessEqual(abs(tau@w),64*np.finfo(float).eps*np.linalg.norm(w)**2*np.linalg.norm(L))
 def test_offline_velocity_derivative(self):
  # Functional-law derivative only;actual ConstantForceField tangent is ZERO
  # during each held input step. No implicit Jacobian claim.
  def skew(w):return np.array([[0,-w[2],w[1]],[w[2],0,-w[0]],[-w[1],w[0],0]])
  I=np.diag([1.3e-11,.98e-11,.98e-11]);w=np.array([7.,-12.,-10.]);J=skew(I@w)-skew(w)@I;h=1e-4;fd=np.column_stack([(-np.cross(w+np.eye(3)[k]*h,I@(w+np.eye(3)[k]*h))+np.cross(w-np.eye(3)[k]*h,I@(w-np.eye(3)[k]*h)))/(2*h) for k in range(3)]);self.assertLess(np.linalg.norm(fd-J)/np.linalg.norm(J),1e-8)
if __name__=='__main__':unittest.main()
