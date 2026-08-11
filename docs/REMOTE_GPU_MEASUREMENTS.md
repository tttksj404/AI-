# 원격 GPU 서버 실측 결과

측정일: 2026-08-11 (KST)

## 측정 경계

- `.env.txt`에 있는 JupyterHub에 직접 인증해 원격 사용자 서버의 GPU 커널에서 실행했다. 로컬 RTX 4050은 모델 추론·학습 경로에 사용하지 않았다.
- 원격 서버는 JupyterHub가 직접 접근 가능했다. `.env.txt`의 별도 Citrix Gateway/VPN 포털은 식별했지만, 이미 JupyterHub가 접근 가능하고 VPN 클라이언트·세션을 추가로 열 필요가 없어 로그인하지 않았다.
- 모든 입력은 합성 사기 대화이고, TTS는 Qwen의 비식별 사전 제공 한국어 speaker `Sohee`를 사용했다. 실제 사용자 음성, voice clone, 실제 전화망, call forwarding은 사용하지 않았다.
- 아래 수치는 고정된 소수 합성 샘플의 실측값이다. 일반적인 WER·MOS·identity similarity·실전화 전환 성공률로 확대 해석하지 않는다.

## 원격 실행환경

| 항목 | 실측값 |
|---|---|
| GPU | NVIDIA L40S 4장 |
| GPU 메모리 | GPU당 45,468 MiB |
| NVIDIA driver / compute capability | 570.211.01 / 8.9 |
| Python | 3.12.6 |
| PyTorch | 2.11.0+cu128 |
| CUDA 확인 | `torch.cuda.is_available() == true`, device count 4 |
| 실행 분배 | LLM `cuda:0`, TTS `cuda:1`, STT `cuda:2`, QLoRA `cuda:3` |

초기 원격 venv는 `torch 2.13.0+cu130`으로 설치되어 서버 드라이버가 보고한 CUDA 12.8과 맞지 않았다. `torch 2.11.0+cu128` 및 `torchaudio 2.11.0+cu128`로 맞춘 뒤 새 커널에서 실제 CUDA 연산과 모델 실행을 통과시켰다.

## 모델별 실측

| 단계 | 모델 | 결과 |
|---|---|---|
| LLM 응답 | Qwen3-4B, Transformers, `cuda:0` | cold load 3.568s, 48토큰 생성 1,436.6ms |
| STT | faster-whisper `large-v3-turbo`, `cuda:2` | cold load 26.953s, 합성 한국어 1회 471.0ms, 고정 문장 문자 오류율 0.0 |
| TTS | Qwen3-TTS `12Hz-0.6B-CustomVoice`, `cuda:1`, `Sohee` | cached load 5.776s, 7.2초 오디오 생성 8,713.2ms, RTF 1.21 |
| QLoRA smoke | Qwen3-1.7B 4-bit + PEFT, `cuda:3` | 2 step, trainable 3,211,264개(전체의 0.3151%), loss 7.039534 → 5.896524, 중앙 step 222.0ms |

QLoRA는 합성·안전대화 4건으로 메모리 안에서 2 step만 실행한 학습 경로 스모크다. adapter를 운영 모델로 승격하거나 품질 향상으로 주장할 수 있는 holdout 검증은 하지 않았다.

## 합성 warm-turn 파이프라인

오디오가 준비된 시점부터 `STT → 맥락 포함 LLM → TTS 오디오 준비`를 3회 반복했다. TTS는 비스트리밍 API라서 `audio_ready`는 첫 오디오 chunk가 아니라 전체 응답 오디오가 완성된 시점이다.

| 지표 | 중앙값 |
|---|---:|
| STT | 223.5ms |
| LLM 전체 생성 | 678.4ms |
| LLM 첫 토큰 | 28.4ms |
| TTS | 10,579.0ms |
| 오디오 준비까지 | 11,483.0ms |

따라서 현재 구성은 “통화 중 즉시 봇 전환”의 실시간 목표를 충족하지 않는다. 병목은 LLM이 아니라 TTS이며, 스트리밍 TTS·짧은 발화 단위·VAD/부분 전사·선행 문장 생성·p95 측정이 다음 최적화 대상이다.

## 결론과 다음 게이트

1. 원격 L40S 서버에서 LLM·STT·TTS 추론과 QLoRA 학습 스모크를 실제로 실행했다.
2. 한 합성 문장의 문자 오류율 0.0은 일반 정확도 100%의 증거가 아니다. identity voice similarity는 측정하지 않았고, 실제 사용자 목소리 clone도 하지 않는다.
3. 통화마다 모델 weight를 온라인 업데이트하지 않는다. 현재 설계는 턴 맥락을 제한된 메모리 버퍼로 전달하고, 동의·익명화·세션 분리·holdout을 통과한 데이터만 오프라인 adapter 후보로 만든다.
4. 다음 실험은 streaming TTS의 첫 audio chunk/RTF/p95, 합성·라이선스 holdout WER, 추출 F1/JSON pass rate, context leakage, 안전 fallback을 측정하는 것이다. 실제 통신망 연결은 별도 법무·동의·안전 게이트 뒤의 범위다.

