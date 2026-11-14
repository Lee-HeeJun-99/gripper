# NEXT 03 — 안정성

기준 60f41cf; 개발 코드 커밋 `96174a2ec8c1b75c2f11f607bdecb1d986b148f2`. 실행 중 dirty 상태는 개별 JSON에 그대로 기록했다.
원본/골든 보존, push 없음. 증거: `reports/next_evidence/`; raw/명령/전체 로그: `results/next_phase/`.


**PASS(부분)**: 기존 자동화 20개와 guard 11개 재실행, 새로운 JSON/실험 계약/무효 인자 검사,
30초 simulated-time SOFA 및 12개 .05초 독립 실행의 자식 reap/FD 균형/해시 검사.
짧은 실행은 모두 not_converged이며 유효 강성값이 없다. 실제 wall time 70.970 s.
원시 stability.json의 passed=true는 명시된 프로세스/FD/상한 6개 검사만 뜻한다. **메모리 plateau PASS가 아니다**.

**FAIL: 장시간 RSS plateau / 무한 연속 실행 준비 상태**.
장시간 child RSS 92992→301484 KiB,
peak 301484 KiB, FD peak 5. 후반 RSS range 103672 KiB.
FD leak은 보이지 않았지만 단계에 따라 RSS가 증가해 시간을 무한 연장하지 않았다.

| control / 60000 steps | RSS growth KiB | completed |
| --- | --- | --- |
| engine_free | 211896 | True |
| engine_coupled | 234608 | True |
| writer_no_residual | 219308 | True |
| writer_residual | 228856 | True |


별도 headless driver에서도 clear_timer=0/1000의 증가량은 각각
188416/188668 KiB였다.
따라서 BatchGUI/타이머/신규 전단/관측기 하나의 원인으로 단정하지 않는다.
빈 animation scene은 증가 0, 질량+implicit 및 beam+explicit 기계 장면에서도 증가했다.
첫 explicit 대조는 RequiredPlugin 순서 오류로 FAIL(exit0에도 ERROR); 플러그인을 앞에 배치한 새 실험에서 실행 성공했다.
allocator가 보유한 high-water 메모리인지 누수인지, 정확한 할당 stack은 **미확인**이다. valgrind/heaptrack 없음.
배포 엔진 수정이나 임의 물리 변경으로 숨기지 않았다. native driver의 k100 3초 처짐 회귀는 PASS지만 RSS 문제는 해결하지 못했다.

상한: child 주소 공간 4 GiB, soak RSS 512 MiB/FD256/output512 MiB watchdog,
wall120 s, 반복12회, 총 반복 wall240 s 제한. 신규 연구 runner 최대120000 steps/60초 simulation/41 nodes.
무제한 실행/실패 성능 보상 없음. ASan/UBSan은 신규 컴포넌트 단위 범위 PASS(detect_leaks=0),
전체 SOFA instrumentation **NOT RUN**, LSan의 기존 ptrace 장애 **BLOCKED**. 수 시간 soak **NOT RUN**.
