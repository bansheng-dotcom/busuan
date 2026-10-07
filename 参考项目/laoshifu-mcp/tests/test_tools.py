"""End-to-end checks: the MCP tools must return real engine output."""
from __future__ import annotations

import asyncio
import json
import unittest

from laoshifu_mcp.digest import chart_summary, fusion_payload
from laoshifu_mcp.server import server


def call(name: str, arguments: dict) -> list:
    result = asyncio.run(server.call_tool(name, arguments))
    return list(result.content)


def as_json(name: str, arguments: dict) -> dict:
    content = call(name, arguments)
    return json.loads(content[0].text)


class ToolRegistrationTests(unittest.TestCase):
    def test_all_tools_registered(self):
        tools = asyncio.run(server.list_tools())
        names = {tool.name for tool in tools}
        self.assertEqual(
            names,
            {
                "bazi_ziwei_chart",
                "liuyao_qimen_fusion",
                "hexagram_diagram",
                "resolve_pillars",
                "laoshifu_consultation",
            },
        )

    def test_reading_prompt_registered(self):
        prompts = asyncio.run(server.list_prompts())
        self.assertIn("laoshifu_reading", {prompt.name for prompt in prompts})


class ChartToolTests(unittest.TestCase):
    def test_solar_chart_matches_engine(self):
        chart = as_json(
            "bazi_ziwei_chart",
            {
                "year": 2000,
                "month": 1,
                "day": 1,
                "hour": 12,
                "gender": "male",
                "calendar": "solar",
                "current_year": 2026,
            },
        )
        self.assertEqual(chart["pillars"]["formatted"], "己卯 丙子 戊午 戊午")
        self.assertEqual(len(chart["ziwei"]["gongs"]), 12)
        self.assertEqual(len(chart["dayun"]), 9)
        self.assertEqual(chart["currentYear"]["year"], 2026)
        # bazi/ziwei duplicate blocks are dropped in summary mode
        self.assertNotIn("siZhu", chart["bazi"])
        self.assertNotIn("siZhu", chart["ziwei"])

    def test_full_detail_keeps_duplicates(self):
        chart = as_json(
            "bazi_ziwei_chart",
            {
                "year": 2000,
                "month": 1,
                "day": 1,
                "hour": 12,
                "gender": "male",
                "detail": "full",
                "current_year": 2026,
            },
        )
        self.assertIn("siZhu", chart["bazi"])

    def test_lunar_chart_differs_from_solar(self):
        lunar = as_json(
            "bazi_ziwei_chart",
            {
                "year": 2000,
                "month": 1,
                "day": 1,
                "hour": 12,
                "gender": "male",
                "calendar": "lunar",
                "current_year": 2026,
            },
        )
        self.assertEqual(lunar["meta"]["calendar"], "lunar")
        self.assertNotEqual(lunar["pillars"]["formatted"], "己卯 丙子 戊午 戊午")

    def test_rejects_non_utc8(self):
        payload = as_json(
            "bazi_ziwei_chart",
            {
                "year": 2000,
                "month": 1,
                "day": 1,
                "hour": 12,
                "gender": "male",
                "time_zone": 9,
            },
        )
        self.assertFalse(payload["ok"])

    def test_rejects_impossible_solar_date(self):
        payload = as_json(
            "bazi_ziwei_chart",
            {"year": 2001, "month": 2, "day": 30, "hour": 12, "gender": "female"},
        )
        self.assertFalse(payload["ok"])

    def test_rejects_leap_month_on_solar(self):
        payload = as_json(
            "bazi_ziwei_chart",
            {
                "year": 2000,
                "month": 5,
                "day": 5,
                "hour": 9,
                "gender": "female",
                "is_leap_month": True,
            },
        )
        self.assertFalse(payload["ok"])


