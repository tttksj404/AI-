# Sentinel-30 AI Security Demo

Sentinel-30 is a voice-phishing active-defense concept and presentation artifact. It frames AI as a financial safety workflow: scam intake, AI-assisted response, structured evidence extraction, risk routing, and operator review.

## Portfolio Positioning

This repository demonstrates:

- AI security product planning for voice-phishing response.
- Structured extraction and RAG-style fallback thinking.
- Privacy-aware evidence handling and operator review.
- Visual communication through generated diagrams, slides, and planning documents.

## Project Learning Guide

The project-specific interaction map is documented in [docs/LEARNING_GUIDE.md](docs/LEARNING_GUIDE.md).

The executable voice-pipeline vertical slice and GPU/model/training plan are documented in [docs/VOICE_PIPELINE_IMPLEMENTATION.md](docs/VOICE_PIPELINE_IMPLEMENTATION.md). Remote synthetic GPU measurements are recorded in [docs/REMOTE_GPU_MEASUREMENTS.md](docs/REMOTE_GPU_MEASUREMENTS.md).

The single source of truth for verified, designed, and not-yet-run claims is [docs/CLAIM_STATUS.md](docs/CLAIM_STATUS.md).

```powershell
python -m security_layer_eval.voice_pipeline.demo
```

## Main Artifacts

- `기획서_Sentinel30.md`: full planning document
- `기획서_Sentinel30_lean.md`: concise planning version
- `발표자료_Sentinel30_slides.pdf`: presentation deck
- `images/`: architecture, module map, dashboard, and risk visuals
- `gen_images_*.py`: diagram and slide image generation scripts

## Hiring Signal

This project is useful for AI/data and security-adjacent roles because it shows how to turn an AI idea into a system workflow with safety boundaries, evaluation points, and stakeholder-facing explanation.

## Limitation

This is a concept and presentation repository, not a production anti-fraud service. Real deployment would require legal review, telecom integration, privacy review, audited model behavior, and human operator controls.
