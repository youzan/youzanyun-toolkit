import importlib.util
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "search_knowledge.py"
SPEC = importlib.util.spec_from_file_location("search_knowledge", SCRIPT_PATH)
SEARCH = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(SEARCH)


class SourceHydrationTest(unittest.TestCase):
    def test_markdown_source_url_is_derived_for_token_document(self):
        source_url = "https://doc.youzanyun.com/v2/doc/client/token/example"

        self.assertEqual(
            SEARCH.markdown_source_url(source_url),
            "https://doc.youzanyun.com/v2/doc/client/token/example.md",
        )

    def test_relevant_excerpt_keeps_matching_request_parameter(self):
        markdown = "\n".join(
            [
                "# 查询售后单列表",
                "说明文字",
                "## 请求参数",
                "| 名称 | 类型 | 必填 | 描述 |",
                "| --- | --- | --- | --- |",
                "| tid | String | 否 | 有赞订单号 |",
                "| page_no | Number | 否 | 页码 |",
                "## 响应参数",
            ]
        )

        excerpt = SEARCH.relevant_excerpt(markdown, "订单号 入参 查询", limit=400)

        self.assertIn("tid", excerpt)
        self.assertIn("有赞订单号", excerpt)

    def test_hydration_adds_markdown_excerpt_to_first_evidence_only(self):
        evidence = [
            {
                "title": "查询售后单列表",
                "sourceUrl": "https://doc.youzanyun.com/v2/doc/client/token/example",
            },
            {
                "title": "其他文档",
                "sourceUrl": "https://doc.youzanyun.com/v2/doc/client/token/other",
            },
        ]
        markdown = "## 请求参数\n| tid | String | 否 | 有赞订单号 |"

        with mock.patch.object(SEARCH, "fetch_text", return_value=markdown) as fetch_text:
            SEARCH.hydrate_evidence(evidence, "订单号 入参 查询", depth=1, timeout=5, excerpt_limit=800)

        self.assertEqual(fetch_text.call_count, 1)
        self.assertIn("有赞订单号", evidence[0]["sourceExcerpt"])
        self.assertNotIn("sourceExcerpt", evidence[1])


if __name__ == "__main__":
    unittest.main()
