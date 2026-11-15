# 현재 GRASP 상태

브랜치 development/regrip-validated-grasp. 전체 목표 **미완료/EXPERIMENTAL**.
최종코드/문서커밋은 `git log -5 --oneline`, 증거기준은 GRASP_EVIDENCE_MANIFEST.json.

완료된 하위검증: elastic stick/slip unit/API/SOFA,구형 동일조건6방향hold 및24s해제·핑거복원,
8층quarterdt,Optuna24COMPLETE,원본Python/600golden,별도SDK MappingGraph 최소메모리시험,
67Python tests/clean release/ASan·UBSan·LSan unit/실제2401frame 재생.

실패/차단: 공간접촉수렴FAIL(최종q증가8.474%),pointwrench rank5,전체에너지BLOCKED,
파지목적최적화BLOCKED. native3D표면은 일시반력만 관측/EXPERIMENTAL.
원통·박스 전체6방향/토크/실물물성/수시간fullengine메모리/GUI실행NOTRUN.

기존45gate/골든원본 변경없음,1243개 이전증거 hash일치. 원격push없음.
모든 새데이터/가상환경/소스build는 외장디스크ROOT아래. boundedchild유지,기본설치SOFA교체없음.
다음 우선순위는GRASP_NEXT_TASKS.md. 같은출력명 재사용시 원자적거부가 정상이다.
