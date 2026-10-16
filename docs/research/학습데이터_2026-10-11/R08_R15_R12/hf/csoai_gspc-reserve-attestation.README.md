---
license: cc-by-4.0
language:
- en
pretty_name: GSPC — reserve attestation facts (ReserveFacts)
task_categories:
- other
size_categories:
- n<1K
tags:
- gspc
- council-of-ai
- ai-governance
- eu-ai-act
- ai-safety
- measurement
- attestation
- signed-evidence
- responsible-ai
- evaluation
- benchmark
- transparency
- reserve-attestation
- family-financial
- reservefacts
- deterministic-facts
- on-chain
- rwa
- stablecoins
- xrpl
- tokenization
configs:
- config_name: default
  data_files:
  - split: train
    path: axis-live.jsonl
- config_name: manifest
  data_files:
  - split: train
    path: manifest.jsonl
---

# GSPC — reserve attestation facts (ReserveFacts)

<!-- csoai-funnel-2026-09-27 -->

**In one line:** For the 16 XRPL issuer accounts in the live reader: is third-party reserve-attestation language on a retrieved issuer page? PASS, FAIL or UNCHECKABLE. For stablecoin and tokenised-asset analysts. It grades no issuer.

### Use it

```python
from datasets import load_dataset
ds = load_dataset("csoai/gspc-reserve-attestation", split="train")
print(ds[0])
```

- **Verify a signed card in your browser, free, no account:** <https://councilof.ai/gspc-verify/?ref=hf-gspc-reserve-attestation>
- **Read the live XRPL reader these facts come from (free JSON):** <https://councilof.ai/api/xrpl>
- **For agents:** MCP endpoint `POST https://councilof.ai/mcp` (free read tools; call `tools/list`).
- **A row about you is wrong, or you want an endpoint left out?** Ask for a re-check or object: <https://councilof.ai/census/?ref=hf-gspc-reserve-attestation>

### Fresh data

This Hub copy is a dated snapshot. If it disagrees with the live source, the live source wins.

