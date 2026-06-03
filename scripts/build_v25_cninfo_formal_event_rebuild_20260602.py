#!/usr/bin/env python3
"""Rebuild CNINFO formal GenAI announcement candidates.

This run fixes two limitations of the old v3 CNINFO pilot:
1. It queries SZSE, SSE, and BSE CNINFO columns separately instead of only
   `column=szse`.
2. It treats "人工智能" as broad recall only; Qian-style candidates still need
   strict GenAI terms and concrete initiative language in the announcement text.
"""

from __future__ import annotations

import csv
import html
import json
import math
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUN_TAG = "20260602"
OUT_DIR = ROOT / "results" / f"v25_cninfo_formal_event_rebuild_{RUN_TAG}"
DOC_PATH = ROOT / "docs" / "empirical_runs" / f"88_v25_cninfo_formal_event_rebuild_{RUN_TAG}.md"
RAW_DIR = ROOT / "data" / "raw" / f"cninfo_formal_event_rebuild_{RUN_TAG}"
RAW_JSON_DIR = RAW_DIR / "raw_json"
PDF_DIR = RAW_DIR / "raw_pdf"
TXT_DIR = RAW_DIR / "text"

QUERY_URL = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
STATIC_BASE = "https://static.cninfo.com.cn/"
SEARCH_PAGE = "http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search"

START_DATE = "2023-01-01"
END_DATE = "2026-06-02"
PAGE_SIZE = 30

MARKET_SCOPES = [
    {"scope": "szse_a", "column": "szse", "plate": "sz"},
    {"scope": "sse_a", "column": "sse", "plate": "sh"},
    {"scope": "bse_a", "column": "third", "plate": "bj"},
]

ALLOWED_PAGE_COLUMNS = {"SZZB", "SZCY", "SHZB", "SHKCB", "BJS"}
A_SHARE_CODE_PAT = re.compile(r"^(?:(?:000|001|002|003|300|301|600|601|603|605|688)\d{3}|[489]\d{5})$")
MAIN_A_SHARE_CODE_PAT = re.compile(r"^(000|001|002|003|300|301|600|601|603|605|688)\d{3}$")

# Query terms. "人工智能" is broad recall, not treatment evidence.
QUERY_TERMS = [
    "大模型",
    "大语言模型",
    "生成式人工智能",
    "生成式AI",
    "AIGC",
    "ChatGPT",
    "GPT",
    "DeepSeek",
    "模型备案",
    "人工智能大模型",
    "文心一言",
    "通义千问",
    "讯飞星火",
    "星火认知",
    "盘古大模型",
    "混元大模型",
    "豆包",
    "Kimi",
    "智谱",
    "人工智能",
]

STRICT_GENAI_TERMS = [
    "生成式人工智能",
    "生成式AI",
    "生成式 AI",
    "AIGC",
    "ChatGPT",
    "GPT",
    "大模型",
    "大语言模型",
    "语言大模型",
    "基础模型",
    "预训练模型",
    "多模态大模型",
    "DeepSeek",
    "文心一言",
    "通义千问",
    "通义",
    "讯飞星火",
    "星火认知",
    "盘古大模型",
    "混元大模型",
    "腾讯混元",
    "豆包",
    "Kimi",
    "智谱",
    "模型备案",
]

GENERIC_AI_PAT = re.compile(r"人工智能|AI|智能化|智能制造|算法|算力|机器学习|深度学习", re.I)
STRICT_GENAI_PAT = re.compile("|".join(re.escape(t) for t in sorted(STRICT_GENAI_TERMS, key=len, reverse=True)), re.I)

TITLE_EXCLUDE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("periodic_report", re.compile(r"年度报告|年报|半年度报告|半年报|季度报告|一季度报告|三季度报告|中期报告")),
    ("performance_meeting", re.compile(r"业绩说明会|投资者关系|调研活动|机构调研|网上集体接待日|接待日活动")),
    ("exchange_inquiry", re.compile(r"问询函|回复函|审核问询|监管工作函|关注函|问询")),
    ("advisor_opinion", re.compile(r"核查意见|法律意见书|保荐|独立财务顾问|审计报告|评估报告|评级报告")),
    ("offering_or_risk_filler", re.compile(r"募集说明书|摊薄即期回报|填补措施|承诺|发行人及其他责任主体|募集资金具体运用情况")),
    ("fund_or_index", re.compile(r"基金|交易型开放式指数|ETF|做市服务|招募说明书|基金合同|托管协议|产品资料概要")),
    ("shareholder_meeting_only", re.compile(r"股东大会通知|股东大会决议|代表委任表格|通函")),
    ("abstract_or_summary", re.compile(r"摘要|取消")),
]

