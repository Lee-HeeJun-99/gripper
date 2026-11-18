"""Passive diagnostics of preserved depth rejection; never raises its budget."""
import argparse,csv,json,shutil,subprocess
from curve_common import ROOT,sha,write_json
from film_guarded_process import guarded
def main():
 p=argparse.ArgumentParser();p.add_argument('--tag',required=True);a=p.parse_args();parent=ROOT/'results/autonomous_film_20261119_stationary_to238_1559';m=json.loads((parent/'summary.json').read_text())
 if m['status']!='FAIL' or m['failure_reason']!='endpoint-controlled depth budget;original gates unchanged':raise ValueError('specific preserved depth failure required')
 for f,d in m['source_hashes'].items():
  if sha(parent/'sources'/f)!=d:raise ValueError('compiled source changed')
 for f,d in m['raw_hashes'].items():
  if sha(parent/f)!=d:raise ValueError('reference raw changed')
 out=ROOT/'results'/('autonomous_film_'+a.tag);out.mkdir(exist_ok=False);shutil.copy2(__file__,out/'runner.py');shutil.copy2(parent/'input.checkpoint',out/'input.checkpoint');shutil.copytree(parent/'sources',out/'sources');header=out/'sources/models/film_coupled_collocation/EndpointControlledRows.h';text=header.read_text();anchor='releaseObserver={}){'
 if text.count(anchor)!=1:raise ValueError('frozen trace signature changed')
 text=text.replace(anchor,'releaseObserver={},\n const std::function<void(const RowsResult&,double,double,unsigned,bool,double,bool)>&attemptObserver={}){')
 old='[&](const RowsResult&){endpoint=true;}'
 if text.count(old)!=1:raise ValueError('endpoint observer anchor changed')
 text=text.replace(old,'[&](const RowsResult&r){endpoint=true;if(attemptObserver)attemptObserver(r,start,step,depth,true,std::numeric_limits<double>::quiet_NaN(),false);}')
 old='if(gap< -1e-10||activeGap){split=true;++out.stageRejected;}'
 if text.count(old)!=1:raise ValueError('stage acceptance anchor changed')
 header.write_text(text.replace(old,old+'\n   if(attemptObserver)attemptObserver(result,start,step,depth,false,gap,activeGap);'))
 cpp=out/'sources/diagnostics/film_three_finger/StationaryPersistent.cpp';text=cpp.read_text();anchor=' for(unsigned macro=0;'
 if text.count(anchor)!=1:raise ValueError('frozen reference loop anchor differs')
 observer=''' std::ofstream trace(std::string(argv[2])+".attempts.csv");trace<<std::setprecision(17)<<"start,h_s,depth,endpoint_exception,whole_min_gap_mm,active_gap_violation,stage,time,finger,triangle,feature,stage_gap_mm,rescan_gap_mm,force_N,q,v\\n";
 auto attemptObserver=[&](const regrip_collocation::RowsResult&r,double start,double step,unsigned depth,bool endpoint,double whole,bool active){for(unsigned k=0;k<2;++k){const auto&z=r.stages[k];for(unsigned f=0;f<3;++f){auto picked=s.selected(z.q,f);trace<<start<<','<<step<<','<<depth<<','<<endpoint<<',';if(std::isfinite(whole))trace<<whole;else trace<<"null";trace<<','<<active<<','<<k+1<<','<<z.time<<','<<f<<','<<picked.triangle<<','<<picked.feature<<','<<z.geometry.gap(f)<<','<<picked.gap<<','<<z.force(f);for(const auto*v:{&z.q,&z.v}){trace<<",\\\"";for(double x:*v)trace<<x<<' ';trace<<'\\\"';}trace<<'\\n';}}trace.flush();};
''';text=text.replace(anchor,observer+anchor);anchor='[&](const auto&x){return s.clearance(x);});'
 if text.count(anchor)!=1:raise ValueError('single unchanged contact solve call required')
 cpp.write_text(text.replace(anchor,'[&](const auto&x){return s.clearance(x);},63,5,{},attemptObserver);'))
 compile=guarded(['g++','-O2','-std=c++17','-ffp-contract=off','-I/usr/include/eigen3',cpp,'-o',out/'reference'],out/'compile',120);r=dict(status='FAIL',scope='passive independent attempt trace ONLY;NOT actual SOFA or physical horizon PASS',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),source_hashes={str(f.relative_to(out/'sources')):sha(f) for f in (out/'sources').rglob('*') if f.is_file()},parent_summary_sha256=sha(parent/'summary.json'),input_checkpoint_sha256=sha(out/'input.checkpoint'),compile=compile,physical_horizon_status='FAIL remains;no new accepted SOFA state',change_scope='opt-in observer only;budget63/depth5,force/control/tolerance unchanged')
 if compile['exit_code']==0:
  positive=guarded([out/'reference',out/'input.checkpoint',out/'positive.csv','2','111'],out/'positive_process',480);failure=guarded([out/'reference',out/'input.checkpoint',out/'probe.csv','3','111'],out/'probe_process',480);old=list(csv.DictReader((parent/'reference.csv').open()));same=list(csv.DictReader((out/'positive.csv').open()))==old;stages=list(csv.DictReader((out/'positive.csv.stages.csv').open()))==list(csv.DictReader((parent/'reference.csv.stages.csv').open()));reason=(out/'probe_process/stderr.log').read_text().strip();rows=list(csv.DictReader((out/'probe.csv.attempts.csv').open()));gap=[float(x['stage_gap_mm']) for x in rows];requery=max(abs(float(x['stage_gap_mm'])-float(x['rescan_gap_mm'])) for x in rows);features=sorted({(int(x['finger']),int(x['triangle']),int(x['feature'])) for x in rows});r.update(status='PASS' if positive['exit_code']==0 and failure['exit_code']!=0 and reason==m['failure_reason'] and same and stages and requery==0 else 'FAIL',positive_process=positive,probe_process=failure,accepted_prefix_state_rows_exact=same,accepted_prefix_force_stage_rows_exact=stages,reproduced_failure_reason=reason,observations=len(rows),minimum_attempt_h_s=min(float(x['h_s']) for x in rows),maximum_depth=max(int(x['depth']) for x in rows),minimum_stage_gap_mm=min(gap),maximum_stage_gap_mm=max(gap),geometry_requery_max_abs_mm=requery,observed_features=features,binary_sha256=sha(out/'reference'))
 r['raw_hashes']={f.name:sha(f) for f in out.iterdir() if f.suffix in ('.txt','.csv')};write_json(out/'summary.json',r);print(json.dumps({k:v for k,v in r.items() if k not in ('source_hashes','compile','positive_process','probe_process','raw_hashes')}))
if __name__=='__main__':main()
