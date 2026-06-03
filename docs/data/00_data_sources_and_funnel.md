# Data Sources and Sample Funnel

## Current Position

This project is a China replication audit of Qian et al.'s GenAI announcement supplier market-reaction design. The current data work has completed broad CNINFO full-text retrieval, A-share filtering, priority candidate construction, and PDF download/text extraction. It has not yet completed manual event validation.

Current funnel as of 2026-06-03:

| Stage | Rows | Announcements | Firms |
|---|---:|---:|---:|
| CNINFO raw query hits | 280,662 | 111,935 | 5,359 |
| CNINFO deduplicated announcements | 111,935 | 111,935 | 5,359 |
| A-share formal rows | 111,685 | 111,685 | 5,327 |
| Candidate pool for manual review | 13,900 | 13,900 | 2,306 |
| Priority manual event candidates | 1,289 | 1,289 | 640 |
| Priority top3 PDF audit pool | 1,055 | 1,055 | 640 |
| PDF/text extraction success | 1,055 | 1,055 | 640 |
| Machine-likely Qian-style initiatives | 106 | 106 | 91 |
| Review-possible or backfill pool | 921 | 921 | 575 |

The `111,685` A-share rows are not the human-reading sample. They are a broad formal-disclosure universe produced by CNINFO title+full-text retrieval. The current high-precision human-reading sample is the `1,055` priority PDF pool, with a stricter first pass on the 106 machine-likely initiatives.

## Critical Funnel Concern: 111,685 to 1,055

The largest unresolved data-risk is the shrinkage from `111,685` A-share formal rows to the `1,055` PDF audit pool. This is not a single mechanical filter. It combines strict GenAI-context filtering, action/title prioritization, and per-firm top3 selection.

| Step | Rows | Interpretation | Leakage Risk |
|---|---:|---|---|
| A-share formal rows | 111,685 | Broad CNINFO title+full-text universe with valid A-share code and PDF URL | Starting universe |
| Exclude no strict GenAI context after snippet | 97,083 | Keyword retrieval hits without retained strict GenAI context in the normalized metadata/snippet fields | Must be sampled; this is the largest exclusion |
| Review denial or uncertain GenAI | 702 | Denial, clarification, attention-only, or uncertain GenAI context | Lower, but should be spot-checked |
| Strict GenAI context without action | 5,089 | GenAI terms appear, but current metadata rules do not detect launch/adoption/investment/cooperation/action language | High; action-pattern leakage is plausible |
| Backfill or noisy document with action | 7,522 | Action language appears, but title looks like annual report, meeting material, advisor opinion, financing support, inquiry reply, or another noisy/backfill document | High; may contain true initiatives or first-date clues |
| Priority manual event candidates | 1,289 | Strict GenAI context, action language, and title not flagged as noisy/backfill | High-precision candidate layer |
| Priority top3 PDF audit pool | 1,055 | First three priority candidates per firm, covering 640 firms | Moderate; drops 234 priority rows after the third candidate |

Therefore, `1,055` should be understood as the current high-precision audit pool, not proof that the other `110,630` rows are irrelevant. The immediate audit question is whether the `5,089` and `7,522` middle layers contain many true Qian-style initiatives.

Recommended leakage audit:

1. Randomly sample 100 rows from the `97,083` excluded-no-strict-context layer.
2. Randomly sample 150 rows from the `5,089` strict-context-without-action layer.
3. Randomly sample 200 rows from the `7,522` backfill/noisy-with-action layer.
4. Compare top3, top5, and top10 per-firm candidate pools before finalizing the human-review workload.
5. If leakage is low, proceed with the 1,055-row PDF audit pool. If leakage is high, expand the review pool before claiming a Qian-style replication sample.

## Provisional Event-Study Use of the 1,055 Pool

The `1,055` PDF pool can be used for a preliminary POM/Qian-style main-effect run, but only as a diagnostic.

Acceptable use:

- stress-test whether the supplier-linking and AR/CAR pipeline runs on the rebuilt CNINFO event source;
- compare three noisy treatment definitions: all 1,055 priority PDFs, 106 machine-likely initiatives, and the broader possible/backfill pool;
- check whether signs are grossly positive, zero, or negative before manual coding;
- identify where supplier-link coverage collapses.

