# ReGrip — conservative beam and grasp verification

## 최종 판정

**최우선 Beam 문제: 독립 재현 및 신규 모델에서 해결한 범위 PASS.**
**전체100mm 파지 시스템: 미완료/EXPERIMENTAL. 파지 목적 최적화: BLOCKED.**

기존 BeamFEM의 유한변형 모멘트 결함을 단순한 관측기 좌표 오류로 치부하지 않았다.
실제 내부 힘을 독립 재현하고 누락된 기하학적 couple과 수치적으로 일치함을 확인했다.
기존 원본을 수정하지 않고 에너지에서 힘·토크·접선을 얻는 별도SO(3) Beam을 구현했다.
실제 SOFA의 동일3핑거+Tz 조건에서 전체 힘·모멘트 평형과24s해제·복원을 통과했다.
그러나 접촉 적분·마찰 이력·dt 수렴은 여전히 실패하고 통합 에너지 항이 미완료다.
따라서 이를 완전6DOF파지 또는 제작 최적 설계로 확대 해석하지 않는다.

## Git 및 증거 식별

- 시작: `b468346f3277369d92f25cd2f5d5044c29124737`.
- 브랜치: `development/regrip-conservative-beam-grasp`.
- 검증·발행 코드: `c4b0bb9c1930d96a3b58caba9fbfb4fffe33540e`.
- 최종 문서/증거 커밋은 이 보고서를 포함하는 커밋이다. 정확한 SHA:
  `git log -1 --format=%H -- reports/CONSERVATIVE_BEAM_FINAL_REPORT.md`.
- 실제 각 실험은 당시 Git/dirty/source/binary/command를 기록했다. 전 실험이
  마지막 코드 커밋에서 생성됐다고 주장하지 않는다. 핵심 compiled-source manifest는 별도다.

기존 main/검증/이전 개발 브랜치,원본 BeamFEM,기존 plugin/골든/인수인계,
이전 raw/SQLite/빌드는 보존했다. 원격push,강제push,이력재작성,설치SOFA 덮어쓰기 없음.
새 raw약3GiB는 외장디스크 내부 `results/beam_20261115`에만 저장하고 Git에서 제외했다.
소형JSON/CSV,비교PNG,명령·소스·바이너리·raw 해시를 `reports/beam_evidence` 및
`CONSERVATIVE_BEAM_EVIDENCE_MANIFEST.json`에 보존한다. 실패도 포함한다.
실제 모델 실행 목록과 자동화 고장주입/손상 fixture 목록은 별도 CSV로 분리했다.
최초 발행 초안의 혼합 분류는 최종 발행 전에 수정하고 초안도 raw하위에 보존했다.

## 환경 및 라이브러리 범위

Ubuntu22.04.5,커널6.8.0-138,GCC/G++11.4,CMake3.22.1,CondaPython3.10.20.
외장디스크1.2TiB가용,RAM31GiB중 약27GiBavailable 관측;시스템Python 변경 없음.
프로젝트 경로:
`/media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip`.

SOFA26.06 설치원본은 그대로다. matched headless SDK는 설치 git-info와 동일한
7c18e95d5c5f2839079892c69e7d89a313c79603 archive에 공식 MappingGraph weak-parent
수정을 적용한 기존 별도빌드를 재사용했다. archive는 독립 Git checkout이 아니므로
상위 ReGrip Git SHA를 SDK SHA로 오인하지 않는다. 실제 MappingGraph 소스/라이브러리
해시,ldd 및 이전 SDK 출처 증거를 검증한다.
Native collision은 설치SDK에 맞춰 Beam/Frame을 별도 재빌드한 독립 프로세스다.
matched SDK에 없는 collision라이브러리를 설치SDK에서 섞어 로딩하지 않았다.
기존 isolatedCPython3.12/SofaPython3/Optuna4.6을 재사용했고 재설치하지 않았다.

## 신규 코드와 수정 근거

`models/conservative_beam`: midpoint/reduced-integration rod energy,정확한2차AD,
SOFAForceField,독립 작은평면 정적FEM,source-controlled 장면 template.
`diagnostics/conservative_beam`: inherited couple,동적 에너지,hot/cold profiling,
동일프로세스 scene reload/heap probes.
`tests/test_conservative*`, `test_beam*`, `tests/conservative_beam`: FD/objectivity/
moment/kFactor/강성조립/cache/오류/대회전/선형극한/보상합산 및 Python계약 검사.
`tools/beam_*`: bounded 실제실행,수렴·전역반력·Native 자식Jacobian 감사,
독립 구조Optuna/후보 재검증,소형증거/해시검증,실제상태 재생.
`scenes/beam_native_surface.py`: 신규 Beam을 사용하는 독립 Native표면 연구.
README/AGENTS는 최신 재개 위치와 gate정책을 추가했으며 과거 기록은 지우지 않았다.

