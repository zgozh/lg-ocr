import types
import unittest

from llm_extract import build_fallback_people, build_prompt, extract_people


TEST_TEMPLATE = {
    "name": "demo",
    "display_name": "测试表",
    "fields": [
        {"name": "姓名", "default": "X", "description": "人员姓名"},
        {"name": "性别", "default": "X", "description": "人员性别"}
    ],
    "fallback_record": {"姓名": "X", "性别": "X"}
}


class FakeClient:
    def __init__(self, responses):
        self._responses = responses

    def chat(self, model, messages, **kwargs):
        item = self._responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return types.SimpleNamespace(message=types.SimpleNamespace(content=item))


class LLMExtractTests(unittest.TestCase):
    def test_build_prompt_includes_field_names(self):
        prompt = build_prompt(["姓名", "张三"], TEST_TEMPLATE)

        self.assertIn("测试表", prompt)
        self.assertIn("姓名", prompt)
        self.assertIn("性别", prompt)

    def test_retries_then_succeeds(self):
        responses = [
            RuntimeError("temporary failure"),
            "```json\n[{\"姓名\": \"张三\", \"性别\": \"男\"}]\n```"
        ]

        result = extract_people(
            ["姓名", "张三"],
            TEST_TEMPLATE,
            "http://localhost:11434",
            "qwen3:14b",
            max_retries=2,
            retry_delay_seconds=0,
            client_factory=lambda host: FakeClient(responses),
            sleep_fn=lambda seconds: None,
        )

        self.assertEqual(result, [{"姓名": "张三", "性别": "男"}])

    def test_raises_after_retry_exhausted(self):
        responses = [RuntimeError("boom"), RuntimeError("boom-again")]

        with self.assertRaisesRegex(
            RuntimeError, "LLM extraction failed after 2 attempts"
        ):
            extract_people(
                ["姓名", "张三"],
                TEST_TEMPLATE,
                "http://localhost:11434",
                "qwen3:14b",
                max_retries=2,
                retry_delay_seconds=0,
                client_factory=lambda host: FakeClient(responses),
                sleep_fn=lambda seconds: None,
            )

    def test_build_fallback_people_uses_template(self):
        self.assertEqual(
            build_fallback_people(TEST_TEMPLATE),
            [{"姓名": "X", "性别": "X"}],
        )


if __name__ == "__main__":
    unittest.main()
