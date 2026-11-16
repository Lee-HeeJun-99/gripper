"""Draw actual recorded film states;explicit vertical magnification,not fake data."""
import argparse,csv,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.runtime/matplotlib_design'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from design_regrip import put,obj
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();folder=ROOT/'designs/visualizations'/a.tag;folder.mkdir(exist_ok=False)
 fig,axes=plt.subplots(1,2,figsize=(12,5))
 for n,name in enumerate(('narrow06','wide06')):
  raw=ROOT/'results'/('autonomous_film_20261116_'+name);row=list(csv.DictReader((raw/'4/journal.csv').open()))[-1];values=list(map(float,row['x'].split()));v=[values[i:i+3]for i in range(0,len(values),3)];ny=5;nx=len(v)//ny;faces=[]
  for i in range(nx-1):
   for j in range(ny-1):q=i*ny+j;faces.extend([(q,q+1,q+ny),(q+1,q+ny+1,q+ny)])
  put(folder/(name+'_actual.obj'),obj([(v,faces)]).replace('Concept / implemented mesh geometry ONLY;not SOFA deformed output','ACTUAL SOFA recorded state;fixed plane coupon,NOT free-object grasp'))
  polygons=[[[v[i][0],v[i][1]+50*v[i][2]]for i in f]for f in faces];colors=['#d8894a'if max(v[i][2]for i in f)>.1 else'#80b4c2'for f in faces]
  axes[n].add_collection(PolyCollection(polygons,facecolors=colors,edgecolors='#3d6574',linewidths=.35));axes[n].autoscale_view();axes[n].set_xlabel('x [mm]');axes[n].set_ylabel('y + 50*z [mm] (z exaggerated ×50)');axes[n].set_title(f'Actual SOFA {name}\nclipped reference contact area={float(row["contact_area"]):.3f} mm²');axes[n].grid(alpha=.2)
 fig.suptitle('Actual film deformation under fixed plane stop — NOT validated grasp');fig.tight_layout();fig.savefig(folder/'actual_coupon.png',dpi=160);plt.close(fig)
 (folder/'source.json').write_text(json.dumps(dict(source='actual CSV state,unmodified coordinates in OBJ;PNGz50magnification',raw=['results/autonomous_film_20261116_narrow06/4/journal.csv','results/autonomous_film_20261116_wide06/4/journal.csv']),indent=2))
 print(folder/'actual_coupon.png')
if __name__=='__main__':main()
