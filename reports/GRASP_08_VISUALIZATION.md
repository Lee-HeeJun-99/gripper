# GRASP 08 — 선택적 실제 상태 재생

**PASS:** SOFA headless 실제 저장상태2401frames 재생 및 commanded jam ON/OFF 표시.
**NOT RUN:** 실제 GUI 창/화면 이미지/동영상. **EXPERIMENTAL:** 파지 자체이며 시각화는 물리 인증이 아니다.

`scenes/grasp_replay.py`, `tools/grasp_visualize.py`는 hash 검증된
`final_sphere_xplus/state.txt`의 모든 실제위치/쿼터니언만 사용한다.
양쪽2층 핑거 centerlines,actual cable offset guide,구형물체 skin/fullpose를 기본 SOFA OglModel/RigidMapping으로 표시한다.
위치·자세를 만들어내거나 재생에서 다시 물리 시뮬레이션을 수행하지 않는다.
주황/파랑은 설정의 commanded pressure state이며 측정된 압력 센서값이 아니다.
접촉력 화살표/실제필름 표면은 미구현. 현재재생은 sphere용이며 다른형상에 구형skin을 적용하지 않는다.

첫10frame 재생 이후 전체frame color 업데이트의 `OglModel.color` API 오류와 중복 BaseState/Mapping 경고를
실제로그에서 발견했다. 오류exit0를FAIL로 기록하고,
material Data 사용+노드당1개 visual state/mapping으로 수정했다.
`visualization_final_v2`는2401step,ERROR/undefined 없음,frame9 및 OFF→ON→OFF marker 확인 PASS.
실제GUI는 trial마다 실행하지 않았고GUI가없어도 headless를 유지한다.

재생 재현(기존 디렉터리 덮어쓰기 방지):

```bash
PYTHONPATH=.:tools python tools/grasp_visualize.py --name visualization_review_01 --source final_sphere_xplus --all-frames
```

선택 GUI 명령은 `results/grasp_20261115/visualization_final_v2/gui_command.json`,필요환경은 environment.json.
`REGRIP_REPLAY_DATA`는 같은디렉터리 replay.json, Python312 isolated runtime/LD_LIBRARY_PATH/PYTHONPATH가 필요하다.
사용자선택GUI 실행전 권한정책을 따른다. GUI소견이 numericalgate를 대체하지 않는다.
