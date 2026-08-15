#!/usr/bin/env python3
"""DocExtractor 文档信息提取系统 - 图形界面版本"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import queue

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import OCRLLMConfig, _CONFIG_DATA
from template_loader import get_builtin_template_path, load_template


class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DocExtractor 文档信息提取系统")
        self.root.geometry("1200x820")  

        # 设置窗口图标（如果有的话）
        try:
            # self.root.iconbitmap('icon.ico')
            pass
        except:
            pass

        # 配置变量
        self.config_path = self._get_default_config_path()
        self.template_path = get_builtin_template_path()
        self.is_paginated = tk.BooleanVar(value=True)
        self.input_dir = tk.StringVar()

        # 加载配置和模板
        self.config_data = None
        self.template = None
        self.reload_config()
        self.reload_template()

        # 处理状态
        self.is_processing = False
        self.log_queue = queue.Queue()

        # 创建界面
        self.create_widgets()

        # 启动日志更新
        self.update_log()

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
            messagebox.showerror("错误", f"配置文件加载失败: {e}")
            return False

    def reload_template(self):
        """重新加载模板文件"""
        try:
            self.template = load_template(self.template_path)
            return True
        except Exception as e:
            messagebox.showerror("错误", f"模板文件加载失败: {e}")
            return False

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 标题
        title_label = ttk.Label(
            main_frame,
            text="DocExtractor 文档信息提取系统",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))

        # 创建标签页
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # OCR 识别标签页
        ocr_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(ocr_frame, text="OCR 识别")
        self.create_ocr_tab(ocr_frame)

        # 模型训练标签页
        training_frame = ttk.Frame(self.notebook, padding="5")
        self.notebook.add(training_frame, text="模型训练")
        self.create_training_tab(training_frame)

        # 状态栏
        self.create_status_bar()

    def create_ocr_tab(self, parent):
        """创建 OCR 识别标签页 - 左右布局"""
        # 配置 parent 的行列权重
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=0)  # 左侧固定宽度
        parent.columnconfigure(1, weight=1)  # 右侧自适应

        # 左侧功能区
        left_frame = ttk.Frame(parent, padding="5", width=400)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        left_frame.grid_propagate(False)  # 固定宽度
        left_frame.columnconfigure(0, weight=1)

        # 右侧日志区
        right_frame = ttk.Frame(parent, padding="5")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # 创建左侧内容
        self.create_ocr_left_panel(left_frame)

        # 创建右侧日志
        self.create_ocr_log_panel(right_frame)

    def create_ocr_left_panel(self, parent):
        """创建 OCR 左侧功能面板"""
        # 配置信息框
        self.create_config_frame(parent)

        # 输入目录选择
        self.create_input_frame(parent)

        # 选项设置
        self.create_options_frame(parent)

        # 按钮区域
        self.create_button_frame(parent)

    def create_ocr_log_panel(self, parent):
        """创建 OCR 右侧日志面板"""
        log_frame = ttk.LabelFrame(parent, text="处理日志", padding="10")
        log_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Consolas", 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置标签颜色
        self.log_text.tag_config("info", foreground="black")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("warning", foreground="orange")

    def create_config_frame(self, parent):
        """创建配置信息框"""
        config_frame = ttk.LabelFrame(parent, text="当前配置", padding="10")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)

        # 模板
        ttk.Label(config_frame, text="模板:").grid(row=0, column=0, sticky=tk.W)
        template_name = self.template.get("display_name", "未知") if self.template else "未加载"
        self.template_label = ttk.Label(config_frame, text=template_name, foreground="blue")
        self.template_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # 设备
        ttk.Label(config_frame, text="设备:").grid(row=1, column=0, sticky=tk.W)
        device = self.config_data.get("device", "N/A") if self.config_data else "N/A"
        ttk.Label(config_frame, text=device).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))

        # 模型
        ttk.Label(config_frame, text="LLM 模型:").grid(row=2, column=0, sticky=tk.W)
        model = self.config_data.get("ollama", {}).get("model", "N/A") if self.config_data else "N/A"
        ttk.Label(config_frame, text=model).grid(row=2, column=1, sticky=tk.W, padx=(10, 0))

        # 按钮框架
        button_frame = ttk.Frame(config_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0), sticky=tk.W)

        # 设置按钮
        ttk.Button(button_frame, text="设置", command=self.open_settings, width=15).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        # 测试连接按钮
        ttk.Button(button_frame, text="测试连接", command=self.test_connection, width=15).pack(
            side=tk.LEFT
        )

    def create_input_frame(self, parent):
        """创建输入目录选择框"""
        input_frame = ttk.LabelFrame(parent, text="图片目录", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)

        # 输入框
        entry = ttk.Entry(input_frame, textvariable=self.input_dir)
        entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        # 浏览按钮
        ttk.Button(input_frame, text="浏览...", command=self.browse_directory).grid(
            row=0, column=1
        )

    def create_options_frame(self, parent):
        """创建选项设置框"""
        options_frame = ttk.LabelFrame(parent, text="处理选项", padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # 隔页推理
        ttk.Checkbutton(
            options_frame,
            text="隔页推理（双面扫描时启用）",
            variable=self.is_paginated
        ).grid(row=0, column=0, sticky=tk.W, pady=2)

    def create_log_frame(self, parent):
        """创建日志输出区域"""
        log_frame = ttk.LabelFrame(parent, text="处理日志", padding="10")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            height=15,
            state=tk.DISABLED,
            font=("Consolas", 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置标签颜色
        self.log_text.tag_config("info", foreground="black")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("warning", foreground="orange")

    def create_button_frame(self, parent):
        """创建按钮区域"""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        # 开始按钮
        self.start_button = ttk.Button(
            button_frame,
            text="开始识别",
            command=self.start_processing,
            width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))

        # 停止按钮
        self.stop_button = ttk.Button(
            button_frame,
            text="停止",
            command=self.stop_processing,
            state=tk.DISABLED,
            width=15
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))

        # 清空日志按钮
        ttk.Button(
            button_frame,
            text="清空日志",
            command=self.clear_log,
            width=15
        ).pack(side=tk.LEFT)

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = ttk.Label(
            self.root,
            text="就绪",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))

    def browse_directory(self):
        """浏览选择目录"""
        directory = filedialog.askdirectory(title="选择图片目录")
        if directory:
            self.input_dir.set(directory)

    def open_settings(self):
        """打开设置窗口"""
        SettingsWindow(self.root, self)

    def set_status(self, text):
        """设置状态栏文本"""
        self.status_bar.config(text=text)

    def log(self, message, level="info"):
        """添加日志"""
        self.log_queue.put((message, level))

    def update_log(self):
        """更新日志显示"""
        try:
            while True:
                message, level = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, message + "\n", level)
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass

        # 继续更新
        self.root.after(100, self.update_log)

    def clear_log(self):
        """清空日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def test_connection(self):
        """测试 Ollama 连接"""
        if self.is_processing:
            messagebox.showwarning("警告", "正在处理中，无法测试连接")
            return

        # 在新线程中测试
        thread = threading.Thread(target=self._test_connection_thread, daemon=True)
        thread.start()

    def _test_connection_thread(self):
        """测试连接（后台线程）"""
        try:
            from llm_extract import check_ollama_connection

            self.log("=" * 60, "info")
            self.log("开始测试 Ollama 连接", "info")
            self.log("=" * 60, "info")
            self.update_status("测试连接中...")

            if not self.config_data:
                self.log("✗ 配置文件未加载", "error")
                self.update_status("测试失败")
                messagebox.showerror("错误", "配置文件未加载")
                return

            host = self.config_data.get("ollama", {}).get("host", "")
            model = self.config_data.get("ollama", {}).get("model", "")

            self.log(f"配置信息:", "info")
            self.log(f"  服务地址: {host}", "info")
            self.log(f"  模型名称: {model}", "info")
            self.log("", "info")

            self.log("正在连接...", "info")

            # 测试连接
            success, error_msg = check_ollama_connection(host, model, timeout=10)

            self.log("", "info")
            if success:
                self.log("✓ 连接成功！", "success")
                self.log("  Ollama 服务正常", "success")
                self.log("  模型可用", "success")
                self.update_status("连接成功")
                messagebox.showinfo("成功", "Ollama 连接成功！\n服务正常，模型可用。")
            else:
                self.log("✗ 连接失败", "error")
                self.log(f"  {error_msg}", "error")
                self.log("", "info")
                self.log("请检查:", "warning")
                self.log("  1. Ollama 服务是否已启动", "warning")
                self.log("  2. 服务地址是否正确", "warning")
                self.log("  3. 模型是否已下载", "warning")
                self.log("  4. 网络是否可达", "warning")
                self.update_status("连接失败")
                messagebox.showerror("失败", f"Ollama 连接失败！\n\n{error_msg}")

            self.log("=" * 60, "info")

        except Exception as e:
            self.log("", "info")
            self.log(f"✗ 测试出错: {str(e)}", "error")
            self.update_status("测试出错")
            messagebox.showerror("错误", f"测试出错:\n{str(e)}")

    def update_status(self, text):
        """更新状态栏"""
        self.status_bar.config(text=text)

    def start_processing(self):
        """开始处理"""
        # 验证输入
        input_dir = self.input_dir.get().strip()
        if not input_dir:
            messagebox.showwarning("警告", "请选择图片目录")
            return

        if not os.path.exists(input_dir):
            messagebox.showerror("错误", f"目录不存在: {input_dir}")
            return

        if not os.path.isdir(input_dir):
            messagebox.showerror("错误", f"不是有效目录: {input_dir}")
            return

        # 禁用开始按钮，启用停止按钮
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_processing = True

        # 清空日志
        self.clear_log()

        # 在新线程中处理
        thread = threading.Thread(target=self.process_images, daemon=True)
        thread.start()

    def stop_processing(self):
        """停止处理"""
        self.is_processing = False
        self.log("用户请求停止处理...", "warning")
        self.update_status("正在停止...")

    def process_images(self):
        """处理图片（在后台线程中运行）"""
        try:
            input_dir = self.input_dir.get().strip()

            # 先显示日志，让用户知道程序已经开始
            self.log("=" * 60, "info")
            self.log("开始处理", "info")
            self.log("=" * 60, "info")
            self.log(f"图片目录: {input_dir}", "info")
            self.log(f"模板: {self.template['display_name']}", "info")
            self.log(f"隔页推理: {'是' if self.is_paginated.get() else '否'}", "info")
            self.log("", "info")
            self.log("正在加载依赖模块...", "info")

            # 然后再导入模块（这个过程可能需要几秒钟）
            import time
            from file_scanner import collect_image_files, create_result_directory, get_output_xlsx_path
            from llm_extract import build_fallback_people, extract_people, check_ollama_connection
            from ocr_pipeline import build_pipeline, run_table_ocr
            from excel_writer import extract_data_excel
            from utils.sort_boxes import sort_texts_by_boxes

            self.log("✓ 模块加载完成", "success")
            self.log("", "info")
            # 创建配置
            config = OCRLLMConfig(
                input_dir=input_dir,
                is_paginated=self.is_paginated.get(),
                template_path=self.template_path,
            )

            # 检测 Ollama 连接
            self.log("正在检测 Ollama 服务...", "info")
            self.update_status("检测 Ollama 连接...")

            success, error_msg = check_ollama_connection(config.ollama_host, config.llm_model)
            if not success:
                self.log(f"✗ Ollama 连接失败: {error_msg}", "error")
                self.log(f"服务地址: {config.ollama_host}", "error")
                self.log(f"模型名称: {config.llm_model}", "error")
                messagebox.showerror("错误", f"Ollama 连接失败:\n{error_msg}")
                return

            self.log(f"✓ Ollama 服务连接成功", "success")
            self.log(f"  服务地址: {config.ollama_host}", "info")
            self.log(f"  模型名称: {config.llm_model}", "info")
            self.log("", "info")

            # 初始化 OCR 模型
            self.log("正在初始化 OCR 模型...", "info")
            self.update_status("初始化 OCR 模型...")

            pipeline = build_pipeline(config)
            self.log("✓ OCR 模型初始化完成", "success")
            self.log("", "info")

            # 扫描图片
            self.log("正在扫描图片文件...", "info")
            self.update_status("扫描图片文件...")

            all_image_files = collect_image_files(input_dir, self.is_paginated.get())
            if not all_image_files:
                self.log("✗ 未找到任何图片文件", "error")
                messagebox.showwarning("警告", "未找到任何图片文件")
                return

            self.log(f"✓ 找到 {len(all_image_files)} 个图片文件", "success")
            self.log("", "info")

            # 处理图片
            self.log("开始处理图片...", "info")
            self.log("-" * 60, "info")

            start_time = time.time()
            success_count = 0

            for idx, image_path in enumerate(all_image_files, 1):
                if not self.is_processing:
                    self.log("", "info")
                    self.log("处理已停止", "warning")
                    break

                # 更新状态
                self.update_status(f"处理中: {idx}/{len(all_image_files)}")
                self.log(f"[{idx}/{len(all_image_files)}] {os.path.basename(image_path)}", "info")

                try:
                    # 处理单张图片
                    image_name = os.path.splitext(os.path.basename(image_path))[0]
                    result_dir = create_result_directory(image_path)
                    root_xlsx_path = get_output_xlsx_path(image_path)

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
                                self.template,
                                config.ollama_host,
                                config.llm_model,
                                max_retries=config.llm_max_retries,
                                retry_delay_seconds=config.llm_retry_delay_seconds,
                            )
                            extract_data_excel(people, root_xlsx_path, image_path, self.template)

                    success_count += 1
                    self.log(f"  ✓ 处理成功", "success")

                except Exception as e:
                    self.log(f"  ✗ 处理失败: {str(e)}", "error")
                    # 写入兜底数据
                    try:
                        root_xlsx_path = get_output_xlsx_path(image_path)
                        extract_data_excel(
                            build_fallback_people(self.template),
                            root_xlsx_path,
                            image_path,
                            self.template,
                        )
                    except:
                        pass

            # 完成
            end_time = time.time()
            elapsed = int(end_time - start_time)

            self.log("", "info")
            self.log("-" * 60, "info")
            self.log("处理完成！", "success")
            self.log(f"总文件数: {len(all_image_files)}", "info")
            self.log(f"成功: {success_count}", "success")
            self.log(f"失败: {len(all_image_files) - success_count}", "error" if len(all_image_files) - success_count > 0 else "info")
            self.log(f"耗时: {elapsed} 秒", "info")

            if all_image_files:
                output_path = get_output_xlsx_path(all_image_files[0])
                self.log(f"输出文件: {output_path}", "info")

            self.log("=" * 60, "info")

            self.update_status("处理完成")
            messagebox.showinfo("完成", f"处理完成！\n成功: {success_count}\n失败: {len(all_image_files) - success_count}")

        except Exception as e:
            self.log("", "info")
            self.log(f"✗ 发生错误: {str(e)}", "error")
            import traceback
            self.log(traceback.format_exc(), "error")
            self.update_status("处理失败")
            messagebox.showerror("错误", f"处理失败:\n{str(e)}")

        finally:
            # 恢复按钮状态
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.is_processing = False

    def quit_app(self):
        """退出应用"""
        if self.is_processing:
            if messagebox.askyesno("确认", "正在处理中，确定要退出吗？"):
                self.is_processing = False
                self.root.quit()
        else:
            self.root.quit()


    def create_training_tab(self, parent):
        """创建模型训练标签页 - 左右布局"""
        # 配置 parent 的行列权重
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=0)  # 左侧固定宽度
        parent.columnconfigure(1, weight=1)  # 右侧自适应

        # 左侧功能区
        left_frame = ttk.Frame(parent, padding="5", width=500)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        left_frame.grid_propagate(False)  # 固定宽度
        left_frame.columnconfigure(0, weight=1)

        # 右侧日志区
        right_frame = ttk.Frame(parent, padding="5")
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        # 训练变量
        self.train_model_type = tk.StringVar(value="det")
        self.dataset_root_dir = tk.StringVar()
        self.pretrained_model = tk.StringVar(value="./pretrained_models/det/PP-OCRv5_server_det_pretrained.pdparams")
        self.epoch_num = tk.IntVar(value=500)
        self.batch_size = tk.IntVar(value=8)
        self.learning_rate = tk.DoubleVar(value=0.001)
        self.gpu_id = tk.StringVar(value="0")
        self.aug_count = tk.IntVar(value=5)

        # 训练状态
        self.is_training = False
        self.training_executor = None
        self.training_metrics = {"epochs": [], "losses": [], "accs": [], "lrs": []}

        # 创建左侧内容
        self.create_training_left_panel(left_frame)

        # 创建右侧日志
        self.create_training_log_panel(right_frame)

    def create_training_left_panel(self, parent):
        """创建训练左侧功能面板"""
        # 模型选择区
        self.create_model_selection_frame(parent)

        # 数据集配置区
        self.create_dataset_config_frame(parent)

        # 数据增强区
        self.create_data_augmentation_frame(parent)

        # 训练参数区
        self.create_training_params_frame(parent)

        # 训练控制按钮
        self.create_training_button_frame(parent)

    def create_training_log_panel(self, parent):
        """创建训练右侧日志面板"""
        # 创建 Notebook 用于日志和曲线切换
        log_notebook = ttk.Notebook(parent)
        log_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 日志标签页
        log_tab = ttk.Frame(log_notebook)
        log_notebook.add(log_tab, text="日志输出")

        self.training_log_text = scrolledtext.ScrolledText(
            log_tab,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Consolas", 9)
        )
        self.training_log_text.pack(fill=tk.BOTH, expand=True)

        # 配置日志颜色
        self.training_log_text.tag_config("info", foreground="black")
        self.training_log_text.tag_config("success", foreground="green")
        self.training_log_text.tag_config("error", foreground="red")
        self.training_log_text.tag_config("warning", foreground="orange")

        # 曲线标签页
        curve_tab = ttk.Frame(log_notebook)
        log_notebook.add(curve_tab, text="训练曲线")

        # 使用 Canvas 绘制曲线
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure

            self.training_figure = Figure(figsize=(8, 4), dpi=80)
            self.training_canvas = FigureCanvasTkAgg(self.training_figure, curve_tab)
            self.training_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # 创建子图
            self.ax_loss = self.training_figure.add_subplot(121)
            self.ax_acc = self.training_figure.add_subplot(122)

            self.ax_loss.set_title("Loss")
            self.ax_loss.set_xlabel("Epoch")
            self.ax_loss.set_ylabel("Loss")
            self.ax_loss.grid(True)

            self.ax_acc.set_title("Accuracy")
            self.ax_acc.set_xlabel("Epoch")
            self.ax_acc.set_ylabel("Accuracy")
            self.ax_acc.grid(True)

            self.training_figure.tight_layout()

        except ImportError:
            ttk.Label(curve_tab, text="需要安装 matplotlib 才能显示训练曲线\n运行: pip install matplotlib").pack(
                expand=True
            )

    def create_model_selection_frame(self, parent):
        """创建模型选择区"""
        model_frame = ttk.LabelFrame(parent, text="模型选择", padding="10")
        model_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        models = [
            ("PP-OCRv5_server_det (检测模型)", "det"),
            ("PP-OCRv5_server_rec (识别模型)", "rec"),
            ("SLANeXt_wired (表格模型)", "table"),
        ]

        for idx, (text, value) in enumerate(models):
            ttk.Radiobutton(
                model_frame,
                text=text,
                variable=self.train_model_type,
                value=value,
                command=self.on_model_type_changed
            ).grid(row=idx, column=0, padx=10, pady=2, sticky=tk.W)

    def create_dataset_config_frame(self, parent):
        """创建数据集配置区"""
        dataset_frame = ttk.LabelFrame(parent, text="数据集配置", padding="10")
        dataset_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        dataset_frame.columnconfigure(1, weight=1)

        # 数据集根目录
        ttk.Label(dataset_frame, text="数据集目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(dataset_frame, textvariable=self.dataset_root_dir).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5)
        )
        ttk.Button(dataset_frame, text="浏览...", command=self.browse_dataset_root).grid(
            row=0, column=2
        )

        # 说明文字
        info_label = ttk.Label(
            dataset_frame,
            text="目录结构：train_images/, val_images/, train.txt, val.txt",
            foreground="gray"
        )
        info_label.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))

        # 验证数据集按钮
        ttk.Button(dataset_frame, text="验证数据集", command=self.validate_dataset).grid(
            row=2, column=0, columnspan=3, pady=(10, 0)
        )

    def create_data_augmentation_frame(self, parent):
        """创建数据增强区"""
        aug_frame = ttk.LabelFrame(parent, text="数据增强", padding="10")
        aug_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        aug_frame.columnconfigure(1, weight=1)

        # 说明文字
        info_label = ttk.Label(
            aug_frame,
            text="对现有数据集进行增强，生成更多训练样本",
            foreground="gray"
        )
        info_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))

        # 增强数量
        ttk.Label(aug_frame, text="每张图片增强数量:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(aug_frame, from_=1, to=50, textvariable=self.aug_count, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=(10, 0)
        )

        # 增强状态指示
        self.aug_status_label = ttk.Label(aug_frame, text="", foreground="blue")
        self.aug_status_label.grid(row=1, column=2, sticky=tk.W, padx=(20, 0))

        # 增强策略说明
        strategy_text = "增强策略：几何变换、噪声、亮度对比度、模糊等"
        ttk.Label(aug_frame, text=strategy_text, foreground="gray", font=("Arial", 8)).grid(
            row=2, column=0, columnspan=3, sticky=tk.W, pady=(5, 10)
        )

        # 按钮区
        button_frame = ttk.Frame(aug_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(5, 0))

        ttk.Button(button_frame, text="开始增强", command=self.start_data_augmentation, width=15).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        ttk.Button(button_frame, text="查看增强结果", command=self.view_augmented_data, width=15).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        ttk.Button(button_frame, text="删除增强数据", command=self.delete_augmented_data, width=15).pack(
            side=tk.LEFT
        )

    def create_training_params_frame(self, parent):
        """创建训练参数区"""
        params_frame = ttk.LabelFrame(parent, text="训练参数", padding="10")
        params_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        params_frame.columnconfigure(1, weight=1)
        params_frame.columnconfigure(3, weight=1)

        # 预训练模型（可选）
        ttk.Label(params_frame, text="预训练模型:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(params_frame, textvariable=self.pretrained_model).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5)
        )
        ttk.Button(params_frame, text="浏览...", command=self.browse_pretrained_model).grid(
            row=0, column=2, padx=(0, 20)
        )

        # Epoch 数量
        ttk.Label(params_frame, text="Epoch:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Spinbox(params_frame, from_=1, to=10000, textvariable=self.epoch_num, width=10).grid(
            row=1, column=1, sticky=tk.W, padx=(10, 0)
        )

        # Batch Size
        ttk.Label(params_frame, text="Batch Size:").grid(row=1, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        ttk.Spinbox(params_frame, from_=1, to=512, textvariable=self.batch_size, width=10).grid(
            row=1, column=3, sticky=tk.W, padx=(10, 0)
        )

        # 学习率
        ttk.Label(params_frame, text="学习率:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(params_frame, textvariable=self.learning_rate, width=15).grid(
            row=2, column=1, sticky=tk.W, padx=(10, 0)
        )

        # GPU 设备
        ttk.Label(params_frame, text="GPU 设备:").grid(row=2, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        ttk.Entry(params_frame, textvariable=self.gpu_id, width=10).grid(
            row=2, column=3, sticky=tk.W, padx=(10, 0)
        )

    def create_training_log_frame(self, parent):
        """创建训练日志和曲线区"""
        log_frame = ttk.LabelFrame(parent, text="训练日志", padding="10")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # 创建 Notebook 用于日志和曲线切换
        log_notebook = ttk.Notebook(log_frame)
        log_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 日志标签页
        log_tab = ttk.Frame(log_notebook)
        log_notebook.add(log_tab, text="日志输出")

        self.training_log_text = scrolledtext.ScrolledText(
            log_tab,
            wrap=tk.WORD,
            height=15,
            state=tk.DISABLED,
            font=("Consolas", 9)
        )
        self.training_log_text.pack(fill=tk.BOTH, expand=True)

        # 配置日志颜色
        self.training_log_text.tag_config("info", foreground="black")
        self.training_log_text.tag_config("success", foreground="green")
        self.training_log_text.tag_config("error", foreground="red")
        self.training_log_text.tag_config("warning", foreground="orange")

        # 曲线标签页
        curve_tab = ttk.Frame(log_notebook)
        log_notebook.add(curve_tab, text="训练曲线")

        # 使用 Canvas 绘制曲线
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            from matplotlib.figure import Figure

            self.training_figure = Figure(figsize=(8, 4), dpi=80)
            self.training_canvas = FigureCanvasTkAgg(self.training_figure, curve_tab)
            self.training_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

            # 创建子图
            self.ax_loss = self.training_figure.add_subplot(121)
            self.ax_acc = self.training_figure.add_subplot(122)

            self.ax_loss.set_title("Loss")
            self.ax_loss.set_xlabel("Epoch")
            self.ax_loss.set_ylabel("Loss")
            self.ax_loss.grid(True)

            self.ax_acc.set_title("Accuracy")
            self.ax_acc.set_xlabel("Epoch")
            self.ax_acc.set_ylabel("Accuracy")
            self.ax_acc.grid(True)

            self.training_figure.tight_layout()

        except ImportError:
            ttk.Label(curve_tab, text="需要安装 matplotlib 才能显示训练曲线\n运行: pip install matplotlib").pack(
                expand=True
            )

    def create_training_button_frame(self, parent):
        """创建训练控制按钮"""
        button_frame = ttk.LabelFrame(parent, text="训练控制", padding="10")
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))

        self.start_training_btn = ttk.Button(
            button_frame,
            text="开始训练",
            command=self.start_training,
            width=15
        )
        self.start_training_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_training_btn = ttk.Button(
            button_frame,
            text="停止训练",
            command=self.stop_training,
            state=tk.DISABLED,
            width=15
        )
        self.stop_training_btn.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(button_frame, text="清空日志", command=self.clear_training_log, width=15).pack(
            side=tk.LEFT, padx=(0, 10)
        )

        ttk.Button(button_frame, text="查看训练模型", command=self.view_trained_models, width=15).pack(
            side=tk.LEFT
        )

    # 训练相关方法
    def on_model_type_changed(self):
        """模型类型改变时的处理"""
        model_type = self.train_model_type.get()

        # 自动加载对应的预训练模型
        pretrained_model_map = {
            "det": "./pretrained_models/det/PP-OCRv5_server_det_pretrained.pdparams",
            "rec": "./pretrained_models/rec/PP-OCRv5_server_rec_pretrained.pdparams",
            "table": "./pretrained_models/table/SLANeXt_wired_pretrained.pdparams",
        }

        pretrained_path = pretrained_model_map.get(model_type, "")
        if pretrained_path and os.path.exists(pretrained_path):
            self.pretrained_model.set(pretrained_path)

        # 根据模型类型调整默认参数
        if model_type == "det":
            self.batch_size.set(8)
            self.epoch_num.set(500)
        elif model_type == "rec":
            self.batch_size.set(128)
            self.epoch_num.set(500)
        elif model_type == "table":
            self.batch_size.set(32)
            self.epoch_num.set(400)

    def browse_dataset_root(self):
        """浏览数据集根目录"""
        directory = filedialog.askdirectory(title="选择数据集根目录")
        if directory:
            self.dataset_root_dir.set(directory)
            # 检查增强数据状态
            self.check_augmented_data_status()

    def browse_pretrained_model(self):
        """浏览预训练模型"""
        filename = filedialog.askopenfilename(
            title="选择预训练模型文件",
            filetypes=[("模型文件", "*.pdparams"), ("所有文件", "*.*")]
        )
        if filename:
            self.pretrained_model.set(filename)

    def validate_dataset(self):
        """验证数据集格式"""
        if self.is_training:
            messagebox.showwarning("警告", "训练进行中，无法验证数据集")
            return

        dataset_root = self.dataset_root_dir.get()
        if not dataset_root:
            messagebox.showerror("错误", "请先选择数据集根目录")
            return

        # 自动构建路径
        train_data_dir = os.path.join(dataset_root, "train_images")
        train_label = os.path.join(dataset_root, "train.txt")
        val_data_dir = os.path.join(dataset_root, "val_images")
        val_label = os.path.join(dataset_root, "val.txt")

        # 检查路径是否存在
        missing_paths = []
        if not os.path.exists(train_data_dir):
            missing_paths.append("train_images/")
        if not os.path.exists(train_label):
            missing_paths.append("train.txt")
        if not os.path.exists(val_data_dir):
            missing_paths.append("val_images/")
        if not os.path.exists(val_label):
            missing_paths.append("val.txt")

        if missing_paths:
            messagebox.showerror(
                "错误",
                f"数据集目录结构不完整，缺少：\n" + "\n".join(missing_paths)
            )
            return

        model_type = self.train_model_type.get()

        if not train_data_dir or not train_label:
            messagebox.showwarning("警告", "请先选择训练集目录和标注文件")
            return

        self.log_training("开始验证数据集...", "info")

        def validate_thread():
            try:
                from dataset_validator import DatasetValidator

                validator = DatasetValidator()
                success, errors, warnings = validator.validate(model_type, train_data_dir, train_label)

                if success:
                    self.log_training("✓ 数据集验证通过", "success")
                    for warning in warnings:
                        self.log_training(f"  {warning}", "warning")
                    messagebox.showinfo("成功", "数据集验证通过！")
                else:
                    self.log_training("✗ 数据集验证失败", "error")
                    for error in errors[:10]:  # 只显示前 10 个错误
                        self.log_training(f"  {error}", "error")
                    messagebox.showerror("失败", f"数据集验证失败！\n\n{chr(10).join(errors[:5])}")

            except Exception as e:
                self.log_training(f"验证失败: {str(e)}", "error")
                messagebox.showerror("错误", f"验证失败: {str(e)}")

        thread = threading.Thread(target=validate_thread, daemon=True)
        thread.start()

    def start_training(self):
        """开始训练"""
        if self.is_training:
            messagebox.showwarning("警告", "训练已在进行中")
            return

        # 验证输入
        dataset_root = self.dataset_root_dir.get()
        if not dataset_root:
            messagebox.showwarning("警告", "请先选择数据集根目录")
            return

        # 自动检测是否存在增强后的数据集，优先使用增强数据
        dataset_root_path = Path(dataset_root)
        aug_train_images = dataset_root_path / "train_images_aug"
        aug_train_label = dataset_root_path / "train_aug.txt"
        aug_val_images = dataset_root_path / "val_images_aug"
        aug_val_label = dataset_root_path / "val_aug.txt"

        # 检查是否存在增强数据
        has_aug_data = (
            aug_train_images.exists() and
            aug_train_label.exists() and
            aug_val_images.exists() and
            aug_val_label.exists()
        )

        if has_aug_data:
            # 使用增强后的数据
            train_data_dir = str(aug_train_images)
            train_label = str(aug_train_label)
            val_data_dir = str(aug_val_images)
            val_label = str(aug_val_label)
            self.log_training("检测到增强数据集，将使用增强后的数据进行训练", "info")
        else:
            # 使用原始数据
            train_data_dir = str(dataset_root_path / "train_images")
            train_label = str(dataset_root_path / "train.txt")
            val_data_dir = str(dataset_root_path / "val_images")
            val_label = str(dataset_root_path / "val.txt")
            self.log_training("使用原始数据集进行训练", "info")

        # 检查路径是否存在
        if not os.path.exists(train_data_dir) or not os.path.exists(train_label):
            messagebox.showwarning("警告", "训练数据集不完整（缺少 train_images/ 或 train.txt）")
            return

        if not os.path.exists(val_data_dir) or not os.path.exists(val_label):
            messagebox.showwarning("警告", "验证数据集不完整（缺少 val_images/ 或 val.txt）")
            return

        # 确认开始训练
        if not messagebox.askyesno("确认", "确定要开始训练吗？\n训练可能需要较长时间。"):
            return

        self.is_training = True
        self.start_training_btn.config(state=tk.DISABLED)
        self.stop_training_btn.config(state=tk.NORMAL)
        self.set_status("训练中...")

        # 清空训练指标
        self.training_metrics = {"epochs": [], "losses": [], "accs": [], "lrs": []}

        def training_thread():
            try:
                from training_config import TrainingConfigGenerator
                from training_executor import TrainingExecutor

                # 生成配置文件
                self.log_training("生成训练配置...", "info")
                generator = TrainingConfigGenerator()

                model_type = self.train_model_type.get()
                params = {
                    "train_data_dir": train_data_dir,
                    "train_label": train_label,
                    "val_data_dir": val_data_dir,
                    "val_label": val_label,
                    "pretrained_model": self.pretrained_model.get() if self.pretrained_model.get() else None,
                    "epoch_num": self.epoch_num.get(),
                    "batch_size": self.batch_size.get(),
                    "learning_rate": self.learning_rate.get(),
                    "save_model_dir": f"./trained_models/{model_type}",
                }

                config_path = f"./training/configs/{model_type}/training_config.yml"
                generator.generate_and_save(model_type, params, config_path)
                self.log_training(f"配置文件已生成: {config_path}", "success")

                # 启动训练
                self.log_training("启动训练进程...", "info")
                self.training_executor = TrainingExecutor(
                    log_callback=self.log_training,
                    metric_callback=self.update_training_metrics
                )

                if self.training_executor.start_training(config_path, self.gpu_id.get()):
                    self.log_training("训练已启动", "success")
                else:
                    self.log_training("训练启动失败", "error")
                    self.is_training = False
                    self.start_training_btn.config(state=tk.NORMAL)
                    self.stop_training_btn.config(state=tk.DISABLED)
                    self.set_status("就绪")

            except Exception as e:
                self.log_training(f"训练失败: {str(e)}", "error")
                messagebox.showerror("错误", f"训练失败: {str(e)}")
                self.is_training = False
                self.start_training_btn.config(state=tk.NORMAL)
                self.stop_training_btn.config(state=tk.DISABLED)
                self.set_status("就绪")

        thread = threading.Thread(target=training_thread, daemon=True)
        thread.start()

    def stop_training(self):
        """停止训练"""
        if not self.is_training:
            return

        if messagebox.askyesno("确认", "确定要停止训练吗？"):
            if self.training_executor:
                self.training_executor.stop_training()

            self.is_training = False
            self.start_training_btn.config(state=tk.NORMAL)
            self.stop_training_btn.config(state=tk.DISABLED)
            self.set_status("就绪")

    def log_training(self, text, log_type="info"):
        """输出训练日志"""
        self.training_log_text.config(state=tk.NORMAL)
        self.training_log_text.insert(tk.END, f"{text}\n", log_type)
        self.training_log_text.see(tk.END)
        self.training_log_text.config(state=tk.DISABLED)

    def clear_training_log(self):
        """清空训练日志"""
        self.training_log_text.config(state=tk.NORMAL)
        self.training_log_text.delete(1.0, tk.END)
        self.training_log_text.config(state=tk.DISABLED)

    def update_training_metrics(self, epoch, loss, acc, lr):
        """更新训练指标"""
        self.training_metrics["epochs"].append(epoch)
        self.training_metrics["losses"].append(loss)
        self.training_metrics["accs"].append(acc)
        self.training_metrics["lrs"].append(lr)

        # 更新曲线
        try:
            self.ax_loss.clear()
            self.ax_acc.clear()

            self.ax_loss.plot(self.training_metrics["epochs"], self.training_metrics["losses"], "b-")
            self.ax_loss.set_title("Loss")
            self.ax_loss.set_xlabel("Epoch")
            self.ax_loss.set_ylabel("Loss")
            self.ax_loss.grid(True)

            self.ax_acc.plot(self.training_metrics["epochs"], self.training_metrics["accs"], "g-")
            self.ax_acc.set_title("Accuracy")
            self.ax_acc.set_xlabel("Epoch")
            self.ax_acc.set_ylabel("Accuracy")
            self.ax_acc.grid(True)

            self.training_figure.tight_layout()
            self.training_canvas.draw()

        except Exception as e:
            pass  # 忽略绘图错误

    def view_trained_models(self):
        """查看已训练的模型"""
        trained_models_dir = Path("./trained_models")
        if not trained_models_dir.exists():
            messagebox.showinfo("提示", "还没有训练过的模型")
            return

        # 打开文件管理器
        import subprocess
        import platform

        system = platform.system()
        if system == "Windows":
            os.startfile(str(trained_models_dir))
        elif system == "Darwin":  # macOS
            subprocess.run(["open", str(trained_models_dir)])
        else:  # Linux
            subprocess.run(["xdg-open", str(trained_models_dir)])

    def start_data_augmentation(self):
        """开始数据增强"""
        if self.is_training:
            messagebox.showwarning("警告", "训练进行中，无法进行数据增强")
            return

        dataset_root = self.dataset_root_dir.get()
        if not dataset_root:
            messagebox.showwarning("警告", "请先选择数据集根目录")
            return

        if not os.path.exists(dataset_root):
            messagebox.showerror("错误", f"数据集目录不存在: {dataset_root}")
            return

        # 确认开始增强
        aug_count = self.aug_count.get()
        if not messagebox.askyesno("确认", f"确定要对数据集进行增强吗？\n每张图片将生成 {aug_count} 张增强图片。"):
            return

        # 在新线程中执行增强
        thread = threading.Thread(target=self._augment_data_thread, daemon=True)
        thread.start()

    def _augment_data_thread(self):
        """数据增强线程"""
        try:
            from ocr_data_augmentor import OCRDataAugmentor

            dataset_root = self.dataset_root_dir.get()
            model_type = self.train_model_type.get()
            aug_count = self.aug_count.get()

            self.log_training("=" * 60, "info")
            self.log_training("开始数据增强", "info")
            self.log_training("=" * 60, "info")
            self.log_training(f"数据集目录: {dataset_root}", "info")
            self.log_training(f"模型类型: {model_type}", "info")
            self.log_training(f"增强数量: {aug_count}", "info")
            self.log_training("", "info")

            # 创建增强器
            augmentor = OCRDataAugmentor(
                dataset_root=dataset_root,
                model_type=model_type,
                aug_count=aug_count
            )

            # 验证数据集
            self.log_training("验证数据集格式...", "info")
            valid, errors = augmentor.validate_dataset()
            if not valid:
                self.log_training("✗ 数据集验证失败:", "error")
                for error in errors:
                    self.log_training(f"  {error}", "error")
                messagebox.showerror("错误", "数据集验证失败！\n\n" + "\n".join(errors))
                return

            self.log_training("✓ 数据集验证通过", "success")
            self.log_training("", "info")

            # 执行增强
            result = augmentor.augment_all()

            if result:
                self.log_training("", "info")
                self.log_training("=" * 60, "info")
                self.log_training("✓ 数据增强完成！", "success")
                self.log_training("=" * 60, "info")
                self.log_training(f"训练集: {result['train_original']} -> {result['train_total']}", "success")
                self.log_training(f"验证集: {result['val_original']} -> {result['val_total']}", "success")
                self.log_training(f"总计增加: {result['train_total'] + result['val_total'] - result['train_original'] - result['val_original']} 张", "success")
                self.log_training("", "info")
                self.log_training("提示: 训练时将自动使用增强后的数据集", "info")

                # 弹出提示，询问是否使用增强后的数据集进行训练
                use_aug = messagebox.askyesno(
                    "完成",
                    f"数据增强完成！\n\n"
                    f"训练集: {result['train_original']} -> {result['train_total']}\n"
                    f"验证集: {result['val_original']} -> {result['val_total']}\n\n"
                    f"增强后的数据保存在 *_aug 目录中\n\n"
                    f"训练时将自动使用增强后的数据集，无需重新选择目录。"
                )

                # 更新增强数据状态
                self.check_augmented_data_status()
            else:
                self.log_training("✗ 数据增强失败", "error")
                messagebox.showerror("错误", "数据增强失败！")

        except Exception as e:
            self.log_training("", "info")
            self.log_training(f"✗ 数据增强出错: {str(e)}", "error")
            import traceback
            self.log_training(traceback.format_exc(), "error")
            messagebox.showerror("错误", f"数据增强出错:\n{str(e)}")

    def view_augmented_data(self):
        """查看增强后的数据"""
        dataset_root = self.dataset_root_dir.get()
        if not dataset_root:
            messagebox.showwarning("警告", "请先选择数据集根目录")
            return

        aug_dir = Path(dataset_root) / "train_images_aug"
        if not aug_dir.exists():
            messagebox.showinfo("提示", "还没有增强过的数据\n请先执行数据增强")
            return

        # 打开文件管理器
        import subprocess
        import platform

        system = platform.system()
        if system == "Windows":
            os.startfile(str(aug_dir))
        elif system == "Darwin":  # macOS
            subprocess.run(["open", str(aug_dir)])
        else:  # Linux
            subprocess.run(["xdg-open", str(aug_dir)])

    def delete_augmented_data(self):
        """删除增强数据"""
        dataset_root = self.dataset_root_dir.get()
        if not dataset_root:
            messagebox.showwarning("警告", "请先选择数据集根目录")
            return

        dataset_root_path = Path(dataset_root)
        aug_dirs = [
            dataset_root_path / "train_images_aug",
            dataset_root_path / "val_images_aug",
        ]
        aug_files = [
            dataset_root_path / "train_aug.txt",
            dataset_root_path / "val_aug.txt",
        ]

        # 检查是否存在增强数据
        has_aug = any(d.exists() for d in aug_dirs) or any(f.exists() for f in aug_files)

        if not has_aug:
            messagebox.showinfo("提示", "没有找到增强数据")
            return

        # 确认删除
        if not messagebox.askyesno("确认", "确定要删除所有增强数据吗？\n此操作不可恢复！"):
            return

        try:
            # 删除目录
            for aug_dir in aug_dirs:
                if aug_dir.exists():
                    shutil.rmtree(aug_dir)
                    self.log_training(f"已删除: {aug_dir}", "info")

            # 删除文件
            for aug_file in aug_files:
                if aug_file.exists():
                    aug_file.unlink()
                    self.log_training(f"已删除: {aug_file}", "info")

            self.log_training("✓ 增强数据已全部删除", "success")
            messagebox.showinfo("完成", "增强数据已删除")

            # 更新状态
            self.check_augmented_data_status()

        except Exception as e:
            self.log_training(f"✗ 删除失败: {str(e)}", "error")
            messagebox.showerror("错误", f"删除失败:\n{str(e)}")

    def check_augmented_data_status(self):
        """检查增强数据状态"""
        dataset_root = self.dataset_root_dir.get()
        if not dataset_root:
            self.aug_status_label.config(text="")
            return

        dataset_root_path = Path(dataset_root)
        aug_train_images = dataset_root_path / "train_images_aug"
        aug_train_label = dataset_root_path / "train_aug.txt"
        aug_val_images = dataset_root_path / "val_images_aug"
        aug_val_label = dataset_root_path / "val_aug.txt"

        # 检查是否存在增强数据
        has_aug_data = (
            aug_train_images.exists() and
            aug_train_label.exists() and
            aug_val_images.exists() and
            aug_val_label.exists()
        )

        if has_aug_data:
            # 统计增强数据量
            try:
                with open(aug_train_label, 'r', encoding='utf-8') as f:
                    train_count = len(f.readlines())
                with open(aug_val_label, 'r', encoding='utf-8') as f:
                    val_count = len(f.readlines())

                self.aug_status_label.config(
                    text=f"✓ 已增强 (训练:{train_count} 验证:{val_count})",
                    foreground="green"
                )
            except:
                self.aug_status_label.config(text="✓ 已增强", foreground="green")
        else:
            self.aug_status_label.config(text="未增强", foreground="gray")


