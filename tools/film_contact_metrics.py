"""Geometry diagnostics only; discrete row locations do not measure contact area."""
import math

def circular_span_radians(angles):
    ordered=sorted(float(value)%math.tau for value in angles)
    if not ordered:return None
    if not all(math.isfinite(value) for value in ordered):raise ValueError('finite angular positions required')
    gaps=[b-a for a,b in zip(ordered,ordered[1:])]+[ordered[0]+math.tau-ordered[-1]]
    return math.tau-max(gaps)
