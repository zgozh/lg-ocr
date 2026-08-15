import unittest

from config import _CONFIG_DATA, build_predict_flags


class BuildPredictFlagsTests(unittest.TestCase):
    def test_flags_come_from_pipeline_config_not_hardcoded(self):
        """predict() 的开关应来自 config.json 的 pipeline 段，而非硬编码。"""
        original = dict(_CONFIG_DATA["pipeline"])
        try:
            # 设成与真实配置相反的值，验证确实被读取而非写死
            _CONFIG_DATA["pipeline"] = {
                "use_layout_detection": False,
                "use_doc_orientation_classify": True,
                "use_doc_unwarping": True,
            }

            flags = build_predict_flags()

            self.assertFalse(flags["use_layout_detection"])
            self.assertTrue(flags["use_doc_orientation_classify"])
            self.assertTrue(flags["use_doc_unwarping"])
            self.assertFalse(flags["use_table_orientation_classify"])
        finally:
            _CONFIG_DATA["pipeline"] = original


if __name__ == "__main__":
    unittest.main()
