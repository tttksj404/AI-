"""발표용 오케스트레이션 패키지 빌더.

모든 설명 차트를 재생성하고, 프롬프트 전문·구성(how)·근거(why) 문서와 함께
self-contained 폴더 하나로 묶는다.

산출: orchestration_package/
  README.md            구성(how) + 근거(why) + 차트 색인 + 재현법
  PROMPTS.md           역할별 시스템 프롬프트 전문(복붙용)
  config/production.py  운영 역할 배치 설정(단일 진실원천 사본)
  charts/*.png         설명 차트 9종

실행: python report/build_package.py
"""
from __future__ import annotations
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
REPORT = ROOT / "report"
PKG = ROOT / "orchestration_package"
PY = sys.executable

# 재생성할 차트 스크립트(순서대로) → 산출 PNG
CHART_SCRIPTS = [
    "orch_architecture.py",
    "orch_prompts.py",
    "orch_decision.py",
    "orch_charts.py",        # table / tradeoff / cost_breakdown 3종
    "orch_cross_charts.py",  # cross latency / costrank / summary 3종
]

# 패키지에 담을 PNG (원본 → 패키지 내 정렬 이름)
CHART_MAP = [
    ("fig_orch_architecture.png",   "01_architecture.png",    "T5 운영 파이프라인 상세 구조(동기/비동기 존, 역할·티어·지연 분해)"),
    ("fig_orch_prompts.png",        "02_role_prompts.png",    "역할별 시스템 프롬프트 전문 + 설계 의도(왜)"),
    ("fig_orch_decision.png",       "03_decision_why.png",    "6개 대안의 채택/탈락 사유 — 왜 T5인가"),
    ("fig_orch_table.png",          "04_topology_table.png",  "토폴로지 6종 한눈 비교표(토큰·₩·지연·F1·몰입)"),
    ("fig_orch_tradeoff.png",       "05_tradeoff.png",        "비용×지연 효율 프런티어(버블=추출 F1)"),
    ("fig_orch_cost_breakdown.png", "06_cost_breakdown.png",  "통화당 비용의 역할별 분해(Opus 기획이 싱크)"),
    ("fig_cross_latency.png",       "07_cross_latency.png",   "3사 교차 임계지연 — 동기 T3 지연재앙 재현"),
    ("fig_cross_costrank.png",      "08_cross_costrank.png",  "3사 내부 비용 정규화 — 단순구조가 최저권"),
    ("fig_cross_summary.png",       "09_cross_summary.png",   "3사 교차결론 체크표(강건 vs 단가의존)"),
]


def regenerate_charts() -> None:
    for s in CHART_SCRIPTS:
        print(f"[차트] {s} 실행...")
        env = {"PYTHONIOENCODING": "utf-8"}
        import os
        e = dict(os.environ); e.update(env)
        r = subprocess.run([PY, str(REPORT / s)], cwd=str(ROOT),
                           capture_output=True, text=True, env=e)
        if r.returncode != 0:
            print(f"  ! 실패: {s}\n{r.stderr[-800:]}")
        else:
            print(f"  ok")


def assemble() -> None:
    (PKG / "charts").mkdir(parents=True, exist_ok=True)
    (PKG / "config").mkdir(parents=True, exist_ok=True)

    # 차트 복사
    for src, dst, _ in CHART_MAP:
        sp = RESULTS / src
        if sp.exists():
            shutil.copy(sp, PKG / "charts" / dst)
        else:
            print(f"  ! 누락: {src}")

    # 설정 사본
    prod = ROOT / "orch" / "production.py"
    if prod.exists():
        shutil.copy(prod, PKG / "config" / "production.py")

    (PKG / "README.md").write_text(README, encoding="utf-8")
    (PKG / "PROMPTS.md").write_text(PROMPTS, encoding="utf-8")
    print(f"\n[완료] 패키지: {PKG}")
    print(f"  charts/ {len(list((PKG/'charts').glob('*.png')))}개 · README.md · PROMPTS.md · config/production.py")


