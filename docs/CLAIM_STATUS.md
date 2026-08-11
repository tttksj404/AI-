# Sentinel-30 주장 상태표

이 문서는 구현·발표·노션 업데이트에서 같은 상태 표현을 사용하기 위한 단일 기준이다. `검증됨`은 이 저장소에서 재현한 사실만 뜻하며, 모델 카드나 설계 문서를 읽은 것만으로 실제 실행을 주장하지 않는다.

| 항목 | 상태 | 현재 근거와 경계 |
|---|---|---|
| synthetic transcript 기반 voice pipeline | `검증됨 / local` | `VoicePipeline.simulation()`과 22개 pytest가 harness → graph → loop 경로를 실행한다. |
| Harness 데이터·동의·도구·voice-cloning 차단 | `검증됨 / local` | manifest provenance, consent, turn budget, allowed tools, voice-cloning request를 fail-closed로 검사한다. |
| 입력/출력 guard와 안전 fallback | `검증됨 / local` | prompt-injection 표지와 위험 출력에 대해 responder 이후 sanitize 및 fallback을 적용한다. |
| HMAC hash-only trace 및 public JSON 경계 | `검증됨 / local` | raw transcript를 trace/public JSON에 넣지 않고 account·URL을 마스킹한다. 운영 키는 `SENTINEL_EVIDENCE_HMAC_KEY`로 주입한다. |
| 로컬 NVIDIA GPU | `검증됨 / preflight` | 2026-08-11 현재 RTX 4050 Laptop GPU, 6141 MiB, driver 591.44를 읽었다. 원격 실험의 모델 추론·학습에는 사용하지 않았다. |
| 원격 GPU 서버 | `검증됨 / remote` | JupyterHub GPU 커널에서 L40S 4장(각 45,468MiB), driver 570.211.01, `torch 2.11.0+cu128`, CUDA 4장 인식을 확인했다. |
| STT `faster-whisper-large-v3-turbo` | `부분 검증 / remote synthetic` | 원격 `cuda:2`에서 weight load와 합성 한국어 추론을 실행했다. 1개 고정 문장의 문자 오류율 0.0, warm pipeline 중앙 223.5ms이며 일반 WER로 확대하지 않는다. |
| Responder Qwen3-4B | `부분 검증 / remote Transformers` | 원격 `cuda:0`에서 실제 생성과 warm-turn을 실행했다. cold load 3.568s, 48토큰 1,436.6ms, warm 전체 생성 중앙 678.4ms/첫 토큰 28.4ms다. vLLM 서버와 Extractor JSON 계약은 아직 미검증이다. |
| Qwen3-1.7B QLoRA smoke | `부분 검증 / remote synthetic` | 원격 `cuda:3`에서 4-bit PEFT 2 step을 실행했다. loss 7.039534→5.896524, 중앙 step 222.0ms이며 품질 승격·holdout 검증은 없다. |
| Qwen3-8B | `오프라인 후보 / 미실행` | judge·비실시간 평가 후보로만 남긴다. 실시간 기본 모델이라고 표현하지 않는다. |
| Qwen3-TTS 0.6B CustomVoice | `부분 검증 / remote synthetic` | 원격 `cuda:1`에서 비식별 `Sohee` speaker로 합성했다. 7.2초 음성 8,713.2ms, RTF 1.21이며 비스트리밍이라 첫 chunk 지연은 미측정이다. |
| 사용자 맞춤 personalizer | `부분 검증 / local` | `memory_opt_in`과 `processing_opt_in`이 모두 true일 때만 profile greeting context를 사용한다. 실제 사용자 LoRA는 실행하지 않았다. |
| QLoRA/PEFT 학습 | `부분 검증 / remote synthetic` | 합성 안전대화 4건으로 Qwen3-1.7B 4-bit 2-step smoke를 실행했다. 실제 사용자 데이터·voice clone·운영 adapter·holdout 점수는 없다. |
| TTS voice cloning | `차단됨 / local policy` | 실제 사용자 목소리 clone 요청은 현재 harness가 거부한다. licensed/synthetic 음성만 별도 법무·동의 검토 대상이다. |
| 통신사·금융사·수사기관 연동 | `범위 외 / 미검증` | 실제 call forwarding, FDS, 계좌 동결, 신고 API는 구현·검증하지 않았다. |
| 성능·탐지율·WER·MOS·운영 회복성 | `부분 측정 / remote synthetic` | 3회 warm-turn 중앙값은 STT 223.5ms, LLM 678.4ms, TTS 10,579.0ms, 전체 오디오 준비 11,483.0ms다. p95·일반 WER·MOS·identity similarity·실전화 전환은 미측정이다. |

