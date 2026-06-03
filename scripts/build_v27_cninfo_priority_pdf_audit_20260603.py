#!/usr/bin/env python3
"""Download and audit priority CNINFO PDFs for Qian-style initiative coding."""

from __future__ import annotations

import csv
import html
import json
import re
import subprocess
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUN_TAG = "20260603"
DEFAULT_INPUT_PATH = (
    ROOT
    / "results"
    / f"v26_cninfo_fulltext_harvest_{RUN_TAG}"
    / "manual_review_priority_2023_2024_top3_candidates_per_firm.csv"
)
DEFAULT_LABEL = "2023_2024"
OUT_DIR = ROOT / "results" / f"v27_cninfo_priority_pdf_audit_{DEFAULT_LABEL}_{RUN_TAG}"
DOC_PATH = ROOT / "docs" / "empirical_runs" / f"90_v27_cninfo_priority_pdf_audit_{DEFAULT_LABEL}_{RUN_TAG}.md"
RAW_DIR = ROOT / "data" / "raw" / f"cninfo_priority_pdf_audit_{DEFAULT_LABEL}_{RUN_TAG}"
PDF_DIR = RAW_DIR / "raw_pdf"
TXT_DIR = RAW_DIR / "text"
STATIC_BASE = "https://static.cninfo.com.cn/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://www.cninfo.com.cn/new/fulltextSearch",
}

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
    "AI大模型",
    "多模态大模型",
    "基础大模型",
    "垂直大模型",
    "行业大模型",
    "通用大模型",
    "大模型",
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
STRICT_GENAI_PAT = re.compile("|".join(re.escape(t) for t in sorted(STRICT_GENAI_TERMS, key=len, reverse=True)), re.I)

ACTION_PAT = re.compile(
    r"发布|推出|上线|接入|集成|部署|落地|应用|商用|商业化|备案通过|通过备案|服务备案|服务登记|"
    r"签署|合作|共建|投资|建设|采购|中标|增资|设立|成立|收购|研发|升级|启动|发布会|"
    r"产品|平台|解决方案|智算中心|算力中心|训练中心|技术合作|战略合作|"
    r"launch|release|deploy|integrat",
    re.I,
)
TITLE_EVENT_PAT = re.compile(
    r"关于.*(签署|合作|框架协议|投资|增资|建设|采购|中标|收到.*通知书|自愿性信息披露|发布|上线|推出|接入|设立|成立|收购|备案|项目)"
)
COMPANY_ACTOR_PAT = re.compile(r"公司|本公司|子公司|控股子公司|全资子公司|集团|股份有限公司|有限公司|拟|已|将")
DENIAL_PAT = re.compile(
    r"暂未|暂无|尚未|尚无|不涉及|未涉及|未使用|没有.*业务|无.*业务|不存在|尚处|预研阶段|不确定性|风险|澄清|不构成",
    re.I,
)
ATTENTION_PAT = re.compile(r"密切关注|持续关注|积极关注|探索|研究相关机会|敬请关注|以公告为准")
NOISE_TITLE_PAT = re.compile(
    r"年度报告|半年度报告|季度报告|财务报告|董事会工作报告|董事会报告|监事会工作报告|"
    r"社会责任|ESG|可持续发展|环境、社会|内部控制|独立董事.*述职|股东大会|股东会|"
    r"持续督导|核查意见|法律意见|保荐|审计|评估报告|评级|问询|回复|反馈|"
    r"发行公告|发行安排|发行股票|招股|上市公告|募集说明书|方案论证|限制性股票|激励计划|员工持股|"
    r"业绩预告|异常波动|质量回报双提升|利润分配|估值提升计划|公司章程|制度"
)


def safe_name(text: str, limit: int = 180) -> str:
    text = re.sub(r"[\\/:*?\"<>|]", "_", str(text))
    text = re.sub(r"\s+", "_", text)
    return text[:limit].strip("_")


def strip_text(text: object) -> str:
    value = html.unescape(str(text or ""))
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value).strip()