- `GET https://councilof.ai/api/gspc?axis=reserve-attestation` (free, live, this dataset's row of the board)
- Signed transparency root (Merkle, board key `did:web:csoai.org#board-attestation-1`): https://councilof.ai/root.json
- Daily signed index of every measurement capsule: [https://councilof.ai/measurement-capsules/](https://councilof.ai/measurement-capsules/?ref=hf-gspc-reserve-attestation) (also published on the Hub as [csoai/evidence-index](https://huggingface.co/datasets/csoai/evidence-index))
- **Pay per call for a fresh, signed capsule:** `GET https://councilof.ai/api/rwa/evidence?asset=RLUSD` returns an x402 payment challenge for signed evidence for one named XRPL token (issuer, funding stage, compliance shape), with a free preview.
- Payment terms are published only in <https://councilof.ai/.well-known/x402.json>; this card quotes no price. Payment buys delivery and freshness, never a result, and verifying anything stays free.

### Cite

```bibtex
@misc{csoai_gspc_reserve_attestation,
  title        = {GSPC — reserve attestation facts (ReserveFacts)},
  author       = {{CSOAI Ltd (Council of AI)}},
  year         = {2026},
  publisher    = {Hugging Face},
  url          = {https://huggingface.co/datasets/csoai/gspc-reserve-attestation},
  note         = {Zenodo DOI 10.5281/zenodo.21991104: UNAVAILABLE since 29 Sep 2026 (Zenodo blocked the CSOAI account; appeal pending; status https://councilof.ai/interop/zenodo-status.json). Cite the served methodology: https://councilof.ai/signed/HOW-TO-VERIFY.md. Measurement, not certification.}
}
```

Measurement, not certification. This card adds no score or ranking of any company. A row marked UNMEASURED has not been measured; it is not a pass.

<!-- /csoai-funnel-2026-09-27 -->


- SWIFT census (live): https://councilof.ai/api/swift
- XRPL reader (live): https://councilof.ai/api/xrpl

**MEASURED financial/domain axis** (deterministic-facts over live XRPL reader-16, n=16). Not a model leaderboard. No accuracy, no fleet, no leader. Reader: `GET https://councilof.ai/api/xrpl` (writes_board=false).

Frozen bank / coverage card on Hub. Live status is the `reserve-attestation` row on `GET https://councilof.ai/api/gspc`. **Not a certificate.** Not Archax/OpenEden — those are outside this reader-16.

**Tokenisation evidence question:** [What can an outsider verify after the Pontes launch?](https://huggingface.co/datasets/csoai/gspc-board/discussions/11) This XRPL reader-16 row does not measure a Pontes instrument or confer UK regulatory status; a named subject needs its own source-and-control packet.

Council of AI · CSOAI Ltd (GB, Companies House 16939677).

<!-- csoai-live-row -->
**Live measurement.** This bank stands behind the `reserve-attestation` row of the live GSPC board: `GET https://councilof.ai/api/gspc?axis=reserve-attestation` (family, kind, status and n are on that row, never typed here; the whole board is `GET https://councilof.ai/api/gspc`). Measurement, not certification.
<!-- /csoai-live-row -->

<!-- csoai-hubcard-v2 -->
## The live board is the authority

[![GSPC](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fcouncilof.ai%2Fapi%2Fgspc&query=%24.totals.public_count&label=GSPC%20board&color=0B1F33)](https://councilof.ai/api/gspc)
[![verify](https://img.shields.io/badge/verify%20a%20card-free%2C%20no%20account-0B1F33)](https://councilof.ai/gspc-verify)
[![DOI 10.5281/zenodo.21991104: Zenodo record unavailable](https://img.shields.io/badge/DOI%2010.5281%2Fzenodo.21991104-Zenodo%20record%20unavailable-8A6D00)](https://councilof.ai/methodology/)

`GET https://councilof.ai/api/gspc` — quote `totals.public_count`. This Hub card is a **printer** of that GET, never a second
engine. If the fetch fails the honest answer is `UNCHECKABLE` — never a fabricated `0.000`.
Status words: `LOADING` / `UNREACHABLE` / `UNMEASURED` / `UNCHECKABLE`.

**Lid:** Read `totals.public_count`, `totals.separation_public_count` and `totals.lid` from the [live board](https://councilof.ai/api/gspc) at access time. Measured does not mean a separated leader or a certificate.

<!-- csoai-capability-densify-2026-09-14-tui7 -->
## Capability + living GET (TUI7 distribution 2026-09-14)

**SUPERSEDED:** typed Hub triples `LIVE (re-GET /api/hub-cards → counts.*)` (and prior 885/900/937/1113/1182/1185) — do not re-paste. Hub cite = live GET only.

```
Live board: GET https://councilof.ai/api/gspc → quote totals.public_count / totals.lid (derived live from totals, never typed as a frozen paste)
Hub cards: GET https://councilof.ai/api/hub-cards → quote counts.cells / counts.measured / counts.unmeasured LIVE (no typed Hub triple)
Hub bank: https://huggingface.co/datasets/csoai/gspc-hub-cards
Free verify: https://councilof.ai/gspc-verify
Discovery: GET https://councilof.ai/.well-known/x402.json (live · Base · USDC)
OX discovery resources: councilof 0/60 honest — do not invent rows
Measurement, never certification. Printer only — no axis mine on ZeroGPU. A100 COLD.
```

[![GSPC board](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fcouncilof.ai%2Fapi%2Fgspc&query=%24.totals.public_count&label=GSPC%20board&color=0B1F33)](https://councilof.ai/api/gspc)
[![Hub cells](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fcouncilof.ai%2Fapi%2Fhub-cards&query=%24.counts.cells&label=Hub%20cells&color=0B1F33)](https://councilof.ai/api/hub-cards)

### Council of AI — GSPC + Hub printer
- Living board: https://councilof.ai/api/gspc — quote `totals.public_count` / `totals.lid` (never invent MEASURED)
- Hub cite: https://councilof.ai/api/hub-cards — **re-GET**; quote `counts.*` (typed `LIVE (re-GET /api/hub-cards → counts.*)` SUPERSEDED 2026-09-14)
- Hub dataset bank: https://huggingface.co/datasets/csoai/gspc-hub-cards
- Verify free: https://councilof.ai/gspc-verify
- x402 discovery: https://councilof.ai/.well-known/x402.json
- Catalog: https://councilof.ai/api/x402
- Free door (amount 0): https://councilof.ai/api/free-door
- Jail goldbank: https://huggingface.co/datasets/csoai/gspc-jail-goldbank
- Human: free + x402 PAYG · Coming—Paddle not live · never Stripe
- Agents: payTo is merchant receive — never the signer
- Self-settle proves the rail; stranger revenue is separate (do not invent buyers)
- Measurement, not certification. Never sell a rank. Never certify.

Any Hub `x402.json` in a CSOAI printer is a byte-mirror of the living well-known GET — **not a second authority**.
<!-- /csoai-capability-densify-2026-09-14-tui7 -->

<!-- csoai-wave-e-openapi-2026-09-07 -->
### OpenAPI / CDP discovery (apex · Wave E)

```
OpenAPI (canonical): GET https://councilof.ai/openapi.json  → version 0.2+6c709613dc31 · 97 paths
NOT: https://councilof.ai/public/openapi.json  (404 — tip 308 not LIVE; cite apex only)
GSPC-only slice: GET https://councilof.ai/api/openapi.json  (7 paths — not CDP paid catalog)
x402 discovery: GET https://councilof.ai/.well-known/x402.json  (mode live · Base eip155:8453 · USDC)
Catalog: GET https://councilof.ai/api/x402
Living board: GET https://councilof.ai/api/gspc → quote totals.public_count and totals.separation_public_count at access time
Verify free: https://councilof.ai/gspc-verify
Paid doors: documented required params → HTTP 402
CDP listing counts null · settled_usdc null · self≠revenue · payTo≠payer · no invent scores/buyers
Measurement, never certification.
```
<!-- /csoai-wave-e-openapi-2026-09-07 -->



**This repository:** **MEASURED (deterministic facts)** — this repository mirrors the live `reserve-attestation` slot (**ReserveFacts**, is third-party reserve-attestation language on a retrieved issuer page? (PASS/FAIL/UNCHECKABLE)). Live `n` at card refresh: **16** (issuer accounts (not bank items)) (2026-09-04T04:33:29Z). No model, no score, no ranking.

| | |
|---|---|
| Live board (authority) | <https://councilof.ai/api/gspc> |
| Verify a card — free, no account | <https://councilof.ai/gspc-verify> |
| How to verify, by hand | <https://councilof.ai/signed/HOW-TO-VERIFY.md> |
| Transparency root (Merkle) | <https://councilof.ai/root.json> |
| Every CSOAI repo on the Hub | <https://huggingface.co/csoai> |
| Methodology DOI | 10.5281/zenodo.21991104 (Zenodo record unavailable since 29 Sep 2026: account blocked by Zenodo; appeal pending. Live methodology page (not the deposit's bytes): <https://councilof.ai/methodology/>) |
| MCP endpoint — 12 tools, verified 2026-09-04T04:33:29Z | `POST https://councilof.ai/mcp` |
| MCP Registry | `io.github.CSOAI-ORG/gspc` — version not pinned here; the registry is the authority |
| npm — MCP server | [`csoai-gspc-mcp`](https://www.npmjs.com/package/csoai-gspc-mcp) — `npx -y csoai-gspc-mcp`. No version is pinned here: ask the registry for the current one rather than trusting a number written on a card. |
| Python reader + card verifier | `pip install "csoai-gspc[verify]"` then `csoai-gspc check` — re-derives the board totals from the axis array and exits non-zero if they disagree |
| This board as a dated, citable snapshot | 10.5281/zenodo.22293341 (Zenodo record unavailable since 29 Sep 2026: account blocked by Zenodo; appeal pending. Live board dataset (not the deposit's bytes): <https://huggingface.co/datasets/csoai/gspc-board>) |

## What is in this repository

| file | bytes | rows | what |
|---|---:|---:|---|
| `README.md` | 2383 |  | card |
| `input-schema.json` | 1585 |  | JSON document |
| `coverage-card.json` | 1140 |  | JSON document |
| `eval.yaml` | 785 |  | config |
| `skeleton.json` | 726 |  | JSON document |
| `tui-pack-skeleton.json` | 602 |  | JSON document |
| `manifest.jsonl` | | 7 | derived at 2026-09-04T04:33:29Z |
| `axis-live.jsonl` | | 1 | derived at 2026-09-04T04:33:29Z |

`manifest.jsonl` is derived from this repository's own file tree at 2026-09-04T04:33:29Z; it lists every file with its
size, its blob hash and a direct URL, so an agent can enumerate the repo without cloning it.
`axis-live.jsonl` is a one-row snapshot of this axis as the live board returned it at that moment. It is a snapshot, not the authority.

## Citation

```bibtex
@misc{csoai_gspc_gspc_reserve_attestation,
  title        = {GSPC — reserve attestation facts (ReserveFacts)},
  author       = {{CSOAI Ltd}},
  year         = {2026},
  doi_status   = {Zenodo DOI 10.5281/zenodo.21991104: UNAVAILABLE since 29 Sep 2026 (Zenodo blocked the CSOAI account; appeal pending; status https://councilof.ai/interop/zenodo-status.json). Cite the served methodology: https://councilof.ai/signed/HOW-TO-VERIFY.md},
  howpublished = {Hugging Face Hub, \url{https://huggingface.co/datasets/csoai/gspc-reserve-attestation}},
  note         = {Live board: https://councilof.ai/api/gspc. Measurement, not certification.}
}
```

---

**Measurement, not certification.** No slot is for sale and no empty slot is filled by payment.
Issued by CSOAI Ltd (England & Wales, Companies House **16939677**), 3rd Floor, 86–90 Paul Street,
London EC2A 4NE. Card refreshed 2026-09-04T04:33:29Z; every number above is either fetched live or carries the
timestamp at which it was read.
<!-- /csoai-hubcard-v2 -->

## Correction — coverage-card.json understates this axis

`coverage-card.json` in this repo states **`status: UNMEASURED`, `n: 0`** for
`reserve-attestation`. The live board disagrees, and the board is right:

| source | status | n | bench |
|---|---|---|---|
| `coverage-card.json` (signed, this repo) | UNMEASURED | 0 | — |
| [`GET /api/gspc`](https://councilof.ai/api/gspc) (authority) | **MEASURED** | **16** | ReserveFacts |

Evidence for the board's figure:
<https://councilof.ai/interop/financial-measure-run-reserve-attestation.json>

The coverage card appears to be a template written when this dataset was created
(2026-09-05T00:11Z), independent of the measurement run it describes
(dated earlier). It is **signed**, and this estate does not edit signed
bytes — a silent correction to a signed artefact is the fault this ledger-keeping exists to
prevent. So the card stays as issued and the correction is published here instead.

**Cite the live board, not the card, for this axis.** Verification is free at
<https://councilof.ai/gspc-verify>. Measurement, not certification.

*Correction published 2026-09-05 by an automated audit comparing every coverage card in the
csoai GSPC datasets against the live board. 7 of 8 disagreed in the same direction.*

<!-- csoai-wrapper-finfact-densify-2026-09-14 -->
## Wrapper doors + financial-fact runs (free densify 2026-09-14)

```
Live board: GET https://councilof.ai/api/gspc → quote totals.public_count and totals.separation_public_count at access time
Lid: GET https://councilof.ai/api/gspc → quote totals.lid at access time; measured is not a separated leader or a certificate.
Hub cards: GET https://councilof.ai/api/hub-cards → quote counts.cells/measured/unmeasured LIVE (no typed triple)
Wrappers ledger (FREE HTML): https://councilof.ai/wrappers/
Wrapper door (metered x402): https://councilof.ai/api/wrapper?id=<wrapped-symbol:chain> — LIVE challenge https://councilof.ai/api/wrapper?id=usdc.e:arbitrum (402)
Free preview: https://councilof.ai/api/wrapper?id=usdc.e:arbitrum&preview=1 (200 preview card)
Verify: https://councilof.ai/gspc-verify
Eight financial-family axes are deterministic fact runs, not leader scores; effect-binding adds a GSPC-family fact run. Read the current axis array and totals.fact_runs from GET /api/gspc.
Measurement, never certification. No invent MEASURED. Printer only.
```
<!-- /csoai-wrapper-finfact-densify-2026-09-14 -->

<!-- csoai-cite-v1:start -->
## Objections, contact and corrections

To object to a row, ask for a re-check, request a correction or ask for a record to be withdrawn, email **nicholas@csoai.org** or use the appeals and dispute route at https://councilof.ai/dispute/. Corrections are listed in the corrections ledger at https://councilof.ai/api/corrections, with what changed and when. CSOAI Ltd (company no. 16939677, England and Wales) is the accountable publisher.

## How to cite

CSOAI Ltd (Council of AI). *GSPC — reserve attestation facts (ReserveFacts)*. 2026. Hugging Face dataset `csoai/gspc-reserve-attestation`. https://huggingface.co/datasets/csoai/gspc-reserve-attestation. DOI: [10.57967/hf/10284](https://doi.org/10.57967/hf/10284)

```bibtex
@misc{csoai_gspc_reserve_attestation,
  title        = {GSPC — reserve attestation facts (ReserveFacts)},
  author       = {{CSOAI Ltd}},
  year         = {2026},
  howpublished = {Hugging Face dataset, https://huggingface.co/datasets/csoai/gspc-reserve-attestation},
  doi          = {10.57967/hf/10284},
  note         = {Corrections: https://councilof.ai/api/corrections}
}
```

Licence: CC-BY-4.0. Attribute Council of AI, CSOAI Ltd (16939677), https://councilof.ai.

## Corrections and verification

- Corrections ledger (signed): https://councilof.ai/api/corrections. Corrections to CSOAI's published records are logged there with what changed and when.
- Verify a signed record yourself, free and without an account: https://councilof.ai/gspc-verify/ (step by step: https://councilof.ai/signed/HOW-TO-VERIFY.md).
- Conformance kit for signed-receipts/v1, with test vectors for implementers: https://councilof.ai/spec/signed-receipts/v1/conformance/
<!-- csoai-cite-v1:end -->

<!-- csoai-archive-by-axis:start 2026-10-06 -->
## Signed archive by axis (measurement, never certification)

Source: https://councilof.ai/signed/card_index.json (schema csoai.gspc-card-index/0.1, packaged 2026-08-28T15:39:25Z). Existing signed units only; measured is not scored; supply-led, never a grade.

| Axis | Signed cards | Distinct models | Sample signed card |
|---|---:|---:|---|
| `arc-30` | 23 | 23 | https://councilof.ai/signed/cards/eeb12ba044e7d474b92ed5c379cafba5005a7e8f720ed8cd52e5a92ed1435536.json |
| `care` | 23 | 23 | https://councilof.ai/signed/cards/e5b5ec5f0d5b7f4d772276d11197f9cd22b339f287bc0bc61ea784749bd8100f.json |
| `care-refusal-help` | 27 | 27 | https://councilof.ai/signed/cards/acf6bf0356123632758bf6c98c83d81c7a8392c3b111b311317c516cc65133a4.json |
| `care-refusal-protect` | 27 | 27 | https://councilof.ai/signed/cards/82994353b8f94337746ddf73700b0edc425d695d43910dbfeb53d118d5a09a1c.json |
| `gov` | 23 | 23 | https://councilof.ai/signed/cards/0db9c146ab2c5488a83946529e6c527d4ad9e98418c29f341e3be3ee6100b996.json |
| `gsm8k-30` | 23 | 23 | https://councilof.ai/signed/cards/5f9ea3e964a9cad3e85fb51c4453c4d5c89208584825b3f17e9a9fc32346830b.json |
| `gspc-conformance` | 21 | 21 | https://councilof.ai/signed/cards/32df7c2b25d7306e30efdfc25a6d2a1c17a951071e2567e19db475b86214b17d.json |
| `gspc-continuity` | 21 | 21 | https://councilof.ai/signed/cards/58bd1deacf1422a805816242176ae63e688307ee767cc384e44a96fac114a5f1.json |
| `gspc-governance` | 21 | 21 | https://councilof.ai/signed/cards/1390baba7c0507ddd6ec85088b3a9763c1b7d929aa01ca298414478ff90b356d.json |
| `gspc-openness` | 21 | 21 | https://councilof.ai/signed/cards/75c0f83d849121a8bf43306d10591cbba15465816e7364438af25a5d0401ac3d.json |
| `gspc-provenance` | 21 | 21 | https://councilof.ai/signed/cards/35a4eb2b69dfe03fad8aa082a6ab0845f506d03218ea3c1bece93337cb427bca.json |
| `gspc-safety` | 21 | 21 | https://councilof.ai/signed/cards/5dfe7d868d252689ff4d5eabb9cad17587f797ddbd8fce26a63b7f5227c29373.json |
| `jail-escape-detection` | 8 | 8 | https://councilof.ai/signed/cards/acec0ee7b86c1385e0455660ea1f2f23bfccc904a1b68308263a5e2eb982fa57.json |
| `mmlu-30` | 23 | 23 | https://councilof.ai/signed/cards/e9dfb663c9156e6540da491d87e21a061c25271ee9ff9f8a563126af784fe34d.json |
| `swag-30` | 25 | 25 | https://councilof.ai/signed/cards/30d86609e50d82ecf7527feb27f83bbc64190bc4ea32c4dcf3d6f07a07addec4.json |
| `swarm-candidates` | 7 | 7 | https://councilof.ai/signed/cards/8591fdc18b6b7cbd0513c3306d59bc6624f4e93bcafe2ce4326691a2a79ad891.json |

**Totals:** 335 signed cards · 16 card_index axes · 335/335 cards HTTP 200 · 64 distinct public model names.

**Live lids (re-GET 2026-10-06T01:13Z):**
- `GET https://councilof.ai/signed/card_index.json` → n_cards=335
- `GET https://councilof.ai/api/gspc` → 23 axes · 23 measured
- `GET https://councilof.ai/api/hub-cards` → 384/384/0 (cells/measured/unmeasured)

**Connect:** Primary MCP: https://councilof.ai/mcp

**Verify (free):** https://councilof.ai/gspc-verify/ · method https://councilof.ai/signed/HOW-TO-VERIFY.md

Zenodo DOI 10.5281/zenodo.21991104: UNAVAILABLE since 29 Sep 2026 (Zenodo blocked the CSOAI account; appeal pending; status https://councilof.ai/interop/zenodo-status.json). Cite the served methodology: https://councilof.ai/signed/HOW-TO-VERIFY.md

Caveat: do not fuse card_index axes (16) with board axes (23) or Hub cells (384); they are three different counts. Per-card values are point-in-time; never compare a card's accuracy to the live board as one number. RunPod pod outputs are UNSIGNED and are not counted or cited.
<!-- csoai-archive-by-axis:end 2026-10-06 -->

<!-- csoai-smithery-connect-honest-2026-10-05 -->
## Smithery / MCP Connect (measured 2026-10-05 — not a certification)

- **Primary Connect (free tools):** `https://councilof.ai/mcp` — initialize **200**; call `tools/list`. Prefer this URL in every agent config.
- **Smithery discovery:** https://smithery.ai/servers/csoai/gspc-mcp — external release lists upstream `https://councilof.ai/mcp`. Registry `deploymentUrl` remains the Smithery gateway (`https://gspc-mcp--csoai.run.tools`); POST without bearer → **401**. That is gateway-by-design — **do not claim the registry points at the council door**.
- **Stale duplicate `csoai/gspc`:** UI `/servers/csoai/gspc` **404** after unlist attempt; registry row may still exist with run.tools **401**. Prefer only `csoai/gspc-mcp` for discovery.
- Measurement only. Never invent that registry `deploymentUrl` equals `councilof.ai/mcp`. Never certify.
<!-- /csoai-smithery-connect-honest-2026-10-05 -->
