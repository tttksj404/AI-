"""GPT/DeepSeek 백엔드 통합 로직 검증(실 API 키 불필요 — 응답 모킹).

검증 항목:
1. 추상 티어 → 실제 모델 매핑 (haiku→gpt-4o-mini / opus→o1, deepseek-reasoner)
2. 추론모델 분기 (temperature 제거 + max_completion_tokens, 비추론은 temperature=0+max_tokens)
3. usage 파싱 + 캐시 차감 (input = prompt - cached, cache_read = cached)
4. DeepSeek 캐시 필드(prompt_cache_hit_tokens) 별도 경로
5. meta.provider 세팅 + complete_metered 디스패치
6. provider별 단가 계산 (metrics.call_cost_krw)

실행: python tests/test_providers_mock.py
"""
import os
import sys
import types
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ── 가짜 openai 모듈 주입 (from openai import OpenAI 가 이걸 잡음) ──────
_NEXT = {"content": "", "usage": None}
_RECORDED = {}


class _Details:
    def __init__(self, cached):
        self.cached_tokens = cached


class _Usage:
    def __init__(self, prompt, completion, cached=None, ds_hit=None):
        self.prompt_tokens = prompt
        self.completion_tokens = completion
        if cached is not None:
            self.prompt_tokens_details = _Details(cached)
        if ds_hit is not None:
            self.prompt_cache_hit_tokens = ds_hit


class _Msg:
    def __init__(self, content):
        self.content = content


class _Choice:
    def __init__(self, content):
        self.message = _Msg(content)


class _Resp:
    def __init__(self, content, usage):
        self.choices = [_Choice(content)]
        self.usage = usage


class _Completions:
    def create(self, **kwargs):
        _RECORDED.clear()
        _RECORDED.update(kwargs)
        return _Resp(_NEXT["content"], _NEXT["usage"])


class _Chat:
    def __init__(self):
        self.completions = _Completions()


class _FakeOpenAI:
    def __init__(self, **kw):
        self.init_kwargs = kw
        self.chat = _Chat()


_fake = types.ModuleType("openai")
_fake.OpenAI = _FakeOpenAI
sys.modules["openai"] = _fake

import bot.llm as L  # noqa: E402
import orch.metrics as M  # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    mark = "PASS" if cond else "FAIL"
    print(f"  [{mark}] {name}{(' — ' + detail) if detail else ''}")


# 키 가드 통과용 더미 (가짜 클라이언트는 무시)
os.environ["OPENAI_API_KEY"] = "sk-dummy"
os.environ["DEEPSEEK_API_KEY"] = "sk-dummy"

print("── 1. GPT(openai) 비추론 티어: haiku → gpt-4o-mini ──")
_NEXT["content"] = "할머니 응답"
_NEXT["usage"] = _Usage(prompt=1000, completion=200, cached=400)
text, meta = L._complete_openai("시스템", "유저", "haiku", 60)
check("모델 매핑 haiku→gpt-4o-mini", _RECORDED["model"] == "gpt-4o-mini", _RECORDED["model"])
check("비추론: temperature=0", _RECORDED.get("temperature") == 0)
check("비추론: max_tokens=1024", _RECORDED.get("max_tokens") == 1024)
check("비추론: max_completion_tokens 미사용", "max_completion_tokens" not in _RECORDED)
check("provider=openai", meta["provider"] == "openai")
check("input = prompt - cached (1000-400=600)", meta["input_tokens"] == 600, str(meta["input_tokens"]))
check("cache_read=400", meta["cache_read"] == 400)
check("output_tokens=200", meta["output_tokens"] == 200)
check("api_ms 측정됨(>=0)", meta["api_ms"] >= 0)
check("text 반환", text == "할머니 응답")

print("── 2. GPT(openai) 추론 티어: opus → o1 ──")
_NEXT["content"] = "전략"
_NEXT["usage"] = _Usage(prompt=500, completion=300, cached=0)
_, meta_o = L._complete_openai("시스템", "유저", "opus", 60)
check("모델 매핑 opus→o1", _RECORDED["model"] == "o1", _RECORDED["model"])
check("추론: max_completion_tokens=2048", _RECORDED.get("max_completion_tokens") == 2048)
check("추론: temperature 미사용", "temperature" not in _RECORDED)
check("추론: max_tokens 미사용", "max_tokens" not in _RECORDED)

