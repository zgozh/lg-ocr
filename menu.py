import os
import sys
import time
import traceback
from pathlib import Path

from config import OCRLLMConfig, _CONFIG_DATA
from template_loader import get_builtin_template_path, load_template


class AppSettings:
    """应用运行时设置"""
    def __init__(self):
        self.config_path = self._get_default_config_path()
        self.template_path = get_builtin_template_path()
        self.is_paginated = True
        self.template = None
        self.config_data = None
        self.reload_config()
        self.reload_template()

    def _get_default_config_path(self):
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base_dir = Path(sys._MEIPASS)
        else:
            base_dir = Path(__file__).resolve().parent
        return str(base_dir / "config.json")

    def reload_config(self):
        """重新加载配置文件"""
        try:
            import json
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config_data = json.load(f)
            return True
        except Exception as e:
            print(f"✗ 配置文件加载失败: {e}")
            return False

    def reload_template(self):
        """重新加载模板文件"""
        try:
            self.template = load_template(self.template_path)
            return True
        except Exception as e:
            print(f"✗ 模板文件加载失败: {e}")
            return False

    def get_template_name(self):
        """获取模板显示名称"""
        if self.template:
            return self.template.get("display_name", "未知模板")
        return "未加载"

    def get_config_filename(self):
        """获取配置文件名"""
        return Path(self.config_path).name

    def get_template_filename(self):
        """获取模板文件名"""
        return Path(self.template_path).name


