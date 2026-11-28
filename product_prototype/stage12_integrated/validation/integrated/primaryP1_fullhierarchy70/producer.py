"""Exact P1 full-volume vector difference on a verified conforming hierarchy.
Reconstruct actual saved bisections and parent IDs; never extrapolate or align.
This certifies comparison on FIXED original polyhedral domain, not curved CAD.
"""
import sys,json,shutil,numpy as np
from baseline_registry import ROOT,REPO,ref,dump
V=ROOT/'validation/integrated';out=V/sys.argv[1];out.mkdir();shutil.copyfile(__file__,out/'producer.py')
tags=['primaryP1_bothfast68h5','primaryP1_inplane70l1','primaryP1_inplane70l2','primaryP1_mixed70l1b']
states=[(V/tag,np.load(V/tag/'field.npz')) for tag in tags]
vp=V/'primaryP1_inplanevectors70';mp=V/'primaryP1_mixedvectors70'
mapping={(0,1):np.load(vp/'parent_0_1.npz')['fine_to_coarse_tetra'],(0,2):np.load(vp/'parent_0_2.npz')['fine_to_coarse_tetra'],(1,2):np.load(vp/'parent_1_2.npz')['fine_to_coarse_tetra'],(2,3):np.load(mp/'parent_0_1.npz')['fine_to_coarse_tetra']}
for i in [0,1]:mapping[(i,3)]=mapping[(i,2)][mapping[(2,3)]]
journal=[dict(independently_reconstructed_hierarchy=ref(vp/'summary.json')),dict(independently_reconstructed_hierarchy=ref(mp/'summary.json')),dict(composition='Exact discrete parent0or1_of2[parent2_of3]; every finevertex and parent partition checked again for all6pairs, no spatial observer/extrapolation.')]
rows=[]
for (i,j),parent in sorted(mapping.items()):
 src,a=states[i];target,b=states[j];pc,tc,uc=a['points_mm'],a['tetra'],a['displacement_mm'];pf,tf,uf=b['points_mm'],b['tetra'],b['displacement_mm'];xyz=pf[tf];dx=pc[tc[:,1:]]-pc[tc[:,0,None]];inverse=np.linalg.inv(np.transpose(dx,(0,2,1)));bc3=np.einsum('tij,taj->tai',inverse[parent],xyz-pc[tc[parent,0,None]]);bc=np.concatenate([1-bc3.sum(2)[:,:,None],bc3],axis=2);assert bc.min()>-1e-10;assert abs(np.einsum('tai,tij->taj',bc,pc[tc[parent]])-xyz).max()<1e-8
 coarse_on_fine=np.einsum('tai,tij->taj',bc,uc[tc[parent]]);diff=uf[tf]-coarse_on_fine;vol=abs(np.linalg.det(pf[tf[:,1:]]-pf[tf[:,0,None]]))/6;cv=abs(np.linalg.det(dx))/6;parentvol=np.bincount(parent,weights=vol,minlength=len(tc));volumeerror=float(abs(parentvol-cv).max());assert volumeerror<1e-8
 def squared(u):return float(np.sum(vol*(np.sum(u.sum(1)**2,axis=1)+np.sum(u*u,axis=(1,2))))/20)
 err=(squared(diff)/vol.sum())**.5;rc=(squared(coarse_on_fine)/vol.sum())**.5;rf=(squared(uf[tf])/vol.sum())**.5;coarse_s=json.loads((src/'summary.json').read_text());fine_s=json.loads((target/'summary.json').read_text());full=all(coarse_s['checks'].values()) and all(fine_s['checks'].values());np.savez_compressed(out/f'parent_{i}_{j}.npz',fine_to_coarse_tetra=parent,coarse_barycentric_at_fine_vertices=bc)
 # Wrong parent is rejected by the same strict barycentric domain check.
 wrong=(parent+max(1,len(tc)//2))%len(tc);wb3=np.einsum('tij,taj->tai',inverse[wrong[:100]],xyz[:100]-pc[tc[wrong[:100],0,None]]);wb=np.concatenate([1-wb3.sum(2)[:,:,None],wb3],axis=2);wrong_min=float(wb.min());assert wrong_min<-1e-10
 rows.append(dict(coarse=ref(src/'summary.json'),fine=ref(target/'summary.json'),parent_map=ref(out/f'parent_{i}_{j}.npz'),all_points_covered=True,minimum_barycentric=float(bc.min()),maximum_parent_volume_partition_error_mm3=volumeerror,exact_fullvolume_vector_difference_RMS_mm=err,coarse_volume_RMS_mm=rc,fine_volume_RMS_mm=rf,relative_with_fine_denominator=err/rf,relative_with_coarse_denominator=err/rc,original1percent_both_directions=bool(err/rf<.01 and err/rc<.01),both_full_load_local=full,wrong_parent_minimum_barycentric=wrong_min,wrong_parent_rejected=True,no_alignment=True))
dump(out/'summary.json',dict(status='ACTUAL_P1_EXACT_NESTED_POLYHEDRAL_FULLVOLUME_VECTOR_CONTRAST',candidate=fine_s['candidate'],producer=ref(out/'producer.py'),hierarchy=journal,rows=rows,newly_qualified_system_gate_ids=[],whole_system_release=False,scope='Exact quadratic integral of P1 field difference over every verified fine tetra; original domain and volume preserved; BOTH denominators, no alignment or hidden gauge. This is NOT exact curved CAD domain, source-minimum strength, dt, globalenergy, or83body certificate.'))
print(json.dumps(dict(rows=rows)))
