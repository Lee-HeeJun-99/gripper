"""Same-force first-order friction AD refinement, sequential180s children."""
from stabilization_grasp import run
from stabilization_common import OUT,write_json

def main():
    rows={}
    for name,nodes,samples,duration in [('sphere_fast_mesh21_full',21,32,12),('sphere_fast_mesh41_holdonly',41,16,8)]:
        rows[name]=run(name,nodes=nodes,samples=samples,duration=duration)
        write_json(OUT/'grasp/fast_fine_summary.json',dict(records=rows,max_workers=1,physics='unchanged; same-force regression verified before launch'))

if __name__=='__main__':main()
