import unittest

from utils.json_parser import parse_llm_json


class JsonParserTests(unittest.TestCase):
    def test_strips_code_fence(self):
        result = parse_llm_json("```json\n[{\"姓名\": \"张三\"}]\n```")

        self.assertEqual(result, [{"姓名": "张三"}])

    def test_strips_think_tags(self):
        result = parse_llm_json("<think>ignored</think>\n[{\"姓名\": \"张三\"}]")

        self.assertEqual(result, [{"姓名": "张三"}])


if __name__ == "__main__":
    unittest.main()
