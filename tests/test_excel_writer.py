import unittest

from excel_writer import build_output_rows


TEST_TEMPLATE = {
    "fields": [
        {"name": "姓名", "default": ""},
        {"name": "性别", "default": ""}
    ],
    "output": {
        "first_row_overrides": {"性别": "户主"},
        "columns": [
            {"header": "案卷号", "source": "image_parent_name"},
            {"header": "姓名", "source": "field", "field": "姓名"},
            {"header": "性别", "source": "field", "field": "性别"},
            {"header": "原始图片名称", "source": "image_name"}
        ]
    }
}


class ExcelWriterTests(unittest.TestCase):
    def test_build_output_rows_uses_template_columns(self):
        rows = build_output_rows(
            [{"姓名": "张三", "性别": "男"}],
            TEST_TEMPLATE,
            r"E:\data\case001\page01\image.png",
        )

        self.assertEqual(rows[0]["案卷号"], "page01")
        self.assertEqual(rows[0]["姓名"], "张三")
        self.assertEqual(rows[0]["性别"], "户主")
        self.assertEqual(rows[0]["原始图片名称"], "image.png")


if __name__ == "__main__":
    unittest.main()