ACTION_PAT = re.compile(
    r"发布|推出|上线|接入|集成|部署|适配|落地|应用|商业化|备案通过|通过备案|"
    r"通过生成式人工智能服务登记|登记|签署|合作|共建|投资|建设|采购|中标|"
    r"成立|设立|收购|研发|升级|启动|推出|launch|release|deploy|integrat",
    re.I,
)
STRONG_TITLE_ACTION_PAT = re.compile(
    r"关于.*(发布|推出|上线|接入|集成|部署|备案|签署|合作|共建|投资|建设|采购|中标|成立|设立|收购|升级)"
)
DENIAL_PAT = re.compile(r"暂无|尚无|不涉及|未涉及|没有.*业务|无.*业务|澄清|风险提示")
COMPANY_ACTOR_PAT = re.compile(r"公司|本公司|子公司|控股子公司|全资子公司|集团|股份有限公司|有限公司|拟|已|将")
WEAK_ATTENTION_PAT = re.compile(r"密切关注|持续关注|积极关注|探索|研究相关机会|以公告为准|敬请关注")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": SEARCH_PAGE,
    "Origin": "http://www.cninfo.com.cn",
}


def strip_tags(text: object) -> str:
    value = html.unescape(str(text or ""))
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value).strip()


def compact_text(text: object) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def safe_name(text: str, limit: int = 170) -> str:
    text = re.sub(r"[\\/:*?\"<>|]", "_", text)
    text = re.sub(r"\s+", "_", text)
    return text[:limit].strip("_")