class EventToolTests(unittest.TestCase):
    EVENT = {
        "question": "这个月底前，甲方会不会签下这份合同？",
        "category": "career",
        "method": "numbers",
        "numbers": [12, 35, 8],
        "year": 2026,
        "month": 9,
        "day": 17,
        "hour": 10,
        "minute": 30,
        "time_zone": 8,
    }

    def test_numbers_method_returns_both_systems(self):
        fusion = as_json("liuyao_qimen_fusion", dict(self.EVENT))
        self.assertEqual(fusion["question"]["text"], self.EVENT["question"])
        self.assertTrue(fusion["conclusions"])
        self.assertIn("liuyao", fusion["methods"])
        self.assertIn("qimen", fusion["methods"])
        # the deprecated legacy blob is dropped in summary mode
        self.assertNotIn("diagram", fusion)
        self.assertIn("diagramData", fusion)

    def test_time_method(self):
        args = dict(self.EVENT)
        args["method"] = "time"
        args.pop("numbers")
        fusion = as_json("liuyao_qimen_fusion", args)
        self.assertTrue(fusion["diagramData"])

    def test_time_method_rejects_numbers(self):
        args = dict(self.EVENT)
        args["method"] = "time"
        self.assertFalse(as_json("liuyao_qimen_fusion", args)["ok"])

    def test_numbers_method_requires_three(self):
        args = dict(self.EVENT)
        args["numbers"] = [12, 35]
        self.assertFalse(as_json("liuyao_qimen_fusion", args)["ok"])

    def test_diagram_returns_png_and_text(self):
        content = call("hexagram_diagram", dict(self.EVENT))
        kinds = [type(item).__name__ for item in content]
        self.assertIn("ImageContent", kinds)
        self.assertIn("TextContent", kinds)
        image = next(item for item in content if type(item).__name__ == "ImageContent")
        self.assertEqual(image.mime_type, "image/png")
        self.assertGreater(len(image.data), 10_000)
        text = next(item for item in content if type(item).__name__ == "TextContent")
        self.assertIn("逐爻", text.text)

    def test_diagram_rejects_bad_numbers(self):
        args = dict(self.EVENT)
        args["numbers"] = [0, 1, 2]
        content = call("hexagram_diagram", args)
        self.assertEqual(len(content), 1)
        self.assertFalse(json.loads(content[0].text)["ok"])


class PillarLookupTests(unittest.TestCase):
    def test_unique_candidate_is_found(self):
        payload = as_json(
            "resolve_pillars",
            {"pillars": "己卯 丙子 戊午 戊午", "start_year": 1999, "end_year": 2000},
        )
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["candidates"][0]["date"], "2000-01-01")
        self.assertEqual(payload["candidates"][0]["range"], "11:00-13:00")

    def test_ambiguous_range_returns_many_candidates(self):
        payload = as_json(
            "resolve_pillars",
            {"pillars": "己卯 丙子 戊午 戊午", "start_year": 1900, "end_year": 2100},
        )
        self.assertGreater(payload["count"], 1)
        self.assertEqual(
            [candidate["date"] for candidate in payload["candidates"]][:2],
            ["2000-01-01", "2059-12-17"],
        )

    def test_rejects_non_pillar_text(self):
        payload = as_json(
            "resolve_pillars",
            {"pillars": "己卯 丙子", "start_year": 1999, "end_year": 2000},
        )
        self.assertFalse(payload["ok"])


class ConsultationEntryTests(unittest.TestCase):
    def test_entry_points_are_present(self):
        payload = as_json("laoshifu_consultation", {})
        self.assertTrue(payload["ok"])
        urls = {entry["url"] for entry in payload["entryPoints"]}
        self.assertTrue(any("skillhub.cn" in url for url in urls))
        self.assertIn("双系统交叉验证", payload["intro"])


class DigestTests(unittest.TestCase):
    def test_chart_summary_does_not_mutate_input(self):
        original = {"bazi": {"siZhu": {"year": "甲"}, "dayMaster": "戊"}, "meta": {"input": {}}}
        summary = chart_summary(original)
        self.assertIn("siZhu", original["bazi"])
        self.assertNotIn("siZhu", summary["bazi"])

    def test_fusion_payload_keeps_diagram_data(self):
        original = {"diagram": {"legacy": True}, "diagramData": {"pillars": []}}
        payload = fusion_payload(original, "summary")
        self.assertNotIn("diagram", payload)
        self.assertIn("diagramData", payload)
        self.assertIn("diagram", fusion_payload(original, "full"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
