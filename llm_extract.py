import time

try:
    from utils.json_parser import parse_llm_json
except ImportError:
    from .utils.json_parser import parse_llm_json


def build_prompt(sorted_texts, template):
    document_type = template.get("prompt", {}).get(
        "document_type", template["display_name"]
    )
    rules = template.get("prompt", {}).get("rules", [])
    field_lines = []
    for index, field in enumerate(template["fields"], start=1):
        description = field.get("description", "")
        default = field.get("default", "")
        field_lines.append(
            f"{index}. {field['name']}，默认值：{default}，说明：{description}"
        )

    rule_lines = [f"{index}. {rule}" for index, rule in enumerate(rules, start=1)]
    fields_text = "\n".join(field_lines)
    rules_text = "\n".join(rule_lines) if rule_lines else "1. 严格按OCR原文提取。"

    return f"""
# OCR信息提取处理提示
## 文档类型
{document_type}

## OCR结果
{sorted_texts}

## 目标字段
{fields_text}

## 抽取规则
{rules_text}

## 输出要求
1. 输出必须是JSON数组。
2. 数组中每个元素是一条完整记录。
3. JSON对象的键必须与目标字段名称完全一致。
4. 没有对应信息时使用字段默认值。
5. 严禁输出JSON以外的内容。
"""


def _create_client(host):
    from ollama import Client

    return Client(host=host)


def check_ollama_connection(host, model, timeout=5):
    """
    检测 Ollama 服务是否可用

    Args:
        host: Ollama 服务地址
        model: 模型名称
        timeout: 超时时间（秒）

    Returns:
        (bool, str): (是否成功, 错误信息)
    """
    try:
        from ollama import Client

        client = Client(host=host, timeout=timeout)

        # 尝试列出模型
        try:
            models_response = client.list()

            # 处理不同的返回格式
            model_names = []

            # 情况1: 返回的是字典 {'models': [...]}
            if isinstance(models_response, dict):
                models_list = models_response.get('models', [])
                for m in models_list:
                    if isinstance(m, dict) and 'name' in m:
                        model_names.append(m['name'])
                    elif isinstance(m, dict) and 'model' in m:
                        model_names.append(m['model'])

            # 情况2: 返回的是对象，有 models 属性
            elif hasattr(models_response, 'models'):
                for m in models_response.models:
                    if hasattr(m, 'name'):
                        model_names.append(m.name)
                    elif hasattr(m, 'model'):
                        model_names.append(m.model)
                    elif isinstance(m, dict):
                        model_names.append(m.get('name') or m.get('model', ''))

            # 情况3: 返回的直接是列表
            elif isinstance(models_response, list):
                for m in models_response:
                    if isinstance(m, dict):
                        model_names.append(m.get('name') or m.get('model', ''))
                    elif isinstance(m, str):
                        model_names.append(m)

            # 过滤空值
            model_names = [name for name in model_names if name]

            # 检查指定模型是否存在
            if model_names and model not in model_names:
                available = ', '.join(model_names) if model_names else '无'
                return False, f"模型 '{model}' 不存在\n可用模型: {available}\n请运行: ollama pull {model}"

            # 如果无法获取模型列表，尝试直接测试模型
            if not model_names:
                # 尝试发送一个测试请求
                try:
                    test_response = client.chat(
                        model=model,
                        messages=[{"role": "user", "content": "test"}],
                    )
                    # 如果没有抛出异常，说明模型可用
                    return True, ""
                except Exception as test_error:
                    return False, f"模型 '{model}' 不可用: {str(test_error)}"

            return True, ""

        except Exception as e:
            return False, f"无法获取模型列表: {str(e)}\n提示: 请确认模型名称是否正确"

    except ImportError:
        return False, "未安装 ollama 库，请运行: pip install ollama"
    except Exception as e:
        error_msg = str(e)
        if "Connection" in error_msg or "connect" in error_msg.lower():
            return False, f"无法连接到 Ollama 服务 ({host})\n请确认:\n1. Ollama 服务是否已启动\n2. 服务地址是否正确\n3. 网络是否可达"
        return False, f"连接失败: {error_msg}"


def extract_people(
    sorted_texts,
    template,
    host,
    model,
    max_retries=3,
    retry_delay_seconds=1.0,
    client_factory=_create_client,
    sleep_fn=time.sleep,
):
    last_error = None
    prompt = build_prompt(sorted_texts, template)

    for attempt in range(1, max_retries + 1):
        try:
            client = client_factory(host)
            response = client.chat(
                model=model,
                messages=[
                    {"role": "system", "content": "/set nothink"},
                    {"role": "user", "content": prompt},
                ],
                think=False,
                stream=False,
            )
            print(response.message.content)
            return parse_llm_json(response.message.content)
        except Exception as exc:
            last_error = exc
            if attempt < max_retries:
                sleep_fn(retry_delay_seconds)

    raise RuntimeError(
        f"LLM extraction failed after {max_retries} attempts: {last_error}"
    ) from last_error


def build_fallback_people(template):
    """从 fields 自动生成兜底记录"""
    record = {}
    for field in template["fields"]:
        record[field["name"]] = field.get("default", "")
    return [record]
