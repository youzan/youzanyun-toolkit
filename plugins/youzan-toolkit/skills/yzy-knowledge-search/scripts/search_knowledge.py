#!/usr/bin/env python3
"""查询有赞内部知识库。"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from typing import Any


ENDPOINT = "http://doc.youzanyun.com/api/doc/knowledge/search"
LLMS_INDEX_URL = "https://doc.youzanyun.com/llms.txt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="查询有赞知识库。")
    parser.add_argument("query", help="搜索词，例如：订单接口")
    parser.add_argument("--original-query", help="原始问题，用于记录上下文")
    parser.add_argument("--top-k", type=int, default=3, help="返回结果数量")
    parser.add_argument("--endpoint", default=ENDPOINT, help="覆盖默认搜索接口地址")
    parser.add_argument("--timeout", type=float, default=30.0, help="请求超时时间，单位秒")
    parser.add_argument("--format", choices=("json", "pretty"), default="json", help="输出格式，默认 json")
    parser.add_argument("--full-response", action="store_true", help="在输出中附带接口完整原始响应")
    parser.add_argument("--no-navigation", action="store_true", help="不读取 llms.txt 文档导航")
    parser.add_argument("--navigation-url", default=LLMS_INDEX_URL, help="llms.txt 导航地址")
    parser.add_argument("--navigation-top-n", type=int, default=5, help="返回导航候选数量")
    parser.add_argument("--navigation-timeout", type=float, default=5.0, help="导航请求超时时间，单位秒")
    parser.add_argument("--navigation-module-depth", type=int, default=3, help="读取前 N 个模块的二级目录")
    parser.add_argument("--no-source-hydration", action="store_true", help="不读取首条结果的 Markdown 原文")
    parser.add_argument("--source-depth", type=int, default=1, help="读取前 N 条结果的 Markdown 原文")
    parser.add_argument("--source-timeout", type=float, default=5.0, help="原文请求超时时间，单位秒")
    parser.add_argument("--source-excerpt-limit", type=int, default=2500, help="每条原文相关片段的最大字符数")
    return parser.parse_args()


def first_value(item: dict[str, Any], names: tuple[str, ...]) -> Any:
    for name in names:
        if name in item and item[name] not in (None, ""):
            return item[name]
    return None


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " / ".join(stringify(part) for part in value if stringify(part))
    return json.dumps(value, ensure_ascii=False)


def truncate(text: str, limit: int = 240) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


def markdown_source_url(url: str) -> str:
    """Return the downloadable Markdown URL for a supported Youzan doc URL."""
    clean_url = url.strip().rstrip("/")
    if not clean_url:
        return ""
    if clean_url.endswith(".md"):
        return clean_url
    if re.match(
        r"^https?://doc\.youzanyun\.com/(?:v2/doc/(?:client|cloud)/token|resource/doc)/[^/?#]+$",
        clean_url,
    ):
        return f"{clean_url}.md"
    return ""


def relevant_excerpt(markdown: str, query: str, limit: int = 2500) -> str:
    """Keep compact Markdown windows around the lines most relevant to the query."""
    if limit < 1:
        return ""
    lines = markdown.splitlines()
    if not lines:
        return ""

    terms = sorted(query_terms(query), key=len, reverse=True)
    scored_lines: list[tuple[int, int]] = []
    for index, line in enumerate(lines):
        lowered = line.lower()
        score = sum(max(1, len(term)) for term in terms if term in lowered)
        if score:
            scored_lines.append((score, index))

    if not scored_lines:
        return truncate(markdown, limit)

    selected: list[int] = []
    for _, index in sorted(scored_lines, reverse=True):
        if all(abs(index - previous) > 12 for previous in selected):
            selected.append(index)
        if len(selected) == 3:
            break

    windows: list[tuple[int, int]] = []
    for index in sorted(selected):
        start = max(0, index - 5)
        end = min(len(lines), index + 9)
        if windows and start <= windows[-1][1]:
            windows[-1] = (windows[-1][0], max(windows[-1][1], end))
        else:
            windows.append((start, end))

    excerpt = "\n\n...\n\n".join("\n".join(lines[start:end]).strip() for start, end in windows)
    return truncate(excerpt, limit)


def hydrate_evidence(
    evidence: list[dict[str, str]],
    query: str,
    depth: int,
    timeout: float,
    excerpt_limit: int,
) -> None:
    """Attach relevant Markdown excerpts so the agent does not need repeated fetches."""
    for item in evidence[: max(0, depth)]:
        markdown_url = markdown_source_url(item.get("sourceUrl", ""))
        if not markdown_url:
            continue
        try:
            markdown = fetch_text(markdown_url, timeout)
            excerpt = relevant_excerpt(markdown, query, excerpt_limit)
            if excerpt:
                item["sourceExcerpt"] = excerpt
                item["hydratedSourceUrl"] = markdown_url
        except Exception as exc:  # noqa: BLE001 - search evidence remains usable when hydration fails.
            item["sourceHydrationError"] = f"读取原文失败：{exc}"


def fetch_text(url: str, timeout: float) -> str:
    request = urllib.request.Request(url, headers={"Accept": "text/plain, text/markdown, */*"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8")


def parse_markdown_links(markdown: str) -> list[dict[str, str]]:
    entries = []
    pattern = re.compile(r"^\s*[-*]\s+\[([^\]]+)\]\(([^)]+)\)\s*(?:[-:：]\s*)?(.*)$")
    for line in markdown.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        title, url, summary = match.groups()
        entries.append(
            {
                "title": title.strip(),
                "url": url.strip(),
                "summary": summary.strip(),
            }
        )
    return entries


def query_terms(text: str) -> set[str]:
    terms: set[str] = set()
    for token in re.findall(r"[A-Za-z0-9_.:/-]{2,}|[\u4e00-\u9fff]{2,}", text.lower()):
        terms.add(token)
        if re.fullmatch(r"[\u4e00-\u9fff]{3,}", token):
            terms.update(token[index : index + 2] for index in range(len(token) - 1))
    return terms


def rank_entries(query: str, entries: list[dict[str, str]], limit: int) -> list[dict[str, Any]]:
    terms = query_terms(query)
    ranked = []
    for entry in entries:
        haystack = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
        score = sum(1 for term in terms if term and term in haystack)
        if query and query.lower() in haystack:
            score += 5
        ranked.append({**entry, "score": score})
    ranked.sort(key=lambda item: (item["score"], item["title"]), reverse=True)
    if any(item["score"] > 0 for item in ranked):
        ranked = [item for item in ranked if item["score"] > 0]
    return ranked[:limit]


def build_navigation(
    query: str,
    index_url: str,
    top_n: int,
    timeout: float,
    module_depth: int,
) -> dict[str, Any]:
    navigation: dict[str, Any] = {
        "indexUrl": index_url,
        "modules": [],
        "limitations": "llms.txt 仅用于定位文档目录范围；最终结论仍需结合知识库检索结果。",
    }
    try:
        index_text = fetch_text(index_url, timeout)
        modules = rank_entries(query, parse_markdown_links(index_text), top_n)
    except Exception as exc:  # noqa: BLE001 - surface navigation failure without failing search.
        navigation["error"] = f"读取导航失败：{exc}"
        return navigation

    enriched_modules = []
    for module in modules:
        enriched = {
            "title": module["title"],
            "url": module["url"],
            "summary": module["summary"],
            "score": module["score"],
            "documents": [],
        }
        if len(enriched_modules) < module_depth:
            try:
                module_text = fetch_text(module["url"], timeout)
                enriched["documents"] = rank_entries(query, parse_markdown_links(module_text), top_n)
            except Exception as exc:  # noqa: BLE001
                enriched["documentError"] = f"读取模块目录失败：{exc}"
        enriched_modules.append(enriched)

    navigation["modules"] = enriched_modules
    return navigation


def find_result_list(data: Any) -> list[Any]:
    if isinstance(data, list):
        return data
    if not isinstance(data, dict):
        return []

    preferred_keys = (
        "data",
        "result",
        "results",
        "items",
        "list",
        "records",
        "documents",
        "docs",
        "knowledgeList",
    )
    for key in preferred_keys:
        value = data.get(key)
        if isinstance(value, list):
            return value
        if isinstance(value, dict):
            nested = find_result_list(value)
            if nested:
                return nested

    for value in data.values():
        nested = find_result_list(value)
        if nested:
            return nested
    return []


def normalize_item(item: Any) -> dict[str, str]:
    if not isinstance(item, dict):
        return {
            "sourceType": "knowledge",
            "title": "",
            "summary": truncate(stringify(item)),
            "categoryPath": "",
            "url": "",
            "sourceUrl": "",
            "docId": "",
        }

    title = stringify(first_value(item, ("title", "docTitle", "name", "question", "heading")))
    summary = stringify(
        first_value(
            item,
            (
                "summary",
                "snippet",
                "content",
                "answer",
                "text",
                "description",
                "docContent",
                "chunk",
            ),
        )
    )
    category_path = stringify(
        first_value(item, ("categoryPath", "category", "path", "catalogPath", "docPath", "breadcrumb"))
    )
    url = stringify(first_value(item, ("url", "link", "docUrl", "sourceUrl")))
    doc_id = stringify(first_value(item, ("docId", "documentId", "id", "knowledgeId", "sourceId")))

    if not summary:
        remaining = {
            key: value
            for key, value in item.items()
            if key
            not in {
                "title",
                "docTitle",
                "name",
                "question",
                "heading",
                "categoryPath",
                "category",
                "path",
                "catalogPath",
                "docPath",
                "breadcrumb",
                "url",
                "link",
                "docUrl",
                "sourceUrl",
                "docId",
                "documentId",
                "id",
                "knowledgeId",
                "sourceId",
            }
        }
        summary = stringify(remaining)

    return {
        "sourceType": "knowledge",
        "title": title,
        "summary": truncate(summary),
        "categoryPath": category_path,
        "url": url,
        "sourceUrl": url,
        "docId": doc_id,
    }


def append_source_link(links: list[dict[str, str]], seen: set[tuple[str, str]], source: dict[str, str]) -> None:
    url = source.get("url") or source.get("sourceUrl")
    title = source.get("title") or source.get("docId") or url
    if not url:
        return
    key = (source.get("sourceType", ""), url)
    if key in seen:
        return
    seen.add(key)
    links.append(
        {
            "sourceType": source.get("sourceType", ""),
            "title": title,
            "url": url,
        }
    )


def build_traceability(evidence: list[dict[str, str]], navigation: dict[str, Any] | None) -> dict[str, Any]:
    links: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for item in evidence:
        append_source_link(links, seen, item)

    if navigation:
        index_url = navigation.get("indexUrl")
        if index_url:
            append_source_link(
                links,
                seen,
                {
                    "sourceType": "navigation-index",
                    "title": "有赞云 llms.txt 文档目录",
                    "url": index_url,
                },
            )
        for module in navigation.get("modules") or []:
            append_source_link(
                links,
                seen,
                {
                    "sourceType": "navigation-module",
                    "title": stringify(module.get("title")),
                    "url": stringify(module.get("url")),
                },
            )
            for doc in module.get("documents") or []:
                append_source_link(
                    links,
                    seen,
                    {
                        "sourceType": "navigation-document",
                        "title": stringify(doc.get("title")),
                        "url": stringify(doc.get("url")),
                    },
                )

    missing_evidence_links = [
        item.get("title") or item.get("docId") or item.get("summary", "")[:40]
        for item in evidence
        if not item.get("sourceUrl")
    ]
    return {
        "sourceLinks": links,
        "missingEvidenceLinks": [item for item in missing_evidence_links if item],
        "limitations": "回答必须引用 sourceLinks 中的原始链接；缺少链接的 evidence 只能作为弱依据。",
    }


def build_answer(
    original_query: str,
    used_query: str,
    top_k: int,
    data: Any,
    full_response: bool,
    navigation: dict[str, Any] | None,
    source_depth: int = 1,
    source_timeout: float = 5.0,
    source_excerpt_limit: int = 2500,
) -> dict[str, Any]:
    raw_items = find_result_list(data)
    evidence = [normalize_item(item) for item in raw_items[:top_k]]
    evidence = [item for item in evidence if any(item.values())]
    if source_depth > 0:
        hydrate_evidence(evidence, used_query, source_depth, source_timeout, source_excerpt_limit)

    if evidence:
        primary = evidence[0]
        primary_name = primary["title"] or primary["summary"] or primary["docId"] or "首条结果"
        conclusion = f"知识库返回 {len(evidence)} 条与“{used_query}”相关的结果，优先参考：{primary_name}"
    else:
        conclusion = f"知识库未返回与“{used_query}”可归纳的结果。"

    sources = [
        {
            "sourceType": item["sourceType"],
            "title": item["title"],
            "categoryPath": item["categoryPath"],
            "url": item["url"],
            "sourceUrl": item["sourceUrl"],
            "docId": item["docId"],
        }
        for item in evidence
        if item["title"] or item["categoryPath"] or item["url"] or item["docId"]
    ]

    answer: dict[str, Any] = {
        "originalQuery": original_query,
        "usedQuery": used_query,
        "topK": top_k,
        "conclusion": conclusion,
        "evidence": evidence,
        "sources": sources,
        "navigation": navigation,
        "traceability": build_traceability(evidence, navigation),
        "limitations": "仅基于知识库接口返回内容归纳；未返回的信息不作推断。",
    }
    if full_response:
        answer["fullResponse"] = data
    return answer


def print_pretty(answer: dict[str, Any]) -> None:
    if answer.get("usedQuery") != answer.get("originalQuery"):
        print(f"检索词：{answer['usedQuery']}")
        print(f"原始问题：{answer['originalQuery']}\n")
    print(f"结论：{answer['conclusion']}")
    evidence = answer.get("evidence") or []
    if evidence:
        print("\n关键依据：")
        for index, item in enumerate(evidence, start=1):
            title = item.get("title") or item.get("docId") or f"结果 {index}"
            print(f"{index}. {title}")
            if item.get("summary"):
                print(f"   摘要：{item['summary']}")
            if item.get("sourceExcerpt"):
                print("   原文相关片段：")
                print(item["sourceExcerpt"])
            if item.get("hydratedSourceUrl"):
                print(f"   Markdown 原文：{item['hydratedSourceUrl']}")
            if item.get("categoryPath"):
                print(f"   类目路径：{item['categoryPath']}")
            if item.get("url"):
                print(f"   URL：{item['url']}")
            if item.get("docId"):
                print(f"   文档 ID：{item['docId']}")
            if not item.get("sourceUrl"):
                print("   链接状态：缺少原始链接，仅作弱依据")
    navigation = answer.get("navigation") or {}
    modules = navigation.get("modules") or []
    if modules:
        print("\n目录导航：")
        for index, module in enumerate(modules, start=1):
            print(f"{index}. {module['title']} - {module.get('summary', '')}")
            print(f"   {module['url']}")
            documents = module.get("documents") or []
            for doc in documents[:3]:
                print(f"   - {doc['title']}: {doc.get('url', '')}")
    elif navigation.get("error"):
        print(f"\n目录导航：{navigation['error']}")
    traceability = answer.get("traceability") or {}
    links = traceability.get("sourceLinks") or []
    if links:
        print("\n原始链接：")
        for index, link in enumerate(links, start=1):
            print(f"{index}. [{link.get('sourceType', '')}] {link.get('title', '')}")
            print(f"   {link.get('url', '')}")
    missing_links = traceability.get("missingEvidenceLinks") or []
    if missing_links:
        print("\n缺少原始链接的弱依据：")
        for item in missing_links:
            print(f"- {item}")
    print(f"\n限制：{answer['limitations']}")
    if "fullResponse" in answer:
        print("\n原始响应：")
        print(json.dumps(answer["fullResponse"], ensure_ascii=False, indent=2))


def main() -> int:
    args = parse_args()
    if args.top_k < 1:
        print("--top-k 必须大于等于 1", file=sys.stderr)
        return 2

    used_query = args.query.strip()
    original_query = (args.original_query or used_query).strip()
    navigation = None
    if not args.no_navigation:
        navigation = build_navigation(
            used_query,
            args.navigation_url,
            args.navigation_top_n,
            args.navigation_timeout,
            args.navigation_module_depth,
        )
    payload = json.dumps({"query": used_query, "topK": args.top_k}, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        args.endpoint,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code}: {detail}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"请求失败：{exc}", file=sys.stderr)
        return 1

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        print(body)
        return 0

    answer = build_answer(
        original_query,
        used_query,
        args.top_k,
        data,
        args.full_response,
        navigation,
        source_depth=0 if args.no_source_hydration else args.source_depth,
        source_timeout=args.source_timeout,
        source_excerpt_limit=args.source_excerpt_limit,
    )
    if args.format == "pretty":
        print_pretty(answer)
    else:
        print(json.dumps(answer, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
