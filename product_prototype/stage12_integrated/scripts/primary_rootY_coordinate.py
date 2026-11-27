"""Original P1 physical RootY as one unpenalized coordinate, not a support.
Retains every equality row and every physical inequality; MotorY unchanged.
Gamma stationarity is -Root_free_Y multiplier=0, NOT prescribed gamma.
"""
import numpy as np
from scipy import sparse

def augment_rootY(P,q,A,lower,upper,gauge_labels,contact_rows=2169):
 labels=list(gauge_labels);ri=labels.index('Root_free_Y');mi=labels.index('Motor_free_Y');assert ri!=mi
 row=contact_rows+ri;assert lower[row]==upper[row]
 col=sparse.csc_matrix(([-1.],([row],[0])),shape=(A.shape[0],1))
 augmented=sparse.hstack([A,col],format='csc')
 metric=sparse.block_diag([P,sparse.csc_matrix((1,1))],format='csc')
 return metric,np.r_[q,0.],augmented,lower.copy(),upper.copy(),dict(original_RootY_row=row,original_MotorY_row=contact_rows+mi,gamma_column=A.shape[1],gamma_stationarity='-physical_RootY_gauge_dual_N=0',physical_fixation_added=False)
