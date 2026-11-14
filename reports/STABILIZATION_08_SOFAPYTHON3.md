# SofaPython3

**BLOCKED.** ldd에서 libpython3.12.so.1.0 not found. Conda offline 런타임 설치는 캐시 부재로 실패.
isolated dependency 경로를 사용했으며 system Python/가짜 ABI symlink를 변경하지 않았다.
새 Python smoke는 exit0이어도 실제 plugin/scene ERROR를 냈으므로 FAIL이다.
원본 FREE/전단 Python 비교는 NOT RUN. XML/C++ 실험은 별도로 실제 실행했다.
재개 조건: 정상 network 또는 CPython3.12 공유 런타임/stdlib 및 호환 NumPy의 offline packages.

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