def http_get_bytes(url: str, timeout: int = 45) -> tuple[int, bytes]:
    last_exc: Exception | None = None
    for attempt in range(5):
        try:
            req = Request(url, headers=HEADERS, method="GET")
            with urlopen(req, timeout=timeout) as resp:
                return int(getattr(resp, "status", 200)), resp.read()
        except Exception as exc:
            last_exc = exc
            time.sleep(0.8 + attempt * 0.5)
    raise RuntimeError(f"GET failed after retries: {last_exc}")


def local_paths(row: pd.Series) -> tuple[Path, Path]:
    name = safe_name(
        f"{row.get('announcement_date','')}_{str(row.get('sec_code','')).zfill(6)}_"
        f"{row.get('sec_name','')}_{row.get('announcement_id','')}_{row.get('announcement_title','')}"
    )
    return PDF_DIR / f"{name}.pdf", TXT_DIR / f"{name}.txt"


def download_extract(row: pd.Series) -> dict[str, object]:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path, txt_path = local_paths(row)
    out = {
        "download_status": "",
        "pdf_file": "",
        "txt_file": "",
        "pdf_bytes": 0,
        "text_chars": 0,
        "download_error": "",
    }
    url = str(row.get("pdf_url") or "")
    try:
        if not pdf_path.exists():
            status, content = http_get_bytes(url)
            if status != 200:
                out["download_status"] = f"download_failed_{status}"
                return out
            if b"%PDF" not in content[:4096]:
                out["download_status"] = "download_failed_not_pdf"
                out["download_error"] = content[:120].decode("utf-8", errors="replace")
                return out
            pdf_path.write_bytes(content)
        if not txt_path.exists() or txt_path.stat().st_size == 0:
            proc = subprocess.run(
                ["pdftotext", "-layout", str(pdf_path), str(txt_path)],
                capture_output=True,
                text=True,
            )
            if proc.returncode != 0:
                out["download_status"] = "pdftotext_failed"
                out["download_error"] = (proc.stderr or proc.stdout or "")[:300]
                out["pdf_file"] = str(pdf_path.relative_to(ROOT))
                out["pdf_bytes"] = pdf_path.stat().st_size if pdf_path.exists() else 0
                return out
        text = txt_path.read_text(encoding="utf-8", errors="ignore") if txt_path.exists() else ""
        out.update(
            {
                "download_status": "ok",
                "pdf_file": str(pdf_path.relative_to(ROOT)),
                "txt_file": str(txt_path.relative_to(ROOT)),
                "pdf_bytes": pdf_path.stat().st_size,
                "text_chars": len(text),
            }
        )
        return out
    except Exception as exc:
        out["download_status"] = f"error_{type(exc).__name__}"
        out["download_error"] = str(exc)[:300]
        return out


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def snippets(text: str, max_hits: int = 12, width: int = 180) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for match in STRICT_GENAI_PAT.finditer(text):
        start = max(0, match.start() - width)
        end = min(len(text), match.end() + width)
        snip = compact(text[start:end])
        if snip and snip not in seen:
            out.append(snip)
            seen.add(snip)
        if len(out) >= max_hits:
            break
    return out


def matched_terms(text: str) -> str:
    found = {t for t in STRICT_GENAI_TERMS if re.search(re.escape(t), text, flags=re.I)}
    return ";".join(sorted(found, key=lambda x: (len(x), x)))


