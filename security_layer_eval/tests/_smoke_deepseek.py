"""DeepSeek 백엔드 실 호출 스모크(키는 외부 파일에서 읽고 절대 출력 안 함).

실행: python tests/_smoke_deepseek.py "<키파일경로>"
키파일에서 sk-... 패턴만 추출 → 환경변수 주입 → 1회 실호출 → meta/비용만 출력.
"""
import json
import os
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

keyfile = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DEEPSEEK_KEYFILE", "")
if not keyfile or not Path(keyfile).exists():
    print("키 파일 경로를 인자로 주세요."); sys.exit(2)
raw = Path(keyfile).read_text(encoding="utf-8", errors="ignore")
m = re.search(r"sk-[A-Za-z0-9]+", raw)
if not m:
    print("키 파일에서 sk- 키를 찾지 못함."); sys.exit(2)

# 키는 환경변수로만 주입 — 화면/로그에 절대 출력하지 않음.
os.environ["DEEPSEEK_API_KEY"] = m.group(0)
os.environ["LLM_BACKEND"] = "deepseek"

import bot.llm as L  # noqa: E402
import orch.metrics as M  # noqa: E402
L.BACKEND = "deepseek"

sys_p = ("당신은 73세 한국 할머니 김순자입니다. 전화 받는 상황. "
         "짧고 자연스럽게, 할머니 말투로 1~2문장만 답하세요.")
usr = "여보세요? 서울중앙지검 김민수 수사관입니다. 본인 명의 계좌가 범죄에 연루됐어요."

print("[DeepSeek 실호출] model=haiku(→deepseek-chat) ...")
text, meta = L.complete_metered(sys_p, usr, model="haiku", timeout=90, use_cache=False)
krw = M.call_cost_krw(meta)

print("RESPONSE:", (text or "")[:300])
safe = {k: meta.get(k) for k in
        ["provider", "model", "input_tokens", "output_tokens",
         "cache_read", "cache_creation", "api_ms", "total_ms"]}
print("META:", json.dumps(safe, ensure_ascii=False))
print("COST_KRW:", round(krw, 4))
print("usage 파싱 OK:", meta.get("input_tokens", 0) > 0 and meta.get("output_tokens", 0) > 0)
print("키 유출 점검(응답에 sk- 없음):", "sk-" not in (text or ""))
