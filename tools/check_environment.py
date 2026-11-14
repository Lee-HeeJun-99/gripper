"""Read-only SOFA environment checks. No ReGrip physics validation is implied."""
import csv
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOFA = Path(os.environ.get("SOFA_ROOT", "/home/ubuntu/SOFA/v26.06.00"))


def main():
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    out = ROOT / "results" / stamp
    out.mkdir(parents=True)
    exe = str(SOFA / "bin/runSofa-26.06.00")
    batch = [exe, "--noautoload", "--tmp", "-g", "batch", "-a", "-n", "2", "--hideProgressBar"]
    checks = [
        ("cmake", ["cmake", "--version"], None),
        ("gcc", ["gcc", "--version"], None),
        ("gxx", ["g++", "--version"], None),
        ("python", [sys.executable, "--version"], None),
        ("sofa_dependencies", ["ldd", exe], None),
        ("python_plugin_dependencies", ["ldd", str(SOFA / "plugins/SofaPython3/lib/libSofaPython3.so")], None),
        ("xml_batch", batch + [str(ROOT / "scenes/environment_smoke.scn")], "2 iterations done"),
        ("python_batch", batch + ["-l", "SofaPython3", str(ROOT / "scenes/python_smoke.py")], "REGRIP_PYTHON_SMOKE"),
    ]
    rows = []
    for name, command, marker in checks:
        try:
            run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 text=True, timeout=30)
            log, code = run.stdout, run.returncode
            failed = code != 0 or bool(re.search(r"\[ERROR\]|not found|Traceback", log))
            if marker:
                failed = failed or marker not in log or "2 iterations done" not in log
            status = "FAIL" if failed else "PASS"
        except subprocess.TimeoutExpired as exc:
            raw = exc.stdout or b""
            log = raw.decode(errors="replace") if isinstance(raw, bytes) else raw
            code, status = None, "TIMEOUT"
        except OSError as exc:
            log, code, status = str(exc), None, "FAIL"
        (out / (name + ".log")).write_text(log)
        (out / (name + ".command.json")).write_text(json.dumps(command, indent=2))
        rows.append(dict(check=name, status=status, exit_code=code, log=name + ".log"))
        print(name, status, "exit_code=", code)
    for name, path in [
        ("forcefield_header", SOFA / "include/Sofa.Core/sofa/core/behavior/ForceField.h"),
        ("core_cmake_config", SOFA / "lib/cmake/Sofa.Core/Sofa.CoreConfig.cmake"),
    ]:
        rows.append(dict(check=name, status="PASS" if path.is_file() else "FAIL", exit_code="", log=str(path)))
    with (out / "environment.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["check", "status", "exit_code", "log"])
        writer.writeheader()
        writer.writerows(rows)
    print("Evidence:", out)
    return int(any(row["status"] != "PASS" for row in rows))


if __name__ == "__main__":
    sys.exit(main())
