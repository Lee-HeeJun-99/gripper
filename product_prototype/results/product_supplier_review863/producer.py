"""Sections and instance BOM from actual new mesh recipes,NOT fabrication drawings approval."""
import argparse,csv,json,os,subprocess
from pathlib import Path
import numpy as np
from manufacturing_assembly import BASE,evaluate,sha

def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();out=BASE/'results'/a.tag;out.mkdir(exist_ok=False);os.environ['MPLCONFIGDIR']=str(out/'mplconfig')
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 sources=[BASE/'meshes'/x/'full_assembly_recipe.json' for x in ('b3_root_thrust_v39','b3_supplier_eyelet_seat_v43')];old,new=[json.loads(x.read_text())['parts'] for x in sources];fig,axes=plt.subplots(1,3,figsize=(16,6));names=['palm_bridge_bores','f0_c0_root_redirect','f0_c0_root_mounted_bridge','f0_c0_root_headed_pin','f0_c0_s0_eyelet','f0_c0_s0_support','f0_c0_s0_bondline_RESEARCH'];colors=['.65','tab:blue','tab:green','tab:purple','tab:orange','tab:red','black']
 for axis,parts,title in zip(axes[:2],(old,new),('V39 reference / NOT supplier-qualified','New ONE Root unit / joints still UNQUALIFIED')):
  for name,color in zip(names,colors):
   part=next((p for p in parts if p['name']==name),None)
   if part is None:continue
   section=evaluate(part['shape']).section(plane_origin=[0,36,0],plane_normal=[0,1,0])
   if section is None:continue
   for i,line in enumerate(section.discrete):axis.plot(line[:,0],line[:,2],color=color,lw=1,label=name.replace('f0_c0_','') if i==0 else None)
  axis.set(xlim=(38,68),ylim=(-20,8),xlabel='world x [mm]',ylabel='world z [mm]',title=title);axis.set_aspect('equal');axis.legend(fontsize=6)
 profile=np.array(json.loads((BASE/'meshes/b3_supplier_root_module_v41/profile_mm.json').read_text()));axes[2].plot(profile[:,0],profile[:,1],color='tab:blue');axes[2].add_patch(plt.Circle((5.85,0),.225,fill=False,color='black',ls='--',label='DESIGN wire D0.45 (not deformedSOFA)'));axes[2].set(xlim=(5.4,7.1),ylim=(-1.05,1.05),xlabel='radius from axle [mm]',ylabel='axial z [mm]',title='Actual revolved profile, design dimensions');axes[2].text(5.43,.97,'RootD11.25 / pitchD11.70\nGroove cross-section R0.2385\nOD13.75 / width1.8 / boreD1.2',fontsize=8,va='top');axes[2].set_aspect('equal');axes[2].legend(fontsize=6,loc='lower center')
 fig.suptitle('Actual mesh CAD sections ONLY — no SOFA state or fabrication qualification\nNew0.45mm wire/recentred Root/translated first guide/rebuilt mount/UNSELECTED finite bondline;not all6Root units',fontsize=11);fig.tight_layout()
 for ext in ('png','svg'):fig.savefig(out/('supplier_root_sections.'+ext),dpi=160)
 plt.close(fig)
 with (out/'instance_BOM.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['actual_part_name','quantity','group','qualification'])
  for part in new:w.writerow([part['name'],1,part.get('group','design_part'),'DESIGN_ONLY_NOT_MATERIAL_OR_ASSEMBLY_APPROVED'])
 result=dict(status='ACTUAL_CAD_SECTIONS_AND_INSTANCE_BOM_ONLY',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),input_hashes={str(x.relative_to(BASE)):sha(x) for x in [Path(__file__),BASE/'cad/manufacturing_assembly.py',*sources,BASE/'meshes/b3_supplier_root_module_v41/profile_mm.json']},actual_BOM_instances=len(new),STEP_generated=False,fabrication_ready=False,scope='Actual mesh plane sections atworldy36,not a full3Dinterferenceproof ormanufacturingtolerance drawing. Dashed wirecircle isexplicit DESIGNreference,notSOFA. BOM all293actualrecipeinstances,NOTselectedmotors/materials orpurchaseauthorization. No Native/dynamics execution inthisCADcycle.')
 (out/'producer.py').write_bytes(Path(__file__).read_bytes());(out/'summary.json').write_text(json.dumps(result,indent=2));print(out/'supplier_root_sections.png')
if __name__=='__main__':main()
