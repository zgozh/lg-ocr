#!/usr/bin/env python3
"""测试 Ollama 连接"""

from config import _CONFIG_DATA
from llm_extract import check_ollama_connection


def main():
    print("=" * 50)
    print("Ollama 连接测试")
    print("=" * 50)
    print()

    host = _CONFIG_DATA["ollama"]["host"]
    model = _CONFIG_DATA["ollama"]["model"]

    print(f"配置信息:")
    print(f"  服务地址: {host}")
    print(f"  模型名称: {model}")
    print()

    print("正在检测连接...")
    success, error_msg = check_ollama_connection(host, model, timeout=10)

    print()
    if success:
        print("✓ 连接成功！")
        print("  Ollama 服务正常，可以开始识别任务")
    else:
        print("✗ 连接失败！")
        print(f"  {error_msg}")
        print()
        print("解决方案:")
        print("  1. 确认 Ollama 服务已启动: ollama serve")
        print("  2. 确认模型已下载: ollama pull " + model)
        print("  3. 检查服务地址是否正确")
        print("  4. 检查网络连接")

    print()
    print("=" * 50)


if __name__ == "__main__":
    main()
