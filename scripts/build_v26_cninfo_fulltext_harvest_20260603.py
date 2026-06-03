#!/usr/bin/env python3
"""Harvest CNINFO top-search fulltext GenAI announcement metadata.

This run is deliberately metadata-first. CNINFO fulltext search has enough
recall for a Qian-scale event funnel, but downloading every matched PDF would
mostly collect periodic reports, inquiry replies, advisor opinions, and other
backfill documents. The safer workflow is:

1. Harvest all search-result metadata and snippets for 2023-2026.
2. Deduplicate announcements across search terms.
3. Flag likely event-source candidates versus noisy backfill documents.
4. Download PDFs only for the shortlisted manual-review pool in a later step.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import math
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUN_TAG = "20260603"
OUT_DIR = ROOT / "results" / f"v26_cninfo_fulltext_harvest_{RUN_TAG}"
DOC_PATH = ROOT / "docs" / "empirical_runs" / f"89_v26_cninfo_fulltext_harvest_{RUN_TAG}.md"
RAW_DIR = ROOT / "data" / "raw" / f"cninfo_fulltext_harvest_{RUN_TAG}"
RAW_JSON_DIR = RAW_DIR / "raw_json"

SEARCH_URL = "https://www.cninfo.com.cn/new/fulltextSearch/full"
STATIC_BASE = "https://static.cninfo.com.cn/"
SEARCH_PAGE = "https://www.cninfo.com.cn/new/fulltextSearch"

START_DATE = "2023-01-01"
END_DATE = "2026-06-03"
PAGE_SIZE = 100
DEFAULT_DELAY_SECONDS = 0.15


@dataclass(frozen=True)
class QueryTerm:
    term: str
    tier: str


# `人工智能` is intentionally excluded from the default harvest. It is useful
# for broad AI projects but not for a Qian-style GenAI initiative treatment.
QUERY_TERMS = [
    QueryTerm("大语言模型", "core_recall"),
    QueryTerm("语言大模型", "core_recall"),
    QueryTerm("生成式AI", "core_recall"),
    QueryTerm("AIGC", "core_recall"),
    QueryTerm("ChatGPT", "core_recall"),
    QueryTerm("GPT", "core_recall"),
    QueryTerm("DeepSeek", "core_recall"),
    QueryTerm("通义千问", "named_model"),
    QueryTerm("文心一言", "named_model"),
    QueryTerm("讯飞星火", "named_model"),
    QueryTerm("星火认知", "named_model"),
    QueryTerm("盘古大模型", "named_model"),
    QueryTerm("腾讯混元", "named_model"),
    QueryTerm("豆包", "named_model"),
    QueryTerm("Kimi", "named_model"),
    QueryTerm("智谱", "named_model"),
    QueryTerm("百川智能", "named_model"),
    QueryTerm("生成式人工智能", "zero_or_exact_check"),
    QueryTerm("生成式人工智能服务", "zero_or_exact_check"),
    QueryTerm("大模型", "broad_genai_recall"),
    QueryTerm("混元大模型", "broad_genai_recall"),
    QueryTerm("模型备案", "registry_recall"),
]

CORE_TIERS = {"core_recall", "named_model", "zero_or_exact_check"}
NO_BROAD_TIERS = {"core_recall", "named_model", "zero_or_exact_check"}

ALLOWED_PAGE_COLUMNS = {"SZZB", "SZCY", "SHZB", "SHKCB", "BJS"}
A_SHARE_CODE_PAT = re.compile(r"^(?:(?:000|001|002|003|300|301|600|601|603|605|688)\d{3}|[489]\d{5})$")
MAIN_A_SHARE_CODE_PAT = re.compile(r"^(000|001|002|003|300|301|600|601|603|605|688)\d{3}$")

STRICT_GENAI_TERMS = [
    "生成式人工智能",
    "生成式AI",
    "生成式 AI",
    "AIGC",
    "ChatGPT",
    "GPT",
    "DeepSeek",
    "大语言模型",
    "大型语言模型",
    "语言大模型",
    "大模型",
    "AI大模型",
    "多模态大模型",
    "基础大模型",
    "垂直大模型",
    "行业大模型",
    "模型备案",
    "生成式人工智能服务备案",
    "生成式人工智能服务登记",
    "通义千问",
    "文心一言",
    "讯飞星火",
    "星火认知",
    "盘古大模型",
    "混元大模型",
    "腾讯混元",
    "豆包",
    "Kimi",
    "智谱",
    "百川智能",
]

ACTION_PAT = re.compile(
    r"发布|推出|上线|接入|集成|部署|适配|落地|应用|商业化|备案通过|通过备案|"
    r"服务备案|服务登记|登记|签署|合作|共建|投资|建设|采购|中标|"
    r"成立|设立|收购|研发|升级|启动|发布会|产品|平台|解决方案|"
    r"launch|release|deploy|integrat",
    re.I,
)
DENIAL_PAT = re.compile(r"暂无|尚无|不涉及|未涉及|没有.*业务|无.*业务|不存在|澄清|风险提示|不构成")
WEAK_ATTENTION_PAT = re.compile(r"密切关注|持续关注|积极关注|探索|研究相关机会|以公告为准|敬请关注")
COMPANY_ACTOR_PAT = re.compile(r"公司|本公司|子公司|控股子公司|全资子公司|集团|股份有限公司|有限公司|拟|已|将")
STRICT_GENAI_PAT = re.compile("|".join(re.escape(t) for t in sorted(STRICT_GENAI_TERMS, key=len, reverse=True)), re.I)

TITLE_EXCLUDE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("periodic_report", re.compile(r"年度报告|年报|半年度报告|半年报|季度报告|一季度报告|三季度报告|中期报告|董事会工作报告|监事会工作报告")),
    ("esg_or_internal_control_report", re.compile(r"社会责任报告|ESG|可持续发展报告|环境、社会|环境社会|社会及治理|内部控制评价报告|内部控制自我评价报告")),
    ("annual_or_interim_summary", re.compile(r"年度报告摘要|半年度报告摘要|季度报告正文|摘要")),
    ("trading_anomaly_or_value_plan", re.compile(r"股票交易异常波动|异常波动公告|质量回报双提升|业绩预告")),
    ("governance_meeting_materials", re.compile(r"股东大会材料|股东大会文件|独立董事.*述职|董事会决议公告|监事会决议公告|董事会报告|公司章程")),
    ("financing_or_incentive_support", re.compile(r"方案论证分析报告|发行股票方案|持续督导|限制性股票|股票激励计划|员工持股计划|考核管理办法|募集资金|募投项目")),
    ("performance_meeting_or_ir", re.compile(r"业绩说明会|投资者关系|调研活动|机构调研|网上集体接待日|接待日活动|活动记录表")),
    ("exchange_inquiry_or_reply", re.compile(r"问询函|回复函|审核问询|监管工作函|关注函|问询|反馈意见|落实函")),
    ("advisor_opinion", re.compile(r"核查意见|法律意见书|保荐|独立财务顾问|审计报告|评估报告|评级报告|专项意见")),
    ("offering_or_listing_document", re.compile(r"募集说明书|招股说明书|上市公告书|发行保荐书|发行股份|重组报告书|购买资产")),
    ("risk_or_commitment_filler", re.compile(r"摊薄即期回报|填补措施|承诺|风险提示|说明公告|澄清公告")),
    ("fund_or_index", re.compile(r"基金|交易型开放式指数|ETF|做市服务|招募说明书|基金合同|托管协议|产品资料概要")),
    ("shareholder_meeting_only", re.compile(r"股东大会通知|股东大会决议|股东会会议资料|代表委任表格|通函")),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": SEARCH_PAGE,
}


def strip_tags(text: object) -> str:
    value = html.unescape(str(text or ""))
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value).strip()


def compact_text(text: object) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def safe_name(text: str, limit: int = 120) -> str:
    text = re.sub(r"[\\/:*?\"<>|]", "_", text)
    text = re.sub(r"\s+", "_", text)
    return text[:limit].strip("_")


def ts_to_date(ms: object) -> str:
    try:
        return datetime.fromtimestamp(int(ms) / 1000).strftime("%Y-%m-%d")
    except Exception:
        return ""


def http_get_json(params: dict[str, object], timeout: int = 35) -> dict:
    url = f"{SEARCH_URL}?{urlencode(params)}"
    last_exc: Exception | None = None
    for attempt in range(6):
        try:
            req = Request(url, headers=HEADERS, method="GET")
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
            return json.loads(raw.decode("utf-8", errors="replace"))
        except Exception as exc:
            last_exc = exc
            time.sleep(0.8 + 0.5 * attempt)
    raise RuntimeError(f"CNINFO GET failed after retries: {last_exc}")


def query_page(
    term: str,
    page_num: int,
    start_date: str,
    end_date: str,
    page_size: int,
    refresh: bool,
) -> dict:
    term_dir = RAW_JSON_DIR / safe_name(term) / f"{start_date}_to_{end_date}"
    term_dir.mkdir(parents=True, exist_ok=True)
    raw_path = term_dir / f"page_{page_num:05d}.json"
    if raw_path.exists() and not refresh:
        try:
            return json.loads(raw_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            raw_path.unlink()

    params = {
        "searchkey": term,
        "sdate": start_date,
        "edate": end_date,
        "isfulltext": "true",
        "sortName": "pubdate",
        "sortType": "desc",
        "pageNum": page_num,
        "pageSize": page_size,
        "type": "",
    }
    payload = http_get_json(params)
    raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def normalize_hit(
    row: dict,
    query: QueryTerm,
    page_num: int,
    row_in_page: int,
    query_start_date: str,
    query_end_date: str,
) -> dict[str, object]:
    adjunct = row.get("adjunctUrl") or ""
    sec_code_raw = str(row.get("secCode") or "")
    sec_code = sec_code_raw.zfill(6) if sec_code_raw else ""
    title = strip_tags(row.get("announcementTitle"))
    short_title = strip_tags(row.get("shortTitle"))
    content = strip_tags(row.get("announcementContent"))
    content_html = html.unescape(str(row.get("announcementContent") or ""))
    return {
        "query_term": query.term,
        "query_tier": query.tier,
        "query_start_date": query_start_date,
        "query_end_date": query_end_date,
        "query_page": page_num,
        "query_row_in_page": row_in_page,
        "sec_code_raw": sec_code_raw,
        "sec_code": sec_code,
        "sec_name": strip_tags(row.get("secName")),
        "tile_sec_name": strip_tags(row.get("tileSecName")),
        "org_id": row.get("orgId") or "",
        "announcement_id": str(row.get("announcementId") or ""),
        "announcement_title": title,
        "short_title": short_title,
        "announcement_date": ts_to_date(row.get("announcementTime")),
        "announcement_time_ms": str(row.get("announcementTime") or ""),
        "adjunct_url": adjunct,
        "pdf_url": urljoin(STATIC_BASE, adjunct) if adjunct else "",
        "adjunct_size_kb": row.get("adjunctSize") or "",
        "adjunct_type": row.get("adjunctType") or "",
        "page_column": row.get("pageColumn") or "",
        "column_id": row.get("columnId") or "",
        "announcement_type": row.get("announcementType") or "",
        "announcement_content": content,
        "announcement_content_html": content_html,
    }


def first_title_exclusion(title: str) -> str:
    for label, pat in TITLE_EXCLUDE_PATTERNS:
        if pat.search(title):
            return label
    return ""


def matched_genai_terms(text: str, query_terms: str) -> str:
    found = {t for t in STRICT_GENAI_TERMS if re.search(re.escape(t), text, flags=re.I)}
    return ";".join(sorted(found, key=lambda x: (len(x), x)))


def first_snippet(text: str, pat: re.Pattern[str], width: int = 80) -> str:
    m = pat.search(text)
    if not m:
        return ""
    start = max(0, m.start() - width)
    end = min(len(text), m.end() + width)
    return text[start:end]


def join_unique(values: pd.Series) -> str:
    out: set[str] = set()
    for value in values.dropna().astype(str):
        out.update(v for v in value.split(";") if v)
    return ";".join(sorted(out))


def deduplicate(raw_hits: pd.DataFrame) -> pd.DataFrame:
    if raw_hits.empty:
        return raw_hits.copy()

    sort_cols = ["announcement_date", "sec_code", "announcement_id", "query_page", "query_row_in_page"]
    raw_hits = raw_hits.sort_values(sort_cols).copy()
    group_key = "announcement_id"
    first_cols = [
        "sec_code_raw",
        "sec_code",
        "sec_name",
        "tile_sec_name",
        "org_id",
        "announcement_title",
        "short_title",
        "announcement_date",
        "announcement_time_ms",
        "adjunct_url",
        "pdf_url",
        "adjunct_size_kb",
        "adjunct_type",
        "page_column",
        "column_id",
        "announcement_type",
        "announcement_content",
        "announcement_content_html",
    ]
    agg = {col: (col, "first") for col in first_cols}
    agg.update(
        {
            "query_terms": ("query_term", join_unique),
            "query_tiers": ("query_tier", join_unique),
            "query_hit_count": ("query_term", "size"),
            "first_query_page": ("query_page", "min"),
        }
    )
    dedup = raw_hits.groupby(group_key, dropna=False).agg(**agg).reset_index()
    return dedup.sort_values(["announcement_date", "sec_code", "announcement_id"]).reset_index(drop=True)


def add_flags(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["announcement_date_dt"] = pd.to_datetime(out["announcement_date"], errors="coerce")
    out["announcement_year"] = out["announcement_date_dt"].dt.year
    out["is_allowed_page_column"] = out["page_column"].isin(ALLOWED_PAGE_COLUMNS)
    out["is_a_share_code_shape"] = out["sec_code"].astype(str).map(lambda x: bool(A_SHARE_CODE_PAT.match(x)))
    out["is_main_a_share_code_shape"] = out["sec_code"].astype(str).map(lambda x: bool(MAIN_A_SHARE_CODE_PAT.match(x)))
    out["title_exclusion_reason"] = out["announcement_title"].astype(str).map(first_title_exclusion)
    out["title_excluded"] = out["title_exclusion_reason"].ne("")
    out["has_pdf_url"] = out["pdf_url"].astype(str).str.len().gt(0)

    blobs = (
        out["announcement_title"].fillna("")
        + " "
        + out["short_title"].fillna("")
        + " "
        + out["announcement_content"].fillna("")
    )
    out["matched_genai_terms"] = [
        matched_genai_terms(text, qterms) for text, qterms in zip(blobs.astype(str), out["query_terms"].astype(str))
    ]
    out["has_strict_genai_context"] = out["matched_genai_terms"].astype(str).str.len().gt(0)
    out["action_flag"] = blobs.astype(str).map(lambda x: bool(ACTION_PAT.search(x)))
    out["company_actor_flag"] = blobs.astype(str).map(lambda x: bool(COMPANY_ACTOR_PAT.search(x)))
    out["denial_or_correction_flag"] = blobs.astype(str).map(lambda x: bool(DENIAL_PAT.search(x)))
    out["weak_attention_flag"] = blobs.astype(str).map(lambda x: bool(WEAK_ATTENTION_PAT.search(x)))
    out["action_snippet"] = blobs.astype(str).map(lambda x: first_snippet(x, ACTION_PAT))
    out["denial_snippet"] = blobs.astype(str).map(lambda x: first_snippet(x, DENIAL_PAT))
    out["is_a_share_formal_row"] = out["is_allowed_page_column"] & out["is_a_share_code_shape"] & out["has_pdf_url"]

    out["qian_recall_score"] = (
        out["has_strict_genai_context"].astype(int) * 2
        + out["action_flag"].astype(int) * 2
        + out["company_actor_flag"].astype(int)
        + out["is_main_a_share_code_shape"].astype(int)
        + (~out["title_excluded"]).astype(int)
        - out["denial_or_correction_flag"].astype(int)
        - out["weak_attention_flag"].astype(int)
    )
    out["candidate_tier"] = "exclude_non_a_share_or_no_pdf"
    out.loc[
        out["is_a_share_formal_row"] & out["has_strict_genai_context"] & out["action_flag"] & ~out["title_excluded"],
        "candidate_tier",
    ] = "priority_manual_event_candidate"
    out.loc[
        out["is_a_share_formal_row"] & out["has_strict_genai_context"] & out["action_flag"] & out["title_excluded"],
        "candidate_tier",
    ] = "backfill_or_noisy_doc_with_action"
    out.loc[
        out["is_a_share_formal_row"] & out["has_strict_genai_context"] & ~out["action_flag"],
        "candidate_tier",
    ] = "strict_genai_context_without_action"
    out.loc[
        out["is_a_share_formal_row"] & ~out["has_strict_genai_context"],
        "candidate_tier",
    ] = "exclude_no_strict_genai_after_snippet"
    out.loc[
        out["candidate_tier"].eq("priority_manual_event_candidate") & out["denial_or_correction_flag"] & ~out["action_flag"],
        "candidate_tier",
    ] = "exclude_denial_without_action"
    out.loc[
        out["is_a_share_formal_row"]
        & out["has_strict_genai_context"]
        & (out["denial_or_correction_flag"] | out["weak_attention_flag"]),
        "candidate_tier",
    ] = "review_denial_or_uncertain_genai"
    return out


def select_terms(mode: str) -> list[QueryTerm]:
    if mode == "all":
        return QUERY_TERMS
    if mode == "core":
        return [q for q in QUERY_TERMS if q.tier in CORE_TIERS]
    if mode == "no-broad":
        return [q for q in QUERY_TERMS if q.tier in NO_BROAD_TIERS]
    selected = {x.strip() for x in mode.split(",") if x.strip()}
    return [q for q in QUERY_TERMS if q.term in selected]


def parse_date(value: str) -> date:
    return datetime.strptime(value, "%Y-%m-%d").date()


def date_to_str(value: date) -> str:
    return value.strftime("%Y-%m-%d")


def split_date_range(start_date: str, end_date: str) -> tuple[tuple[str, str], tuple[str, str]] | None:
    start = parse_date(start_date)
    end = parse_date(end_date)
    if start >= end:
        return None
    mid = start + (end - start) // 2
    right_start = mid + timedelta(days=1)
    return (date_to_str(start), date_to_str(mid)), (date_to_str(right_start), date_to_str(end))


def payload_total_and_pages(payload: dict, page_size: int) -> tuple[int, int]:
    total = int(payload.get("totalRecordNum") or payload.get("totalAnnouncement") or 0)
    pages_from_payload = int(payload.get("totalpages") or 0)
    pages_from_total = math.ceil(total / page_size) if total else 0
    return total, max(pages_from_payload, pages_from_total)


def plan_date_shards(
    query: QueryTerm,
    start_date: str,
    end_date: str,
    args: argparse.Namespace,
    depth: int = 0,
) -> list[dict[str, object]]:
    first = query_page(query.term, 1, start_date, end_date, args.page_size, args.refresh)
    total, pages = payload_total_and_pages(first, args.page_size)
    if pages <= args.page_cap or start_date == end_date:
        return [
            {
                "start_date": start_date,
                "end_date": end_date,
                "total": total,
                "pages": pages,
                "first_payload": first,
                "shard_depth": depth,
            }
        ]
    pieces = split_date_range(start_date, end_date)
    if pieces is None:
        return [
            {
                "start_date": start_date,
                "end_date": end_date,
                "total": total,
                "pages": pages,
                "first_payload": first,
                "shard_depth": depth,
            }
        ]
    left, right = pieces
    print(
        f"  split {query.term} {start_date}..{end_date}: total={total}, pages={pages}",
        flush=True,
    )
    return plan_date_shards(query, left[0], left[1], args, depth + 1) + plan_date_shards(
        query,
        right[0],
        right[1],
        args,
        depth + 1,
    )


def harvest(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    RAW_JSON_DIR.mkdir(parents=True, exist_ok=True)
    terms = select_terms(args.terms)
    if not terms:
        raise SystemExit(f"No query terms selected for --terms={args.terms!r}")

    query_rows: list[dict[str, object]] = []
    raw_rows: list[dict[str, object]] = []
    for query in terms:
        shards = plan_date_shards(query, args.start_date, args.end_date, args)
        print(f"CNINFO fulltext {query.term}: shards={len(shards)}", flush=True)
        for shard_index, shard in enumerate(shards, start=1):
            shard_start = str(shard["start_date"])
            shard_end = str(shard["end_date"])
            total = int(shard["total"])
            pages = int(shard["pages"])
            if args.max_pages_per_term:
                pages = min(pages, args.max_pages_per_term)
            first = shard["first_payload"]
            query_row = {
                "query_term": query.term,
                "query_tier": query.tier,
                "query_start_date": shard_start,
                "query_end_date": shard_end,
                "query_shard_index": shard_index,
                "query_shard_count": len(shards),
                "query_shard_depth": shard["shard_depth"],
                "total_records": total,
                "target_pages": pages,
                "successful_pages": 1 if pages else 0,
                "failed_pages": 0,
                "failed_page_numbers": "",
                "failed_page_errors": "",
                "page_size": args.page_size,
            }
            query_rows.append(query_row)
            print(
                f"  shard {shard_index}/{len(shards)} {query.term} {shard_start}..{shard_end}: total={total}, pages={pages}",
                flush=True,
            )
            page_payloads: dict[int, dict] = {1: first} if pages else {}
            failed_page_records: list[tuple[int, str]] = []
            remaining_pages = list(range(2, pages + 1))
            if args.workers <= 1:
                for page_num in remaining_pages:
                    try:
                        page_payloads[page_num] = query_page(
                            query.term,
                            page_num,
                            shard_start,
                            shard_end,
                            args.page_size,
                            args.refresh,
                        )
                    except Exception as exc:
                        failed_page_records.append((page_num, str(exc)))
                        print(f"    failed {query.term} page {page_num}: {exc}", flush=True)
                    time.sleep(args.delay)
            elif remaining_pages:
                with ThreadPoolExecutor(max_workers=args.workers) as executor:
                    futures = {
                        executor.submit(
                            query_page,
                            query.term,
                            page_num,
                            shard_start,
                            shard_end,
                            args.page_size,
                            args.refresh,
                        ): page_num
                        for page_num in remaining_pages
                    }
                    for completed, future in enumerate(as_completed(futures), start=1):
                        page_num = futures[future]
                        try:
                            page_payloads[page_num] = future.result()
                        except Exception as exc:
                            print(f"    retry {query.term} page {page_num} after error: {exc}", flush=True)
                            try:
                                time.sleep(1.0)
                                page_payloads[page_num] = query_page(
                                    query.term,
                                    page_num,
                                    shard_start,
                                    shard_end,
                                    args.page_size,
                                    True,
                                )
                            except Exception as retry_exc:
                                failed_page_records.append((page_num, str(retry_exc)))
                                print(f"    failed {query.term} page {page_num}: {retry_exc}", flush=True)
                        if completed % 50 == 0 or completed == len(futures):
                            print(
                                f"    fetched {query.term} {shard_start}..{shard_end}: {completed + 1}/{pages} pages",
                                flush=True,
                            )
            query_row["successful_pages"] = len(page_payloads)
            query_row["failed_pages"] = len(failed_page_records)
            query_row["failed_page_numbers"] = ";".join(str(x[0]) for x in failed_page_records)
            query_row["failed_page_errors"] = " || ".join(f"p{x[0]}:{x[1][:120]}" for x in failed_page_records)
            for page_num in range(1, pages + 1):
                if page_num not in page_payloads:
                    continue
                payload = page_payloads[page_num]
                announcements = payload.get("announcements") or []
                for row_in_page, row in enumerate(announcements, start=1):
                    raw_rows.append(normalize_hit(row, query, page_num, row_in_page, shard_start, shard_end))
    raw_hits = pd.DataFrame(raw_rows)
    query_counts = pd.DataFrame(query_rows)
    dedup = add_flags(deduplicate(raw_hits)) if not raw_hits.empty else pd.DataFrame()
    return raw_hits, dedup, query_counts


def md_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df.empty:
        return "无"
    show = df.head(max_rows).copy()
    cols = list(show.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in show.iterrows():
        values = [str(row.get(c, "")).replace("\n", " ").replace("|", "\\|")[:220] for c in cols]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def save_outputs(raw_hits: pd.DataFrame, dedup: pd.DataFrame, query_counts: pd.DataFrame, args: argparse.Namespace) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw_hits.to_csv(OUT_DIR / "cninfo_fulltext_raw_query_hits.csv.gz", index=False, compression="gzip")
    dedup.to_csv(OUT_DIR / "cninfo_fulltext_dedup_announcements.csv.gz", index=False, compression="gzip")
    query_counts.to_csv(OUT_DIR / "cninfo_fulltext_query_counts.csv", index=False, encoding="utf-8-sig")

    a_share = dedup[dedup["is_a_share_formal_row"]].copy()
    a_share.to_csv(OUT_DIR / "cninfo_fulltext_a_share_announcements.csv.gz", index=False, compression="gzip")
    candidates = a_share[a_share["candidate_tier"].isin(
        [
            "priority_manual_event_candidate",
            "backfill_or_noisy_doc_with_action",
            "strict_genai_context_without_action",
        ]
    )].copy()
    candidates.to_csv(OUT_DIR / "cninfo_fulltext_candidate_pool.csv.gz", index=False, compression="gzip")

    tier_order = {
        "priority_manual_event_candidate": 0,
        "backfill_or_noisy_doc_with_action": 1,
        "strict_genai_context_without_action": 2,
    }
    if not candidates.empty:
        candidates["candidate_tier_rank"] = candidates["candidate_tier"].map(tier_order).fillna(99)
        candidates = candidates.sort_values(
            ["sec_code", "announcement_date_dt", "candidate_tier_rank", "qian_recall_score"],
            ascending=[True, True, True, False],
        )
        first_per_firm = candidates.groupby("sec_code", as_index=False).head(1)
        top3_per_firm = candidates.groupby("sec_code", as_index=False).head(3)
    else:
        first_per_firm = candidates.copy()
        top3_per_firm = candidates.copy()
    first_per_firm = first_per_firm.copy()
    top3_per_firm = top3_per_firm.copy()

    priority = a_share[a_share["candidate_tier"].eq("priority_manual_event_candidate")].copy()
    if not priority.empty:
        priority = priority.sort_values(
            ["sec_code", "announcement_date_dt", "qian_recall_score"],
            ascending=[True, True, False],
        )
        priority_first_per_firm = priority.groupby("sec_code", as_index=False).head(1).copy()
        priority_top3_per_firm = priority.groupby("sec_code", as_index=False).head(3).copy()
        priority_2023_2024 = priority[priority["announcement_year"].between(2023, 2024, inclusive="both")].copy()
        priority_2023_2024_first = priority_2023_2024.groupby("sec_code", as_index=False).head(1).copy()
        priority_2023_2024_top3 = priority_2023_2024.groupby("sec_code", as_index=False).head(3).copy()
    else:
        priority_first_per_firm = priority.copy()
        priority_top3_per_firm = priority.copy()
        priority_2023_2024_first = priority.copy()
        priority_2023_2024_top3 = priority.copy()

    review_cols = [
        "manual_keep_qian_0_1",
        "manual_exclusion_reason",
        "manual_company_is_actor_0_1",
        "manual_event_date_verified_0_1",
        "manual_event_date_corrected",
        "manual_initiative_type",
        "manual_confidence_1_3",
        "manual_notes",
        "sec_code",
        "sec_name",
        "announcement_date",
        "announcement_title",
        "short_title",
        "candidate_tier",
        "qian_recall_score",
        "query_terms",
        "query_tiers",
        "matched_genai_terms",
        "title_exclusion_reason",
        "announcement_content",
        "action_snippet",
        "denial_snippet",
        "pdf_url",
        "announcement_id",
        "page_column",
        "announcement_type",
    ]
    for frame in [
        first_per_firm,
        top3_per_firm,
        priority_first_per_firm,
        priority_top3_per_firm,
        priority_2023_2024_first,
        priority_2023_2024_top3,
    ]:
        for col in review_cols:
            if col not in frame.columns:
                frame[col] = ""

    first_per_firm[review_cols].to_csv(
        OUT_DIR / "manual_review_first_candidate_per_firm.csv",
        index=False,
        encoding="utf-8-sig",
    )
    top3_per_firm[review_cols].to_csv(
        OUT_DIR / "manual_review_top3_candidates_per_firm.csv",
        index=False,
        encoding="utf-8-sig",
    )
    priority_first_per_firm[review_cols].to_csv(
        OUT_DIR / "manual_review_priority_first_candidate_per_firm.csv",
        index=False,
        encoding="utf-8-sig",
    )
    priority_top3_per_firm[review_cols].to_csv(
        OUT_DIR / "manual_review_priority_top3_candidates_per_firm.csv",
        index=False,
        encoding="utf-8-sig",
    )
    priority_2023_2024_first[review_cols].to_csv(
        OUT_DIR / "manual_review_priority_2023_2024_first_candidate_per_firm.csv",
        index=False,
        encoding="utf-8-sig",
    )
    priority_2023_2024_top3[review_cols].to_csv(
        OUT_DIR / "manual_review_priority_2023_2024_top3_candidates_per_firm.csv",
        index=False,
        encoding="utf-8-sig",
    )

    sample_flow = pd.DataFrame(
        [
            {
                "stage": "raw_query_hits",
                "rows": len(raw_hits),
                "announcements": raw_hits["announcement_id"].nunique() if not raw_hits.empty else 0,
                "firms": raw_hits["sec_code"].nunique() if not raw_hits.empty else 0,
            },
            {
                "stage": "dedup_announcements",
                "rows": len(dedup),
                "announcements": dedup["announcement_id"].nunique() if not dedup.empty else 0,
                "firms": dedup["sec_code"].nunique() if not dedup.empty else 0,
            },
            {
                "stage": "a_share_formal_rows",
                "rows": len(a_share),
                "announcements": a_share["announcement_id"].nunique() if not a_share.empty else 0,
                "firms": a_share["sec_code"].nunique() if not a_share.empty else 0,
            },
            {
                "stage": "priority_manual_event_candidate",
                "rows": int(a_share["candidate_tier"].eq("priority_manual_event_candidate").sum()) if not a_share.empty else 0,
                "announcements": a_share.loc[a_share["candidate_tier"].eq("priority_manual_event_candidate"), "announcement_id"].nunique() if not a_share.empty else 0,
                "firms": a_share.loc[a_share["candidate_tier"].eq("priority_manual_event_candidate"), "sec_code"].nunique() if not a_share.empty else 0,
            },
            {
                "stage": "candidate_pool_for_manual_review",
                "rows": len(candidates),
                "announcements": candidates["announcement_id"].nunique() if not candidates.empty else 0,
                "firms": candidates["sec_code"].nunique() if not candidates.empty else 0,
            },
            {
                "stage": "first_candidate_per_firm",
                "rows": len(first_per_firm),
                "announcements": first_per_firm["announcement_id"].nunique() if not first_per_firm.empty else 0,
                "firms": first_per_firm["sec_code"].nunique() if not first_per_firm.empty else 0,
            },
            {
                "stage": "priority_first_candidate_per_firm",
                "rows": len(priority_first_per_firm),
                "announcements": priority_first_per_firm["announcement_id"].nunique() if not priority_first_per_firm.empty else 0,
                "firms": priority_first_per_firm["sec_code"].nunique() if not priority_first_per_firm.empty else 0,
            },
            {
                "stage": "priority_2023_2024_first_candidate_per_firm",
                "rows": len(priority_2023_2024_first),
                "announcements": priority_2023_2024_first["announcement_id"].nunique() if not priority_2023_2024_first.empty else 0,
                "firms": priority_2023_2024_first["sec_code"].nunique() if not priority_2023_2024_first.empty else 0,
            },
            {
                "stage": "priority_2023_2024_top3_candidates_per_firm",
                "rows": len(priority_2023_2024_top3),
                "announcements": priority_2023_2024_top3["announcement_id"].nunique() if not priority_2023_2024_top3.empty else 0,
                "firms": priority_2023_2024_top3["sec_code"].nunique() if not priority_2023_2024_top3.empty else 0,
            },
        ]
    )
    sample_flow.to_csv(OUT_DIR / "sample_flow.csv", index=False, encoding="utf-8-sig")

    candidate_tiers = (
        a_share.groupby(["candidate_tier"], dropna=False)
        .agg(rows=("announcement_id", "size"), announcements=("announcement_id", "nunique"), firms=("sec_code", "nunique"))
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    candidate_tiers.to_csv(OUT_DIR / "candidate_tier_counts.csv", index=False, encoding="utf-8-sig")

    year_counts = (
        a_share.groupby(["announcement_year", "candidate_tier"], dropna=False)
        .agg(rows=("announcement_id", "size"), firms=("sec_code", "nunique"))
        .reset_index()
        .sort_values(["announcement_year", "candidate_tier"])
    )
    year_counts.to_csv(OUT_DIR / "year_candidate_counts.csv", index=False, encoding="utf-8-sig")

    title_exclusions = (
        a_share[a_share["title_excluded"]]
        .groupby("title_exclusion_reason", dropna=False)
        .agg(rows=("announcement_id", "size"), firms=("sec_code", "nunique"))
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    title_exclusions.to_csv(OUT_DIR / "title_exclusion_counts.csv", index=False, encoding="utf-8-sig")

    examples_cols = [
        "sec_code",
        "sec_name",
        "announcement_date",
        "announcement_title",
        "candidate_tier",
        "query_terms",
        "matched_genai_terms",
        "qian_recall_score",
        "announcement_content",
    ]
    priority_examples = a_share[a_share["candidate_tier"].eq("priority_manual_event_candidate")][examples_cols].sort_values(
        ["announcement_date", "sec_code"]
    )
    first_examples = first_per_firm[examples_cols].sort_values(["announcement_date", "sec_code"]) if not first_per_firm.empty else pd.DataFrame(columns=examples_cols)
    priority_first_examples = priority_first_per_firm[examples_cols].sort_values(["announcement_date", "sec_code"]) if not priority_first_per_firm.empty else pd.DataFrame(columns=examples_cols)

    report = f"""# v26 CNINFO Fulltext GenAI Harvest