def clear_screen():
    """清屏"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    """打印标题"""
    print("=" * 40)
    print(f"{title:^40}")
    print("=" * 40)


def print_separator():
    """打印分隔线"""
    print("-" * 40)


def wait_key():
    """等待用户按键"""
    input("\n按回车返回...")


def show_main_menu(settings):
    """显示主菜单"""
    clear_screen()
    print("=" * 40)
    print("    DocExtractor 文档信息提取系统")
    print("=" * 40)
    print()
    print("当前配置:")
    print(f"  模板: {settings.get_template_name()}")
    print(f"  隔页推理: {'是' if settings.is_paginated else '否'}")
    if settings.config_data:
        print(f"  设备: {settings.config_data.get('device', 'N/A')}  |  模型: {settings.config_data.get('ollama', {}).get('model', 'N/A')}")
    print()
    print_separator()
    print("[1] 开始识别")
    print("[2] 设置")
    print("[3] 退出")
    print_separator()


def show_settings_menu(settings):
    """显示设置菜单"""
    clear_screen()
    print_header("设置")
    print()
    print("当前配置:")
    print(f"  配置文件: {settings.get_config_filename()}")
    print(f"  模板文件: {settings.get_template_filename()}")
    print(f"  隔页推理: {'是' if settings.is_paginated else '否'}")
    print()
    print_separator()
    print("[1] 修改配置文件路径")
    print("[2] 修改模板文件路径")
    print(f"[3] 切换隔页推理 (当前: {'是' if settings.is_paginated else '否'})")
    print("[4] 返回主菜单")
    print_separator()


def modify_config_path(settings):
    """修改配置文件路径"""
    clear_screen()
    print_header("修改配置文件路径")
    print()
    print(f"当前: {settings.config_path}")
    print()

    new_path = input("请输入新路径 (输入 'c' 取消): ").strip()
    if new_path.lower() == 'c':
        return

    if not new_path:
        print("✗ 路径不能为空")
        wait_key()
        return

    if not os.path.exists(new_path):
        print(f"✗ 文件不存在: {new_path}")
        wait_key()
        return

    # 验证配置文件
    try:
        import json
        with open(new_path, "r", encoding="utf-8") as f:
            json.load(f)
        print("\n[验证中...]")
        time.sleep(0.5)
        print("✓ 配置文件有效")
        settings.config_path = new_path
        settings.reload_config()
        print("\n已更新！")
    except Exception as e:
        print(f"\n✗ 配置文件无效: {e}")

    wait_key()


def modify_template_path(settings):
    """修改模板文件路径"""
    clear_screen()
    print_header("修改模板文件路径")
    print()
    print(f"当前: {settings.template_path}")
    print()

    # 列出内置模板
    templates_dir = Path(__file__).parent / "templates"
    if templates_dir.exists():
        print("内置模板:")
        template_files = list(templates_dir.glob("*.json"))
        for idx, tpl in enumerate(template_files, 1):
            print(f"  [{idx}] {tpl.name}")
        print()

    user_input = input("请输入路径或编号 (输入 'c' 取消): ").strip()
    if user_input.lower() == 'c':
        return

    if not user_input:
        print("✗ 输入不能为空")
        wait_key()
        return

    # 判断是编号还是路径
    new_path = None
    if user_input.isdigit():
        idx = int(user_input) - 1
        if 0 <= idx < len(template_files):
            new_path = str(template_files[idx])
        else:
            print("✗ 编号无效")
            wait_key()
            return
    else:
        new_path = user_input

    if not os.path.exists(new_path):
        print(f"✗ 文件不存在: {new_path}")
        wait_key()
        return

    # 验证模板文件
    try:
        print("\n[验证中...]")
        time.sleep(0.5)
        template = load_template(new_path)
        field_count = len(template.get("fields", []))
        print(f"✓ 模板文件有效 ({field_count}个字段)")
        settings.template_path = new_path
        settings.reload_template()
        print("\n已更新！")
    except Exception as e:
        print(f"\n✗ 模板文件无效: {e}")

    wait_key()


def toggle_paginated(settings):
    """切换隔页推理"""
    clear_screen()
    print_header("隔页推理设置")
    print()
    print(f"当前: {'是' if settings.is_paginated else '否'}")
    print()
    print("说明: 启用后只处理奇数或偶数页图片")
    print()

    new_value = not settings.is_paginated
    confirm = input(f"确认切换为 [{'是' if new_value else '否'}]? (y/n): ").strip().lower()

    if confirm in ['y', 'yes', '是']:
        settings.is_paginated = new_value
        print(f"\n✓ 已切换为: {'是' if new_value else '否'}")
    else:
        print("\n已取消")

    wait_key()


def process_single_image(pipeline, image_path, root_xlsx_path, settings):
    """处理单张图片"""
    from excel_writer import extract_data_excel
    from file_scanner import create_result_directory, get_output_xlsx_path
    from llm_extract import build_fallback_people, extract_people
    from ocr_pipeline import run_table_ocr
    from utils.sort_boxes import sort_texts_by_boxes

    try:
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        result_dir = create_result_directory(image_path)

        config = OCRLLMConfig(
            input_dir=os.path.dirname(image_path),
            is_paginated=settings.is_paginated,
            template_path=settings.template_path,
        )

        output = run_table_ocr(pipeline, image_path, config.device)

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
                    settings.template,
                    config.ollama_host,
                    config.llm_model,
                    max_retries=config.llm_max_retries,
                    retry_delay_seconds=config.llm_retry_delay_seconds,
                )
                extract_data_excel(
                    people,
                    root_xlsx_path,
                    image_path,
                    settings.template,
                )
        return True
    except Exception as e:
        print(f"\n  处理失败: {image_path}")
        print(f"    错误: {str(e)}")
        extract_data_excel(
            build_fallback_people(settings.template),
            root_xlsx_path,
            image_path,
            settings.template,
        )
        return False


def start_recognition(settings):
    """开始识别"""
    # 延迟导入，避免启动时加载所有依赖
    from tqdm import tqdm
    from excel_writer import extract_data_excel
    from file_scanner import collect_image_files, create_result_directory, get_output_xlsx_path
    from llm_extract import build_fallback_people, extract_people
    from ocr_pipeline import build_pipeline, run_table_ocr
    from utils.sort_boxes import sort_texts_by_boxes

    clear_screen()
    print_header("开始识别")
    print()
    print("当前配置:")
    print(f"  模板: {settings.get_template_name()}")
    print(f"  隔页推理: {'是' if settings.is_paginated else '否'}")
    print()

    input_dir = input("请输入图片目录: ").strip()

    if not input_dir:
        print("✗ 目录不能为空")
        wait_key()
        return

    if not os.path.exists(input_dir):
        print(f"✗ 目录不存在: {input_dir}")
        wait_key()
        return

    if not os.path.isdir(input_dir):
        print(f"✗ 不是有效目录: {input_dir}")
        wait_key()
        return

    # 扫描文件
    print("\n[扫描中...]")
    all_image_files = collect_image_files(input_dir, settings.is_paginated)

    if not all_image_files:
        print("✗ 未找到图片文件")
        wait_key()
        return

    print(f"找到 {len(all_image_files)} 个图片文件")
    print()

    confirm = input("确认开始? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes', '是']:
        print("已取消")
        wait_key()
        return

    # 检测 Ollama 连接
    print()
    print_separator()
    print("正在检测 Ollama 服务...")

    from llm_extract import check_ollama_connection

    config = OCRLLMConfig(
        input_dir=input_dir,
        is_paginated=settings.is_paginated,
        template_path=settings.template_path,
    )

    success, error_msg = check_ollama_connection(config.ollama_host, config.llm_model)
    if not success:
        print(f"✗ Ollama 连接失败:")
        print(f"  {error_msg}")
        print()
        print(f"配置信息:")
        print(f"  服务地址: {config.ollama_host}")
        print(f"  模型名称: {config.llm_model}")
        wait_key()
        return

    print(f"✓ Ollama 服务连接成功")
    print(f"  服务地址: {config.ollama_host}")
    print(f"  模型名称: {config.llm_model}")

    # 初始化OCR模型
    print()
    print_separator()
    print("正在初始化OCR模型...")

    try:
        pipeline = build_pipeline(config)
        print("✓ 模型加载完成")
        print()
    except Exception as e:
        print(f"✗ 模型加载失败: {e}")
        print(traceback.format_exc())
        wait_key()
        return

    # 开始处理
    start_time = time.time()
    success_count = 0

    with tqdm(total=len(all_image_files), desc="处理进度", unit="张") as pbar:
        for image_path in all_image_files:
            root_xlsx_path = get_output_xlsx_path(image_path)
            try:
                if process_single_image(pipeline, image_path, root_xlsx_path, settings):
                    success_count += 1
            except Exception:
                pass
            pbar.update(1)

    end_time = time.time()
    elapsed = int(end_time - start_time)

    # 显示结果
    print()
    print_separator()
    print("处理完成！")
    print(f"  成功: {success_count}  |  失败: {len(all_image_files) - success_count}  |  耗时: {elapsed}s")
    print(f"  输出: {get_output_xlsx_path(all_image_files[0])}")

    wait_key()


def settings_menu(settings):
    """设置菜单循环"""
    while True:
        show_settings_menu(settings)
        choice = input("请选择: ").strip()

        if choice == '1':
            modify_config_path(settings)
        elif choice == '2':
            modify_template_path(settings)
        elif choice == '3':
            toggle_paginated(settings)
        elif choice == '4':
            break
        else:
            print("✗ 无效选项")
            time.sleep(1)


def main():
    """主程序"""
    settings = AppSettings()

    while True:
        show_main_menu(settings)
        choice = input("请选择: ").strip()

        if choice == '1':
            start_recognition(settings)
        elif choice == '2':
            settings_menu(settings)
        elif choice == '3':
            confirm = input("\n确认退出? (y/n): ").strip().lower()
            if confirm in ['y', 'yes', '是']:
                print("\n再见！")
                break
        else:
            print("✗ 无效选项")
            time.sleep(1)


if __name__ == "__main__":
    main()
