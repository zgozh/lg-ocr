# 内置训练环境说明

## 目录结构

```
training/
├── ppocr/              # PaddleOCR 核心训练模块（需从官方仓库复制）
├── tools/              # 训练脚本（需从官方仓库复制）
├── configs/            # 配置模板
│   ├── det/           # 检测模型配置
│   ├── rec/           # 识别模型配置
│   └── table/         # 表格模型配置
└── requirements.txt    # 训练依赖

## 环境准备

### 1. 安装 PaddleOCR 训练依赖

```bash
pip install paddlepaddle-gpu
pip install -r training/requirements.txt
```

### 2. 复制 PaddleOCR 训练模块

从 PaddleOCR 官方仓库复制以下目录到 `training/` 下：

- `ppocr/` - 核心训练模块
- `tools/train.py` - 训练脚本
- `tools/eval.py` - 评估脚本
- `tools/export_model.py` - 模型导出脚本

或者直接克隆官方仓库：

```bash
cd training
git clone https://github.com/PaddlePaddle/PaddleOCR.git temp
cp -r temp/ppocr ./
cp -r temp/tools ./
rm -rf temp
```

## 数据集格式

### 检测模型（PP-OCRv5_server_det）

```
datasets/detection/
├── train_images/
│   ├── img_001.jpg
│   └── ...
├── train.txt          # 格式: img_001.jpg\t[{"transcription": "文字", "points": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]}]
└── val.txt
```

### 识别模型（PP-OCRv5_server_rec）

```
datasets/recognition/
├── train_images/
│   ├── word_001.jpg
│   └── ...
├── train.txt          # 格式: word_001.jpg\t文字内容
└── val.txt
```

### 表格模型（SLANeXt_wired）

```
datasets/table/
├── train_images/
│   ├── table_001.jpg
│   └── ...
├── train.txt          # 格式: table_001.jpg\t<html><table>...</table></html>
└── val.txt
```

## 使用方式

通过图形界面的"模型训练"标签页进行训练，无需手动配置。
