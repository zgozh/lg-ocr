import os
import time
import traceback

from tqdm import tqdm

from config import OCRLLMConfig
from excel_writer import extract_data_excel
from file_scanner import collect_image_files, create_result_directory, get_output_xlsx_path
from llm_extract import build_fallback_people, extract_people, check_ollama_connection
from ocr_pipeline import build_pipeline, run_table_ocr
from template_loader import get_builtin_template_path, load_template
from utils.sort_boxes import sort_texts_by_boxes


CURRENT_CONFIG = None
CURRENT_TEMPLATE = None


def process_single_image(pipeline, image_path, root_xlsx_path):
    try:
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        result_dir = create_result_directory(image_path)
        output = run_table_ocr(pipeline, image_path, CURRENT_CONFIG.device)

        if output:
            for res in output:
                overall_ocr_res = res["overall_ocr_res"]
                rec_texts = overall_ocr_res["rec_texts"]
                rec_boxes = overall_ocr_res["rec_boxes"]
                sorted_texts = sort_texts_by_boxes(rec_texts, rec_boxes, 0.3)

                json_path = os.path.join(result_dir, f"{image_name}.json")
                res.save_to_json(json_path)
                
                people = extract_people(
                    sorted_texts,
                    CURRENT_TEMPLATE,
                    CURRENT_CONFIG.ollama_host,
                    CURRENT_CONFIG.llm_model,
                    max_retries=CURRENT_CONFIG.llm_max_retries,
                    retry_delay_seconds=CURRENT_CONFIG.llm_retry_delay_seconds,
                )
                extract_data_excel(
                    people,
                    root_xlsx_path,
                    image_path,
                    CURRENT_TEMPLATE,
                )
        return True
    except Exception as e:
        print(f"\n  处理失败: {image_path}")
        print(f"    错误信息: {str(e)}")
        print(traceback.format_exc())
        print("    已写入兜底数据...")
        extract_data_excel(
            build_fallback_people(CURRENT_TEMPLATE),
            root_xlsx_path,
            image_path,
            CURRENT_TEMPLATE,
        )
        return False


def prompt_bool(message, default=True):
    while True:
        input_str = input(message).strip().lower()
        if not input_str:
            return default
        if input_str in ["y", "yes", "是"]:
            return True
        if input_str in ["n", "no", "否"]:
            return False
        print("输入无效，请重新输入（y/n/是/否）")


def prompt_input_dir():
    while True:
        input_dir = input("请输入要处理的图片目录的绝对路径: ").strip()
        if not input_dir:
            print("输入不能为空，请重新输入。")
            continue
        if not os.path.exists(input_dir):
            print(f"目录不存在: {input_dir}")
            continue
        if not os.path.isdir(input_dir):
            print(f"输入的不是目录: {input_dir}")
            continue
        return input_dir


def prompt_template_path():
    default_path = get_builtin_template_path()
    while True:
        value = input(
            f"请输入模板文件路径（回车使用默认模板: {default_path}）: "
        ).strip()
        template_path = value or default_path
        if not os.path.exists(template_path):
            print(f"模板不存在: {template_path}")
            continue
        return template_path


def main():
    global CURRENT_CONFIG, CURRENT_TEMPLATE

    input_dir = prompt_input_dir()
    template_path = prompt_template_path()
    is_paginated = prompt_bool("选择是否隔页推理 (y/n，默认y，可输入是/否): ", default=True)
    print(f"隔页推理设置：{'是' if is_paginated else '否'}")

    CURRENT_CONFIG = OCRLLMConfig(
        input_dir=input_dir,
        is_paginated=is_paginated,
        template_path=template_path,
    )
    CURRENT_TEMPLATE = load_template(template_path)
    print(f"已加载模板：{CURRENT_TEMPLATE['display_name']}")

    print("\n正在检测 Ollama 服务连接...")
    success, error_msg = check_ollama_connection(
        CURRENT_CONFIG.ollama_host,
        CURRENT_CONFIG.llm_model
    )
    if not success:
        print(f"✗ Ollama 连接失败:")
        print(f"  {error_msg}")
        print(f"\n配置信息:")
        print(f"  服务地址: {CURRENT_CONFIG.ollama_host}")
        print(f"  模型名称: {CURRENT_CONFIG.llm_model}")
        return
    print(f"✓ Ollama 服务连接成功")
    print(f"  服务地址: {CURRENT_CONFIG.ollama_host}")
    print(f"  模型名称: {CURRENT_CONFIG.llm_model}")

    print("\n正在初始化OCR模型...")
    try:
        pipeline = build_pipeline(CURRENT_CONFIG)
        print("OCR模型初始化完成")
    except Exception as e:
        print(f"OCR模型初始化失败: {str(e)}")
        print(traceback.format_exc())
        return

    all_image_files = collect_image_files(input_dir, is_paginated)
    if not all_image_files:
        print("未找到任何图片文件")
        return

    print(f"找到 {len(all_image_files)} 个图片文件")
    print("开始处理图片...")

    start_time = time.time()
    success_count = 0

    with tqdm(total=len(all_image_files), desc="处理进度", unit="张") as pbar:
        for image_path in all_image_files:
            root_xlsx_path = get_output_xlsx_path(image_path)
            try:
                if process_single_image(pipeline, image_path, root_xlsx_path):
                    success_count += 1
            except Exception:
                pass
            pbar.update(1)

    end_time = time.time()
    print("\n处理完成")
    print(f"总文件数: {len(all_image_files)}")
    print(f"成功处理: {success_count}")
    print(f"失败数量: {len(all_image_files) - success_count}")
    print(f"总处理时间: {end_time - start_time:.2f} 秒")


if __name__ == "__main__":
    main()