def classify(row: pd.Series) -> dict[str, object]:
    text = ""
    txt_file = str(row.get("txt_file") or "")
    if txt_file:
        path = ROOT / txt_file
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="ignore")
    title = compact(str(row.get("announcement_title") or ""))
    search_blob = compact(f"{title} {text}")
    term_snips = snippets(search_blob)
    context = " || ".join(term_snips)
    terms = matched_terms(search_blob)
    context_action = bool(ACTION_PAT.search(context))
    full_action = bool(ACTION_PAT.search(search_blob))
    title_event = bool(TITLE_EVENT_PAT.search(title))
    company_actor = bool(COMPANY_ACTOR_PAT.search(context) or COMPANY_ACTOR_PAT.search(title))
    denial = bool(DENIAL_PAT.search(context) or DENIAL_PAT.search(title))
    attention = bool(ATTENTION_PAT.search(context))
    noisy_title = bool(NOISE_TITLE_PAT.search(title))
    has_terms = bool(terms)

    if row.get("download_status") != "ok":
        label = "exclude_download_or_text_failed"
        keep = 0
    elif not has_terms:
        label = "exclude_no_fulltext_genai"
        keep = 0
    elif denial:
        label = "review_denial_or_uncertain"
        keep = 0
    elif noisy_title and (context_action or full_action):
        label = "review_backfill_or_support_doc"
        keep = 0
    elif title_event and context_action and company_actor:
        label = "likely_qian_initiative"
        keep = 1
    elif context_action and company_actor and not attention:
        label = "review_possible_initiative"
        keep = 0
    elif context_action:
        label = "review_action_context_unclear_actor"
        keep = 0
    else:
        label = "exclude_mention_without_initiative"
        keep = 0

    return {
        "fulltext_matched_genai_terms": terms,
        "auto_pdf_label": label,
        "auto_keep_likely_qian": keep,
        "title_event_flag": int(title_event),
        "noisy_title_flag": int(noisy_title),
        "context_action_flag": int(context_action),
        "full_action_flag": int(full_action),
        "company_actor_flag": int(company_actor),
        "denial_or_uncertain_flag": int(denial),
        "attention_only_flag": int(attention),
        "pdf_genai_context": context[:6000],
    }


def md_table(df: pd.DataFrame, max_rows: int = 30) -> str:
    if df.empty:
        return "无"
    show = df.head(max_rows).copy()
    cols = list(show.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in show.iterrows():
        vals = [str(row.get(c, "")).replace("\n", " ").replace("|", "\\|")[:220] for c in cols]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def write_report(
    df: pd.DataFrame,
    sample_flow: pd.DataFrame,
    label_counts: pd.DataFrame,
    input_path: Path,
    label: str,
) -> None:
    examples_cols = [
        "sec_code",
        "sec_name",
        "announcement_date",
        "announcement_title",
        "auto_pdf_label",
        "fulltext_matched_genai_terms",
        "pdf_genai_context",
        "pdf_url",
    ]
    likely = df[df["auto_pdf_label"].eq("likely_qian_initiative")][examples_cols].sort_values(
        ["announcement_date", "sec_code"]
    )
    review = df[df["auto_pdf_label"].str.startswith("review", na=False)][examples_cols].sort_values(
        ["auto_pdf_label", "announcement_date", "sec_code"]
    )
    report = f"""# v27 CNINFO Priority PDF Audit

Date: 2026-06-03

## Purpose

This run downloads and extracts the `{input_path.name}` pool from v26. It tests whether the metadata-only CNINFO funnel still contains Qian-style concrete GenAI initiative events after reading the actual PDFs.

Run label: `{label}`

## Sample Flow

{md_table(sample_flow)}

## Auto Labels

{md_table(label_counts)}

## Likely Qian Initiative Examples

{md_table(likely, max_rows=40)}

## Review Examples

{md_table(review, max_rows=40)}

## Interpretation

`likely_qian_initiative` is still a machine triage label, not final treatment coding. The manual rule should remain strict: keep only events where the listed company or its controlled subsidiary is the actor, the text describes a concrete GenAI initiative, and the event date is not merely a later support document or retrospective report.
"""
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(report, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT_PATH), help="Candidate CSV from v26")
    parser.add_argument("--label", default=DEFAULT_LABEL, help="Output label, e.g. 2023_2024 or 2023_2026")
    parser.add_argument("--doc-index", default="90", help="Empirical-run report number")
    parser.add_argument("--workers", type=int, default=4)
    return parser.parse_args()


