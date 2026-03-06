#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts"


def run(cmd: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        env={**os.environ, **(env or {})},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def fail(message: str, *, output: str | None = None, code: int = 1) -> None:
    print(f"FAIL: {message}")
    if output:
        print(output.rstrip())
    raise SystemExit(code)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON: {path}", output=str(exc))
    return {}


def require_file(path: Path, description: str) -> None:
    if not path.exists():
        fail(f"Missing {description}: {path}")


def demo_mode() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    report_path = ARTIFACTS_DIR / "db2_guardrails.json"
    guard = run([sys.executable, "tools/db2_guardrails.py", "--format", "json", "--out", str(report_path)])
    if guard.returncode != 0:
        fail("DB2 guardrails failed (demo mode must be offline).", output=guard.stdout)

    report = load_json(report_path)
    if report.get("summary", {}).get("errors", 0) != 0:
        fail("DB2 guardrails reported errors.", output=json.dumps(report.get("findings", []), indent=2))

    demo = run([sys.executable, "pipelines/pipeline_demo.py"])
    if demo.returncode != 0:
        fail("Offline demo pipeline failed.", output=demo.stdout)

    out_path = REPO_ROOT / "data" / "processed" / "events_jsonl" / "events.jsonl"
    require_file(out_path, "offline demo output")
    if out_path.stat().st_size == 0:
        fail("Offline demo output is empty.", output=str(out_path))

    for required in ["NOTICE.md", "COMMERCIAL_LICENSE.md", "GOVERNANCE.md"]:
        require_file(REPO_ROOT / required, required)

    license_text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8", errors="replace")
    if "it.freddy.alvarez@gmail.com" not in license_text:
        fail("LICENSE must include the commercial licensing contact email.")

    print("OK: demo-mode tests passed (offline).")


def production_mode() -> None:
    if os.environ.get("PRODUCTION_TESTS_CONFIRM") != "1":
        fail(
            "Production-mode tests require an explicit opt-in.",
            output=(
                "Set `PRODUCTION_TESTS_CONFIRM=1` and rerun:\n"
                "  TEST_MODE=production PRODUCTION_TESTS_CONFIRM=1 python3 tests/run_tests.py\n"
            ),
            code=2,
        )

    ran_external_integration = False

    # Option A: Run a real DB2 client ping if configured
    dsn = os.environ.get("DB2_TEST_DSN", "").strip()
    if dsn:
        clp = shutil.which("db2")
        if clp is None:
            fail(
                "DB2_TEST_DSN is set but the DB2 CLP (`db2`) is missing.",
                output="Install a DB2 client and rerun production mode, or unset DB2_TEST_DSN.",
                code=2,
            )
        ran_external_integration = True

        connect = run([clp, "connect", "to", dsn])
        if connect.returncode != 0:
            fail(
                "DB2 connect failed.",
                output=(
                    "Verify DB2_TEST_DSN is correct and credentials/network access are available.\n\n"
                    + connect.stdout
                ),
            )

        ping = run([clp, "connect", "reset"])
        if ping.returncode != 0:
            fail("DB2 connect reset failed.", output=ping.stdout)

    # Option B: Terraform validate (real external dependency)
    if os.environ.get("TERRAFORM_VALIDATE") == "1":
        tf = shutil.which("terraform")
        if tf is None:
            fail(
                "TERRAFORM_VALIDATE=1 requires terraform.",
                output="Install Terraform and rerun production mode, or unset TERRAFORM_VALIDATE.",
                code=2,
            )
        ran_external_integration = True
        example_dir = REPO_ROOT / "infra" / "examples" / "dev"
        init = run([tf, "init", "-backend=false"], cwd=example_dir)
        if init.returncode != 0:
            fail("terraform init failed.", output=init.stdout, code=2)
        validate = run([tf, "validate"], cwd=example_dir)
        if validate.returncode != 0:
            fail("terraform validate failed.", output=validate.stdout)

    if not ran_external_integration:
        fail(
            "No external integration checks were executed in production mode.",
            output=(
                "Enable at least one real integration:\n"
                "- Set `DB2_TEST_DSN` to run a DB2 client connectivity check (requires the `db2` CLI), or\n"
                "- Set `TERRAFORM_VALIDATE=1` to run Terraform validate.\n\n"
                "Then rerun:\n"
                "  TEST_MODE=production PRODUCTION_TESTS_CONFIRM=1 python3 tests/run_tests.py\n"
            ),
            code=2,
        )

    print("OK: production-mode tests passed (integrations executed).")


def main() -> None:
    mode = os.environ.get("TEST_MODE", "demo").strip().lower()
    if mode not in {"demo", "production"}:
        fail("Invalid TEST_MODE. Expected 'demo' or 'production'.", code=2)

    if mode == "demo":
        demo_mode()
        return

    production_mode()


if __name__ == "__main__":
    main()

