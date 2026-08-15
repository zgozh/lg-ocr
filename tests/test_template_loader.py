import unittest
import tempfile
import json

from template_loader import get_builtin_template_path, load_template


class TemplateLoaderTests(unittest.TestCase):
    def test_load_builtin_template(self):
        template = load_template(get_builtin_template_path())

        self.assertEqual(template["name"], "hukou_register")
        self.assertTrue(template["fields"])
        self.assertTrue(template["output"]["columns"])

    def test_load_template_normalizes_name_to_header(self):
        template_data = {
            "name": "demo",
            "display_name": "演示模板",
            "fields": [{"name": "姓名", "default": ""}],
            "output": {
                "columns": [
                    {"name": "姓名", "source": "field", "field": "姓名"}
                ]
            }
        }

        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as file:
            json.dump(template_data, file, ensure_ascii=False)
            temp_path = file.name

        try:
            template = load_template(temp_path)
        finally:
            import os
            os.unlink(temp_path)

        self.assertEqual(template["output"]["columns"][0]["header"], "姓名")


if __name__ == "__main__":
    unittest.main()
