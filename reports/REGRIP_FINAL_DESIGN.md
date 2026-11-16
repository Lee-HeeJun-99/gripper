# 최종 설계 판정 — 선정 보류(EXPERIMENTAL)

## 2026-11-16 실제 구현 갱신 — 선정 보류 유지

단일 핑거 Film+flexible Rails+실제 경로 Tendon 힘 전달과 복원은 SOFA에서
구현했다. 이는 50 mm 본체의 3핑거 조립/파지 검증이 아니다. 동등 코어 체적
직사각형 쿠폰은 tapered 후보와 구분한다. 시간·자가 충돌·물체 접촉·강도 Gate가
남아 최종 설계를 확정하지 않는다. 작은 장력 복원 결과를 실제 지급 액추에이터
성능이나 PET 물성 검증으로 주장하지 않는다. 상세 FILM_CONTACT_DYNAMICS_20261116.md.

## Current qualification update — final design still deferred

Actual SOFA film Newton defects were corrected and coupon endpoint balance
recovered. Full dynamic convergence, coupled Film+Rails force transfer, wire
wrapping and free-object tests are not qualified. Therefore the provisional
common-wire/cartridge candidate remains a fabrication candidate, not a proven
winning gripper. Neither new solver implementation nor endpoint force balance
changes unknown actuator/material/rule constraints or proves a five-day build.

## 5일 제작용 잠정 기본 후보 — 성능 최종 선정 아님

공통와이어 equalizer+교체 Skin/edge backing카트리지+탄성복원으로 기능을
단순화한 기본안을 우선 제작 검토한다. equal_volume_v2도면은0.05mm Skin,
0.10mm×2.07233mm backing두개로439.33979mm³ core를맞췄다. 공급재료/구동부/
규정/팀역량확인 전 제작 확정은 BLOCKED다. 목표 본체R50mm는계속설계제약이다.
선택적 근위 기계압착은옵션,3구간진공은 기본기능성공후연구안으로둔다.
동일체적 쿠폰의 넓은 접촉 가설은 실제 SOFA에서 일부 관측했지만 전체공간/
동역학/파지 Gate실패가남아 최종성능우위/Optuna최적후보를선정하지않았다.

[동일체적 단면](../designs/film_contact/equal_volume_v2/section.svg),
[실제 SOFA 쿠폰 상태](../designs/visualizations/film_actual_v1/actual_coupon.png),
REGRIP_COMPETITION_TECHNICAL_BASIS.md 및 별도 APPLICATION_DRAFT.md 참조.
지원서의 성능숫자는목표이며실제파지달성실적으로사용하지않는다.

최종 제작 설계나 최적 설계는 아직 선정하지 않았다. baseline을 최종안으로
확정하지 않고,Concept v2의 **tapered film cartridge + 선택 재밍 sleeve**를
후속 비교 후보로 유지한다. 넓은면적은장점가설,5.74배재료량/밀봉/배관/
얇은필름주름/마모는명백한위험이다. 성능 우위는 입증되지 않았다.

구현한 것은 재현가능한 기하 생성,실제 OBJ/XML/SVG/PNG,메시검사와SOFA
로딩,독립EB순응도선별이다. 실제Shell파지·접촉압·자유6DOF유지·복원은
NOT RUN. 공통 마찰시간 Gate와에너지 미완료로 최종 파지Optuna는 BLOCKED.

선정전 요구:동일재료량/힘조건에서Baseline,film,selective의Shell/Contact
수렴 비교;압력회로의실제봉합/진공누설/층간마찰시험;Sphere/Cylinder/Box
힘·토크12방향과해제복원;에너지계측. 제작용PET/TPU물성·두께·마찰·와이어
가이드손실·고정강성은모두미측정이다.

도면:

- [3D 기하 투영 PNG](../designs/visualizations/concept_v2/assembly.png)
- [정면·측면·평면·등각 SVG](../designs/visualizations/concept_v2/assembly_views.svg)
- [단면·와이어·3구간 회로 SVG](../designs/visualizations/concept_v2/mechanism_section.svg)
- [기구학적 접근·첫접촉·해제 순서](../designs/visualizations/concept_v2/sequence.svg)

그림은Concept Design/Implemented Mesh Geometry이며Actual SOFA Result
형태의변형그림이아니다.처방곡률을실제시뮬레이션성공처럼표시하지않는다.

재현(기존버전덮어쓰기금지):

```
PY=/home/ubuntu/miniconda3/envs/robot_ws/bin/python
$PY tools/design_regrip.py --tag UNIQUE
$PY tools/design_validate.py --version UNIQUE --tag UNIQUE
$PY tools/design_render.py --version UNIQUE
$PY tools/moving_sphere_run.py --tag UNIQUE
```
