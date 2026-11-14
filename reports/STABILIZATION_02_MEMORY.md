# MappingGraph 수명

**동일 프로세스 plateau FAIL; 공식 원인/수정 확인 PASS; 패치 엔진 실행 BLOCKED.**
기존 weak_ptr9/9 및 최소 장면4/4 생존 증거를 무결성 검증 후 활용했다.
이번에는 같은 프로세스에서120000step→unload/trim→reload→120000step을 실제 실행했다.
live heap846256→83443056(60000)→166003056(120000)→165848624(unload),
reload 후166017520→248605504→331165504→331010080(unload) bytes.
마지막 구간 증가율1376 bytes/step, FD5 유지, PSS/RSS/Private_Dirty도 함께 기록했다.
unload/malloc_trim이 live allocation을 거의 해제하지 못했다. allocator cache만의 현상이 아니다.

공식 [이슈6230](https://github.com/sofa-framework/sofa/issues/6230)과
[PR6259](https://github.com/sofa-framework/sofa/pull/6259)는 부모 back-reference를 weak_ptr로 바꾸는 수정이다.
PR은2026-09-03 master에1c8a469로 병합됐다. 이 내용은 외부 출처이며 이번 패치 실행 결과가 아니다.
설치 SDK는 여전히 양방향 shared_ptr이다. public API는 const adjacency만 제공한다.
원본 SDK 덮어쓰기/private 강제 해제를 하지 않았다. 호환되는 전체 source build 확보가 필요하며
헤더만 바꿔 기존 바이너리 ABI와 섞지 않는다. 실제 수정 SDK 비교는 NOT RUN.
bounded child4GiB/180s 및 kill/reap를 유지한다. 수 시간 안정성은 NOT RUN.
LSan 재시도는 실제 ptrace fatal error(exit1)로 BLOCKED. ASan/UBSan detect_leaks=0와 구분한다.

## 공통 증거/범위

환경: Ubuntu22.04.5, kernel6.8.0-138-generic, GCC11.4, CMake3.22.1,
Python3.10.20(robot_ws), SOFA v26.06.00(`/home/ubuntu/SOFA/v26.06.00`).
실물 측정값0건. 연구 단위 F/mm/s와 기존 E=250, A≈.732233mm², I=.0426667mm⁴를 사용한다.
기존 plugin/integrated/finite_rotation/multilayer 원본과 골든 파일을 변경하지 않았다.
raw: `results/stabilization_20261115/`; 작은 증거: `reports/stabilization_evidence/`.
설정/명령은 실험별 config.json/command.json/scene.scn, 결과는 metrics.json과 artifact hashes.
정적 잔차<1e-3, 병진/각속도<1e-5, tail drift<1e-4를 유지했다.
실행 성공과 평형/파지 검증을 구분한다. EXPERIMENTAL은 실물 인증이나 전체 모델 PASS가 아니다.
기존45 gate는 이전 소스/바이너리 무결성으로 승계하며 신규 모델에 합산하지 않는다.
