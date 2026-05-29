"""미끼봇 오케스트레이션 효율 실험 러너.

토폴로지별로 동일 스크립트 통화를 돌려 토큰(실측)·비용(₩, 공시단가)·
동기 임계경로 지연(duration_api_ms)·추출 F1·몰입 판정(Opus)을 측정한다.

실행:
  python run_orch_eval.py                       # 스모크: call1, 6턴, 5토폴로지, 판정 ON
  python run_orch_eval.py --turns 4             # 빠른 점검
  python run_orch_eval.py --calls all --topos T1,T4 --no-judge
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path

try:  # ₩/한글 print 가 cp949 콘솔에서 깨지지 않도록(백그라운드 실행 대비)
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from orch import judge as J
from orch.scripts import CALLS
from orch.topologies import TOPOLOGIES, run_topology

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=6, help="통화당 사용할 사기범 턴 수")
    ap.add_argument("--calls", default="call1_prosecutor",
                    help="콤마구분 콜 id 또는 'all'")
    ap.add_argument("--topos", default="all", help="콤마구분 토폴로지 id 또는 'all'")
    ap.add_argument("--judge", dest="judge", action="store_true", default=True)
    ap.add_argument("--no-judge", dest="judge", action="store_false")
    ap.add_argument("--out", default="orch_results.json")
    args = ap.parse_args()

    call_ids = list(CALLS) if args.calls == "all" else \
        [c.strip() for c in args.calls.split(",") if c.strip()]
    topo_ids = list(TOPOLOGIES) if args.topos == "all" else \
        [t.strip() for t in args.topos.split(",") if t.strip()]

    runs = []
    t_start = time.time()
    for cid in call_ids:
        call = CALLS[cid]
        for tid in topo_ids:
            t0 = time.time()
            print(f"[run] {cid} × {tid} ({TOPOLOGIES[tid]['name']}) ...", flush=True)
            r = run_topology(call, tid, turns=args.turns)
            r["call_id"] = cid
            if args.judge:
                r["judge"] = J.judge_transcript(r["history"], model="opus")
            r["wall_s"] = round(time.time() - t0, 1)
            tk = r["tokens"]; cm = r["critical_ms"]; ex = r["extraction"]
            jv = r.get("judge", {})
            print(f"    토큰={tk['total_tokens']:>6}  ₩={tk['cost_krw']:>7.1f}  "
                  f"임계지연(med)={cm['median']:>6.0f}ms  추출F1={ex['f1']:.2f}  "
                  f"몰입={jv.get('overall','-')}  콜={r['n_calls']}  ({r['wall_s']}s)",
                  flush=True)
            runs.append(r)

    out = {
        "meta": {
            "turns": args.turns, "calls": call_ids, "topos": topo_ids,
            "judge": args.judge, "elapsed_s": round(time.time() - t_start, 1),
            "note": "토큰=usage 실측 / 비용=공시단가 계산(₩) / 지연=duration_api_ms "
                    "동기 임계경로 합(프로세스 spawn 제외, 상대비교용)",
        },
        "runs": runs,
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    outp = RESULTS / args.out
    outp.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n[저장] {outp}  (총 {out['meta']['elapsed_s']}s, {len(runs)} runs)")


if __name__ == "__main__":
    main()
