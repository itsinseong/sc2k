---
license: other
license_name: original-publishers
license_link: https://github.com/gcf3711/audit-report-archive
language:
  - en
tags:
  - security
  - smart-contracts
  - audit-reports
  - blockchain
  - solidity
pretty_name: Smart Contract Audit Report Archive
size_categories:
  - 1K<n<10K
---

# Smart Contract Audit Report Archive

An archive of **6,153 public smart-contract audit reports** from 22 audit
firms and contest platforms, collected 2026-07-06. Metadata, provenance and
the collection pipeline live in the companion GitHub repo:
**https://github.com/gcf3711/audit-report-archive**

## Layout

```
reports/<source>/<report>.{pdf,html}   the report files
catalog/<source>.json                  per-report metadata
```

Each catalog entry records project, date, canonical source URL
(`report_url`), download URL, sha256 and file size — see the GitHub README
for the full schema. `local_path` values (`data/reports/...`) map to
`reports/...` here.

## Sources

ChainSecurity, Trail of Bits, MixBytes, Certora, Spearbit, Cantina,
Quantstamp, Sigma Prime, OpenZeppelin, PeckShield, Code4rena, ABDK,
Statemind, Halborn, Omniscia, Zellic, Runtime Verification, Pessimistic,
ConsenSys Diligence, Nethermind, Cyfrin, Sherlock.

## Download

```bash
hf download gcf3711/audit-report-archive --repo-type dataset \
    --include 'reports/*' --local-dir data
```

## License / copyright

The reports are publicly published documents whose copyright remains with
the respective audit firms. This dataset redistributes them unmodified for
research purposes, with per-file provenance URLs in `catalog/`. If you are a
rights holder and want a file removed, open an issue on the GitHub repo.