def configure_paths(label: str, doc_index: str) -> None:
    global OUT_DIR, DOC_PATH, RAW_DIR, PDF_DIR, TXT_DIR
    OUT_DIR = ROOT / "results" / f"v27_cninfo_priority_pdf_audit_{label}_{RUN_TAG}"
    DOC_PATH = ROOT / "docs" / "empirical_runs" / f"{doc_index}_v27_cninfo_priority_pdf_audit_{label}_{RUN_TAG}.md"
    RAW_DIR = ROOT / "data" / "raw" / f"cninfo_priority_pdf_audit_{label}_{RUN_TAG}"
    PDF_DIR = RAW_DIR / "raw_pdf"
    TXT_DIR = RAW_DIR / "text"


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    configure_paths(args.label, str(args.doc_index))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TXT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = pd.read_csv(input_path)
    if candidates.empty:
        raise SystemExit(f"No candidates: {input_path}")

    rows: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(download_extract, row): i for i, (_, row) in enumerate(candidates.iterrows(), start=1)}
        for done, future in enumerate(as_completed(futures), start=1):
            i = futures[future]
            row = candidates.iloc[i - 1].to_dict()
            info = future.result()
            row.update(info)
            rows.append(row)
            if done % 25 == 0 or done == len(futures):
                print(f"download/extract {done}/{len(futures)}", flush=True)

    downloaded = pd.DataFrame(rows).sort_values(["sec_code", "announcement_date", "announcement_id"])
    classified = pd.DataFrame([classify(row) for _, row in downloaded.iterrows()])
    out = pd.concat([downloaded.reset_index(drop=True), classified], axis=1)

    out.to_csv(OUT_DIR / "cninfo_priority_pdf_downloaded_classified.csv.gz", index=False, compression="gzip")
    out.to_csv(OUT_DIR / "manual_review_priority_pdf_all.csv", index=False, encoding="utf-8-sig")
    likely = out[out["auto_keep_likely_qian"].eq(1)].copy()
    likely.to_csv(OUT_DIR / "manual_review_likely_qian_initiatives.csv", index=False, encoding="utf-8-sig")
    review = out[out["auto_pdf_label"].str.startswith("review", na=False)].copy()
    review.to_csv(OUT_DIR / "manual_review_possible_or_backfill.csv", index=False, encoding="utf-8-sig")

    sample_flow = pd.DataFrame(
        [
            {"stage": "input_priority_top3_rows", "rows": len(candidates), "announcements": candidates["announcement_id"].nunique(), "firms": candidates["sec_code"].nunique()},
            {"stage": "download_ok", "rows": int(out["download_status"].eq("ok").sum()), "announcements": out.loc[out["download_status"].eq("ok"), "announcement_id"].nunique(), "firms": out.loc[out["download_status"].eq("ok"), "sec_code"].nunique()},
            {"stage": "likely_qian_initiative", "rows": len(likely), "announcements": likely["announcement_id"].nunique(), "firms": likely["sec_code"].nunique() if not likely.empty else 0},
            {"stage": "review_possible_or_backfill", "rows": len(review), "announcements": review["announcement_id"].nunique() if not review.empty else 0, "firms": review["sec_code"].nunique() if not review.empty else 0},
        ]
    )
    sample_flow.to_csv(OUT_DIR / "sample_flow.csv", index=False, encoding="utf-8-sig")
    label_counts = (
        out.groupby("auto_pdf_label", dropna=False)
        .agg(rows=("announcement_id", "size"), announcements=("announcement_id", "nunique"), firms=("sec_code", "nunique"))
        .reset_index()
        .sort_values(["rows"], ascending=False)
    )
    label_counts.to_csv(OUT_DIR / "auto_pdf_label_counts.csv", index=False, encoding="utf-8-sig")
    write_report(out, sample_flow, label_counts, input_path, args.label)

    print(f"input_rows={len(candidates)}", flush=True)
    print(f"download_ok={int(out['download_status'].eq('ok').sum())}", flush=True)
    print(f"likely_qian={len(likely)}", flush=True)
    print(f"out_dir={OUT_DIR}", flush=True)
    print(f"doc={DOC_PATH}", flush=True)


if __name__ == "__main__":
    main()
