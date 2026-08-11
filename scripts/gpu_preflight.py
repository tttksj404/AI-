# /// script
# requires-python = ">=3.12"
# ///
"""Report GPU readiness without starting a model or exposing environment secrets.

How to run: python scripts/gpu_preflight.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class GpuDevice:
    """Sanitized GPU facts needed for model placement decisions."""

    name: str
    memory_total: str
    driver_version: str


def probe_nvidia_smi() -> tuple[GpuDevice, ...]:
    """Read device name, memory, and driver only when nvidia-smi is available."""
    executable = shutil.which("nvidia-smi")
    if executable is None:
        return ()
    completed = subprocess.run(
        [executable, "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return ()
    devices: list[GpuDevice] = []
    for line in completed.stdout.splitlines():
        fields = [field.strip() for field in line.split(",")]
        if len(fields) == 3:
            devices.append(GpuDevice(fields[0], fields[1], fields[2]))
    return tuple(devices)


def main() -> int:
    """Print a machine-readable preflight result."""
    devices = probe_nvidia_smi()
    payload = {
        "gpu_available": bool(devices),
        "devices": [asdict(device) for device in devices],
        "runtime_mode": "gpu_target" if devices else "simulation",
        "model_download_or_inference_started": False,
    }
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
