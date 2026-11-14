# SofaPython3 복구

**BLOCKED.** 실제 libSofaPython3.so의 ldd에서 libpython3.12.so.1.0 not found를 재확인.
기존 Python3.10을3.12로 위장하거나 symlink하지 않았다. CPython3.12와 NumPy의 격리
Conda 복구는 offline 캐시 부재 및 online DNS 장애로 실패했다.
`runSofa --noautoload --tmp -g batch -a -n 3 -l SofaPython3 scenes/python_smoke.py`
종료 코드0이어도 오류 로그가 있으므로 실패이며, 시간 적분 성공으로 인정하지 않는다.
원본 V1.0.9 FREE/V1.1.0 Python 비교는 NOT RUN. XML/C++ 실제 실행은 별도로 계속했다.
필요 조건: 허용된 네트워크 또는 CPython3.12 공유 런타임/stdlib 및 ABI호환 NumPy offline package.
재개: 새 출력 루트에서 `python tools/next_environment.py`, 이후 `tools/revalidate_python.py` 검토.
정확한 명령·exit·ABI log는 dependencies/environment/summary.json을 참조한다.

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