print("── 3. DeepSeek 캐시 필드(prompt_cache_hit_tokens) 경로 ──")
_NEXT["content"] = "디섹 응답"
# details 없이 deepseek 전용 필드만 → 별도 경로 검증
_NEXT["usage"] = _Usage(prompt=2000, completion=100, ds_hit=700)
text_d, meta_d = L._complete_deepseek("시스템", "유저", "opus", 60)
check("모델 매핑 opus→deepseek-reasoner", _RECORDED["model"] == "deepseek-reasoner", _RECORDED["model"])
check("추론분기 적용(reasoner)", _RECORDED.get("max_completion_tokens") == 2048)
check("provider=deepseek", meta_d["provider"] == "deepseek")
check("ds 캐시 차감 input(2000-700=1300)", meta_d["input_tokens"] == 1300, str(meta_d["input_tokens"]))
check("ds cache_read=700", meta_d["cache_read"] == 700)

print("── 4. complete_metered 디스패치(BACKEND=openai) ──")
L.BACKEND = "openai"
_NEXT["content"] = "디스패치 응답"
_NEXT["usage"] = _Usage(prompt=300, completion=50, cached=0)
text_m, meta_m = L.complete_metered("시스템", "유저", model="sonnet", timeout=60, use_cache=False)
check("디스패치→openai 라우팅", meta_m["provider"] == "openai")
check("sonnet→gpt-4o 매핑", _RECORDED["model"] == "gpt-4o", _RECORDED["model"])
check("wall_s/seconds 기록됨", "seconds" in meta_m and meta_m["seconds"] >= 0)
L.BACKEND = "cli"  # 원복

print("── 5. provider별 단가 계산(metrics) ──")
# openai haiku: in 0.15, out 0.60 / (600*0.15 + 400*0.075 + 200*0.60)/1e6 *1400
exp_oa = (600 * 0.15 + 400 * 0.075 + 200 * 0.60) / 1e6 * M.USD_KRW
got_oa = M.call_cost_krw(meta)
check("openai haiku ₩ 계산 정확", abs(got_oa - exp_oa) < 1e-6, f"{got_oa:.4f} vs {exp_oa:.4f}")
# deepseek opus: in 0.55, out 2.19, cache_read 0.14
exp_ds = (1300 * 0.55 + 700 * 0.14 + 100 * 2.19) / 1e6 * M.USD_KRW
got_ds = M.call_cost_krw(meta_d)
check("deepseek opus ₩ 계산 정확", abs(got_ds - exp_ds) < 1e-6, f"{got_ds:.4f} vs {exp_ds:.4f}")
# 하위호환: provider 없는 meta → claude 단가
legacy = {"model": "sonnet", "input_tokens": 1000, "output_tokens": 500,
          "cache_read": 0, "cache_creation": 0}
exp_cl = (1000 * 3.0 + 500 * 15.0) / 1e6 * M.USD_KRW
check("provider 없음→claude 단가(하위호환)", abs(M.call_cost_krw(legacy) - exp_cl) < 1e-6,
      f"{M.call_cost_krw(legacy):.4f} vs {exp_cl:.4f}")

print("── 6. 환경변수 모델 오버라이드 ──")
os.environ["OPENAI_MODEL_OPUS"] = "gpt-5.5"
ov = L._tier_map("OPENAI", {"opus": "o1"})
check("OPENAI_MODEL_OPUS 오버라이드", ov["opus"] == "gpt-5.5", ov["opus"])
del os.environ["OPENAI_MODEL_OPUS"]

print()
print(f"== 결과: {len(PASS)} PASS, {len(FAIL)} FAIL ==")
if FAIL:
    print("FAILED:", FAIL)
    sys.exit(1)
print("모든 통합 로직 검증 통과 (모킹 — 실 API 키 없이).")