## 2026-08-11 addendum: first-audio budget and personalization

The five-second acceptance metric is **time to first playable response audio**, not time until a complete WAV/MP3 is generated. The measured stage contract is:

`handoff -> ASR endpoint -> LLM TTFT -> TTS first chunk -> media send -> first audio`

The repository now records this contract in `security_layer_eval/voice_pipeline/latency.py` and keeps full-audio completion separate. The current remote Qwen3-TTS Python path cannot populate `TTS first chunk`: the installed source states that `non_streaming_mode=False` only simulates streaming text input rather than enabling true streaming generation. A runtime call with that flag returned a full `tuple` after `4,555.3ms` for `3.68s` of audio on an L40S.

For the responder, four warm runs per case on remote `cuda:0` were measured after one warmup:

| Case | Median full generation | p95 full generation | Synthetic context check |
|---|---:|---:|---|
| Qwen3-4B zero-shot | 990.1ms | 996.4ms | bank/app keywords retained |
| Qwen3-4B opt-in profile context | 454.6ms | 455.0ms | bank keyword retained; style is not a quality score |
| Qwen3-4B mid-call handoff context | 710.6ms | 733.6ms | app-install context retained |

The QLoRA smoke used Qwen3-1.7B 4-bit on remote `cuda:3`, four synthetic training pairs, and no user audio. Loss moved from `6.98871` to `5.55347`; trainable parameters were `3,211,264 / 1,019,143,168` (`0.3151%`). The synthetic holdout retained a safety keyword. This demonstrates that an adapter can run, not that a real user's personality, knowledge, or voice can be learned accurately.

## Call entry and handoff scenarios

- `FROM_START`: the disclosed test bot owns the conversation from the first turn.
- `MID_CALL_TRANSFER`: the disclosed test endpoint passes a bounded summary, recent turns, and an opt-in style profile into the next responder. Raw transcript text is excluded from trace metadata.
- `HIGH` or `UNKNOWN` risk: `DISCONNECT` is selected before bot audio is emitted in the safe routing contract.

