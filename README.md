# gripper

# ReGrip — Ubuntu SOFA 개발 및 검증

다음 단계 개발: [FINAL_DEVELOPMENT_REPORT.md](reports/FINAL_DEVELOPMENT_REPORT.md),
[현재 상태](reports/CURRENT_STATUS.md), [재개 명령](reports/NEXT_TASKS.md).
기존 검증 모델은 보존하고 별도 3D 접선 컴포넌트·100 mm 연구 장면·다층 정적 FEM을 추가했다.
100 mm SOFA 수치 수렴은 확인했지만 실물 PET/와이어/접촉/진공 성능 인증은 아니다.
Optuna와 SofaPython3는 여전히 의존성 차단이며, 새 장시간 검사에서 RSS 증가가 발견돼 무제한 실행은 보류한다.
신규 통합 JSON 실행: `experiments/run.py`; 모든 신규 출력은 독립 폴더에 기록한다.

최신 독립 재검증: [최종 통합 보고서](reports/FINAL_VERIFICATION_REPORT.md).
회전 좌표 미분·무효 입력·중단/출력 무결성·C++ 소스와 바이너리 결합 검사를 보강했다.
새로 실행한 45개 물리 gate, 20개 자동화 검사 및 11개 최적화 guard는 통과했다.
Optuna 실제 3/24-trial 탐색과 SofaPython3 원본 실행은 의존성 차단 상태다.
아래 기존 결과 설명과 VALIDATION.md는 첫 검증의 이력이며 최신 수치는 통합 보고서를 따른다.

SOFA v26.06.00에서 V1.0.9 FREE의 동일 물리 XML 이식본과 C++ 전단 ForceField를 실행했다.
Windows 600개 시점 회귀 및 45개 물리·수치 검증을 통과했다.
**Optuna 최적화는 의존성 부재로 미실행이며 최적값은 없다.**

## 실행

```bash
cd /home/ubuntu/LHJ/ReGrip
export REGRIP_BUILD_ROOT="$PWD/build/revalidation_new"
/usr/bin/python3 tools/build.py --build-root "$REGRIP_BUILD_ROOT" --logs results/revalidation_new/build
/usr/bin/python3 tools/baseline_regression.py results/baseline_new
/usr/bin/python3 tools/run_trial.py results/custom_k1 --k 1 --duration 3
```

