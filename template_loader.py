import json
import os
import sys


def get_builtin_template_path():
    base_dir = _get_resource_base_dir()
    return os.path.join(
        base_dir,
        "templates",
        "hukou_register.json",
    )


def _get_resource_base_dir():
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    return os.path.dirname(__file__)


def load_template(template_path=None):
    template_path = template_path or get_builtin_template_path()
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template file not found: {template_path}")

    _, ext = os.path.splitext(template_path.lower())
    with open(template_path, "r", encoding="utf-8") as file:
        if ext == ".json":
            template = json.load(file)
        elif ext in {".yml", ".yaml"}:
            import yaml

            template = yaml.safe_load(file)
        else:
            raise ValueError("Only .json, .yml, and .yaml templates are supported")

    template = normalize_template(template)
    validate_template(template)
    return template


def normalize_template(template):
    normalized = dict(template)
    output = dict(normalized.get("output", {}))
    columns = []
    for column in output.get("columns", []):
        normalized_column = dict(column)
        if "header" not in normalized_column and "name" in normalized_column:
            normalized_column["header"] = normalized_column["name"]
        columns.append(normalized_column)
    output["columns"] = columns
    normalized["output"] = output
    return normalized


def validate_template(template):
    required_keys = {"name", "display_name", "fields", "output"}
    missing_keys = required_keys - set(template.keys())
    if missing_keys:
        raise ValueError(f"Template missing required keys: {sorted(missing_keys)}")

    if not template["fields"]:
        raise ValueError("Template fields must not be empty")

    field_names = {field["name"] for field in template["fields"]}
    for column in template["output"].get("columns", []):
        if "header" not in column:
            raise ValueError(f"Output column missing header/name: {column}")
        if column.get("source") == "field" and column.get("field") not in field_names:
            raise ValueError(
                f"Output column references unknown field: {column.get('field')}"
            )