Date: 2026-06-03

## Purpose

This run harvests CNINFO top-search `标题+全文` metadata for GenAI terms from `{args.start_date}` to `{args.end_date}`. It is the source-rebuild step for a Qian-scale China replication and for later China-specific GenAI disclosure research.

It does not download all PDFs. Search-result metadata and snippets are enough to build a recall pool, while full PDFs should be downloaded only after candidate ranking.

## Query Scope

- Endpoint: `https://www.cninfo.com.cn/new/fulltextSearch/full`
- Search mode: `标题+全文`
- Date range: `{args.start_date}` to `{args.end_date}`
- Page size: `{args.page_size}`
- Page cap per date shard: `{args.page_cap}`
- Term mode: `{args.terms}`
- Broad single term `人工智能` is excluded by design.

## Query Counts

{md_table(query_counts, max_rows=80)}

## Sample Flow

{md_table(sample_flow)}

## Candidate Tiers

{md_table(candidate_tiers)}

## Year Counts

{md_table(year_counts, max_rows=80)}

## Title Noise Flags

{md_table(title_exclusions)}

## Priority Candidate Examples

{md_table(priority_examples, max_rows=40)}

## First Candidate Per Firm Examples

{md_table(first_examples, max_rows=40)}

## Priority First Candidate Per Firm Examples

