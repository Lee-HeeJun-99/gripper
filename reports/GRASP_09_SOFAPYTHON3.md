# GRASP 09 — SofaPython3 복구

**PASS:** 실제 ABI3.12 runtime 로딩/초기화/적분/CSV/원본 장면·XML 비교.
시스템 Python/설치SOFA 변경,가짜ABI symlink 없음.

실제 libSofaPython3.so가 요구하는libpython3.12.so.1.0을 확인하고
conda-forge의 CPython3.12.16/NumPy2.5.4를 `.runtime/python312`에 격리 설치했다.
native constraint observer용 SciPy1.18.1도 같은격리환경. 기존robot_ws3.10.20은 그대로다.
`python_recovery/ldd.log`,environment.json,dependencies/python312/command.log에 실제명령/해석결과가 있다.
PYTHONHOME/PYTHONPATH/LD_LIBRARY_PATH는 각child에만 적용하며 전역환경을 덮어쓰지 않는다.

인수인계*.py를 새 raw디렉터리에 byte-identical 복사한 뒤 실행했다.
원본 recorder가내는CSV를복사본옆에저장하여 원본소스/골든을오염시키지않는다.
V109FREE,V110FREE,V110SHEAR(k=.1)각600step/.3s,ERROR없음/600CSV/실제상태변화 확인 PASS.
V110은WindowsDLL아닌기존검증된Linux ForceField를load했다. WindowsDLL실행검증이라는표현은하지않는다.

V109 600시점 time/deflection/vz/XYZrelative 전체 기존tol`1e-10+1e-6|golden|` PASS.
최종처짐.04121379160634628mm,vz−.014380704053554549mm/s,Xslip.0008228072034270895mm.
maxerror tip1.38778e-16,vz1.41553e-14,Xslip0.
이 .3s transient는 정적평형성능이 아니며 허용오차를유지했다.

추가 `python_xml_compare`는각원본과새XML/C++adapter를실제재실행해600시점비교:
V109 time/tip/vz/XYZrelative, V110FREE/SHEAR time/tip/vz 모두PASS,
time최대차2.220446e-16,그외검사값0차이.
V110SHEAR 최종tip.03786004758819707mm. V110원본record의slip은linear quaternion proxy이므로
정확한 mapped-interface slip과동일수치로비교하지않았다(모델차이 아닌관측정의차이).
XML실행기상태not_converged는.3s가평형미도달이라는올바른판정으로그대로남겼다.

smoke로딩만PASS인것과원본수치회귀PASS를구분했다. 실제GUI와Python프로세스수시간안정성은NOTRUN.
재실행은기존raw보존을위해새 `REGRIP_GRASP_OUT` 경로를지정한후
`tools/grasp_python_recovery.py`를사용한다. 비교는기존recovery데이터필요.
