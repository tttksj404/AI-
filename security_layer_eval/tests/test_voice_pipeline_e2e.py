from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_demo_module_emits_machine_readable_pipeline_result() -> None:
    repo = Path(__file__).resolve().parents[2]
    completed = subprocess.run(
        [sys.executable, "-m", "security_layer_eval.voice_pipeline.demo"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["risk"] in {"low", "high", "unknown"}
    assert payload["trace"]
    assert payload["audio_refs"]
