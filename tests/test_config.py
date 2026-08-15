import unittest
from unittest.mock import patch

from config import (
    OCRLLMConfig,
    build_pipeline_kwargs,
    resolve_required_model_dirs,
)


class ConfigTests(unittest.TestCase):
    def test_build_pipeline_kwargs_prefers_delivery_directory_models(self):
        resolved_dirs = {
            "layout_detection_model_dir": r"E:\delivery\models\PP-DocLayout-L",
            "table_classification_model_dir": r"E:\delivery\models\PP-LCNet_x1_0_table_cls",
            "wired_table_structure_recognition_model_dir": r"E:\delivery\models\SLANeXt_wired",
            "wireless_table_structure_recognition_model_dir": r"E:\delivery\models\SLANeXt_wireless",
            "wired_table_cells_detection_model_dir": r"E:\delivery\models\RT-DETR-L_wired_table_cell_det",
            "wireless_table_cells_detection_model_dir": r"E:\delivery\models\RT-DETR-L_wireless_table_cell_det",
            "text_recognition_model_dir": r"E:\delivery\models\PP-OCRv5_server_rec",
            "text_detection_model_dir": r"E:\delivery\models\PP-OCRv5_server_det",
        }
        config = OCRLLMConfig(
            input_dir=r"E:\images",
            is_paginated=True,
            template_path="demo.json",
        )

        with patch("config.resolve_required_model_dirs", return_value=resolved_dirs):
            kwargs = build_pipeline_kwargs(config)

        self.assertEqual(
            kwargs["layout_detection_model_dir"],
            resolved_dirs["layout_detection_model_dir"],
        )
        self.assertEqual(
            kwargs["wired_table_structure_recognition_model_dir"],
            resolved_dirs["wired_table_structure_recognition_model_dir"],
        )
        self.assertEqual(
            kwargs["text_detection_model_dir"],
            resolved_dirs["text_detection_model_dir"],
        )

    def test_config_rejects_is_handwriting(self):
        with self.assertRaises(TypeError):
            OCRLLMConfig(
                input_dir=r"E:\images",
                is_paginated=True,
                is_handwriting=True,
                template_path="demo.json",
            )

    def test_resolve_required_model_dirs_returns_existing_dirs(self):
        import os
        import tempfile

        import config as config_module

        with tempfile.TemporaryDirectory() as tmp:
            model_dir = os.path.join(tmp, "PP-DocLayout-L")
            os.makedirs(model_dir)
            original = config_module.REQUIRED_MODELS
            try:
                config_module.REQUIRED_MODELS = {
                    "layout_detection_model_dir": {
                        "display_name": "PP-DocLayout-L",
                        "path": model_dir,
                    },
                }
                resolved = resolve_required_model_dirs()
                self.assertEqual(resolved["layout_detection_model_dir"], model_dir)
            finally:
                config_module.REQUIRED_MODELS = original

    def test_resolve_required_model_dirs_raises_clear_error_when_missing(self):
        import config as config_module

        original = config_module.REQUIRED_MODELS
        try:
            config_module.REQUIRED_MODELS = {
                "layout_detection_model_dir": {
                    "display_name": "PP-DocLayout-L",
                    "path": r"E:\nonexistent\PP-DocLayout-L",
                },
            }
            with self.assertRaises(FileNotFoundError) as context:
                resolve_required_model_dirs()
        finally:
            config_module.REQUIRED_MODELS = original

        self.assertIn("PP-DocLayout-L", str(context.exception))


if __name__ == "__main__":
    unittest.main()
