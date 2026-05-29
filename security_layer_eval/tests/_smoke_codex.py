"""codex(ChatGPT OAuth) 백엔드 실 호출 스모크. API 키 불필요(codex login 사용)."""
import json
import os
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ["LLM_BACKEND"] = "codex"
import bot.llm as L  # noqa: E402
import orch.metrics as M  # noqa: E402
L.BACKEND = "codex"

sys_p = ("당신은 73세 한국 할머니 김순자입니다. 전화 받는 상황. "
         "짧고 자연스럽게, 할머니 말투로 1~2문장만 답하세요.")
usr = "여보세요? 서울중앙지검 김민수 수사관입니다. 본인 명의 계좌가 범죄에 연루됐어요."

print("[codex 실호출] ChatGPT OAuth, model=haiku(codex 기본모델) ...")
text, meta = L.complete_metered(sys_p, usr, model="haiku", timeout=180, use_cache=False)
krw = M.call_cost_krw(meta)

print("RESPONSE:", (text or "")[:300])
safe = {k: meta.get(k) for k in
        ["provider", "model", "input_tokens", "output_tokens",
         "cache_read", "api_ms", "total_ms"]}
print("META:", json.dumps(safe, ensure_ascii=False))
print("COST_KRW(환산참고치):", round(krw, 4))
print("응답 비어있지 않음:", bool((text or "").strip()))
print("usage 실측됨:", meta.get("input_tokens", 0) > 0)
