# GRASP 06 — MappingGraph 수정 엔진

**PASS(한정 범위):** matched-source 별도 headless SDK 빌드,weak-parent 객체 수명,최소 기계 장면
2×120000step/unload/reload의 live heap plateau,실제 물리 골든 회귀.
**NOT RUN:** 수 시간/전체 collision·Python·GUI·모든 신규 파지의 수정 엔진 무누수 인증.
설치 SOFA는 그대로 두며 기본 실험은 여전히 bounded child를 사용한다.

이전 `STABILIZATION_02_MEMORY.md`의 installed-engine 1376bytes/step와 unload 후 live heap331010080bytes,
graph4/4 잔존 증거는 hash 검증 후 인용했다. 이번 새 측정과 구분한다.
공식 [issue6230](https://github.com/sofa-framework/sofa/issues/6230),
[PR6259](https://github.com/sofa-framework/sofa/pull/6259)의 parent back-reference weak_ptr 수정에 근거했다.

설치git-info commit7c18e95d5c5f2839079892c69e7d89a313c79603과 동일 source를 `.runtime/sofa-source`에 확보하고
MappingGraph.cpp/BaseMappingGraphNode.{h,cpp}의 parent weak ownership/lock 논리를 별도 적용했다.
공식 patch/적용된 소스 해시·빌드 CMakeCache·ldd를 보존한다. 주석 차이는 있으며 시스템 SDK는 수정하지 않았다.
헤더만 교체하지 않았고 tested headless target의 모든 SOFA 의존 라이브러리를 같은 source tree에서 재빌드했다.
SDK export Targets.cmake 미설치 문제는 in-tree `SOFA_EXTERNAL_DIRECTORIES=diagnostics/grasp`로 해결.
불필요 GUI/collision/plugin fetch는OFF. 최종 `ldd`에 설치 `/home/ubuntu/SOFA` 라이브러리 없음.
첫600s build timeout은 보존,증분 재개 및 누락 Constraint.Projective target 빌드 후 성공했다.

실제 graph.clear 후 nodes4,retained0(이전4) 확인.
`audits/sdk_memory`는 동일프로세스120000→unload/trim→reload→120000:

|상태|live heap bytes|RSS bytes|
|---|---:|---:|
|초기|852128|42975232|
|60000|889504|44589056|
|120000|889600|44593152|
|unload|692304|44568576|
|reload|861680|44646400|
|180000|891328|44662784|
|240000|891424|44666880|
|unload|693664|44580864|

각 후반60000step live 증가96bytes(.0016bytes/step). 두 번째 후반 PSS39963→39967KiB,
Private_Dirty6404→6408KiB,RSS43616→43620KiB,FD5 일정.
RSS가 반환되지 않는 현상과 실제 live ownership 누적을 구별했다. 잔존 heap693664가0이라는 주장은 하지 않는다.
해당 plateau 진단기준은 기존처럼 후반 증가<1MiB이며 실제96bytes를 함께 제시한다.
SDK회귀 600시점 FREE2회 모두 기존1e-10+1e-6|golden| PASS;8층3dt force balance도PASS.
신규파지 v4는 설치SDK용 바이너리로 bounded 실행했고 수정SDK에 혼합하지 않았다.
전체 파지 엔진 전환은 matched plugin rebuild+동일 physics gate 후 별도 승인할 개발 과제다.

`build/grasp_20261115/sofa_patched/bin/memory_lifetime build/grasp_20261115/sofa_patched scenes/integrated/minimal_mapping_graph.scn`
명령/소스/라이브러리 hash는 evidence manifest에 있다. 원본 엔진을 교체하지 않는다.
