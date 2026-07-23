#!/usr/bin/env python3
"""查询有赞内部知识库。"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import Any


ENDPOINT = "https://cloud-doc-center.s.qima-inc.com/doc/knowledge/search"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="查询有赞知识库。")
    parser.add_argument("query", help="搜索词，例如：订单接口")
    parser.add_argument("--original-query", help="原始问题，用于记录上下文")
    parser.add_argument("--top-k", type=int, default=3, help="返回结果数量")
    parser.add_argument("--endpoint", default=ENDPOINT, help="覆盖默认搜索接口地址")
    parser.add_argument("--timeout", type=float, default=30.0, help="请求超时时间，单位秒")
    parser.add_argument("--format", choices=("json", "pretty"), default="json", help="输出格式，默认 json")
    parser.add_argument("--full-response", action="store_true", help="在输出中附带接口完整原始响应")
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
            "title": "",
            "summary": truncate(stringify(item)),
            "categoryPath": "",
            "url": "",
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
        "title": title,
        "summary": truncate(summary),
        "categoryPath": category_path,
        "url": url,
        "docId": doc_id,
    }


def build_answer(
    original_query: str,
    used_query: str,
    top_k: int,
    data: Any,
    full_response: bool,
) -> dict[str, Any]:
    raw_items = find_result_list(data)
    evidence = [normalize_item(item) for item in raw_items[:top_k]]
    evidence = [item for item in evidence if any(item.values())]

    if evidence:
        primary = evidence[0]
        primary_name = primary["title"] or primary["summary"] or primary["docId"] or "首条结果"
        conclusion = f"知识库返回 {len(evidence)} 条与“{used_query}”相关的结果，优先参考：{primary_name}"
    else:
        conclusion = f"知识库未返回与“{used_query}”可归纳的结果。"

    sources = [
        {
            "title": item["title"],
            "categoryPath": item["categoryPath"],
            "url": item["url"],
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
            if item.get("categoryPath"):
                print(f"   类目路径：{item['categoryPath']}")
            if item.get("url"):
                print(f"   URL：{item['url']}")
            if item.get("docId"):
                print(f"   文档 ID：{item['docId']}")
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
    )
    if args.format == "pretty":
        print_pretty(answer)
    else:
        print(json.dumps(answer, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