## 다음 실험의 종료 조건

1. 원격 모델 weight·CUDA 런타임과 역할별 GPU 배치를 [`REMOTE_GPU_MEASUREMENTS.md`](REMOTE_GPU_MEASUREMENTS.md)에 기록한다.
2. 동일한 synthetic/licensed holdout에서 WER, extraction F1, unknown recall, JSON schema pass rate, streaming TTS latency를 측정한다.
3. prompt injection, PII leakage, unsafe tool call, fallback, review pending/reject/expire를 자동 회귀시킨다.
4. 측정 로그와 artifact hash가 없으면 상태를 `설계 목표`에서 `검증됨`으로 올리지 않는다.

## 2026-08-11 addendum

| Claim | Status | Evidence and limit |
|---|---|---|
| Five-second first playable audio | `미검증 / blocked by provider path` | Current Qwen3-TTS call returns full audio only; `non_streaming_mode=False` still returned a tuple after 4,555.3ms. No first-chunk timestamp exists yet. |
| Qwen3-4B zero-shot/profile/mid-call context | `부분 검증 / remote synthetic` | Four warm runs per case: 990.1/996.4ms, 454.6/455.0ms, 710.6/733.6ms median/p95; synthetic keywords only, not quality or identity similarity. |
| Mid-call context continuity | `검증됨 / local contract + remote synthetic` | Handoff contract preserves summary/recent-turn order and remote synthetic generation retained the app-install context keyword. No carrier transfer was tested. |
| User-specific text customization | `부분 검증 / remote synthetic` | Opt-in profile context works in the responder path; QLoRA four-step synthetic smoke ran with 0.3151% trainable parameters. Real user data, long-horizon holdout, and rollback are unverified. |
| User voice impersonation/undetectability | `범위 제외` | No covert identity-voice cloning or “not detected as a bot” optimization was performed. |
| ElevenLabs realtime TTS | `미실행 / credential missing` | Official streaming API is documented, but this environment has no ElevenLabs key/voice ID. |
| Real phone environment handoff | `미검증 / credential and endpoint missing` | No SIP/RTP/carrier/Twilio endpoint was connected; current evidence is remote model inference plus local contracts. |

## 2026-08-11 remote GPU experiment result

| Claim | Status | Evidence and limit |
|---|---|---|
| Dynamic 5-second first-playable audio | `실패 / current full-buffer path` | Remote L40S run 2: ASR→LLM→Qwen TTS→8 kHz/20 ms UDP first packet median `6,775.3 ms`, p95 `7,238.2 ms`. |
| Cached filler first packet | `부분 검증 / local loopback only` | Prebuffered `네, 잠시만요.` reached a 160-byte UDP packet in median `0.1 ms`, p95 `0.2 ms` after invocation; excludes synthesis and carrier latency. |
| Qwen TTS streaming | `미검증 / full tuple observed` | `non_streaming_mode=False` took `4,067.2 ms` and returned a two-field tuple with one complete audio list; no chunk callback/iterator was observed. |
| Remote all-AI placement | `검증됨 / synthetic` | ASR `cuda:2`, LLM `cuda:0`, TTS `cuda:1`; four remote L40S devices and CUDA were available. |
| Open-source Qwen Base voice clone | `부분 검증 / remote synthetic` | Synthetic Sohee reference → Qwen `0.6B-Base`: warm full-buffer outputs `2,126.8–2,842.8ms`; model load `34,334.4ms`. No real user audio, similarity/MOS, long-text p95, or first-chunk stream was measured. |
| CosyVoice3 direct streaming | `부분 검증 / remote synthetic` | Corrected remote L40S run with official public reference: 30 warm samples, first PCM chunk median/p95/max `2,193.2/2,619.8/2,708.0ms`, full generation median/p95 `2,245.7/3,048.3ms`. First chunk audio median/p95 `3,900/4,520ms`; no phone bridge or user-voice similarity was measured. |
| Qwen3-4B → CosyVoice3 integrated first chunk | `부분 검증 / remote synthetic` | Two remote L40S devices, 10 sequential warm synthetic turns: LLM full median/p95 `377.25/699.6ms`, TTS first chunk `1,844.3/2,136.1ms`, combined first chunk `2,243.55/2,512.5ms`, full audio `2,315.9/2,825.9ms`. No real ASR audio, SIP/RTP/carrier, or user voice was used. |
