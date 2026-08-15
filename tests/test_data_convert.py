import unittest

from utils.convert_to_2d_array import convert_to_2d_array


class ConvertTo2DArrayTests(unittest.TestCase):
    def test_uses_explicit_field_order(self):
        data = [
            {"姓名": "张三", "性别": "男", "民族": "汉"},
            {"姓名": "李四", "性别": "女", "民族": "满"},
        ]

        result = convert_to_2d_array(data, ["民族", "姓名"])

        self.assertEqual(result, [["汉", "满"], ["张三", "李四"]])

    def test_handles_missing_field(self):
        data = [{"姓名": "张三"}, {"姓名": "李四", "性别": "女"}]

        result = convert_to_2d_array(data, ["姓名", "性别"])

        self.assertEqual(result, [["张三", "李四"], ["", "女"]])


if __name__ == "__main__":
    unittest.main()
