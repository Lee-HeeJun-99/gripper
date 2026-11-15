"""Independent fixed-geometry return-map/interpolation diagnostic.

This proves a representation mechanism, not that it uniquely causes the full
SOFA error. It never changes an engine history state or adds compensating heat.
"""
import math
from birth_common import OUT,write_json
def main():
    length=.1;kt=1.;capacity=1.;omega=80.;rows=[]
    for h in (.01,.005,.0025,.00125):
        count=round(length/h);energy=0
        for i in range(count):
            a=omega*i*h;b=omega*(i+1)*h
            # Exact integral of half kt |linear nodal elastic field|^2.
            energy+=h*capacity**2*(2+math.cos(b-a))/(6*kt)
        exact=.5*capacity**2*length/kt
        rows.append(dict(history_spacing_mm=h,interpolated_field_energy=energy,exact_continuous_return_field_energy=exact,relative_energy_deficit=(exact-energy)/exact))
    # Return each endpoint (2,0),(0,2) then interpolate, versus interpolate the
    # trial first and return (1,1). Both are Coulomb admissible but differ.
    after=(.5,.5);before=(1/math.sqrt(2),1/math.sqrt(2))
    write_json(OUT/'history_representation_diagnostic.json',dict(status='PASS' if all(rows[i+1]['relative_energy_deficit']<rows[i]['relative_energy_deficit']for i in range(3))else'FAIL',scope='independent frozen planar field, NOT proof of full SOFA root cause or dynamic history convergence',physical_assumptions=dict(kt=kt,capacity=capacity,length_mm=length,rotation_rate_per_mm=omega),rows=rows,return_then_interpolate=after,interpolate_then_return=before,limitation='valid lower-energy interpolation is a representation error; not automatically friction heat; no compensating source added'))
    print(rows)
if __name__=='__main__':main()
