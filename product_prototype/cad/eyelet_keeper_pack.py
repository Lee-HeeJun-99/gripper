"""Actual keeper mesh/sections/BOM review pack;no STEP or fabrication approval."""
import argparse,csv,json,os,shutil,subprocess,time,itertools
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha,transform

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);p.add_argument('--name',required=True);p.add_argument('--assembly-case',default='product_eyelet_keeper894');p.add_argument('--source-cases',nargs='*',default=[]);a=p.parse_args()
 if any(Path(n).name!=n for n in [a.tag,a.name,a.assembly_case,*a.source_cases]):p.error('local names required')
 out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);dest=BASE/'meshes'/a.name;draw=BASE/'drawings'/a.name;dest.mkdir(exist_ok=False);draw.mkdir(exist_ok=False);start=time.monotonic();source=BASE/'results'/a.assembly_case;base=BASE/'results/product_eyelet_keeper894';recipe=source/'full_assembly_recipe.json';frame=base/'keeper_frame.json';summary=base/'summary.json';H=np.array(json.loads(frame.read_text()));parts=json.loads(recipe.read_text())['parts'];meta=json.loads(summary.read_text());selected=[p for p in parts if p['name'].startswith('f0_c1_s0_')];solids=[];exploded=[];outputs=[]
 for p in selected:
  body=evaluate(p['shape']);local=body.copy();local.apply_transform(np.linalg.inv(H));solids.append((p['name'],local))
  original=next((folder/(p['name']+'.stl') for folder in (source,*[BASE/'results'/case for case in a.source_cases],base,BASE/'results/product_supplier_second_root886') if (folder/(p['name']+'.stl')).is_file()),source/(p['name']+'.stl'))
  if not original.is_file():raise ValueError('actual saved source STL missing')
  provenance=original.parent/'full_assembly_recipe.json'
  if provenance.is_file():
   producer_part=next(q for q in json.loads(provenance.read_text())['parts'] if q['name']==p['name'])
   if producer_part['shape']!=p['shape']:raise ValueError('saved-STL source recipe identity mismatch:'+p['name'])
  target=dest/original.name;shutil.copy2(original,target);outputs.append(target)
  delta=3 if 'cover' in p['name'] else 6 if 'screw' in p['name'] else -6 if 'nut' in p['name'] else 1.5 if p['name'].endswith('_eyelet') else 0
  T=np.eye(4);T[:3,3]=delta*H[:3,1];exploded.append(dict(p,shape=transform(p['shape'],T)))
 shutil.copy2(recipe,dest/'full_assembly_recipe.json');shutil.copy2(frame,dest/'keeper_frame.json');(dest/'exploded_review_recipe.json').write_text(json.dumps(dict(units='mm',parts=exploded,scope='DESIGN exploded placements only;NOT actual motion or tested service trajectories'),indent=2))
 params=dict(status='UNQUALIFIED_RESEARCH_DESIGN_INPUTS',source_summary_sha256=sha(summary),dimensions=meta['dimensions'],rootward_wall_mm=meta['rootward_wall_mm'],outboard_tabs=meta['outboard_tabs'],actual_material=None,actual_fastener_specification=None,actual_preload_N=None,actual_joint_strength_N=None,STEP_generated=False,fabrication_ready=False);(draw/'parameters.json').write_text(json.dumps(params,indent=2))
 with (draw/'BOM.csv').open('w',newline='') as stream:
  writer=csv.writer(stream);writer.writerow(['part','quantity','group','status'])
  for part in parts:writer.writerow([part['name'],1,part.get('group','design_part'),'DESIGN_ONLY_MATERIAL_AND_FIT_NOT_APPROVED'])
 os.environ['MPLCONFIGDIR']=str(out/'mplconfig');import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,3,figsize=(15,6));colors=['tab:green','tab:orange','tab:purple','tab:purple','tab:red','tab:red','tab:blue']
 for ax,origin,normal,coords,title in zip(axes,([0,-.1,0],[0,.1,0],[0,0,0]),([0,1,0],[0,1,0],[0,0,1]),((2,0),(2,0),(0,1)),('lower section y=-0.1mm','upper section y=+0.1mm','radial section z=0mm')):
  for (name,body),color in zip(solids,itertools.cycle(colors)):
   section=body.section(plane_origin=origin,plane_normal=normal)
   if section is None:continue
   for i,line in enumerate(section.discrete):ax.plot(line[:,coords[0]],line[:,coords[1]],color=color,lw=1,label=name.replace('f0_c1_s0_','') if i==0 else None)
  ax.set(title=title,xlabel='local axial z [mm]' if coords[0]==2 else 'local radial x [mm]',ylabel='local radial x [mm]' if coords[1]==0 else 'local radial y [mm]');ax.set_aspect('equal');ax.legend(fontsize=6)
 fig.suptitle('ACTUAL CAD SECTIONS — mechanical Eyelet review ONLY\nEyelet D3×2; pocket D3.1; axial slack0.1 each; rootward wall0.45; screwsD1/holesD1.2 assumed\nNot Native SOFA states, process tolerances, strength or fabrication qualification',fontsize=10);fig.tight_layout()
 for ext in ('png','svg'):fig.savefig(draw/('keeper_sections.'+ext),dpi=160)
 plt.close(fig)
 status=dict(status='MECHANICAL_KEEPER_CAD_REVIEW_NOT_FABRICATION_RELEASE',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(p.relative_to(BASE)):sha(p) for p in (Path(__file__),recipe,frame,summary)},saved_STL_count=len(outputs),saved_STL_hashes={str(p.relative_to(BASE)):sha(p) for p in outputs},BOM_instances=len(parts),runtime_s=time.monotonic()-start,mesh_output=str(dest.relative_to(BASE)),drawing_output=str(draw.relative_to(BASE)),STEP_generated=False,fabrication_ready=False,scope=f'Copies{len(outputs)}actual saved STL parts and exact{len(parts)}part recipe. 3actual plane sections avoid splitgap;explicit assumed keeper dimensions. Exploded{len(outputs)}part recipe is DESIGNvisualization,NOT tested disassembly/motion or SOFA. No selected fasteners/material/motor,tool/preload/tolerance/strength/fullassembly/fabrication approval.')
 if a.assembly_case!='product_eyelet_keeper894':
  inputs=source/'summary.json';status['input_hashes'][str(inputs.relative_to(BASE))]=sha(inputs);(draw/'rail_clamp_parameters.json').write_bytes(inputs.read_bytes());status['scope']+=' Additional Rail-clamp parameters are original UNLOADED researchsummary,not preload orforcequalification.'
 (draw/'REVIEW_STATUS.json').write_text(json.dumps(status,indent=2));(out/'summary.json').write_text(json.dumps(status,indent=2));(out/'producer.py').write_bytes(Path(__file__).read_bytes());print(draw/'keeper_sections.png')
if __name__=='__main__':main()