No real phone switch, carrier media bridge, SIP/RTP endpoint, or Twilio call was measured. The supplied `.env.txt` contains JupyterHub/VPN access only; no ElevenLabs API key/voice ID or telephony credential was available. ElevenLabs documents HTTP chunked TTS and WebSocket input streaming, so that provider can be measured in a follow-up run once a test-only licensed/synthetic voice credential is supplied: [HTTP streaming](https://elevenlabs.io/docs/api-reference/text-to-speech/stream), [WebSocket realtime TTS](https://elevenlabs.io/docs/eleven-api/guides/how-to/websockets/realtime-tts).

Therefore the verified conclusion is: **current Qwen full-buffer TTS does not meet a five-second first-audio claim; the first-audio and real phone bridge gates remain unverified.**

## 2026-08-11 remote GPU experiment: dynamic response vs cached filler

The second experiment ran ASR, LLM, and TTS on the remote L40S server in one fresh Jupyter kernel and then sent 8 kHz G.711 μ-law-shaped 20 ms packets through a real localhost UDP loopback. This is a consented synthetic test speaker (`Sohee`), not a user's voice and not a carrier call.

| Measurement | Run 2 result | Interpretation |
|---|---:|---|
| ASR / LLM / TTS placement | `cuda:2` / `cuda:0` / `cuda:1`; all CUDA true | All three AI stages ran on the remote GPU server |
| Dynamic first packet after ASR→LLM→full-buffer TTS | median `6,775.3 ms`, p95 `7,238.2 ms` | Fails the 5,000 ms first-playable target |
| Dynamic full-buffer TTS | median `6,242.2 ms`, p95 `6,705.3 ms` | Current Qwen path has no observed first chunk |
| `non_streaming_mode=False` | `4,067.2 ms`, return `tuple(2)`, one complete audio list | Not a first-chunk stream in this runtime |
| Short dynamic TTS samples | median `3,605.5 ms`, p95 `4,598.4 ms` | Short utterances can finish under 5 s in this run, but are still full-buffer |
| Cached filler invocation→first UDP packet | median `0.1 ms`, p95 `0.2 ms`, 160-byte first packet | Prebuffered filler can start immediately on local loopback |
| UDP send→receive overhead | median `0.0 ms`, p95 `0.1 ms` | Transport overhead is not the current bottleneck in this proxy |

The cached filler result does not prove a real phone transition: it assumes audio was synthesized before invocation and measures only the local media loopback. The dynamic response still misses the target by 1.219–2.238 seconds before its first packet. ElevenLabs and carrier/SIP paths were not called because the remote environment reported no ElevenLabs key/voice ID or telephony credential.

## 2026-08-11 open-source voice-clone experiment

To test the user's free-TTS point without using a real person's recording, the remote GPU generated a short reference with the official non-identity `Sohee` speaker and then fed that synthetic reference into `Qwen/Qwen3-TTS-12Hz-0.6B-Base`. This is a voice-clone feasibility proxy, not a user-voice similarity result.

| Measurement | Result | Interpretation |
|---|---:|---|
| Base model load | `34,334.4 ms` | Must be preloaded before a call; cannot be paid on the handoff critical path |
| Clone prompt build | `110.5 ms` | Reference features can be cached per consented profile |
| Warm full-buffer clone, 3 short utterances | `2,842.8 / 2,392.7 / 2,126.8 ms` | Short responses completed under 5 s after warm-up |
| Generated audio lengths | `2.48 / 2.08 / 1.84 s` | These are complete outputs, not first chunks |
| `non_streaming_mode=False` | `1,239.3 ms`, `tuple(2)`, one audio list | No chunk callback/iterator observed in the installed Python API |

This confirms that ElevenLabs is not technically required for a warm, short, open-source voice-clone path. It does **not** prove that a real user's voice is close enough, that long responses meet p95, or that a carrier call can start audio within 5 seconds. Those require explicit consent, a disclosed test endpoint, a speaker-similarity metric/MOS, and a real streaming media measurement.

## 2026-08-11 remote GPU experiment: CosyVoice3 direct PCM streaming

The prior first run was discarded because the remote child probe passed literal
`\\u...` text instead of Korean text, inflating the synthesized audio length.
The corrected run used a fresh isolated Python environment on the remote Jupyter
GPU and three Korean safety-test utterances, ten warm runs per utterance.
The reference was the official public `CosyVoice/CosyVoice/asset/zero_shot_prompt.wav`;
no user audio was used.

| Measurement | Result | Interpretation |
|---|---:|---|
| GPU | NVIDIA L40S, CUDA true | Remote GPU, not the local RTX 4050 |
| Model load | `9,660.4 ms` | Cold/preload cost; must be outside the call critical path |
| First PCM chunk | median `2,193.2 ms`; nearest-rank p95 `2,619.8 ms`; max `2,708.0 ms` | 30 warm samples; 3 utterances × 10 |
| First chunk audio length | median `3,900 ms`; nearest-rank p95 `4,520 ms` | `stream=True` is a generator, but not a 20 ms telephone chunk |
| Full generation | median `2,245.7 ms`; nearest-rank p95 `3,048.3 ms` | Separate from first playable audio |
| Output | `24,000 Hz` PCM | Must resample and packetize to 8 kHz G.711 for phone tests |

This is model-level streaming evidence only. It does not verify the combined
ASR→LLM→TTS path, SIP/RTP/carrier handoff, jitter-buffer stability, user-voice
similarity, MOS, or any covert identity transition. The architecture and release
budget are recorded in `docs/VOICE_PIPELINE_ARCHITECTURE.md` and the executable
state contract is `security_layer_eval/voice_pipeline/realtime_graph.py`.

## 2026-08-11 remote GPU experiment: Qwen3-4B to CosyVoice3 integrated path

The isolated remote venv then loaded Qwen3-4B and CosyVoice3 on two different
NVIDIA L40S devices and ran ten sequential warm synthetic turns. Qwen produced
one short Korean response, which was passed to the CosyVoice3 streaming
generator. Model load was excluded from per-turn latency because it must be
preloaded before a call.

| Measurement | Median | Nearest-rank p95 | Interpretation |
|---|---:|---:|---|
| Qwen full response | `377.25 ms` | `699.6 ms` | Includes the first post-load generation run |
| CosyVoice3 first PCM chunk | `1,844.3 ms` | `2,136.1 ms` | TTS begins after the complete short LLM response in this conservative test |
| Qwen→CosyVoice3 first chunk | `2,243.55 ms` | `2,512.5 ms` | 10 sequential warm runs, no ASR or media transport |
| Qwen→CosyVoice3 full audio | `2,315.9 ms` | `2,825.9 ms` | Completion is tracked separately from first playable audio |

The two model loads were `2,316.5 ms` for Qwen and `9,966.0 ms` for CosyVoice3;
both are startup costs, not handoff-path costs. Adding the design allowance of
250 ms for ASR endpoint, 300 ms for the handoff snapshot, and 150 ms for media
send gives a model-path budget of about `3,212.5 ms` at the measured p95. This
is promising evidence for the proposed architecture, not phone-call proof:
there was no real ASR audio, SIP/RTP/carrier bridge, packet loss, jitter buffer,
barge-in, or user voice.
