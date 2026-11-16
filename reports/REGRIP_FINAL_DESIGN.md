# 최종 설계 판정 — 선정 보류(EXPERIMENTAL)

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
