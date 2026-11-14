# SOFA 메모리 진단

**원인 재현 PASS / 동일 프로세스 plateau FAIL / 외부 엔진 수정 NOT RUN.**

60000 step FREE에서 mallinfo2 live_heap=195384912 bytes, unload 후194904800 bytes.
malloc_trim으로 live allocation은 제거되지 않는다. RSS만 보고 leak으로 단정하지 않았다.
별도 operator new/delete 추적(직접 malloc/aligned 제외)의 stack이
`MappingGraph::build`, `makeMappingGraphNode`, `addEdge`를 지목한다.
SDK BaseMappingGraphNode의 부모·자식 모두 shared_ptr이다. 공개 API graph.clear 후
weak_ptr 9/9 생존, beam/observer/new ForceField가 없는 mass-only 최소 장면에서도4/4 생존.
최소 장면60000 step 종료 live_heap83443728 bytes, unload83289648 bytes.
이 특정 ownership retention은 확인됐지만 모든 메모리 증가가 이 경로뿐이라는 증명은 아니다.

원래10000 step allocation tracing은150s timeout/SIGKILL로 FAIL;1500 step 재시도는 성공(skipped=0).
이전 empty/mass/beam/implicit/explicit/FREE/coupled 대조군은 이전 증거로 보존했다.
이번에는 allocator default/trim, native driver, graph clear, mass-only 최소 재현을 추가했다.
Finite field/recorder 각각의 수 시간 plateau, 전체 엔진 LSan은 NOT RUN.
프로젝트 ASan/UBSan은 detect_leaks=0 범위만 PASS이며 배포 SOFA는 instrument하지 않았다.

외부 SDK·엔진 바이너리/시스템은 수정하지 않았다. 안전한 우회는 실험별 bounded child:
주소 공간4GiB, wall timeout180s, 최대120000 step/60s(일반 runner), 종료 후 reap.
이는 같은 프로세스의 leak 수정이 아니며 장시간 안정성 인증도 아니다.
FD/PSS/Private_Dirty 샘플과 allocator 통계는 memory/summary.json에 남는다.

재현: `python tools/integrated_memory.py`, `python tools/integrated_minimal.py`
(출력 루트를 새로 지정하고 진단 바이너리를 먼저 빌드). 최소 장면은
`scenes/integrated/minimal_mapping_graph.scn`; 외부 엔진 이슈로 제출 가능한 재현이다.

## 공통 범위 및 판정

모든 신규 수치는 연구 단위 F, mm, s의 시뮬레이션이며 실물 측정값은 없다.
원본 `plugin/`, `models/finite_rotation/`, `models/multilayer/beam.py`, 골든 데이터는 변경하지 않았다.
기존 45개 gate는 시작 manifest 무결성을 확인한 **이전 검증**이며 새 모델의 인증으로 합산하지 않는다.
신규 평형 판정은 sampled static residual <1e-3, 최종 병진/각속도 <1e-5,
tail relative drift <1e-4이다. 실패를 숨기기 위해 하중·재료·허용오차를 바꾸지 않았다.
평면 slider/선형 연결은 회전 <.005 rad 및 |qx|,|qz|<1e-8만 인정한다.
초기 v1의 nonzero-load residual floor 때문에 일부 tiny-cable PASS는 강화 감사에서 FAIL로 바뀌었다.
최종 판정은 residual_audit/strict_residual_retry가 우선하며 과거 raw의 상태를 수정하지 않는다.
Raw 위치: `results/integrated_20261115/`; 작은 증거: `reports/integrated_evidence/`.
`metrics.json`은 소스/바이너리 해시, 설정, 명령, 로그, 원시 상태 파일 해시를 포함한다.
PASS는 명시된 검사만 의미하며 EXPERIMENTAL transient의 프로그램 종료는 평형 PASS가 아니다.
