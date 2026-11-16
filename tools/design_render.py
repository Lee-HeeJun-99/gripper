"""Scientific rendering of the generated geometry;not fabricated SOFA states."""
import argparse,json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(__file__).resolve().parents[1]/'.runtime/matplotlib_design'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from design_regrip import ROOT
def main():
 p=argparse.ArgumentParser();p.add_argument('--version',required=True);a=p.parse_args();out=ROOT/'designs/visualizations'/a.version/'assembly.png'
 if out.exists():raise ValueError('refuse old drawing')
 fig=plt.figure(figsize=(15,6));baseline=json.loads((ROOT/'designs/baseline'/a.version/'geometry.json').read_text())
 for i,name in enumerate(('baseline','film_contact','selective_jamming')):
  ax=fig.add_subplot(1,3,i+1)
  def projection(p):return [p[0]-.55*p[2],-p[1]+.3*(p[0]+p[2])]
  if i==0:
   for line in baseline['centerlines']:
    points=[projection([p[0]-95,p[1],p[2]])for p in line];ax.plot([p[0]for p in points],[p[1]for p in points],color='#327d8c')
   ax.set_title('Extracted baseline\n100 mm centerlines / R=95.15 mm')
  else:
   vertices=[];faces=[]
   for line in(ROOT/'designs'/name/a.version/'prescribed_close.obj').read_text().splitlines():
    s=line.split()
    if s and s[0]=='v':vertices.append(list(map(float,s[1:])))
    if s and s[0]=='f':faces.append([int(x)-1 for x in s[1:]])
   polygons=[];colors=[]
   for f in faces:
    polygons.append([projection(vertices[j])for j in f]);station=((f[0]%105)//5)*5
    colors.append(('#acd7dc'if i==1 else('#acd7dc'if station<30 else '#e5c68d'if station<65 else '#c5bce0')))
   ax.add_collection(PolyCollection(polygons,facecolors=colors,edgecolors='#53777b',linewidths=.15,alpha=.9))
   ax.set_title(('Wide tapered film'if i==1 else'Film + three pouch zones')+'\nCONCEPT prescribed curl / R=50 mm')
  ax.set_xlabel('projected x [mm]');ax.set_ylabel('projected height [mm]');ax.set_xlim(-125,125);ax.set_ylim(-50,130);ax.set_aspect('equal');ax.grid(alpha=.15)
 fig.suptitle('ReGrip geometry comparison — NOT SOFA deformation or validated grasp',fontsize=15)
 fig.text(.04,.04,'Film: 24→12 mm taper, 8×assumed 0.05 mm sheets; two edge tendons; shared proximal/middle/distal vacuum circuits.\nNo measured material properties, contact pressure or holding-force advantage is claimed.',fontsize=10)
 fig.subplots_adjust(bottom=.18,top=.8,wspace=.12);fig.savefig(out,dpi=150);plt.close(fig);print(out)
if __name__=='__main__':main()
