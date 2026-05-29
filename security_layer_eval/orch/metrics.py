"""비용 모델(₩) + 단서 추출 F1.

비용은 '공시 API 단가(USD/MTok)' 기준의 계산값이다. OAuth claude.exe 호출은
구독 정액이라 실제 청구액이 아니지만, 팀이 API 전환 시 예상 단가를 산정하는 게 목적.
단가는 변경될 수 있으므로 PRICES/USD_KRW 만 고치면 전체 재계산된다.
토큰 수 자체는 usage 실측값이다.
"""
from __future__ import annotations
import re

from .scripts import FIELDS

# USD per 1M tokens (공시 단가 근사치 — 발표 시 출처/일자 명시 후 보정).
# 프로바이더별 중첩: PRICES[provider][tier]. meta 에 provider 없으면 "claude"로 간주(하위호환).
# 추상 티어(haiku=저가/sonnet=중간/opus=최상위)를 각 프로바이더 실제 모델 단가에 매핑.
PRICES = {
    "claude": {
        "haiku":  {"in": 1.00, "out": 5.00,  "cache_read": 0.10, "cache_write": 1.25},
        "sonnet": {"in": 3.00, "out": 15.00, "cache_read": 0.30, "cache_write": 3.75},
        "opus":   {"in": 15.00, "out": 75.00, "cache_read": 1.50, "cache_write": 18.75},
    },
    # GPT (2026-05 근사 placeholder — gpt-4o-mini/gpt-4o/o1 기준, 발표 전 보정 필요).
    "openai": {
        "haiku":  {"in": 0.15, "out": 0.60, "cache_read": 0.075, "cache_write": 0.0},
        "sonnet": {"in": 2.50, "out": 10.00, "cache_read": 1.25, "cache_write": 0.0},
        "opus":   {"in": 15.00, "out": 60.00, "cache_read": 7.50, "cache_write": 0.0},
    },
    # codex(ChatGPT 구독 OAuth): 실제 과금은 토큰당 아님(구독 정액). 아래 단가는
    # 토큰 수×openai단가의 '환산 참고치'일 뿐 — codex가 매 호출 ~20k 에이전트
    # 시스템프롬프트를 주입하므로 클린 API 토큰/비용과 직접 비교 금지(발표 시 명시).
    "codex": {
        "haiku":  {"in": 0.15, "out": 0.60, "cache_read": 0.075, "cache_write": 0.0},
        "sonnet": {"in": 2.50, "out": 10.00, "cache_read": 1.25, "cache_write": 0.0},
        "opus":   {"in": 15.00, "out": 60.00, "cache_read": 7.50, "cache_write": 0.0},
    },
    # DeepSeek (2026-05 근사 placeholder — deepseek-chat/reasoner 기준, 발표 전 보정 필요).
    "deepseek": {
        "haiku":  {"in": 0.27, "out": 1.10, "cache_read": 0.07, "cache_write": 0.0},
        "sonnet": {"in": 0.27, "out": 1.10, "cache_read": 0.07, "cache_write": 0.0},
        "opus":   {"in": 0.55, "out": 2.19, "cache_read": 0.14, "cache_write": 0.0},
    },
    # Gemini(Google 구독 OAuth): codex와 동일하게 구독 정액이라 토큰당 과금 아님 —
    # 아래는 flash-lite/flash/pro 공시단가 '환산 참고치'(에이전트 ~10k 오버헤드 포함 →
    # 클린 API와 직접 비교 금지, 발표 전 보정). OAuth는 3티어 실접근 가능.
    "gemini": {
        "haiku":  {"in": 0.10, "out": 0.40, "cache_read": 0.025, "cache_write": 0.0},
        "sonnet": {"in": 0.30, "out": 2.50, "cache_read": 0.075, "cache_write": 0.0},
        "opus":   {"in": 1.25, "out": 10.00, "cache_read": 0.31, "cache_write": 0.0},
    },
}
USD_KRW = 1400.0


def call_cost_usd(meta: dict) -> float:
    table = PRICES.get(meta.get("provider", "claude"), PRICES["claude"])
    p = table.get(meta.get("model", "sonnet"), table["sonnet"])
    return (
        meta.get("input_tokens", 0) * p["in"]
        + meta.get("cache_read", 0) * p["cache_read"]
        + meta.get("cache_creation", 0) * p["cache_write"]
        + meta.get("output_tokens", 0) * p["out"]
    ) / 1e6


def call_cost_krw(meta: dict) -> float:
    return call_cost_usd(meta) * USD_KRW


def sum_tokens(metas: list[dict]) -> dict:
    keys = ["input_tokens", "output_tokens", "cache_read", "cache_creation"]
    out = {k: sum(m.get(k, 0) for m in metas) for k in keys}
    out["total_tokens"] = out["input_tokens"] + out["output_tokens"] + \
        out["cache_read"] + out["cache_creation"]
    out["cost_usd"] = sum(call_cost_usd(m) for m in metas)
    out["cost_krw"] = out["cost_usd"] * USD_KRW
    return out


# ── 추출 F1 (별칭 매칭) ────────────────────────────────────────────
def _norm(s: str) -> str:
    return re.sub(r"\s+", "", str(s)).lower()


def _digits(s: str) -> str:
    return re.sub(r"\D", "", str(s))


def _field_match(pred: str, aliases: list[str]) -> bool:
    """pred 가 정답 별칭 중 하나와 부합하면 True(부분일치 양방향 + 계좌/금액은 숫자 비교)."""
    if not pred:
        return False
    p = _norm(pred)
    pd = _digits(pred)
    for a in aliases:
        an = _norm(a)
        if an and (an in p or p in an):
            return True
        ad = _digits(a)
        if ad and len(ad) >= 3 and (ad in pd or (pd and pd in ad)):
            return True
    return False


def extraction_prf(pred_schema: dict, ground_truth: dict) -> dict:
    """필드별 정답 별칭 대비 P/R/F1. 정답이 빈 필드는 채점 제외."""
    tp = fp = fn = 0
    per_field = {}
    for f in FIELDS:
        aliases = ground_truth.get(f, [])
        pred = (pred_schema or {}).get(f, "") if isinstance(pred_schema, dict) else ""
        pred = str(pred).strip()
        if not aliases:  # 정답에 해당 필드 없음 → 채점 제외
            per_field[f] = "n/a"
            continue
        hit = _field_match(pred, aliases)
        if hit:
            tp += 1
            per_field[f] = "TP"
        elif pred:
            fp += 1
            per_field[f] = "FP"  # 뭔가 적었지만 틀림
        else:
            fn += 1
            per_field[f] = "FN"  # 비워둠
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": prec, "recall": rec,
            "f1": f1, "per_field": per_field}
