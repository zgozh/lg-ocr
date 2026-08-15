# 模型准备清单

本文档列出 DocExtractor 文档信息提取系统运行所需的全部模型及其下载地址。按「是否必需」分为三类：

1. [官方推理模型](#一官方推理模型必需) —— 核心 OCR 管线，**必需**
2. [LLM 大语言模型](#二llm-大语言模型必需) —— 信息抽取，**必需**
3. [预训练模型](#三预训练模型可选仅训练微调时需要) —— 模型微调，**可选**

> 说明：所有模型权重均已加入 `.gitignore`，**不会入库**，需在部署时自行下载。

---

## 一、官方推理模型（必需）

位于 `official_models/`，共 8 个，全部来自 Hugging Face 的 [PaddlePaddle](https://huggingface.co/PaddlePaddle) 组织。目录名需与 `config.json` 中 `models.*.path` 保持一致。

| 模型目录名 | 用途 | 下载地址 | 权重体积 |
|---|---|---|---|
| `PP-DocLayout-L` | 版面分析 | [huggingface.co/PaddlePaddle/PP-DocLayout-L](https://huggingface.co/PaddlePaddle/PP-DocLayout-L) | 123 MB |
| `PP-LCNet_x1_0_table_cls` | 表格分类 | [huggingface.co/PaddlePaddle/PP-LCNet_x1_0_table_cls](https://huggingface.co/PaddlePaddle/PP-LCNet_x1_0_table_cls) | 6.4 MB |
| `SLANeXt_wired` | 有线表格结构识别 | [huggingface.co/PaddlePaddle/SLANeXt_wired](https://huggingface.co/PaddlePaddle/SLANeXt_wired) | 348 MB |
| `SLANeXt_wireless` | 无线表格结构识别 | [huggingface.co/PaddlePaddle/SLANeXt_wireless](https://huggingface.co/PaddlePaddle/SLANeXt_wireless) | 348 MB |
| `RT-DETR-L_wired_table_cell_det` | 有线表格单元格检测 | [huggingface.co/PaddlePaddle/RT-DETR-L_wired_table_cell_det](https://huggingface.co/PaddlePaddle/RT-DETR-L_wired_table_cell_det) | 123 MB |
| `RT-DETR-L_wireless_table_cell_det` | 无线表格单元格检测 | [huggingface.co/PaddlePaddle/RT-DETR-L_wireless_table_cell_det](https://huggingface.co/PaddlePaddle/RT-DETR-L_wireless_table_cell_det) | 123 MB |
| `PP-OCRv5_server_rec` | 文字识别 | [huggingface.co/PaddlePaddle/PP-OCRv5_server_rec](https://huggingface.co/PaddlePaddle/PP-OCRv5_server_rec) | 80.5 MB |
| `PP-OCRv5_server_det` | 文字检测 | [huggingface.co/PaddlePaddle/PP-OCRv5_server_det](https://huggingface.co/PaddlePaddle/PP-OCRv5_server_det) | 83.9 MB |

**合计约 1.24 GB。**

### 下载方式

#### 方式一：huggingface-cli（推荐）

```bash
pip install -U huggingface_hub

huggingface-cli download PaddlePaddle/PP-DocLayout-L \
  --local-dir ./official_models/PP-DocLayout-L

huggingface-cli download PaddlePaddle/PP-LCNet_x1_0_table_cls \
  --local-dir ./official_models/PP-LCNet_x1_0_table_cls

huggingface-cli download PaddlePaddle/SLANeXt_wired \
  --local-dir ./official_models/SLANeXt_wired

huggingface-cli download PaddlePaddle/SLANeXt_wireless \
  --local-dir ./official_models/SLANeXt_wireless

huggingface-cli download PaddlePaddle/RT-DETR-L_wired_table_cell_det \
  --local-dir ./official_models/RT-DETR-L_wired_table_cell_det

huggingface-cli download PaddlePaddle/RT-DETR-L_wireless_table_cell_det \
  --local-dir ./official_models/RT-DETR-L_wireless_table_cell_det

huggingface-cli download PaddlePaddle/PP-OCRv5_server_rec \
  --local-dir ./official_models/PP-OCRv5_server_rec

huggingface-cli download PaddlePaddle/PP-OCRv5_server_det \
  --local-dir ./official_models/PP-OCRv5_server_det
```

#### 方式二：浏览器手动下载

访问上表各「下载地址」页面 → Files 标签页 → 下载 `inference.pdiparams`、`inference.json`、`inference.yml`、`config.json` 等文件，放入对应目录。

#### 国内网络：ModelScope 镜像

访问 [modelscope.cn/organization/PaddlePaddle](https://www.modelscope.cn/organization/PaddlePaddle)，搜索同名模型下载，放入 `official_models/` 对应目录即可。

---

## 二、LLM 大语言模型（必需）

通过 Ollama 本地运行，用于语义理解与字段抽取。`config.json` 中 `ollama.model` 默认配置为 `qwen2.5:7b`：

```bash
ollama pull qwen2.5:7b
```

| 模型 | 说明 | 地址 |
|---|---|---|
| `qwen2.5:7b` | 默认配置，速度与精度均衡 | [ollama.com/library/qwen2.5](https://ollama.com/library/qwen2.5) |
| `qwen2.5:14b` / `qwen2.5:32b` | 精度更高，速度更慢 | 同上 |
| `deepseek-r1:32b` | 推理模型（文档示例） | [ollama.com/library/deepseek-r1](https://ollama.com/library/deepseek-r1) |

> 更换模型后需同步修改 `config.json` 的 `ollama.model` 字段。

---

## 三、预训练模型（可选，仅训练微调时需要）

位于 `pretrained_models/`，用于在自有数据上微调检测 / 识别 / 表格模型。**不训练可完全跳过**。

| 文件 | 用途 | 下载地址 | 体积 |
|---|---|---|---|
| `PP-OCRv5_server_det_pretrained.pdparams` | 检测模型微调 | [paddle-model-ecology.bj.bcebos.com/paddlex/official_pretrained_model/PP-OCRv5_server_det_pretrained.pdparams](https://paddle-model-ecology.bj.bcebos.com/paddlex/official_pretrained_model/PP-OCRv5_server_det_pretrained.pdparams) | 101 MB |
| `PP-OCRv5_server_rec_pretrained.pdparams` | 识别模型微调 | [paddle-model-ecology.bj.bcebos.com/paddlex/official_pretrained_model/PP-OCRv5_server_rec_pretrained.pdparams](https://paddle-model-ecology.bj.bcebos.com/paddlex/official_pretrained_model/PP-OCRv5_server_rec_pretrained.pdparams) | 205 MB |
| `SLANeXt_wired_pretrained.pdparams` | 表格模型微调 | [paddle-model-ecology.bj.bcebos.com/paddlex/official_pretrained_model/SLANeXt_wired_pretrained.pdparams](https://paddle-model-ecology.bj.bcebos.com/paddlex/official_pretrained_model/SLANeXt_wired_pretrained.pdparams) | 184 MB |

**合计约 490 MB。**

下载后按 `pretrained_models/README.md` 的目录结构放置：

```
pretrained_models/
├── det/PP-OCRv5_server_det_pretrained.pdparams
├── rec/PP-OCRv5_server_rec_pretrained.pdparams
└── table/SLANeXt_wired_pretrained.pdparams
```

---

## 参考链接

- [PaddlePaddle Hugging Face 组织](https://huggingface.co/PaddlePaddle)
- [PaddleOCR 官方仓库](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleX 文档 - 文本检测模块](https://paddlepaddle.github.io/PaddleX/3.0/module_usage/tutorials/ocr_modules/text_detection.html)
- [PaddleX 文档 - 表格结构识别模块](https://www.paddleocr.ai/main/version3.x/module_usage/table_structure_recognition.html)
- [Ollama 模型库](https://ollama.com/library)