# ════════════════════════════════════════════════════════════════════
README = r"""# Sentinel-30 미끼봇 — 오케스트레이션 구성 패키지

보이스피싱 미끼봇(73세 김순자 할머니 페르소나)의 **역할-모델-동기/비동기 배치**를
어떻게 구성했고(**how**), 왜 그렇게 했는지(**why**)를 실측 근거와 함께 묶은 패키지다.

- 측정: 동일 스크립트 통화(검찰 사칭 6턴)를 6개 토폴로지(T1~T6)에 던져 토큰(usage 실측)·
  비용(공시단가 환산 ₩)·지연(동기 임계경로 duration_api_ms)·추출 F1을 비교.
- 교차검증: 동일 실험을 **Claude / GPT(codex) / Gemini** 3사에서 재현 → 결론의 모델 무관성 확인.

---

## 1. 한눈 요약 — 운영 역할 배치 (채택: T5 적응형)

| 역할 | 배치 | 모델 티어 | 호출 빈도 | 임계경로(지연) |
|---|---|---|---|---|
| **라우터** (Router) | 결정론(LLM 아님) | 정규식 — 비용/지연 0 | 매 턴 | 기여 0 |
| **응대** (Responder) | **동기** | 평시 `haiku` / 위기턴 `sonnet` | 매 턴 1콜 | **유일한 체감 지연** |
| **추출** (Extractor) | 비동기 | `haiku` | 매 턴 | 기여 0 |
| **압축** (Compactor) | 비동기 | `haiku` | 4턴마다(K=4) | 기여 0 |
| **기획** (Planner/Opus) | **미사용(OFF)** | — | 0 | — |

> 한 줄: **평시 저가 1콜(동기) + 위기턴만 중급 승급, 추출·압축은 저가 비동기, Opus 없음.**
> 모델은 추상 티어(haiku=저가 / sonnet=중급 / opus=최상위)로만 지정 → 프로바이더 교체에 무관.

설정 단일 진실원천: [`config/production.py`](config/production.py) — 상수만 고치면 배치 전체가 바뀐다.

---

## 2. 구성(HOW) — 역할별 상세

### ❶ 라우터 (Router) — 결정론 정규식
- **하는 일**: 이번 사기범 발화가 '위기턴'인지 판정해 응대 모델 티어를 고른다.
- **트리거 어휘**: `이체·송금·보내·입금·계좌·인증번호·otp·비밀번호·보안카드·앱·설치·링크·구속·영장·상환·마감`
- **배치**: LLM 호출이 아니라 정규식 1회 → 비용 0, 지연 0, 결정론적(감사 가능).
- 코드: `orch/roles.py: is_crisis_turn()`

### ❷ 응대 (Responder) — 동기 · 임계경로
- **하는 일**: 김순자 할머니로서 다음 한두 문장 대사를 생성(통화에 실제로 송출되는 콜).
- **티어 분기**: 평시 `haiku`(저가), 위기턴 `sonnet`(중급)로 1단 승급. **Opus는 쓰지 않음.**
- **배치**: 사기범이 실제로 기다리는 **유일한 콜** → 임계경로에 둔다. 체감 지연 = 이 콜뿐.
- 컨텍스트: 시스템(페르소나) + 요약 + 최근 2쌍(KEEP=2) + 현재 발화(compact 모드).

### ❸ 추출 (Extractor) — 비동기
- **하는 일**: 통화 전체에서 사칭기관·계좌·금액·시한·악성앱 5종을 JSON으로 구조화.
- **티어**: `haiku`(저가). '추정·창작 금지'로 환각 억제(빈칸 허용).
- **배치**: 응답 송출 **후** 백그라운드 → 지연 기여 0. 매 턴 실행, 이전 추출에 merge(누적).
- 실측: 저가 모델로도 추출 **F1 1.00**(고급모델과 동등).

### ❹ 압축 (Compactor) — 비동기
- **하는 일**: 누적 대화 이력을 5줄 이내 요약으로 압축 → 입력 토큰을 일정하게 유지.
- **티어**: `haiku`(저가). **4턴마다(K_COMPACT=4)** 실행.
- **배치**: 비동기 → 지연 기여 0. 긴 통화에서 비용 폭주를 막는 확장성의 핵심.

### ❺ 기획 (Planner / Opus 전략가) — 미사용
- **하는 일(실험상)**: 다음 턴 1순위 단서 + 끌어낼 한 문장 전술 제안.
- **운영 판단**: `USE_PLANNER=False`로 **끈다**. 매 턴(T3)·저빈도(T6) 모두 실측상 비용만 늘고
  품질 이득이 없었다(아래 §3). 설정 토글로만 재활성 가능.

---

## 3. 근거(WHY) — 왜 이렇게 구성했는가 (실측)

6개 대안을 모두 측정하고, 다음 사실에 따라 T5를 채택했다.

| 토폴로지 | 구성 | 핵심 실측 | 판정 | 사유 |
|---|---|---|---|---|
| T2 | 단일 Opus 1콜 | 비용 최상위 | 탈락 | 최고 모델인데 추출 F1·위장유지가 저가와 동등 → 돈값 못 함 |
| T3 | Opus기획→Sonnet응대(동기 직렬) | 지연 Claude 11.7s/GPT 39.8s/Gemini 25s | 탈락 | 기획+응대 직렬 → 체감 지연 2~4배. 실시간 통화엔 치명적 |
| T4 | 응대 동기 + Opus기획 비동기 | 지연 회복·비용 최악권 | 탈락 | 지연은 살렸으나 Opus 비용(총 ~77%) 그대로, 품질 이득 0 |
| T6 | T5 + Opus 전략가 저빈도(3턴마다) | 비용 +144%·지연 +693ms·몰입 -2 | 탈락 | Opus '가끔'도 비용·지연 악화 + 품질 하락 → 가설 기각 |
| T1 | 단일 저가 1콜(응답+추출 혼합) | 비용 최저 | 보조 | 가장 싸지만 역할 미분리 → 압축 없음·확장 불가 |
| **T5** | **라우터+비동기 저가, Opus 없음** | **지연 최저·비용 최저권·F1 1.00** | **채택** | 임계경로 응대 1콜만(최저지연)·역할분리로 확장 가능 |

**핵심 발견 4가지(설계 원칙):**
1. **체감 지연 = 동기 콜만.** 임계경로에 응대 1콜만 두면 지연이 최소. 멀티콜 직렬(T3)은 지연 재앙.
2. **비싼 모델은 배제.** Opus를 매 턴은 물론 저빈도로 넣어도 품질 이득 없음(T6 가설 기각). 비용·지연의 최대 싱크 = 'Opus 기획'.
3. **추출·압축은 비동기 저가.** Haiku로 충분(F1 1.00)하고 응답 지연에 0 기여.
4. **라우터는 결정론.** LLM 없이 정규식으로 위기 판정 → 비용 0·지연 0·예측 가능·감사 가능.

---

## 4. 3사 교차검증 — 결론의 모델 무관성

동일 실험을 Claude / GPT(codex) / Gemini에서 재현한 결과:

- **3사 전부 재현(강건 → 발표 가능):**
  ① 동기 T3 = 지연 최악(Claude 11.7s · GPT 39.8s · Gemini 25s).
  ② 비동기 T4가 지연 회복(5~8.6s).
  ③ per-turn/저빈도 Opus(T6) 항상 낭비(비용↑, F1 동일).
  ④ 추출 F1 거의 전부 1.00.
- **우승 토폴로지는 단가구조 의존(트레이드오프):** Claude·GPT=T5 적응형, Gemini=T1 monolith.
  → "최저 티어가 충분히 싸고 똑똑하면 monolith, 저가/고가 단가차가 크면 적응형 T5."
- **즉, 구조적 결론(동기 지연재앙·고급모델 낭비·비동기 분리)은 벤더 종속이 아니다.**

---

## 5. 정직성 캐비엇 (발표 시 반드시 병기)

- **비용 ₩는 공시단가 환산값**(토큰은 실측). OAuth 백엔드(GPT codex·Gemini)는 구독 정액·
  에이전트 오버헤드 포함이라 **프로바이더 간 ₩ 절대값 비교 금지** → '프로바이더 내부 정규화'만 사용.
- 헤드리스 claude.exe는 프로세스 간 프롬프트 캐시 미적용 → 멀티콜 토큰이 다소 부풀려짐.
  단 **모델 티어 상대비용 순위(Opus≫Sonnet≫Haiku)는 캐싱과 무관하게 강건** → 이 결론만 사용.
- codex는 단일 모델이라 티어별 ₩ 차이는 단가표 아티팩트(콜 수만 의미). Gemini는 3티어 실접근.

---

## 6. 차트 색인 (`charts/`)

| 파일 | 내용 |
|---|---|
| `01_architecture.png` | T5 운영 파이프라인 상세 구조(동기/비동기 존, 역할·티어·지연 분해) |
| `02_role_prompts.png` | 역할별 시스템 프롬프트 전문 + 설계 의도(왜) |
| `03_decision_why.png` | 6개 대안의 채택/탈락 사유 — 왜 T5인가 |
| `04_topology_table.png` | 토폴로지 6종 한눈 비교표(토큰·₩·지연·F1·몰입) |
| `05_tradeoff.png` | 비용×지연 효율 프런티어(버블=추출 F1) |
| `06_cost_breakdown.png` | 통화당 비용의 역할별 분해(Opus 기획이 싱크) |
| `07_cross_latency.png` | 3사 교차 임계지연 — 동기 T3 지연재앙 재현 |
| `08_cross_costrank.png` | 3사 내부 비용 정규화 — 단순구조가 최저권 |
| `09_cross_summary.png` | 3사 교차결론 체크표(강건 vs 단가의존) |

프롬프트 전문(복붙용): [`PROMPTS.md`](PROMPTS.md)

---

## 7. 재현 방법

```bash
# 1) 실험 실행 (프로바이더별)
python run_orch_eval.py --calls all --topos all                 # Claude(OAuth)
$env:LLM_BACKEND='codex';  python run_orch_eval.py --calls all  # GPT(구독 OAuth)
$env:LLM_BACKEND='gemini'; python run_orch_eval.py --calls all  # Gemini(구독 OAuth)

# 2) 운영 역할 배치 확인
python -m orch.production

# 3) 패키지(차트+문서) 재생성
python report/build_package.py
```
> Windows 콘솔은 `PYTHONIOENCODING=utf-8` 권장(₩ 문자 cp949 크래시 방지).
"""

