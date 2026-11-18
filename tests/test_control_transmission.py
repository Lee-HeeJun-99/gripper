"""Independent linear rail-skin-body model for delayed contact response.

Not ReGrip's nonlinear transfer time or actuator requirement.
"""
import json,math
import numpy as np
def main():
 mr,ms,mb,k=.002,.003,.1,.7
 inverse=np.diag(1/np.array([mr,ms,mb]));J=np.array([[0.,1.,-1.]])
 K=k*np.array([[1.,-1.,0.],[-1.,1.,0.],[0.,0.,0.]])
 tendon=np.array([-1.,0.,0.]);W=J@inverse@J.T
 direct=J@inverse@tendon
 projected=inverse@tendon-inverse@J.T@np.linalg.solve(W,direct)
 second=float(np.linalg.solve(W,J@inverse@K@projected)[0])
 exact_second=k*mb/(mr*(ms+mb))
 assert direct[0]==0 and abs(second-exact_second)<1e-12*exact_second
 omega=math.sqrt(k*(1/mr+1/(ms+mb)));errors=[]
 for t in (1e-3,5e-4,2.5e-4):
  # Analytic step response;stable1-cos formula,not large-energy subtraction.
  exact=2*math.sin(omega*t/2)**2/(mr*(1/mr+1/(ms+mb)))*mb/(ms+mb)
  local=.5*second*t*t
  errors.append(abs(local-exact)/exact)
 assert errors[1]<errors[0]/3.99 and errors[2]<errors[1]/3.99
 print(json.dumps(dict(status='PASS',scope='independent exact linear three-mass delayed-reaction reference;NOT nonlinear ReGrip',direct_gain=float(direct[0]),second_gain=second,relative_local_taylor_errors=errors)))
if __name__=='__main__':main()