장면의 물리 정의를 고정한 상태로 템플릿의 과거 ignored-raw 의존성을 제거했다.
`packaging_check.json`: 검증된 Tz_v2와 새 준비 장면의 물리XML 및 config동일 PASS.
준비만 한 packaging_probe는 NOT RUN이며 새 물리실행 성공으로 계산하지 않는다.

## 실제 측정 결과

|검증|이번 결과|판정 및 범위|
|---|---|---|
|기존 Beam couple 독립6상태|예측/실측차≤1.563e-17F·mm|결함 재현 PASS;기존 모델의 해당 일관성 FAIL|
|기존 전체3핑거27960step|BeamY모멘트−2.26294389207e-5F·mm|새 실제 재현,원본 보존|
|신규61상태|energy FD1.36519e-8,J FD5.47000e-8,moment5.68434e-14|수학/API PASS|
|추가 대회전40상태|energy FD4.02278e-7,J FD5.90219e-7,moment2.27374e-13|커널 PASS,구조 전체 대변형 인증 아님|
|닫힌 경로 일64→256|3.14276e-10→1.96423e-11F·mm|0으로 수렴 PASS|
|비가환SO(3)경로32→128|−3.70616e-4→−2.31638e-5F·mm|약16배 오차감소,유한분할0이라고 주장 안 함|
|v1/v2정확 최적화100상태|E/F/J최대차 모두0|별도동등성 PASS|
|캔틸레버11/21/41node|z−.03117360244/−.03123219611/−.03124684456mm|독립 이론/메시 경향 PASS|
|100mm2·4층FREE/ON|동일 하중 정적평형|PASS,BEAM04 실제표 참조|
|8층기본 표준EulerON|잔차.00125069334|FAIL 보존|
|8층보상합산ON/halfdt/21node/18s|잔차2.92e-5/2.52e-5/3.25e-5/2.64e-5|구조 전용 PASS|
|신규3핑거+Tz|전역힘1.94189e-5,전역모멘트3.07426e-6|동일1e-3기준 PASS 하위gate|
|동일24s시험|이동4.46304e-6mm,최대각.000244127rad|국소 유지 및 해제·복원 PASS|
|24s복원|핑거2.09738e-8mm/2.94701e-10rad,접촉0|PASS 하위gate|
|41nodeq32 actualSOFA|734.780s,전역모멘트.000525316|실행/평형 PASS,전체 수렴 PASS 아님|
|q16→32 병진차|2.54613%|FAIL,1%유지|
|history half병진차|2.75738%|FAIL,1%유지|
|dt half병진차|.449947%|FAIL,.1%유지|
|21→41node q32병진차|.0506788%|한정 메시진단 PASS|
|실제 patch Wrench|rank6,cone원점내부,capped12LPfeasible|수학 PASS;12동적 인증 아님|
|Native 원래 부모J전체반력|모멘트잔차1.0|관측기 불완전 FAIL 보존|
|Native 실제 자식J물리반력12/24|전역모멘트.000311609/.000316214|수정관측 하위gate PASS|
|Native 자유DOF 매핑차|≤6.857e-19impulse|독립매핑 일치 PASS|
|Native sphere표면12→24|병진.00009684%,회전.00013792%|한단계 진단 PASS,전체Native EXPERIMENTAL|
|단일Beam 동적 에너지 dt감소|정규화 미폐합≈−4.99e-12→−5.23e-13→2.81e-14|제한된 작은하중 수지 PASS|
|전체 cable/pressure/friction 수지|필요 구동·파라미터 일 적분 미완료|BLOCKED,미구현항0처리 없음|
|matched 전체장면2×60000steps|liveheap tail−185616/−185632bytes,FD8/3고정,graph잔존0|478.276s 한정 PASS|
|새600시점골든2회|tip.04121379160634628mm,slip.0008228072034270895mm|원래오차1e-10+1e-6×abs(golden) PASS|
|Python/C++/sanitizer|78Python,신규C++/기존3+5실행,제한된ASan/UBSan/LSan|각 실행범위 PASS|

세부 기준·로그·raw 위치·config·실제 argv는 BEAM01..14와 각 실험파일에 있다.
기존45gate는 코드/바이너리/원본 증거 무결성을 확인하여 보존한 과거결과다.
이번에45개 전부 재실행했다고 하거나 신규 접촉인증에 합산하지 않았다.
골든 재검증은600시점×9공유 지표이며,전체 raw 위치/속도도 별도로 저장했다.
골든에 없는 모든 DOF/속도 성분까지 과거CSV와 비교했다고 주장하지 않는다.
원본 Python600회귀는 이전 보존 증거이고,이번 새600회귀는 matched XML 실행이다.
이번 Native/replay실행은 SofaPython3의 실제 동작도 새로 확인했다.

## Beam 이론과 수치적 의미

정식화는 BEAM02와 모델README에 있다. 에너지는γ,κ의 intrinsic-strain차로부터
축·전단·굽힘·비틀림을 모두 포함한다. 공간회전 가상일을 사용하고 대칭 에너지Hessian과
비대칭 spatial force Jacobian을 구분한다. 상대요소회전2.8rad branch제한,
low-order one-point integration과 명시적 GA가 가정이다. 일반 연속체 해의 정확한
재현이나 필름 좌굴/폭방향변형/손상/압력분포를 검증한 모델이 아니다.