class SettingsWindow:
    """设置窗口"""
    def __init__(self, parent, app):
        self.app = app
        self.window = tk.Toplevel(parent)
        self.window.title("设置")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()

        self.create_widgets()

    def create_widgets(self):
        """创建设置界面"""
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 配置文件
        ttk.Label(main_frame, text="配置文件:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        config_frame = ttk.Frame(main_frame)
        config_frame.pack(fill=tk.X, pady=(0, 20))

        self.config_path_var = tk.StringVar(value=self.app.config_path)
        ttk.Entry(config_frame, textvariable=self.config_path_var, state="readonly").pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10)
        )
        ttk.Button(config_frame, text="浏览...", command=self.browse_config).pack(side=tk.LEFT)

        # 模板文件
        ttk.Label(main_frame, text="模板文件:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        template_frame = ttk.Frame(main_frame)
        template_frame.pack(fill=tk.X, pady=(0, 20))

        self.template_path_var = tk.StringVar(value=self.app.template_path)
        ttk.Entry(template_frame, textvariable=self.template_path_var, state="readonly").pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10)
        )
        ttk.Button(template_frame, text="浏览...", command=self.browse_template).pack(side=tk.LEFT)

        # 按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))

        ttk.Button(button_frame, text="确定", command=self.apply_settings).pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="取消", command=self.window.destroy).pack(side=tk.RIGHT)

    def browse_config(self):
        """浏览配置文件"""
        filename = filedialog.askopenfilename(
            title="选择配置文件",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        if filename:
            self.config_path_var.set(filename)

    def browse_template(self):
        """浏览模板文件"""
        filename = filedialog.askopenfilename(
            title="选择模板文件",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")]
        )
        if filename:
            self.template_path_var.set(filename)

    def apply_settings(self):
        """应用设置"""
        # 更新配置路径
        new_config_path = self.config_path_var.get()
        if new_config_path != self.app.config_path:
            self.app.config_path = new_config_path
            if not self.app.reload_config():
                return

        # 更新模板路径
        new_template_path = self.template_path_var.get()
        if new_template_path != self.app.template_path:
            self.app.template_path = new_template_path
            if not self.app.reload_template():
                return

        # 更新界面显示
        template_name = self.app.template.get("display_name", "未知") if self.app.template else "未加载"
        self.app.template_label.config(text=template_name)

        messagebox.showinfo("成功", "设置已更新")
        self.window.destroy()


def main():
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
