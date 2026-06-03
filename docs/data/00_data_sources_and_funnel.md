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

The `111,685` A-share rows are not the human-reading sample. They are a broad formal-disclosure universe produced by CNINFO title+full-text retrieval. The current human-reading sample is the `1,055` priority PDF pool, with a stricter first pass on the 106 machine-likely initiatives.

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

1. Manually code the 106 machine-likely initiatives.
2. Manually code `review_possible_initiative` and `review_backfill_or_support_doc` rows from the 921-row review pool.
3. For backfill/support documents, trace the event to CNINFO or qualified securities media first-public dates.
4. Run a leakage audit by sampling excluded rows from the 13,900 candidate pool and the large excluded pool.
5. Keep both source flags in the final event table: `source_primary = CNINFO` and `source_supplement = qualified_media/company_release` when applicable.

