import json
import re


def parse_llm_json(content):
    cleaned = content.replace("<think>", "").replace("</think>", "")
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    match = re.search(r"\[.*\]", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)

    return json.loads(cleaned)
