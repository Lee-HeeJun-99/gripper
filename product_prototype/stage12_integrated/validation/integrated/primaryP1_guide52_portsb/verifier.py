"""Independent actual guide support section/tools and saved fourmount work audit.
Correct initial16mm metadata against actual6mm support overlap;no geometry repair.
"""
import json,sys,math,shutil
import numpy as np
from scipy.optimize import linprog
from baseline_registry import ROOT,REPO,S1,ref,sha,dump
sys.path.insert(0,str(S1/'scripts'))
from incremental_stage1 import read,bounds,common,box,cyl,cut,fuse,volume
from mechanisms_stage1 import hex_axis
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common

def main():
 out=ROOT/'validation/integrated/primaryP1_guide52_portsb';out.mkdir();shutil.copyfile(__file__,out/'verifier.py');cp=ROOT/'cad/exports/primaryP1_guide52/summary.json';d=json.loads(cp.read_text());vp=ROOT/'validation/integrated/primaryP1_guide52_validationb/summary.json';v=json.loads(vp.read_text());assert all(v['checks'].values());assert all(sha(REPO/r['path'])==r['SHA256'] for r in [*d['part_references'].values(),d['assembly'],d['BOM']]);parts={n:read(REPO/d['part_references'][n]['path']) for n in ['BENCH_ANCHOR_RAIL','BENCH_SUPPORT']};sections=[];tools=[]
 for y in [-58.,39.]:
  support=BRepAlgoAPI_Common(parts['BENCH_SUPPORT'],box(-79.2,y-2,45,.8,4,30)).Shape();tongue=BRepAlgoAPI_Common(parts['BENCH_ANCHOR_RAIL'],box(-77.5,y-2,45,3,4,22)).Shape();sb=bounds(support);tb=bounds(tongue);eng=min(sb[5],tb[5])-max(sb[2],tb[2]);sections.append(dict(y_mm=y,support_local_bounds_mm=sb,tongue_local_bounds_mm=tb,actual_vertical_overlap_mm=eng))
 for i,(x,y) in enumerate([(-59,-58),(101,-58),(-59,39),(101,39)]):
  carriers=cut(cyl(3.8,(x,y,25.3),30),cyl(2.6,(x,y,25.29),30.02));nut=cut(hex_axis((x,y,30.3),(0,0,1),8,29.7),cyl(2.5,(x,y,30.29),29.72));bolt=fuse(cyl(4.25,(x,y,74),35),cyl(2.5,(x,y,54),50));driver=hex_axis((x,y,76.6),(0,0,1),3.9,32)
  for kind,s in [('25mm_nut_feed',nut),('30mm_bolt_feed_head_shank_envelope',bolt),('annular_nutcarrier',carriers),('4AF_driver',driver)]:
   for n,q in parts.items():tools.append(dict(mount=i,tool=kind,against=n,common_mm3=common(s,q)))
 # Reconstruct saved column wrenches from original actual quadrature positions,
 # without using the previously transformed108DOFcolumns in the reconstruction.
 fp=ROOT/'validation/integrated/primaryP1_fourmount52b/summary.json';four=json.loads(fp.read_text());base=json.loads((REPO/four['parent_endpoint']['path']).read_text());cols=[];O=np.array(four['origin_mm']);rng=np.random.default_rng(52);tw=rng.normal(size=(18,6));work=[]
 for i,(x,y) in enumerate([(-59,-58),(101,-58),(-59,39),(101,39)]):
  shift=np.array([x+59,y+58,0.])
  for c in base['contacts']:
   localnames=['BENCH_MOUNT_BOLT_0','BENCH_MOUNT_NUT_0','BENCH_MOUNT_SOCKET_KEY_0','BENCH_MOUNT_SPLIT_PIN_0','BENCH_ANCHOR_RAIL','BENCH_SUPPORT'];ii=localnames.index(c['body_i']);jj=localnames.index(c['body_j']);ii=4*i+ii if ii<4 else ii+12;jj=4*i+jj if jj<4 else jj+12;col=np.zeros((18,6));direct=0
   samples=c.get('quadrature',[dict(point_mm=c.get('point_mm'),normal_force_on_bolt=c.get('force_on_i_per_multiplier_N'),area_mm2=1.)])
   for sm in samples:
    p=np.array(sm['point_mm'])+shift;f=np.array(sm['normal_force_on_bolt'])*sm['area_mm2'];r=p-O;w=np.r_[f,np.cross(r,f)];col[ii]+=w;col[jj]-=w;direct+=f@(tw[ii,:3]+np.cross(tw[ii,3:],r)-tw[jj,:3]-np.cross(tw[jj,3:],r))
   cols.append(col.ravel());work.append(abs(col.ravel()@tw.ravel()-direct))
 A=np.array(cols).T;stored=np.array([r['column'] for r in four['contact_columns']]).T;F=np.array(four['external_load_vector']);certificate=linprog(np.zeros(108),A_ub=-A.T,b_ub=np.zeros(A.shape[1]),A_eq=F.reshape(1,-1),b_eq=[1.],bounds=[(-1000,1000)]*108,method='highs');cert=None
 if certificate.success:
  z=certificate.x;cert=dict(twist_108DOF=z.tolist(),minimum_contact_normal_work=float(min(A.T@z)),external_positive_work=float(F@z),meaning='Farkas separation certificate:nonnegativecontactreactions cannotbalance selectedendpointunitload;NOT wholeproductfailure or missingboreproof')
 guidework=[]
 for u in v['unit_torque_bearing']:
  ww=np.zeros(6)
  for r in u['contacts']:
   f=np.array(r['force_on_receiver_N']);p=np.array(r['point_mm'])-np.array([-76,-9.5,63]);ww+=np.r_[f,np.cross(p,f)]
  guidework.append(dict(sign=u['sign'],reconstructed_wrench=ww.tolist(),max_saved_error=float(max(abs(ww-np.array(u['total_wrench_N_Nmm'])))),missing_one_contact_has_net_force=bool(abs(u['contacts'][0]['magnitude_N'])>1e-6),reverse_contact_would_reverse_torque=bool(abs(ww[5])>1e-6)))
 checks=dict(actual_vertical_overlap_6mm=all(abs(s['actual_vertical_overlap_mm']-6)<1e-6 for s in sections),original16mm_claim_explicitly_rejected=True,all32_mount_tool_envelopes_clear=all(abs(t['common_mm3'])<1e-8 for t in tools),independent108DOFcolumns=float(max(abs(A-stored).flat))<1e-9,independent108DOFvirtualwork=max(work)<1e-9,saved_fourmount_failure_retained=not four['solution']['feasible'],actual_fourmount_failure_certificate=cert is not None and cert['minimum_contact_normal_work']>-1e-6 and abs(cert['external_positive_work']-1)<1e-7,guide_saved_wrench_reconstructs=all(r['max_saved_error']<1e-12 for r in guidework),guide_missing_or_reverse_controls_reject=all(r['missing_one_contact_has_net_force'] and r['reverse_contact_would_reverse_torque'] for r in guidework))
 result=dict(status='ACTUAL_P1_GUIDE_TOOLS_SECTIONS_AND_INDEPENDENT_WRENCH_AUDIT_LOCAL_PASS_NOT_RELEASE' if all(checks.values()) else 'ACTUAL_P1_GUIDE_INDEPENDENT_AUDIT_FAIL',candidate=ref(cp),verifier=ref(out/'verifier.py'),guide_validation=ref(vp),old_fourmount_endpoint=ref(fp),checks={k:bool(v) for k,v in checks.items()},actual_material_sections=sections,mount_tool_checks=tools,independent_column_error=float(max(abs(A-stored).flat)),independent_virtualwork_error=max(work),old_endpoint_Farkas_certificate=cert,guide_wrench_reconstruction=guidework,accepted_physical_product_equilibria=0,newly_qualified_system_gate_ids=[],whole_system_release=False,limitations=['Tools cover4existing mount feed/driver envelopes against2changedsolids;not a newfull128assemblyorhelicalfeedcertificate','Guide corner wrench only;no coupledthread/headseat/key/cage/bore/guide equilibrium atnewyaw','No loadedpressure/capacity/material/notch/stiffness orhostqualification'])
 dump(out/'summary.json',result)
 if all(checks.values()):
  # New canonical metadata only;initialwronginputs and alloriginalCADbytesimmutable.
  oldinputs=json.loads((REPO/d['inputs']['path']).read_text());oldinputs.update(nominal_vertical_engagement_mm=6,corrected_from=ref(REPO/d['inputs']['path']),actual_section_evidence=ref(out/'summary.json'),correction='Initial16mm claimmistook tongue span foractualsupport thickness;actual6mm z60..66,not16mm');ip=cp.parent/'inputs_corrected.json';dump(ip,oldinputs);canonical=dict(d);canonical.update(inputs=ref(ip),initial_uncorrected_geometry_record=ref(cp),metadata_correction='Actualguideengagement6mm;initial16mmrejected;CADunchanged',validation=ref(vp),independent_audit=ref(out/'summary.json'));dump(cp.parent/'summary_corrected.json',canonical)
 print(json.dumps(dict(status=result['status'],checks={k:bool(v) for k,v in checks.items()},sections=sections,certificate=None if cert is None else {k:v for k,v in cert.items() if k!='twist_108DOF'})),flush=True);raise SystemExit(0 if all(checks.values()) else 2)
if __name__=='__main__':main()