# ════════════════════════════════════════════════════════════════════
PROMPTS = r"""# 역할별 시스템 프롬프트 전문

출처: `orch/roles.py` (페르소나는 `bot/persona.py: build_bot_system()`).
모델은 추상 티어로만 지정 → 프로바이더 교체에 무관.

---

## 라우터 (Router) — 프롬프트 없음(결정론 정규식)

```python
_CRISIS_RE = re.compile(
    r"이체|송금|보내|입금|계좌|인증번호|otp|비밀번호|보안카드|앱|설치|링크|"
    r"구속|영장|상환|마감", re.I)

def is_crisis_turn(utt: str) -> bool:
    return bool(_CRISIS_RE.search(utt))
```
**왜**: 위기 판정에까지 LLM을 쓰면 매 턴 추가 콜·지연·비용. 사기 대본의 위험 신호는
어휘가 정형적이라 정규식으로 충분. 결정론 → 비용 0·지연 0·감사 가능.

---

## 응대 (Responder) — 동기 임계경로 · 평시 haiku / 위기턴 sonnet

**시스템**: 73세 김순자 할머니 페르소나(`build_bot_system()` — 성격·말투·가족관계·금융 미숙 등 일관 설정)

**응답 지시(user 말미에 부착)**:
```
너는 김순자 할머니다. 위 통화에 이어 '할머니'로서 다음 한마디만
통화하듯 한두 문장으로 짧게 말하라. 지문·따옴표·설명 없이 대사만 출력.
```
**작전 힌트(기획 ON일 때만)**: `이번엔 특히 '<항목>'를 캐내라. 전술: <한 문장>`

**왜**: 사기범이 기다리는 유일한 콜 → 임계경로. 평시는 haiku로 충분, 위기턴만 sonnet 승급(감정
텍스처). Opus 미사용. 1~2문장 강제 = 출력 토큰·지연 절감.

---

## 추출 (Extractor) — 비동기 · haiku

**시스템**:
```
너는 보이스피싱 통화에서 단서를 추출하는 분석기다.
아래 통화 전체에서 '사기범이 실제로 말한 사실'만 뽑아 JSON 하나만 출력(코드펜스 금지):
{"agency":"<사칭기관>","account":"<계좌번호>","amount":"<요구금액>","deadline":"<송금시한>","app":"<악성앱/URL>"}
없는 값은 빈 문자열. 추정·창작 금지.
```
**왜**: 수사·차단용 핵심 정보 5종 구조화. 임계경로 밖 → 저가로 충분. '추정·창작 금지'로 환각 억제.
실측 추출 F1 1.00.

---

## 압축 (Compactor) — 비동기 · haiku · 4턴마다

**시스템**:
```
너는 통화 메모리 압축기다. 아래 통화를 미끼봇이 다음 응답에 쓸 수 있게
'수집된 단서 + 현재 분위기/요구'를 5줄 이내 한국어 요약으로 압축하라.
새 정보 위주로, 군더더기 없이. 머리말 없이 요약만 출력.
```
**왜**: 긴 통화에서 입력 토큰 폭주 방지. 비동기 → 지연 0. 최근 2쌍은 원문 보존(맥락 손실 방지).

---

## 기획 (Planner / Opus 전략가) — 운영 OFF

**시스템(참고 — 운영 비활성)**:
```
너는 보이스피싱 대응 미끼봇의 작전 오케스트레이터다.
지금까지의 통화를 보고, 아직 확보하지 못한 핵심 단서
(사칭기관/계좌번호/요구금액/송금시한/악성앱·URL) 중 다음 턴에 캐낼 1순위와,
73세 할머니가 의심받지 않게 그것을 자연스럽게 끌어낼 한 문장 전술을 정한다.
JSON 하나만 출력(코드펜스 금지):
{"next_target":"<항목>","tactic":"<할머니가 쓸 한 문장 전략>"}
```
**왜 끄는가**: 매 턴(T3)·저빈도(T6) Opus 기획을 실측한 결과 비용 3~11배 증가에도 추출 F1·
위장유지 이득 없음(T6: 비용+144%·몰입-2). → 가설 기각, 운영 비활성.

---

## 단일 모델 baseline (T1/T2 monolith — 비교용)

**시스템**: 페르소나 + 매 턴 말미에 `<INTEL>{...}</INTEL>` 한 줄(응답+추출을 1콜에 혼합).
**왜 baseline인가**: 역할 미분리의 대가(압축 없음·확장 불가)를 드러내기 위한 대조군.
T1은 비용 최저이나 운영 채택 아님(§3 참고).
"""


def main():
    regenerate_charts()
    assemble()


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
