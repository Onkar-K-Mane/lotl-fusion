# lotl-fusion

Hierarchical PowerShell / Living-off-the-Land detection with learned fusion over heterogeneous text and graph experts.

> **Status:** active research, target submission Q3 2026 to *Cybersecurity* (Springer). Code, data-reassembly scripts, and trained weights will be released alongside the paper.

## What this is

Most PowerShell / LotL detectors pick one modality (tokens *or* AST *or* provenance graph) or concatenate them naively. This project tests whether a *learned fusion layer* over parallel text and graph experts — with a calibrated tree-ensemble triage stage passed in as a third modality — beats concatenative and rule-based fusion baselines on temporally-split, adversarially-augmented PowerShell data.

The primary contribution is not the architecture. It is the **first systematic ablation of five fusion strategies** (late averaging, stacking meta-learner, cross-modal attention, gated fusion, sparse MoE) over identical backbones for PowerShell / LotL detection, evaluated under Tesseract-compliant temporal splits and Invoke-Obfuscation adversarial pressure.

## Architecture

```
                    ┌─────────────────────────┐
                    │  Stage 1: Triage        │
                    │  XGBoost + SHAP         │──┐
                    │  (lexical features)     │  │
                    └─────────────────────────┘  │
                                                 │
   script text ──► DistilBERT / CodeBERT ──► text embedding ──┐
                                                              ├─► Fusion Head ──► logit
   provenance ───► GATv2 (2-layer, h=64) ──► graph embedding ─┘     (5 variants)
      graph                                                  ▲
                                                             │
                                                  triage prob + SHAP vector
                                                  (triage-as-modality)
```

Five fusion heads benchmarked with identical backbones:

1. Late averaging (logit-level)
2. Stacking meta-learner (LR + 2-layer MLP)
3. Cross-modal attention
4. Gated fusion (GMU-style)
5. Sparse Mixture-of-Experts (Soft MoE)

## Data

- **PowerShell corpus** (text branch): reassembled from `das-lab/mpsd`, `GhostPack/Invoke-Evasion`, `Fa2y/Malicious-PowerShell-Dataset`, and `dessertlab/offensive-powershell`. We do *not* depend on the flaky `aka.ms/PowerShellCorpus` short-link. Target: ~15–20k labelled scripts after SHA-256 dedup.
- **Provenance graphs** (graph branch): DARPA TC E3-CADETS pre-processed `.pkl` from `FDUDSDE/MAGIC`. No raw CDM Avro parsing — Colab cannot handle it.
- **Adversarial augmentation**: Invoke-Obfuscation (COMPRESS / ENCODE / STRING / TOKEN), Invoke-CradleCrafter, psobf.
- **Attack-chain case study**: one Cobalt Strike PowerShell loader reconstructed from E3-CADETS, mapped to MITRE ATT&CK via Sigma rules.

## Evaluation

- 3 seeds, mean ± std on every result.
- Tesseract C1 (temporal train → test), AUT(F1) over quarterly buckets.
- Standard metrics: per-class / macro / weighted F1, PR-AUC, **TPR at FPR = 1e-3 and 1e-4** (PowerShell detection convention).
- Expected Calibration Error + reliability diagrams (the fusion layer needs calibrated posteriors).
- Paired bootstrap between the best fusion head and the second-best.

## Baselines

Rerun on our splits: MAGIC, ThreaTrace, FLASH, Fang-2021-mpsd, Hendler-2018 reimplementation, Revoke-Obfuscation (logistic regression anchor).

Reported from authors' numbers (no code / data available): Power-ASTNN, LOTLDetector, Sentence-Transformer PowerShell.

## Runtime target

Google Colab free tier (T4 GPU, 12 GB RAM, ~78 GB disk, 12-hour session cap).

Pinned versions against an April 2026 Colab snapshot — see `requirements.txt`. The environment check notebook (`notebooks/01_env_check.ipynb`) verifies the runtime before anything trains.

## Repository layout

```
lotl-fusion/
├── README.md
├── LICENSE                    # MIT
├── requirements.txt           # pinned versions
├── .gitignore
├── data/
│   ├── manifest.json          # SHA-256 of every dataset file
│   └── README.md              # exact reassembly instructions
├── src/
│   ├── triage/                # XGBoost + SHAP
│   ├── text_branch/           # DistilBERT / CodeBERT
│   ├── graph_branch/          # GATv2 over MAGIC .pkl
│   ├── fusion/                # 5 fusion heads
│   ├── adversarial/           # Invoke-Obfuscation harness
│   └── eval/                  # Tesseract AUT, metrics, plots
├── configs/                   # YAML per experiment
├── notebooks/
│   ├── 01_env_check.ipynb
│   ├── 02_data_assembly.ipynb
│   └── 03_dummy_forward.ipynb
└── scripts/                   # shell entry points
```

## Reproducibility

- Pinned `requirements.txt` (exact versions, not ranges).
- `data/manifest.json` SHA-256 hashes every dataset file.
- 3 seeds with mean ± std on all reported results.
- Dockerfile and trained weights released at paper acceptance (target ACM / IEEE artifact-evaluation badge).

## Citation

Paper in preparation. Citation info will appear here at submission.

## License

Code: MIT. See `LICENSE`.

Datasets are redistributed only where source licenses permit; otherwise `data/README.md` gives reassembly instructions pointing at the original sources.
