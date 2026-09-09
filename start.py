from __future__ import annotations

import argparse
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.resolve()


def local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return "<LAN-IP>"
    finally:
        sock.close()


def require_command(command: str) -> None:
    if shutil.which(command) is None:
        raise RuntimeError(f"Required command not found: {command}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Start TalentScreen V0.1")
    parser.add_argument("--demo", action="store_true", help="Enable foundation demo mode")
    args = parser.parse_args()
    require_command("node")
    require_command("npm")
    python = sys.executable
    os.environ["DEMO_MODE"] = "true" if args.demo else os.getenv("DEMO_MODE", "false")
    backend = subprocess.Popen([python, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"], cwd=ROOT / "backend")
    npm_command = shutil.which("npm") or ("npm.cmd" if os.name == "nt" else "npm")
    frontend = subprocess.Popen([npm_command, "run", "dev"], cwd=ROOT / "frontend")
    print("TalentScreen V0.1 is starting...")
    print("Local URL:   http://localhost:3000")
    print(f"Network URL: http://{local_ip()}:3000")
    print("Backend:     http://localhost:8000")
    processes = [backend, frontend]
    try:
        while all(process.poll() is None for process in processes):
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping TalentScreen...")
    finally:
        for process in processes:
            if process.poll() is None:
                process.send_signal(signal.SIGTERM)
        for process in processes:
            process.wait()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
