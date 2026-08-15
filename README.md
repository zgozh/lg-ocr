# DocExtractor 文档信息提取系统

> 基于 PaddleOCR 与大语言模型（Ollama）的智能文档信息提取工具，批量识别扫描件中的结构化信息，并自动生成 Excel 汇总表。

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![PaddleOCR](https://img.shields.io/badge/PaddleOCR-3.7.0-2962FF)](https://github.com/PaddlePaddle/PaddleOCR)

---

## 📌 项目简介

DocExtractor 文档信息提取系统面向**档案数字化 / 政务文档处理 / 企业文档管理**等场景，将「高精度 OCR 识别」与「大语言模型语义理解」结合，实现对结构化文档（如常住人口登记表、人事档案、证件表单等）的端到端批量信息提取。

典型应用：批量扫描户籍登记表 → 自动识别表格与文字 → LLM 按字段抽取姓名、性别、出生日期、证件号码等信息 → 生成规范 Excel 汇总表。

## ✨ 核心特性

- **高精度 OCR**：基于 PaddleOCR PP-OCRv5 server 系列引擎，支持印刷体与手写体、有线/无线表格、版面分析。
- **智能信息提取**：通过本地大语言模型理解文档语义，按模板字段自动抽取关键信息，失败自动重试并兜底。
- **批量处理**：目录递归扫描、隔页推理、实时进度条、错误自动兜底。
- **灵活配置**：JSON 配置文件 + 模板化字段定义，可自定义文档类型与输出列。
- **多入口**：图形界面（GUI）、交互式菜单、纯命令行三种使用方式。
- **本地化运行**：全程本地处理，数据不出本机，支持离线运行。

## 🧭 处理流程

```
1. 扫描图片文件（支持隔页推理）
        ↓
2. OCR 文字识别（版面分析 + 表格结构识别 + 文字检测/识别）
        ↓
3. 文本阅读顺序排序（从左到右、从上到下）
        ↓
4. 保存中间结果 JSON（ocr_result/ 目录）
        ↓
5. LLM 语义理解 + 按模板字段提取
        ↓
6. 写入 Excel 汇总表（追加式合并）
        ↓
7. 失败图片自动写入兜底记录
```

## 🏗️ 技术架构

```
┌──────────────────────────────────────────┐
│  用户交互层：GUI / 交互式菜单 / 命令行      │
└──────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────┐
│  业务处理层：文件扫描 · 流程控制 · 结果输出  │
└──────────────────────────────────────────┘
                      ↓
┌────────────────────┬─────────────────────┐
│  OCR 识别层         │  LLM 提取层          │
│  · PaddleOCR       │  · Ollama           │
│  · 表格识别         │  · 语义理解          │
│  · 版面分析         │  · 字段抽取          │
└────────────────────┴─────────────────────┘
                      ↓
┌──────────────────────────────────────────┐
│  数据输出层：JSON 结果 · Excel 汇总         │
└──────────────────────────────────────────┘
```

## 🧱 技术栈

| 组件 | 版本 | 说明 |
|---|---|---|
| Python | 3.8+（本项目实测 3.13） | 运行环境 |
| PaddlePaddle | 3.1.1（GPU） | 深度学习框架 |
| PaddleOCR / PaddleX | 3.7.0 / 3.7.2 | OCR 与版面/表格识别管线 |
| Ollama | 0.6.2 | 本地大语言模型服务 |
| pandas / openpyxl | 3.x | Excel 读写 |
| tkinter | 内置 | 图形界面 |

## 📁 目录结构

```
DocExtractor/
├── gui.py                    # 图形界面程序（含模型训练标签页）
├── menu.py                   # 交互式菜单程序（推荐）
├── main.py                   # 纯命令行批处理程序
├── config.py                 # 配置加载模块
├── config.json               # 系统配置（Ollama / 模型路径 / 设备）
├── ocr_pipeline.py           # PaddleOCR 管线构建与调用
├── llm_extract.py            # Ollama 连接检测与字段抽取
├── excel_writer.py           # Excel 汇总输出
├── template_loader.py        # 模板加载与校验
├── file_scanner.py           # 图片文件扫描
├── training_config.py        # 训练配置生成器
├── training_executor.py      # 训练进程执行器
├── ocr_data_augmentor.py     # 数据增强
├── dataset_validator.py      # 数据集校验
├── test_ollama_connection.py # Ollama 连接测试脚本
├── requirements.txt          # Python 依赖
├── MODELS.md                 # 模型准备清单（下载地址）
├── templates/                # 文档模板（字段定义 + 输出列映射）
│   └── hukou_register.json   # 常住人口登记表模板
├── utils/                    # 工具模块（文本框排序 / JSON 解析等）
├── tests/                    # 单元测试
├── test_data/                # 测试数据
├── docs/                    # 项目文档（安装/使用/配置/FAQ 等）
├── official_models/          # 官方推理模型（不入库，需自行准备）
├── pretrained_models/        # 预训练权重（不入库，需自行准备）
└── training/                 # 训练环境（ppocr/tools 需从官方仓库复制）
```

> 注：`official_models/`、`pretrained_models/*.pdparams`、`ocr-env/`、`training/ppocr/`、`training/tools/` 等大体积或可再生成内容已加入 `.gitignore`，不入库。

## 🛠️ 环境要求

### 硬件

| 模式 | 要求 | 处理速度 |
|---|---|---|
| GPU（推荐） | NVIDIA GPU，显存 4GB+ | 3–5 秒/张（RTX 3090） |
| CPU | 4 核 CPU，8GB 内存 | 30–60 秒/张 |

### 软件

- Python 3.8+
- Ollama 服务（已拉取所需 LLM 模型）
- PaddlePaddle（GPU 或 CPU 版）

## 🚀 安装部署

### 1. 准备模型文件

将以下 8 个官方推理模型放入 `official_models/` 目录（目录名需与 `config.json` 一致）：

| 模型 | 用途 |
|---|---|
| `PP-DocLayout-L` | 版面分析 |
| `PP-LCNet_x1_0_table_cls` | 表格分类 |
| `SLANeXt_wired` / `SLANeXt_wireless` | 有线/无线表格结构识别 |
| `RT-DETR-L_wired_table_cell_det` / `RT-DETR-L_wireless_table_cell_det` | 有线/无线表格单元格检测 |
| `PP-OCRv5_server_rec` / `PP-OCRv5_server_det` | 文字识别 / 文字检测 |

模型可从 [PaddlePaddle Hugging Face](https://huggingface.co/PaddlePaddle) 或 PaddleOCR 官方渠道下载。

> 📦 完整模型清单（含 8 个推理模型、LLM 模型、预训练模型的详细下载地址与命令）见 **[MODELS.md](./MODELS.md)**。

### 2. 安装 Python 依赖

```bash
# 创建虚拟环境（可选）
python -m venv ocr-env
ocr-env\Scripts\activate        # Windows
# source ocr-env/bin/activate   # Linux / macOS

# 安装 PaddlePaddle（GPU 版，按需替换为 CPU 版 paddlepaddle）
pip install paddlepaddle-gpu==3.1.1

# 安装 PaddleOCR / PaddleX
pip install paddleocr==3.7.0 paddlex==3.7.2

# 安装其余依赖
pip install -r requirements.txt
```

### 3. 启动 Ollama 并拉取模型

```bash
# 启动 Ollama 服务
ollama serve

# 拉取 LLM 模型（与 config.json 中 model 字段一致）
ollama pull qwen2.5:7b
```

### 4. 验证安装

```bash
# 测试 Ollama 连接
python test_ollama_connection.py
```

预期输出：

```
✓ 连接成功！
  Ollama 服务正常，可以开始识别任务
```

## 🎯 快速开始

### 方式一：图形界面（GUI）

```bash
python gui.py
```

在界面中选择图片目录、模板，点击开始识别；「模型训练」标签页可用于微调模型。

### 方式二：交互式菜单（推荐）

```bash
python menu.py
```

主菜单：

```
[1] 开始识别   # 输入图片目录 → 确认 → 自动处理并生成 Excel
[2] 设置       # 修改配置/模板路径、切换隔页推理
[3] 退出
```

### 方式三：纯命令行

```bash
python main.py
```

按提示依次输入：图片目录 → 模板路径 → 是否隔页推理。

## ⚙️ 配置说明

### config.json

```json
{
  "ollama": {
    "host": "http://127.0.0.1:11434",
    "model": "qwen2.5:7b",
    "max_retries": 3,
    "retry_delay_seconds": 1.0
  },
  "device": "gpu:0",
  "models": {
    "layout_detection": { "name": "PP-DocLayout-L", "path": "./official_models/PP-DocLayout-L" },
    "...": "..."
  },
  "pipeline": {
    "use_layout_detection": true,
    "use_doc_orientation_classify": false,
    "use_doc_unwarping": false
  }
}
```

| 字段 | 说明 |
|---|---|
| `ollama.host` | Ollama 服务地址 |
| `ollama.model` | LLM 模型名称（需已 `ollama pull`） |
| `ollama.max_retries` / `retry_delay_seconds` | LLM 抽取失败重试次数与间隔 |
| `device` | 推理设备，`gpu:0` / `cpu` |
| `models` | 8 个模型的名称与本地路径 |
| `pipeline` | 管线开关（版面分析、方向分类、文档矫正） |

### 文档模板（templates/*.json）

模板定义「要提取哪些字段」以及「如何映射到 Excel 列」：

```json
{
  "name": "hukou_register",
  "display_name": "常住人口登记表",
  "fields": [
    { "name": "姓名", "default": "X", "description": "人员姓名" }
  ],
  "prompt": {
    "document_type": "常住人口登记表",
    "rules": ["仅提取OCR文本中明确存在的信息，不得自行添加、修改或猜测。"]
  },
  "fallback_record": { "姓名": "X" },
  "output": {
    "sheet_name": "Sheet",
    "text_columns": ["出生日期", "登记日期"],
    "first_row_overrides": { "与户主关系": "户主" },
    "columns": [
      { "header": "姓名", "source": "field", "field": "姓名" },
      { "header": "案卷号", "source": "image_parent_name" },
      { "header": "档号", "source": "constant", "value": "" },
      { "header": "原始图片名称", "source": "image_name" }
    ]
  }
}
```

**输出列 `source` 类型：**

| source | 说明 |
|---|---|
| `field` | 取 LLM 提取的字段值 |
| `constant` | 固定值（`value`） |
| `image_name` | 图片文件名 |
| `image_parent_name` | 图片所在目录名 |
| `image_dir_name` | 图片上级目录名 |

## 📤 输出说明

- **JSON 结果**：`{图片目录}/ocr_result/{图片名}.json` —— 每张图片的完整 OCR 识别结果（文本、坐标、表格结构、版面）。
- **Excel 汇总**：`{图片目录的上级目录}/{图片目录名}.xlsx` —— 批量处理结果按行追加合并。
- **兜底标记**：字段提取失败时使用模板默认值（如 `X`），整张失败则写入兜底记录。

## 🎓 模型训练（可选）

系统内置训练环境，可在 GUI 的「模型训练」标签页微调检测 / 识别 / 表格模型。

1. 将 PaddleOCR 官方仓库的 `ppocr/` 与 `tools/` 复制到 `training/` 目录（详见 `training/README.md`）。
2. 准备数据集（检测 / 识别 / 表格三种格式见 `training/README.md`）。
3. 在 GUI 中选择模型类型、数据集路径、预训练模型（位于 `pretrained_models/`）。

使用预训练模型可显著加快收敛并提升精度，详见 `pretrained_models/README.md`。

## 🧪 测试

```bash
python -m pytest tests/ -v
```

测试覆盖：配置加载、模板加载与校验、文本框排序、JSON 解析、Excel 输出、LLM 提取等模块。

## ❓ 常见问题

**Q1：`ollama` 连接失败？**
确认 Ollama 服务已启动（`ollama serve`）、`config.json` 中 `host`/`model` 正确、模型已下载（`ollama list`）。

**Q2：模型目录找不到？**
检查 `config.json` 中 `models.*.path` 指向的目录是否存在且权重完整（`.pdiparams` 文件）。

**Q3：处理速度慢？**
改用 GPU（`device: "gpu:0"`）、使用更小的 LLM 模型、关闭不需要的管线功能。

**Q4：识别结果不准确？**
提高图片质量（300 DPI+）、启用针对性的识别设置、使用更强模型、调整模板 `prompt.rules`。

**Q5：日期在 Excel 中变成数字？**
模板 `output.text_columns` 中已配置的日期列会自动设为文本格式；未覆盖的可手动设置单元格为文本。

## 📈 性能参考

| 指标 | GPU 模式 | CPU 模式 |
|---|---|---|
| 处理速度 | 3–5 秒/张 | 30–60 秒/张 |
| 处理能力 | 600–1000 张/小时 | 60–120 张/小时 |

*以上数据基于 NVIDIA RTX 3090 与 4 核 CPU 环境测试，实际性能因硬件与模型而异。*

## 🔒 数据安全

- 所有处理均在本地完成，不上传任何数据到云端。
- 原始图片不会被修改。
- 支持离线运行（需提前准备模型与依赖）。

## 📚 更多文档

完整项目文档位于 `docs/`：

- `01-系统简介.md` / `02-安装部署指南.md` / `03-使用手册.md`
- `04-配置说明.md` / `05-常见问题.md` / `06-故障排查指南.md`

## 👤 作者

- **zgozh** · [GitHub](https://github.com/zgozh)
- 本项目由作者独立设计开发，借助 AI 编程工具（Vibe Coding）完成，欢迎 Star / Issue / PR。

## 📝 License

本项目采用 [MIT License](./LICENSE)。