def ts_to_date(ms: object) -> str:
    try:
        return datetime.fromtimestamp(int(ms) / 1000).strftime("%Y-%m-%d")
    except Exception:
        return ""


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def http_post_json(url: str, data: dict[str, object], timeout: int = 25) -> dict:
    payload = urlencode(data).encode("utf-8")
    headers = {
        **HEADERS,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    last_exc: Exception | None = None
    for attempt in range(5):
        try:
            req = Request(url, data=payload, headers=headers, method="POST")
            with urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
            return json.loads(raw.decode("utf-8", errors="replace"))
        except Exception as exc:
            last_exc = exc
            time.sleep(0.8 + 0.5 * attempt)
    raise RuntimeError(f"POST failed after retries: {last_exc}")


def http_get_bytes(url: str, timeout: int = 40) -> tuple[int, bytes]:
    last_exc: Exception | None = None
    for attempt in range(4):
        try:
            req = Request(url, headers={"User-Agent": HEADERS["User-Agent"]}, method="GET")
            with urlopen(req, timeout=timeout) as resp:
                return int(getattr(resp, "status", 200)), resp.read()
        except Exception as exc:
            last_exc = exc
            time.sleep(0.6 + 0.4 * attempt)
    raise RuntimeError(f"GET failed after retries: {last_exc}")


def query_cninfo(term: str, scope: dict[str, str], page_num: int) -> dict:
    data = {
        "pageNum": page_num,
        "pageSize": PAGE_SIZE,
        "column": scope["column"],
        "tabName": "fulltext",
        "plate": scope["plate"],
        "stock": "",
        "searchkey": term,
        "secid": "",
        "category": "",
        "trade": "",
        "seDate": f"{START_DATE}~{END_DATE}",
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true",
    }
    return http_post_json(QUERY_URL, data)


def normalize_announcement(row: dict, term: str, scope_name: str) -> dict[str, str]:
    adjunct = row.get("adjunctUrl") or ""
    sec_code_raw = str(row.get("secCode") or "")
    return {
        "query_scope": scope_name,
        "query_terms": term,
        "sec_code_raw": sec_code_raw,
        "sec_code": sec_code_raw.zfill(6) if sec_code_raw else "",
        "sec_name": strip_tags(row.get("secName") or ""),
        "org_id": row.get("orgId") or "",
        "announcement_id": str(row.get("announcementId") or ""),
        "announcement_title": strip_tags(row.get("announcementTitle") or ""),
        "announcement_date": ts_to_date(row.get("announcementTime")),
        "announcement_time_ms": str(row.get("announcementTime") or ""),
        "adjunct_url": adjunct,
        "pdf_url": urljoin(STATIC_BASE, adjunct) if adjunct else "",
        "adjunct_size": str(row.get("adjunctSize") or ""),
        "adjunct_type": row.get("adjunctType") or "",
        "page_column": row.get("pageColumn") or "",
        "column_id": row.get("columnId") or "",
    }


def query_all() -> tuple[pd.DataFrame, pd.DataFrame]:
    RAW_JSON_DIR.mkdir(parents=True, exist_ok=True)
    rows: dict[str, dict[str, str]] = {}
    query_counts: list[dict[str, object]] = []
    for scope in MARKET_SCOPES:
        for term in QUERY_TERMS:
            first = query_cninfo(term, scope, 1)
            total = int(first.get("totalRecordNum") or 0)
            pages = math.ceil(total / PAGE_SIZE) if total else 0
            query_counts.append(
                {
                    "query_scope": scope["scope"],
                    "column": scope["column"],
                    "plate": scope["plate"],
                    "query_term": term,
                    "total": total,
                    "pages": pages,
                }
            )
            print(f"CNINFO {scope['scope']} {term}: total={total}, pages={pages}", flush=True)
            page_payloads = [(1, first)] if pages else []
            for page in range(2, pages + 1):
                time.sleep(0.08)
                page_payloads.append((page, query_cninfo(term, scope, page)))
            for page, payload in page_payloads:
                raw_path = RAW_JSON_DIR / f"{scope['scope']}_{safe_name(term)}_page_{page:04d}.json"
                raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
                for ann in payload.get("announcements") or []:
                    nr = normalize_announcement(ann, term, scope["scope"])
                    aid = nr["announcement_id"]
                    if not aid:
                        continue
                    if aid not in rows:
                        rows[aid] = nr
                    else:
                        terms = set(rows[aid]["query_terms"].split(";")) | {term}
                        scopes = set(rows[aid]["query_scope"].split(";")) | {scope["scope"]}
                        rows[aid]["query_terms"] = ";".join(sorted(t for t in terms if t))
                        rows[aid]["query_scope"] = ";".join(sorted(s for s in scopes if s))
    query_counts_df = pd.DataFrame(query_counts)
    raw_df = pd.DataFrame(sorted(rows.values(), key=lambda r: (r["announcement_date"], r["sec_code"], r["announcement_id"])))
    return raw_df, query_counts_df


def first_title_exclusion(title: str) -> str:
    for label, pat in TITLE_EXCLUDE_PATTERNS:
        if pat.search(title):
            return label
    return ""


def add_initial_filters(raw: pd.DataFrame) -> pd.DataFrame:
    out = raw.copy()
    out["is_allowed_page_column"] = out["page_column"].isin(ALLOWED_PAGE_COLUMNS)
    out["is_a_share_code_shape"] = out["sec_code"].astype(str).map(lambda x: bool(A_SHARE_CODE_PAT.match(x)))
    out["is_main_a_share_code_shape"] = out["sec_code"].astype(str).map(lambda x: bool(MAIN_A_SHARE_CODE_PAT.match(x)))
    out["title_exclusion_reason"] = out["announcement_title"].map(first_title_exclusion)
    out["title_excluded"] = out["title_exclusion_reason"].ne("")
    out["has_pdf_url"] = out["pdf_url"].astype(str).str.len().gt(0)
    out["eligible_for_download"] = (
        out["is_allowed_page_column"]
        & out["is_a_share_code_shape"]
        & out["has_pdf_url"]
        & ~out["title_excluded"]
    )
    return out


def download_and_extract(row: pd.Series) -> dict[str, str]:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    filename = safe_name(
        f"{row['announcement_date']}_{row['sec_code']}_{row['sec_name']}_{row['announcement_id']}_{row['announcement_title']}"
    )
    pdf_path = PDF_DIR / f"{filename}.pdf"
    txt_path = TXT_DIR / f"{filename}.txt"
    out = row.to_dict()
    out.update({"pdf_file": "", "txt_file": "", "download_status": ""})
    try:
        if not pdf_path.exists():
            status, content = http_get_bytes(str(row["pdf_url"]))
            if status != 200 or b"%PDF" not in content[:2048]:
                out["download_status"] = f"download_failed_{status}"
                return out
            pdf_path.write_bytes(content)
            time.sleep(0.05)
        if not txt_path.exists():
            proc = subprocess.run(
                ["pdftotext", "-layout", str(pdf_path), str(txt_path)],
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                out["download_status"] = "pdftotext_failed"
                out["pdf_file"] = str(pdf_path.relative_to(ROOT))
                return out
        out["pdf_file"] = str(pdf_path.relative_to(ROOT))
        out["txt_file"] = str(txt_path.relative_to(ROOT))
        out["download_status"] = "ok"
        return out
    except Exception as exc:
        out["download_status"] = f"error_{type(exc).__name__}"
        return out


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text)
    parts = re.split(r"(?<=[。！？；;])", text)
    return [p.strip() for p in parts if len(p.strip()) >= 8]


def matched_terms(text: str) -> str:
    found = [t for t in STRICT_GENAI_TERMS if re.search(re.escape(t), text, flags=re.I)]
    return ";".join(sorted(set(found), key=lambda x: (len(x), x)))


def genai_context(text: str, max_sentences: int = 10) -> str:
    sentences = split_sentences(text)
    hits = [s for s in sentences if STRICT_GENAI_PAT.search(s) or GENERIC_AI_PAT.search(s)]
    return " || ".join(hits[:max_sentences])[:6000]


def first_snippet(text: str, pat: re.Pattern[str], width: int = 140) -> str:
    m = pat.search(text)
    if not m:
        return ""
    start = max(0, m.start() - width)
    end = min(len(text), m.end() + width)
    return text[start:end]


def classify_downloaded(row: pd.Series) -> dict[str, object]:
    title = compact_text(row.get("announcement_title", ""))
    txt_file = row.get("txt_file", "")
    text = ""
    if isinstance(txt_file, str) and txt_file:
        path = ROOT / txt_file
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="ignore")
    blob = compact_text(f"{title} {text}")
    context = genai_context(blob)
    strict_terms = matched_terms(blob)
    query_terms = compact_text(row.get("query_terms", ""))
    strict_any = bool(strict_terms)
    generic_any = bool(GENERIC_AI_PAT.search(blob))
    title_action = bool(STRONG_TITLE_ACTION_PAT.search(title))
    action_any = bool(ACTION_PAT.search(context) or ACTION_PAT.search(title))
    company_actor = bool(COMPANY_ACTOR_PAT.search(context) or COMPANY_ACTOR_PAT.search(title))
    denial = bool(DENIAL_PAT.search(context) or (DENIAL_PAT.search(title) and not action_any))
    weak_attention = bool(WEAK_ATTENTION_PAT.search(context))
    strict_query = any(term in query_terms for term in STRICT_GENAI_TERMS)
    only_broad_ai_query = query_terms == "人工智能"
    evidence_score = (
        int(strict_any) * 2
        + int(action_any) * 2
        + int(title_action)
        + int(company_actor)
        + int(bool(row.get("is_allowed_page_column")))
        + int(bool(row.get("is_main_a_share_code_shape")))
    )
    if row.get("download_status") != "ok":
        label = "exclude_download_or_text_failed"
        keep = 0
    elif denial and not action_any:
        label = "exclude_denial_or_correction"
        keep = 0
    elif strict_any and action_any and evidence_score >= 6:
        label = "keep_candidate_strong_formal_initiative"
        keep = 1
    elif strict_any and (action_any or title_action) and evidence_score >= 5:
        label = "review_possible_formal_initiative"
        keep = 1
    elif strict_any:
        label = "review_strict_genai_without_clear_action"
        keep = 0
    elif only_broad_ai_query and generic_any and action_any:
        label = "review_generic_ai_possible_project"
        keep = 0
    elif generic_any:
        label = "exclude_broad_ai_only"
        keep = 0
    elif strict_query:
        label = "exclude_strict_query_no_text_match"
        keep = 0
    else:
        label = "exclude_no_genai_evidence"
        keep = 0

    if weak_attention and keep == 0 and label.startswith("review"):
        label = "exclude_attention_only_without_initiative"

    return {
        "matched_genai_terms": strict_terms,
        "has_strict_genai_text": int(strict_any),
        "has_generic_ai_text": int(generic_any),
        "title_action_flag": int(title_action),
        "action_flag": int(action_any),
        "company_actor_flag": int(company_actor),
        "denial_or_correction_flag": int(denial),
        "weak_attention_flag": int(weak_attention),
        "qian_auto_label": label,
        "qian_auto_keep_candidate": keep,
        "qian_evidence_score": evidence_score,
        "genai_context": context,
        "action_snippet": first_snippet(context or title, ACTION_PAT),
        "denial_snippet": first_snippet(context or title, DENIAL_PAT),
        "text_chars": len(text),
    }


