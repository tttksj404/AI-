# /// script
# requires-python = ">=3.12"
# ///
"""Offline executable demo for the Sentinel-30 voice pipeline.

How to run: python -m security_layer_eval.voice_pipeline.demo
"""

from __future__ import annotations

import json

from .contracts import DataManifest, PipelineRequest, Speaker, TranscriptTurn, UserProfile
from .graph import VoicePipeline


def main() -> int:
    """Run one synthetic high-risk scenario and print the result contract."""
    request = PipelineRequest(
        session_id="demo-001",
        synthetic=True,
        consent=True,
        turns=(
            TranscriptTurn(
                speaker=Speaker.CALLER,
                text="금융감독원입니다. 12000원을 02-1234-5678 계좌로 보내고 https://fake.example를 누르세요",
            ),
        ),
        profile=UserProfile("demo-profile", "안녕하세요", True, True),
        manifest=DataManifest("sentinel-demo", "synthetic", "internal-synthetic", "v1"),
    )
    result = VoicePipeline.simulation().run(request)
    print(json.dumps(result.to_json(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