Not acceptable use:

- do not describe the 1,055 rows as final GenAI initiative announcements;
- do not interpret coefficients as a successful or failed replication before manual coding;
- do not use the 1,055-row run as the final main table.

The output should be labeled `pre-manual-coding diagnostic`.

## Main Event Source: CNINFO

The main China source for this replication is CNINFO / 巨潮资讯网 title+full-text search.

Rationale:

- CNINFO captures official A-share disclosure documents and provides stable stock-code matching, announcement dates, titles, and PDF URLs.
- For a China replication, formal announcement timing is easier to audit than general media reporting.
- It is institutionally different from Qian et al.'s U.S. newswire sample, so the paper should label this as a CNINFO formal-disclosure replication rather than a pure newswire replication.

Limitations:

- CNINFO is a formal disclosure portal, not a press-release/newswire source.
- Product launches, cooperation news, model releases, and conference announcements may first appear on company websites, official WeChat accounts, or securities media before CNINFO.
- CNINFO full-text search pulls in many non-event documents, including annual reports, meeting materials, advisor opinions, financing documents, ESG/internal-control reports, and inquiry replies.

## Supplementary Source: Qualified Securities Disclosure Media

As a China-specific supplement to CNINFO, the project should use the media list under CSRC Announcement No. 61 (2020), "具备证券市场信息披露条件的媒体名单".

The working list is:

| Medium | Website |
|---|---|
| 金融时报 | `www.financialnews.com.cn` |
| 经济参考报 | `www.jjckb.cn` |
| 中国日报 | `www.chinadaily.com.cn` |
| 中国证券报 | `www.cs.com.cn` |
| 证券日报 | `www.zqrb.cn` |
| 上海证券报 | `www.cnstock.com` |
| 证券时报 | `www.stcn.com` |

Official source: [CSRC Announcement No. 61 (2020)](https://www.csrc.gov.cn/csrc/c101950/c1047981/content.shtml).

These media are not treated as equivalent to U.S. PR Newswire / Business Wire / GlobeNewswire. They are used as trace-back and supplementation sources when:

- a CNINFO document appears to be a later support document rather than the first public initiative date;
- a company initiative was publicly announced through qualified securities media before appearing in CNINFO;
- a CNINFO title/full-text hit is ambiguous and needs external corroboration.

## Why Not Use General Financial News as the Main Source

General financial-news databases such as CSMAR news, CNRDS, Wind, Choice, and iFinD can be useful lead sources, but they are not the main event source for this replication.

Reason:

- Many records in those databases are media-written reports, reposts, summaries, or secondary interpretations.
- Qian et al. identify firm announcements through leading news agencies; the treatment is a public firm initiative announcement, not any third-party media discussion of GenAI.
- For this China replication, media reports should be traced back to a company action, formal announcement, official release, or qualified securities disclosure medium before being coded as treatment.

## Event Coding Rule

An event is eligible only if manual review verifies all of the following:

1. The A-share listed firm is the acting firm.
2. The disclosure describes a concrete GenAI initiative.
3. The initiative involves launch, adoption, deployment, product/service integration, model/service filing, investment, contract, strategic cooperation, or identifiable workflow/product implementation.
4. The event date is the first public date that investors could observe, using CNINFO date by default and qualified securities media/company releases only when they clearly precede CNINFO.
5. The event is not only denial, "关注/探索" boilerplate, generic AI discussion, industry-background writing, or an investor-question-only keyword hit.

## Next Data Audit

Before final event-study rerun:

1. Run the leakage audit for the `111,685 -> 1,055` shrinkage.
2. Run a pre-manual-coding diagnostic event study on the 1,055 PDF pool.
3. Manually code the 106 machine-likely initiatives.
4. Manually code `review_possible_initiative` and `review_backfill_or_support_doc` rows from the 921-row review pool.
5. For backfill/support documents, trace the event to CNINFO or qualified securities media first-public dates.
6. Keep both source flags in the final event table: `source_primary = CNINFO` and `source_supplement = qualified_media/company_release` when applicable.