def manual_review_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in [
        "manual_keep_qian_0_1",
        "manual_exclusion_reason",
        "manual_company_is_actor_0_1",
        "manual_event_date_verified_0_1",
        "manual_product_or_process",
        "manual_confidence_1_3",
        "manual_notes",
    ]:
        if col not in out.columns:
            out[col] = ""
    first_cols = [
        "manual_keep_qian_0_1",
        "manual_exclusion_reason",
        "manual_company_is_actor_0_1",
        "manual_event_date_verified_0_1",
        "manual_product_or_process",
        "manual_confidence_1_3",
        "manual_notes",
    ]
    useful = [
        "sec_code",
        "sec_name",
        "announcement_date",
        "announcement_title",
        "page_column",
        "query_terms",
        "matched_genai_terms",
        "qian_auto_label",
        "qian_auto_keep_candidate",
        "qian_evidence_score",
        "title_exclusion_reason",
        "action_snippet",
        "denial_snippet",
        "genai_context",
        "pdf_url",
        "txt_file",
        "announcement_id",
    ]
    rest = [c for c in out.columns if c not in first_cols + useful]
    return out[first_cols + [c for c in useful if c in out.columns] + rest]


def save_outputs(raw: pd.DataFrame, query_counts: pd.DataFrame, filtered: pd.DataFrame, downloaded: pd.DataFrame) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    query_counts.to_csv(OUT_DIR / "cninfo_query_counts_by_scope.csv", index=False, encoding="utf-8-sig")
    raw.to_csv(OUT_DIR / "cninfo_raw_hits.csv.gz", index=False, compression="gzip")
    filtered.to_csv(OUT_DIR / "cninfo_raw_hits_with_initial_filters.csv.gz", index=False, compression="gzip")
    downloaded.to_csv(OUT_DIR / "cninfo_downloaded_and_classified.csv.gz", index=False, compression="gzip")

    label_counts = (
        downloaded.groupby(["qian_auto_label"], dropna=False)
        .agg(
            rows=("announcement_id", "size"),
            firms=("sec_code", "nunique"),
            keep_candidates=("qian_auto_keep_candidate", "sum"),
        )
        .reset_index()
        .sort_values(["keep_candidates", "rows"], ascending=False)
    )
    label_counts.to_csv(OUT_DIR / "auto_label_counts.csv", index=False, encoding="utf-8-sig")

    flow_rows = [
        {"stage": "raw_deduplicated_cninfo_hits", "rows": len(filtered), "announcements": filtered["announcement_id"].nunique(), "firms": filtered["sec_code"].nunique()},
        {"stage": "allowed_page_column", "rows": int(filtered["is_allowed_page_column"].sum()), "announcements": filtered.loc[filtered["is_allowed_page_column"], "announcement_id"].nunique(), "firms": filtered.loc[filtered["is_allowed_page_column"], "sec_code"].nunique()},
        {"stage": "a_share_code_shape", "rows": int((filtered["is_allowed_page_column"] & filtered["is_a_share_code_shape"]).sum()), "announcements": filtered.loc[filtered["is_allowed_page_column"] & filtered["is_a_share_code_shape"], "announcement_id"].nunique(), "firms": filtered.loc[filtered["is_allowed_page_column"] & filtered["is_a_share_code_shape"], "sec_code"].nunique()},
        {"stage": "eligible_for_download_after_title_filter", "rows": int(filtered["eligible_for_download"].sum()), "announcements": filtered.loc[filtered["eligible_for_download"], "announcement_id"].nunique(), "firms": filtered.loc[filtered["eligible_for_download"], "sec_code"].nunique()},
        {"stage": "downloaded_text_ok", "rows": int(downloaded["download_status"].eq("ok").sum()), "announcements": downloaded.loc[downloaded["download_status"].eq("ok"), "announcement_id"].nunique(), "firms": downloaded.loc[downloaded["download_status"].eq("ok"), "sec_code"].nunique()},
        {"stage": "auto_keep_candidate", "rows": int(downloaded["qian_auto_keep_candidate"].sum()), "announcements": downloaded.loc[downloaded["qian_auto_keep_candidate"].eq(1), "announcement_id"].nunique(), "firms": downloaded.loc[downloaded["qian_auto_keep_candidate"].eq(1), "sec_code"].nunique()},
    ]
    sample_flow = pd.DataFrame(flow_rows)
    sample_flow.to_csv(OUT_DIR / "sample_flow.csv", index=False, encoding="utf-8-sig")

    review = downloaded.sort_values(
        ["qian_auto_keep_candidate", "qian_evidence_score", "announcement_date"],
        ascending=[False, False, True],
    )
    manual_review_columns(review).to_csv(OUT_DIR / "manual_review_cninfo_formal_candidates.csv", index=False, encoding="utf-8-sig")

    first = downloaded[downloaded["qian_auto_keep_candidate"].eq(1)].copy()
    if not first.empty:
        first["announcement_date_dt"] = pd.to_datetime(first["announcement_date"], errors="coerce")
        first = first.sort_values(["sec_code", "announcement_date_dt", "qian_evidence_score"], ascending=[True, True, False])
        first = first.groupby("sec_code", as_index=False).head(1)
    manual_review_columns(first).to_csv(OUT_DIR / "manual_review_first_auto_keep_per_firm.csv", index=False, encoding="utf-8-sig")

    title_exclusions = (
        filtered[filtered["title_excluded"]]
        .groupby("title_exclusion_reason", dropna=False)
        .agg(rows=("announcement_id", "size"), firms=("sec_code", "nunique"))
        .reset_index()
        .sort_values("rows", ascending=False)
    )
    title_exclusions.to_csv(OUT_DIR / "title_exclusion_counts.csv", index=False, encoding="utf-8-sig")

    write_report(sample_flow, label_counts, title_exclusions, downloaded, first)


