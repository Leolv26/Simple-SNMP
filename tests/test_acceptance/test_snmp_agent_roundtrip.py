import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, Tuple

import pytest

from snmp_monitor.gui.app import MainWindow
from snmp_monitor.gui.workers.agent_worker import AgentWorker
from snmp_monitor.nms.client import SNMPClient
from snmp_monitor.nms import oids

GUI_BULK_BASE_OID = (1, 3, 6, 1, 4, 1, 2021, 4)


def _pick_free_port() -> int:
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _write_agent_config(config_dir: Path, port: int) -> None:
    (config_dir / "config.yaml").write_text(
        "\n".join(
            [
                "snmp_agent:",
                '  host: "127.0.0.1"',
                f"  port: {port}",
                '  community: "public"',
                "",
                "nms:",
                '  agent_host: "127.0.0.1"',
                f"  agent_port: {port}",
                "  trap_port: 11162",
                "",
                "thresholds:",
                "  cpu: 1000",
                "  memory: 1000",
                "  disk: 1000",
                "  check_interval: 3600",
                "  cooldown: 3600",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _start_agent_process(config_dir: Path) -> tuple[subprocess.Popen, Path]:
    log_path = config_dir / "agent.log"
    with log_path.open("w", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            [sys.executable, "-m", "snmp_monitor.agent"],
            cwd=config_dir,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            text=True,
        )
    return process, log_path


def _stop_process(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _wait_until_get_succeeds(client: SNMPClient, oid: Tuple[int, ...], *, timeout_seconds: float, log_path: Path):
    deadline = time.monotonic() + timeout_seconds
    last_error = None

    while time.monotonic() < deadline:
        try:
            result = client.get(oid)
            if result is not None:
                return result
        except Exception as exc:  # pragma: no cover - failure path only
            last_error = exc

        time.sleep(0.2)

    log_output = log_path.read_text(encoding="utf-8") if log_path.exists() else "<missing log>"
    pytest.fail(
        f"Agent did not answer GET for {oid} within {timeout_seconds}s. "
        f"Last error: {last_error!r}\nAgent log:\n{log_output}"
    )


@pytest.fixture
def live_agent(tmp_path: Path):
    port = _pick_free_port()
    _write_agent_config(tmp_path, port)
    process, log_path = _start_agent_process(tmp_path)

    try:
        yield port, log_path, process
    finally:
        _stop_process(process)


def test_agent_worker_launches_package_entrypoint(monkeypatch):
    launched = {}

    class DummyProcess:
        pid = 4321

    def fake_popen(cmd, **kwargs):
        launched["cmd"] = cmd
        launched["kwargs"] = kwargs
        return DummyProcess()

    monkeypatch.setattr(subprocess, "Popen", fake_popen)

    worker = AgentWorker()
    assert worker.start_agent() is True
    assert launched["cmd"] == [sys.executable, "-m", "snmp_monitor.agent"]


def test_live_agent_responds_to_sysname_get(live_agent):
    port, log_path, _process = live_agent
    client = SNMPClient("127.0.0.1", port=port, community="public", timeout=1, retries=0)

    oid, value = _wait_until_get_succeeds(
        client,
        oids.SNMP_SYSTEM_NAME,
        timeout_seconds=10,
        log_path=log_path,
    )

    assert oid == oids.SNMP_SYSTEM_NAME
    assert isinstance(value, str)
    assert value.strip() != ""


def test_live_agent_bulk_query_returns_gui_metrics(live_agent):
    port, log_path, _process = live_agent
    client = SNMPClient("127.0.0.1", port=port, community="public", timeout=1, retries=0)

    _wait_until_get_succeeds(
        client,
        oids.SNMP_SYSTEM_NAME,
        timeout_seconds=10,
        log_path=log_path,
    )

    results = client.get_bulk(GUI_BULK_BASE_OID, max_repetitions=10)
    data = {oid: value for oid, value in results}

    assert MainWindow.CPU_OID in data
    assert MainWindow.MEMORY_OID in data
    assert float(data[MainWindow.CPU_OID]) >= 0.0
    assert float(data[MainWindow.MEMORY_OID]) >= 0.0


def test_gui_worker_start_agent_then_snmp_worker_poll_succeeds(tmp_path: Path, monkeypatch):
    port = _pick_free_port()
    _write_agent_config(tmp_path, port)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).resolve().parents[2]))

    agent_worker = AgentWorker()
    assert agent_worker.start_agent() is True

    try:
        client = SNMPClient("127.0.0.1", port=port, community="public", timeout=1, retries=0)
        _wait_until_get_succeeds(
            client,
            oids.SNMP_SYSTEM_NAME,
            timeout_seconds=10,
            log_path=tmp_path / "agent.log",
        )

        from snmp_monitor.gui.workers.snmp_worker import SNMPWorker

        snmp_worker = SNMPWorker("127.0.0.1", port=port, timeout=1, retries=0)
        data = snmp_worker._poll()

        assert MainWindow.CPU_OID in data
        assert MainWindow.MEMORY_OID in data
    finally:
        agent_worker.stop_agent()
