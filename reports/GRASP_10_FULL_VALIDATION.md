# GRASP 10 — 통합 검증 범위

전체개발 **EXPERIMENTAL / 미완료**. 실행성공,단위수학,모델물리,파지인증을분리한다.

|검사|이번실행결과|범위/증거|
|---|---|---|
|Clean C++ release build|PASS,warning0|final_checks/0,1,2|
|신규 stick18DOF/API/FD/객관성|PASS|maxJ1.09235e-10,moment2.71051e-20|
|ASan/UBSan/LSan|PASS|우리unit source만;sanitizer|
|Python67tests|PASS|python_tests_isolated/tests.log|
|기존C++5개실행|PASS|legacy_units_v2;원래부정API expectedERROR정확검사|
|기존45physicsgate|승계PASS|이전manifest1243hash일치,신규모델인증아님|
|patched SDK600FREE×2|PASS|sdk_regression_v2|
|원본Python600FREE/전단|PASS|python_recovery,python_xml_compare|
|8층dt/half/quarter|PASS|strictresidual<1e-3,independentforce sum차0|
|6방향boundedhold/24s복원|PASS(연구하위gate)|최종인증은EXPERIMENTAL|
|접촉mesh/q|FAIL|41/16→41/32변위8.474%차이|
|완전6DOFwrenchclosure|NOT RUN / 구조적rank5한계|gate.json|
|구/원통/박스전체시퀀스|sphere일부PASS;나머지NOTRUN|다른형상+Xhold만실행|
|전체에너지|BLOCKED|Beam후보E의일반potential실패|
|MappingGraph최소엔진|PASS|240000step/unload,reload;기본설치엔진미수정|
|수시간/fullengine메모리|NOT RUN|boundedchild유지|
|실제Optuna|PASS|27attempt,24COMPLETE,3PRUNED|
|파지목적최적화|BLOCKED|실패모델성능보상없음|
|실제상태headless재생|PASS|2401frames;실제GUI NOTRUN|
|실물성능|NOT RUN|실물측정0|

최초 Python discover는기존fixture출력디렉터리와충돌하여1failure/20errors였다.
기존테스트/골든을수정하지않고새namespace+올바른기존buildroot로67개전부통과했다.
최초unit일괄분류기는의도적인invalidAPI ERROR까지일반장면오류로처리해2개FAIL이었다.
원래단위소스의정확한expectedERROR목록과exit0/PASS를함께검사해재실행했다.
실제 SOFA 장면은여전히어떤ERROR도허용하지않는다. 실패전후로그모두보존.
새입력가드:float stride/shape/axis,NaN,invaliddt/mesh,unsafe trial path,wall>480s거부;
변경후실제contract_repeat는v4fast_repeat와이동량bit동일.
artifact손상주입검출은classifierfixture이며물리실행성능으로계산하지않는다.

## 실행 및 출처

외장디스크ROOT에서robot_ws Python3.10 사용. 아래는기존결과를읽는안전한검증:

```bash
PYTHONPATH=.:tools python tools/grasp_verify_evidence.py --raw
PYTHONPATH=.:tools python tools/stabilization_verify_evidence.py --raw
build/grasp_20261115/release_final/test_grasp_stick
```

새실험은 `REGRIP_GRASP_OUT`의새경로를사용한다. 각실험의command/config/scene/stdout/stderr/metrics와
source/binary/dirty/commit/artifactsha를저장했다. Failedraw도manifest포함.
v1source6b838c5,v2source9395845,v4source3f0b735와후속ad639e0계열소스가공존하므로
하나의바이너리실험처럼혼합하지않는다. v4최적화등가성은참조AD2/FD/실제repeat로검사했다.
핵심기존plugin/models/handoversrc는변경하지않았다. 새래퍼는build-local generated registration용이다.
보고서의JSON/CSV는실측SOFA또는명시된독립FEM/수학검사의projection이며하드코딩성공값으로물리실행을대체하지않는다.