def md_table(df: pd.DataFrame, max_rows: int = 30) -> str:
    if df.empty:
        return "无"
    show = df.head(max_rows).copy()
    cols = list(show.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in show.iterrows():
        values = [str(row.get(c, "")).replace("\n", " ").replace("|", "\\|")[:240] for c in cols]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def write_report(
    sample_flow: pd.DataFrame,
    label_counts: pd.DataFrame,
    title_exclusions: pd.DataFrame,
    downloaded: pd.DataFrame,
    first: pd.DataFrame,
) -> None:
    examples_cols = [
        "sec_code",
        "sec_name",
        "announcement_date",
        "announcement_title",
        "page_column",
        "query_terms",
        "matched_genai_terms",
        "qian_auto_label",
        "qian_evidence_score",
        "action_snippet",
    ]
    examples = downloaded[downloaded["qian_auto_keep_candidate"].eq(1)][
        [c for c in examples_cols if c in downloaded.columns]
    ].sort_values(["announcement_date", "sec_code"])
    first_examples = first[[c for c in examples_cols if c in first.columns]].sort_values(["announcement_date", "sec_code"])
    keep = downloaded[downloaded["qian_auto_keep_candidate"].eq(1)].copy()
    keep["announcement_date_dt"] = pd.to_datetime(keep["announcement_date"], errors="coerce")
    keep["year"] = keep["announcement_date_dt"].dt.year
    keep_by_year = (
        keep.groupby("year", dropna=False)
        .agg(rows=("announcement_id", "nunique"), firms=("sec_code", "nunique"))
        .reset_index()
        .sort_values("year")
    )
    replication_slice = keep[keep["year"].between(2023, 2024, inclusive="both")].copy()
    if not replication_slice.empty:
        replication_slice = replication_slice.sort_values(
            ["sec_code", "announcement_date_dt", "qian_evidence_score"],
            ascending=[True, True, False],
        ).groupby("sec_code", as_index=False).head(1)
    replication_slice_examples = replication_slice[
        [c for c in examples_cols if c in replication_slice.columns]
    ].sort_values(["announcement_date", "sec_code"])
    report = f"""# v25 CNINFO Formal GenAI Event Rebuild

Date: 2026-06-02

## Purpose

This run rebuilds the formal CNINFO announcement source for Qian-style GenAI initiative screening. It does not rerun supplier returns. The goal is to test whether CNINFO formal disclosures can produce a larger, auditable set of concrete GenAI initiative candidates than the old v3/v24 formal slice.

## Key Fixes

- Query SZSE, SSE, and BSE CNINFO columns separately.
- Filter by A-share page columns: `SZZB`, `SZCY`, `SHZB`, `SHKCB`, `BJS`.
- Treat broad `人工智能` as recall only, not as GenAI treatment evidence.
- Download PDFs and classify based on extracted announcement text.
- Output manual-review files; machine labels are triage labels only.

## Sample Flow

{md_table(sample_flow)}

## Auto Labels

{md_table(label_counts)}

## Auto-Keep By Year

{md_table(keep_by_year)}

## 2023-2024 First Auto-Keep Per Firm

{md_table(replication_slice_examples, max_rows=40)}

## Title Exclusions

{md_table(title_exclusions)}

## Auto-Keep Candidate Examples

{md_table(examples, max_rows=40)}

## First Auto-Keep Per Firm

{md_table(first_examples, max_rows=40)}

## Interpretation

This is a source-rebuild audit. The previous "formal source is tiny" conclusion came from the old v3/v24 formal slice and downstream filters, not from CNINFO having no relevant announcements. The rebuilt CNINFO source produces a small but real manually auditable formal-event pool. `manual_review_cninfo_formal_candidates.csv` should be manually coded before any supplier-event-study rerun. The acceptable Qian-style event must be an announcing listed company acting on a concrete GenAI initiative: launch, adoption, deployment, product integration, model/service filing, project investment, contract, or strategic cooperation.

Important limitations:

1. CNINFO is a formal disclosure portal, not a newswire; it is cleaner but narrower than PR Newswire-style sources.
2. Some valid-looking formal announcements are support documents or feasibility reports. They need manual event-date validation.
3. Broad artificial-intelligence infrastructure projects are not automatically GenAI initiatives unless the text clearly links them to large models, generative AI, or named foundation-model services.
"""
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    for path in [OUT_DIR, RAW_JSON_DIR, PDF_DIR, TXT_DIR]:
        path.mkdir(parents=True, exist_ok=True)

    raw, query_counts = query_all()
    if raw.empty:
        raise SystemExit("No CNINFO hits returned")

    filtered = add_initial_filters(raw)
    raw.to_csv(OUT_DIR / "cninfo_raw_hits_preview.csv", index=False, encoding="utf-8-sig")

    to_download = filtered[filtered["eligible_for_download"]].copy()
    downloaded_rows: list[dict[str, str]] = []
    for i, (_, row) in enumerate(to_download.iterrows(), start=1):
        print(
            f"download/extract {i}/{len(to_download)} {row['sec_code']} {row['announcement_date']} {row['announcement_title'][:60]}",
            flush=True,
        )
        downloaded_rows.append(download_and_extract(row))
    downloaded = pd.DataFrame(downloaded_rows)
    if downloaded.empty:
        downloaded = to_download.copy()
        downloaded["download_status"] = ""
        downloaded["pdf_file"] = ""
        downloaded["txt_file"] = ""

    classified = pd.DataFrame([classify_downloaded(row) for _, row in downloaded.iterrows()])
    downloaded = pd.concat([downloaded.reset_index(drop=True), classified], axis=1)
    save_outputs(raw, query_counts, filtered, downloaded)

    print(f"raw_hits={len(raw)}", flush=True)
    print(f"eligible_download={len(to_download)}", flush=True)
    print(f"download_ok={downloaded['download_status'].eq('ok').sum()}", flush=True)
    print(f"auto_keep={downloaded['qian_auto_keep_candidate'].sum()}", flush=True)
    print(f"out_dir={OUT_DIR}", flush=True)
    print(f"doc={DOC_PATH}", flush=True)


if __name__ == "__main__":
    main()
