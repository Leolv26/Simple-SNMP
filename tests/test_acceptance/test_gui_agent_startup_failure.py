import subprocess
from pathlib import Path

from snmp_monitor.gui.workers.agent_worker import AgentWorker


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


class AliveButNoSnmpProcess:
    pid = 4321

    def __init__(self):
        self.terminated = False
        self.killed = False

    def wait(self, timeout=None):
        if self.terminated or self.killed:
            return 0
        raise subprocess.TimeoutExpired(["python", "-m", "snmp_monitor.agent"], timeout)

    def poll(self):
        return 0 if self.terminated or self.killed else None

    def terminate(self):
        self.terminated = True

    def kill(self):
        self.killed = True


def test_agent_worker_does_not_report_started_until_snmp_bulk_is_ready(tmp_path: Path, monkeypatch):
    _write_agent_config(tmp_path, 39999)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).resolve().parents[2]))
    monkeypatch.setattr(AgentWorker, "STARTUP_TIMEOUT_SECONDS", 0.2, raising=False)
    monkeypatch.setattr(AgentWorker, "STARTUP_POLL_INTERVAL_SECONDS", 0.01, raising=False)

    fake_process = AliveButNoSnmpProcess()
    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: fake_process)

    worker = AgentWorker()

    assert worker.start_agent() is False
    assert worker.is_running() is False
    assert fake_process.terminated is True


def test_agent_worker_uses_discovered_config_directory_as_agent_cwd(tmp_path: Path, monkeypatch):
    import snmp_monitor.gui.workers.agent_worker as agent_worker_module

    config_dir = tmp_path / "project"
    launch_dir = tmp_path / "launcher"
    config_dir.mkdir()
    launch_dir.mkdir()

    port = 39998
    _write_agent_config(config_dir, port)
    monkeypatch.chdir(launch_dir)
    monkeypatch.setenv("PYTHONPATH", str(Path(__file__).resolve().parents[2]))

    config = {
        "snmp_agent": {"host": "127.0.0.1", "port": port, "community": "public"},
        "nms": {"agent_host": "127.0.0.1", "agent_port": port, "trap_port": 11162},
        "thresholds": {"cpu": 1000, "memory": 1000, "disk": 1000, "check_interval": 3600, "cooldown": 3600},
    }
    monkeypatch.setattr(agent_worker_module, "load_config", lambda: config)
    monkeypatch.setattr(
        agent_worker_module,
        "find_config_file",
        lambda config_path=None: config_dir / "config.yaml",
        raising=False,
    )

    worker = AgentWorker()
    try:
        assert worker.start_agent() is True
        assert worker.is_running() is True
    finally:
        worker.stop_agent()