{md_table(priority_first_examples, max_rows=40)}

## Output Files

- `cninfo_fulltext_raw_query_hits.csv.gz`: one row per query hit before deduplication.
- `cninfo_fulltext_dedup_announcements.csv.gz`: deduplicated announcements with merged query terms.
- `cninfo_fulltext_a_share_announcements.csv.gz`: A-share formal disclosure rows.
- `cninfo_fulltext_candidate_pool.csv.gz`: ranked pool for later PDF download and manual coding.
- `manual_review_first_candidate_per_firm.csv`: first candidate per firm for Qian-style first-event screening.
- `manual_review_top3_candidates_per_firm.csv`: first three candidates per firm.
- `manual_review_priority_first_candidate_per_firm.csv`: first high-priority action candidate per firm.
- `manual_review_priority_top3_candidates_per_firm.csv`: first three high-priority action candidates per firm.
- `manual_review_priority_2023_2024_first_candidate_per_firm.csv`: high-priority first-candidate file for the Qian replication window.
- `manual_review_priority_2023_2024_top3_candidates_per_firm.csv`: first three high-priority candidates per firm for the Qian replication window.

## Interpretation

This source is large enough for a Qian-style funnel. The priority rows are not final treatment events. Manual coding must still verify that the listed company is the actor, the disclosure describes a concrete GenAI initiative, and the correct event date is the initiative date rather than a later annual-report or inquiry-reply date.
"""
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(report, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-date", default=START_DATE)
    parser.add_argument("--end-date", default=END_DATE)
    parser.add_argument("--page-size", type=int, default=PAGE_SIZE)
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY_SECONDS)
    parser.add_argument("--terms", default="all", help="all, core, no-broad, or comma-separated query terms")
    parser.add_argument("--max-pages-per-term", type=int, default=0)
    parser.add_argument("--page-cap", type=int, default=200)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--refresh", action="store_true", help="Ignore cached raw JSON pages")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_JSON_DIR.mkdir(parents=True, exist_ok=True)
    raw_hits, dedup, query_counts = harvest(args)
    if raw_hits.empty:
        raise SystemExit("No CNINFO hits returned")
    save_outputs(raw_hits, dedup, query_counts, args)
    print(f"raw_query_hits={len(raw_hits)}", flush=True)
    print(f"dedup_announcements={len(dedup)}", flush=True)
    print(f"a_share_rows={int(dedup['is_a_share_formal_row'].sum())}", flush=True)
    print(f"out_dir={OUT_DIR}", flush=True)
    print(f"doc={DOC_PATH}", flush=True)


if __name__ == "__main__":
    main()