Beam 단독의 큰 강체회전 객관성은 확인했지만 통합 FrameLayer 장면은 계속 작은평면
상대회전.005rad한계와명시적 가이드를 사용한다. 신규3D Beam커널과 완전3D핑거는 다르다.
기존 모멘트 결함을 제거한 것이 접촉이력 수렴 실패까지 해결했다는 뜻은 아니다.

프로파일 후 정확 AD연산/요소별 cache만 최적화하여8000step168.626→150.776s.
물리 접선이나허용오차를 근사/완화하지 않았다. 고해상도900s예외는 실제678.494s예측에
근거한 한 번의 제한적 계획이며,기본480s/4GiB/최대4children정책은 유지한다.
몇 시간 안정성,240000연속step,지속접촉 soak는 NOT RUN.
메모리 tailplateau는 해제 이후이며 모든 접촉상태의 무누수인증이 아니다.

## 실제 Optuna와 후보 실패

파지 목적 연구는 gate실패로 BLOCKED,새100mm grasp-objective trial0회다.
독립적으로 허용된100mm2층 작은평면 LINEAR FEM 구조검색은 실제 Optuna로
24COMPLETE/3PRUNED를 수행했다. 기존30mmstudy와 분리하고 dt는 탐색하지 않았다.
SQLite/재개/seed/실패·pruned의 values=None을 추가 실제 검사했다.

후보k84.1732992010,10연결점10..100mm는 독립FEM예측ratio1.68434718895,
slip1.20894798466e-7mm. 실제SOFA5조건 재검증에서ratio1.68405837281,
ONtip.00925550007117mm,slip1.20955737003e-7mm를 얻었다.
평형/반복/dt는 통과했지만21node의최대미끄럼3.55449798290e-7mm로메시검증 FAIL.
따라서 승인된 최적 파라미터는 없다. 전역최적성/실제 제작최적성을 주장하지 않는다.
연결점만의미끄럼으로목적함수를바꿔실패를숨기지않았다.

## 실패·미완료와 다음 우선순위

1. 최우선 남은 과제: moving-contact material-history 전달/return-map과
   active-boundary coupling을 독립 검증하고 q/history/dt수렴을 개선한다.
2. cable command/pressure변화/접촉·마찰·Rayleigh를 포함한 동기화 에너지 journal.
3. gate통과 후 신규 Beam sphere힘·토크12방향/실패대조군/해제재현.
   이어 cylinder/box,압력별실제파지기여도와임계하중·토크 비교.
4. Native는 별도 law/buffer/dt/Beam mesh 검사 필요. 이번 반력관측 수정은
   동역학을바꾸지않고가이드 반력을복원했으며,표면2mesh만으로전체수렴은아니다.
5. 동일물성측정/레이어두께·μ·진공압·케이블경로·체결부/압력분포를 확보해야
   실제PET및제작성능을논할수있다. 연구배치반지름≈95.15mm는50mm목표미충족.
6. 수렴된설계공간에서만 새100mm파지Optuna/후보독립검증. 현재BLOCKED유지.

초기observer initERROR,3s미평형,기본8층FAIL,LSan ptrace실패,큰회전테스트
첫컴파일오류,Native NumPy serialization/자식sparse-padding오류는 보존했다.
수정후통과한범위와원래실패를분리했고같은실패조건을무한재시도하지않았다.
이번 유한한 실행 campaign은핵심 Beam 개발과제 및 위 독립검증을 마쳤지만
후속 접촉/통합에너지 연구까지 완료한 것이 아니다. 미완료를 성공으로 기록하지 않는다.

## 재현 및 증거 검사

전체 명령은 `CONSERVATIVE_BEAM_NEXT_TASKS.md`에 있으며 핵심은:

```bash
cd /media/ubuntu/99419895-2058-45b4-b746-b36ea7112e4e/research/LHJ/ReGrip
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/beam_verify_evidence.py --raw
cmake -S models/conservative_beam -B build/beam_local \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH="$PWD/.runtime/closure_sdk"
cmake --build build/beam_local -j2
ctest --test-dir build/beam_local --output-on-failure
export REGRIP_BEAM_OUT="$PWD/results/beam_resume_conservative_01"
$PY tools/beam_trial.py tip --duration 12
$PY tools/beam_grasp_trial.py Tz_v2 --duration 24
```

기존 출력 이름을 재사용하지 않는다. 준비만 한 장면은 물리 실행으로 계산하지 않는다.
빌드에 필요한 Git dense-reference commit4d19774도 함께 보존했다.
실물 측정0건. 모든 수치는 실제SOFA/독립FEM/수학검증/가정된 파라미터 연구 중 하나이며
실물 성능 인증이 아니다. 사진이나 가상 애니메이션을 성공 근거로 사용하지 않았다.