현재 분석용 NumPy/Matplotlib는 기존 환경에 있다. SOFA에 Python을 내장하지 않고,
이 Python이 별도 프로세스로 네이티브 SOFA를 실행한다.

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/validate_physics.py --out results/revalidation_new/physics
MPLCONFIGDIR=/tmp/regrip-matplotlib /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/make_plots.py --results results/revalidation_new/physics --out reports/figures_new
/usr/bin/python3 tools/summarize_candidate.py --results results/revalidation_new/physics --out reports/candidate_new.json
```

새 검증은 `--out`으로 새 결과 디렉터리를 지정한다. 같은 셸에서 REGRIP_BUILD_ROOT를 유지한다.
실행기는 build_manifest.json으로 C++ 소스와 실제 바이너리가 일치하는지 먼저 검사한다.
기존 실행은 `--resume --out <경로>`로 artifact/설정/바이너리 해시를 확인하고 재사용할 수 있지만,
이번 전체 재검증은 과거 성공 결과를 재사용하지 않고 새로 실행했다.
개별 trial은 기존 출력 폴더를 덮어쓰지 않으므로 새 경로를 지정한다.
독립 CMake 프로젝트는 `diagnostics/CMakeLists.txt`, `plugin/CMakeLists.txt`이며
`build.py`가 두 프로젝트를 configure/build/test하고 로그를 보존한다.
현재 빌드는 Unix Makefiles를 사용하므로 Ninja 설치가 필요 없다.
다른 SOFA 설치는 `SOFA_ROOT`로 지정하되, ABI 및 회귀·물리 검증을 다시 수행해야 한다.

## 결과와 범위

- 0.3초 FREE 처짐: 0.04121379160634628 mm, X 미끄럼: 0.0008228072034270895 mm.
- 3초 FREE 평형 처짐: 0.042187419375712826 mm.
- 고정 sweep 후보: k=100, 연결점 10개, x=3,6,…,30 mm.
- 후보의 평형 강성비: 1.676077, X 미끄럼: 0.00000306237049 mm.
- 원본 Python scene 직접 실행은 미완료다. SofaPython3에 필요한 Python 3.12 공유 라이브러리가 없다.
- 전단 모델은 작은 평면 회전 범위의 선형 근사다. 실제 진공 마찰, 압력, 100 mm 그리퍼 결과가 아니다.

[검증 보고서](VALIDATION.md), [환경 보고서](ENV_REPORT.md), [진행 현황](PROGRESS.md),
[실험 요약 CSV](results/physics_validation/summary.csv),
[검증 gate](results/physics_validation/gate.json),
[기준 비교 그래프](reports/baseline_comparison.png),
[평형 강성·미끄럼 그래프](reports/equilibrium_sweep.png),
[검증된 sweep 후보](reports/best_tested_candidate.json).

## 자동 실험 계약

`run_trial.py`는 조건 JSON, 실행 명령, Git revision/dirty 상태, .so 및 scene 해시,
SOFA 로그, 시계열 CSV, 지표 JSON을 실행별로 남긴다.
timeout은 프로세스 그룹을 종료하고, 프로세스 주소 공간은 4 GiB로 제한한다.
종료 코드뿐 아니라 오류 로그, 실행 횟수, 상태 크기, 시간, 유한값,
변위·속도 한계, 작은 회전 범위, 정적 잔차를 검사한다.
출력 상태는 `complete`, `not_converged`, `timeout`, `crash`, `diverged`, `invalid_physics`다.
평형 미달은 유효 강성으로 변환하지 않는다.
일부 상한 검사는 실행 후 수행되며 모든 발산을 즉시 조기 종료하는 시스템은 아니다.
raw 상태 TXT는 디스크에 보존하되 Git에서 제외했다. 현재 전체 실험 raw 파일은 약 1.2 GiB다.
회귀 CSV·실험 CSV·로그·설정과 보고서는 Git으로 관리한다.

## 최적화 재개

`tools/optimize.py`는 물리 gate와 현재 바이너리·소스 해시를 먼저 확인한다.
k, 연결점 수, 연결 위치를 탐색하고 dt는 탐색하지 않는다.
연결 위치는 현재 11노드의 3 mm 간격 격자에서 선택한다.
두 목적은 평형 강성비 최대화 및 전체 계면 최대 X 미끄럼 최소화이며,
실패·미수렴 trial은 성능값 없이 prune한다.
각 후보는 dt 절반·6초 연장, Pareto 후보는 동일 연결 위치의 21노드 메시로 검증한다.
SQLite study와 trial 파일로 재개할 수 있다. 전역 최적성을 주장하지 않는다.

현재 Optuna가 설치되지 않았다. 이 실행 환경에서 pip 설치는 배포본을 받지 못해 실패했다.
패키지 설치가 가능한 터미널에서 프로젝트 내부 의존성을 설치한 후 실행한다.

```bash
/home/ubuntu/miniconda3/envs/robot_ws/bin/python -m pip install --target .python-deps 'optuna>=3.6,<5'
PYTHONPATH="$PWD/.python-deps" /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/optimize.py --gate results/revalidation_new/physics/gate.json --out results/revalidation_new/optimization --trials 24
```

Optuna 미설치 차단 동작은 확인했다. 실제 sampler/study/trial 경로는 아직 실행 검증하지 못했다.
Python 3.12 설치를 해결하면 원본 SofaPython3 scene도 별도로 재현해야 한다.
상세 설치 장애와 원본 보존 검증은 환경·검증 보고서에 기록했다.

## GitHub 업로드 상태

원격 초기 README는 이 문서 맨 위와 `docs/origin-main-README.md`에 보존했다.
로컬 master의 기존 커밋과 캐시된 origin/main을 삭제 없이 merge했다.
시계열 CSV 25개(1 MiB 초과 22개)는 현재 트리에서 추적을 해제하고 로컬 파일은 보존했다.
기존 커밋의 CSV blob은 이력에 남는다. 이력 삭제/재작성은 수행하지 않았다.
사용자가 CSV 이력 전송을 원하지 않아 push를 보류했다.
상세 점검은 `reports/GIT_PUBLISH_AUDIT.json`, `reports/GIT_UPLOAD_STATUS.md` 참조.

## 2026-11-15 통합 연구 개발

이전 업로드 상태와 위 검증 기록은 과거 기록이다. 이번 작업은 원격 push 없이
`development/regrip-integrated-system`에서 진행했다.
신규 연구 컴포넌트는 [models/integrated](models/integrated/README.md)에 분리했다.
실제 SOFA 100mm 다층·케이블·압력 slider·고정 물체 접촉 및 결정론적 Pareto 후보 검증을 수행했다.
8층 수렴과 자유 물체 파지는 FAIL, Optuna/SofaPython3는 BLOCKED이며 실물 인증은 아니다.
[통합 보고서](reports/INTEGRATED_FINAL_REPORT.md),
[재개/재현 명령](reports/INTEGRATED_NEXT_TASKS.md),
[증거 manifest](reports/INTEGRATED_EVIDENCE_MANIFEST.json)를 우선 참조한다.

## 2026-11-15 GRASP 후속 실행 (현재)

이전 문단은 당시 기록이며 최신 상태는 [GRASP 보고서](reports/GRASP_FINAL_VERIFICATION_REPORT.md)와
[재개 명령](reports/GRASP_NEXT_TASKS.md)이다. 개발 브랜치는 `development/regrip-validated-grasp`,원격push없음.
elastic stick/slip,동일조건 sphere6방향 유지·24s해제/복원 하위gate,8층quarterdt,
실제 Optuna24완료,원본 SofaPython3/600golden,별도 MappingGraph 수정 최소엔진을 실제검증했다.
접촉 공간수렴 FAIL/rank5/전체에너지 BLOCKED이므로 완전6DOF파지·실물성능·파지최적화는 미완료다.
설치SOFA/시스템Python은 덮어쓰지 않았다. 새 raw/build/격리환경은 외장디스크 안에 유지한다.

```bash
PYTHONPATH=.:tools /home/ubuntu/miniconda3/envs/robot_ws/bin/python tools/grasp_verify_evidence.py --raw
```

기존45gate와 신규 파지gate는 별도다. 실험 디렉터리 재사용/기존 study 변경으로 증거를 덮지 않는다.
