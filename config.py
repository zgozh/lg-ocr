import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path


def _get_config_file_path():
    """获取配置文件路径"""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base_dir = Path(sys._MEIPASS)
    else:
        base_dir = Path(__file__).resolve().parent
    return base_dir / "config.json"


def _load_config_json():
    """加载 JSON 配置文件"""
    config_path = _get_config_file_path()
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


_CONFIG_DATA = _load_config_json()


@dataclass
class OCRLLMConfig:
    input_dir: str
    is_paginated: bool
    template_path: str
    ollama_host: str = None
    llm_model: str = None
    device: str = None
    llm_max_retries: int = None
    llm_retry_delay_seconds: float = None

    def __post_init__(self):
        """从配置文件填充默认值"""
        if self.ollama_host is None:
            self.ollama_host = _CONFIG_DATA["ollama"]["host"]
        if self.llm_model is None:
            self.llm_model = _CONFIG_DATA["ollama"]["model"]
        if self.device is None:
            self.device = _CONFIG_DATA["device"]
        if self.llm_max_retries is None:
            self.llm_max_retries = _CONFIG_DATA["ollama"]["max_retries"]
        if self.llm_retry_delay_seconds is None:
            self.llm_retry_delay_seconds = _CONFIG_DATA["ollama"]["retry_delay_seconds"]


def _build_required_models_from_config():
    """从配置文件构建模型配置"""
    models_config = _CONFIG_DATA["models"]

    model_key_mapping = {
        "layout_detection": "layout_detection_model_dir",
        "table_classification": "table_classification_model_dir",
        "wired_table_structure_recognition": "wired_table_structure_recognition_model_dir",
        "wireless_table_structure_recognition": "wireless_table_structure_recognition_model_dir",
        "wired_table_cells_detection": "wired_table_cells_detection_model_dir",
        "wireless_table_cells_detection": "wireless_table_cells_detection_model_dir",
        "text_recognition": "text_recognition_model_dir",
        "text_detection": "text_detection_model_dir",
    }

    required_models = {}
    for config_key, model_dir_key in model_key_mapping.items():
        model_info = models_config[config_key]
        required_models[model_dir_key] = {
            "display_name": model_info["name"],
            "path": model_info["path"],
        }

    return required_models


REQUIRED_MODELS = _build_required_models_from_config()


def resolve_required_model_dirs() -> dict[str, str]:
    """解析模型目录路径"""
    resolved = {}
    missing = []

    for key, spec in REQUIRED_MODELS.items():
        model_path = Path(spec["path"])

        if model_path.is_dir():
            resolved[key] = str(model_path)
        else:
            missing.append((spec["display_name"], str(model_path)))

    if missing:
        message_lines = [
            "未找到以下OCR模型目录，请确认配置文件中的路径是否正确："
        ]
        for model_name, path in missing:
            message_lines.append(f"- {model_name}: {path}")
        raise FileNotFoundError("\n".join(message_lines))

    return resolved


def build_pipeline_kwargs(config: OCRLLMConfig) -> dict:
    model_dirs = resolve_required_model_dirs()
    models_config = _CONFIG_DATA["models"]
    pipeline_config = _CONFIG_DATA["pipeline"]

    return {
        "use_layout_detection": pipeline_config["use_layout_detection"],
        "use_doc_orientation_classify": pipeline_config["use_doc_orientation_classify"],
        "layout_detection_model_name": models_config["layout_detection"]["name"],
        "layout_detection_model_dir": model_dirs["layout_detection_model_dir"],
        "table_classification_model_name": models_config["table_classification"]["name"],
        "table_classification_model_dir": model_dirs["table_classification_model_dir"],
        "wired_table_structure_recognition_model_name": models_config["wired_table_structure_recognition"]["name"],
        "wired_table_structure_recognition_model_dir": model_dirs["wired_table_structure_recognition_model_dir"],
        "wireless_table_structure_recognition_model_name": models_config["wireless_table_structure_recognition"]["name"],
        "wireless_table_structure_recognition_model_dir": model_dirs["wireless_table_structure_recognition_model_dir"],
        "wired_table_cells_detection_model_name": models_config["wired_table_cells_detection"]["name"],
        "wired_table_cells_detection_model_dir": model_dirs["wired_table_cells_detection_model_dir"],
        "wireless_table_cells_detection_model_name": models_config["wireless_table_cells_detection"]["name"],
        "wireless_table_cells_detection_model_dir": model_dirs["wireless_table_cells_detection_model_dir"],
        "text_recognition_model_name": models_config["text_recognition"]["name"],
        "text_recognition_model_dir": model_dirs["text_recognition_model_dir"],
        "text_detection_model_name": models_config["text_detection"]["name"],
        "text_detection_model_dir": model_dirs["text_detection_model_dir"],
        "use_doc_unwarping": pipeline_config["use_doc_unwarping"],
        "device": config.device,
    }


def build_predict_flags() -> dict:
    """构建 pipeline.predict() 调用使用的开关，统一从配置文件 pipeline 段读取。"""
    pipeline_config = _CONFIG_DATA["pipeline"]
    return {
        # 表格方向分类当前不通过配置暴露，固定关闭
        "use_table_orientation_classify": False,
        "use_layout_detection": pipeline_config["use_layout_detection"],
        "use_doc_orientation_classify": pipeline_config["use_doc_orientation_classify"],
        "use_doc_unwarping": pipeline_config["use_doc_unwarping"],
    }
