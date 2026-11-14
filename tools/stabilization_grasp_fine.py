"""Bounded hold-only refinement after full fine-grid release trial times out.

Identical controls/history through t=8. Release phase explicitly NOT RUN here.
Run sequentially to avoid contention; do not increase the180s child limit.
"""
from stabilization_grasp import run
from stabilization_common import OUT,write_json

def main():
    rows={}
    for name,nodes,samples in [('sphere_mesh21_q32_holdonly',21,32),('sphere_mesh41_q16_holdonly',41,16)]:
        rows[name]=run(name,nodes=nodes,samples=samples,duration=8)
        write_json(OUT/'grasp/fine_summary.json',dict(records=rows,release_phase='NOT RUN',max_workers=1))

if __name__=='__main__':main()
