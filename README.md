# 23-T05-qian-supplier-replication-cn

This repository contains the China replication audit for Qian et al.'s GenAI announcement supplier market-reaction design.

## Research Target

Replicate the minimum main effect:

> When a focal customer announces a concrete GenAI initiative, do its pre-existing listed suppliers earn positive abnormal returns around the event date?

This repository is an audit and replication workspace, not a standalone paper narrative.

## Design Boundary

- Main event source is CNINFO title+full-text search and PDF audits. Qualified securities disclosure media are supplementary trace-back sources when they clearly identify an earlier public initiative date.
- The preferred China window is `2023-2026-06-03`, with `2023-2024` retained as the US-comparable window.
- Treatment must be a concrete GenAI initiative, not denial, boilerplate attention, or investor-question-only keyword matching.
- Raw PDFs, extracted full text, and large downloaded datasets are intentionally excluded.

## Docs Structure

- `docs/data/`: data sources, sample funnel, and empirical run logs.
- `docs/theory/`: theory transfer from Qian et al. to China.
- `docs/research_question/`: replication scope and research question.
- `docs/identification/`: event-study design choices and threats.

## Main Pipeline

1. `scripts/run_v23_qian_supplier_replication_20260602.py`
   - Baseline Qian-style supplier event-study audit from the existing v21 panel.
2. `scripts/build_v24_qian_initiative_event_rebuild_20260602.py`
   - Diagnoses the old event-definition problem and rebuilds candidate initiative labels.
3. `scripts/build_v25_cninfo_formal_event_rebuild_20260602.py`
   - First CNINFO formal-announcement rebuild.
4. `scripts/build_v26_cninfo_fulltext_harvest_20260603.py`
   - CNINFO title+full-text harvest for 2023-2026.
5. `scripts/build_v27_cninfo_priority_pdf_audit_20260603.py`
   - PDF download/text audit for the priority candidate pool.

## Key Outputs

- `docs/data/00_data_sources_and_funnel.md`
- `docs/theory/00_theory_mapping.md`
- `docs/research_question/00_research_question.md`
- `docs/identification/00_identification_design.md`
- `docs/data/empirical_runs/86_v23_qian_supplier_replication_20260602.md`
- `docs/data/empirical_runs/87_v24_qian_initiative_event_rebuild_20260602.md`
- `docs/data/empirical_runs/88_v25_cninfo_formal_event_rebuild_20260602.md`
- `docs/data/empirical_runs/89_v26_cninfo_fulltext_harvest_20260603.md`
- `docs/data/empirical_runs/90_v27_cninfo_priority_pdf_audit_20260603.md`
- `docs/data/empirical_runs/91_v27_cninfo_priority_pdf_audit_2023_2026_20260603.md`

The most useful manual-review files are:

- `results/v27_cninfo_priority_pdf_audit_2023_2026_20260603/manual_review_likely_qian_initiatives.csv`
- `results/v27_cninfo_priority_pdf_audit_2023_2026_20260603/manual_review_possible_or_backfill.csv`
- `results/v27_cninfo_priority_pdf_audit_2023_2026_20260603/manual_review_priority_pdf_all.csv`

## Current Audit Counts

As of 2026-06-03:

- CNINFO deduplicated announcement metadata: 111,935 announcements.
- A-share announcement rows: 111,685.
- Priority PDF audit pool: 1,055 announcements from 640 firms.
- Successful PDF/text extraction: 1,055.
- Machine-likely Qian-style initiatives: 106 announcements from 91 firms.
- Review-possible or backfill pool: 921 announcements from 575 firms.

## Excluded Local Data

The following local folders are not committed:

- Raw CNINFO PDF/text cache under `data/raw/`.
- Full CNINFO query-hit tables under `data/raw/` or uncommitted generated outputs.
- CSMAR source data.
- Market-return panels and supply-chain raw tables.
