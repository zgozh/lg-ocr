"""
数据集验证器
验证训练数据集格式是否符合 PaddleOCR 标准
"""
import os
import json
from pathlib import Path
from PIL import Image


class DatasetValidator:
    """数据集验证器"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_detection_dataset(self, data_dir, label_file):
        """
        验证检测数据集
        格式: img_001.jpg\t[{"transcription": "文字", "points": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]}]
        """
        self.errors = []
        self.warnings = []

        # 检查目录
        if not os.path.exists(data_dir):
            self.errors.append(f"数据目录不存在: {data_dir}")
            return False, self.errors, self.warnings

        # 检查标注文件
        if not os.path.exists(label_file):
            self.errors.append(f"标注文件不存在: {label_file}")
            return False, self.errors, self.warnings

        # 读取标注文件
        try:
            with open(label_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            self.errors.append(f"无法读取标注文件: {str(e)}")
            return False, self.errors, self.warnings

        if len(lines) == 0:
            self.errors.append("标注文件为空")
            return False, self.errors, self.warnings

        # 验证每一行
        valid_count = 0
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) != 2:
                self.errors.append(f"第 {line_num} 行格式错误: 应为 '图片路径\\t标注JSON'")
                continue

            img_path, label_json = parts

            # 检查图片文件
            full_img_path = os.path.join(data_dir, img_path)
            if not os.path.exists(full_img_path):
                self.errors.append(f"第 {line_num} 行: 图片不存在 {img_path}")
                continue

            # 验证图片可读
            try:
                img = Image.open(full_img_path)
                img.verify()
            except Exception as e:
                self.errors.append(f"第 {line_num} 行: 图片无法读取 {img_path} - {str(e)}")
                continue

            # 验证 JSON 格式
            try:
                labels = json.loads(label_json)
                if not isinstance(labels, list):
                    self.errors.append(f"第 {line_num} 行: 标注应为 JSON 数组")
                    continue

                for idx, label in enumerate(labels):
                    if not isinstance(label, dict):
                        self.errors.append(f"第 {line_num} 行: 标注 {idx} 应为 JSON 对象")
                        continue

                    if "transcription" not in label:
                        self.errors.append(f"第 {line_num} 行: 标注 {idx} 缺少 'transcription' 字段")
                        continue

                    if "points" not in label:
                        self.errors.append(f"第 {line_num} 行: 标注 {idx} 缺少 'points' 字段")
                        continue

                    points = label["points"]
                    if not isinstance(points, list) or len(points) != 4:
                        self.errors.append(f"第 {line_num} 行: 标注 {idx} 的 'points' 应为 4 个点的数组")
                        continue

                    for point_idx, point in enumerate(points):
                        if not isinstance(point, list) or len(point) != 2:
                            self.errors.append(f"第 {line_num} 行: 标注 {idx} 的点 {point_idx} 格式错误")
                            break

            except json.JSONDecodeError as e:
                self.errors.append(f"第 {line_num} 行: JSON 解析失败 - {str(e)}")
                continue

            valid_count += 1

        if valid_count == 0:
            self.errors.append("没有有效的标注数据")
            return False, self.errors, self.warnings

        self.warnings.append(f"共 {len(lines)} 行，有效 {valid_count} 行")
        return len(self.errors) == 0, self.errors, self.warnings

    def validate_recognition_dataset(self, data_dir, label_file):
        """
        验证识别数据集
        格式: word_001.jpg\t文字内容
        """
        self.errors = []
        self.warnings = []

        # 检查目录
        if not os.path.exists(data_dir):
            self.errors.append(f"数据目录不存在: {data_dir}")
            return False, self.errors, self.warnings

        # 检查标注文件
        if not os.path.exists(label_file):
            self.errors.append(f"标注文件不存在: {label_file}")
            return False, self.errors, self.warnings

        # 读取标注文件
        try:
            with open(label_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            self.errors.append(f"无法读取标注文件: {str(e)}")
            return False, self.errors, self.warnings

        if len(lines) == 0:
            self.errors.append("标注文件为空")
            return False, self.errors, self.warnings

        # 验证每一行
        valid_count = 0
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) != 2:
                self.errors.append(f"第 {line_num} 行格式错误: 应为 '图片路径\\t文字内容'")
                continue

            img_path, text = parts

            # 检查图片文件
            full_img_path = os.path.join(data_dir, img_path)
            if not os.path.exists(full_img_path):
                self.errors.append(f"第 {line_num} 行: 图片不存在 {img_path}")
                continue

            # 验证图片可读
            try:
                img = Image.open(full_img_path)
                img.verify()
            except Exception as e:
                self.errors.append(f"第 {line_num} 行: 图片无法读取 {img_path} - {str(e)}")
                continue

            # 检查文字内容
            if not text:
                self.warnings.append(f"第 {line_num} 行: 文字内容为空")

            valid_count += 1

        if valid_count == 0:
            self.errors.append("没有有效的标注数据")
            return False, self.errors, self.warnings

        self.warnings.append(f"共 {len(lines)} 行，有效 {valid_count} 行")
        return len(self.errors) == 0, self.errors, self.warnings

    def validate_table_dataset(self, data_dir, label_file):
        """
        验证表格数据集
        格式: table_001.jpg\t<html><table>...</table></html>
        """
        self.errors = []
        self.warnings = []

        # 检查目录
        if not os.path.exists(data_dir):
            self.errors.append(f"数据目录不存在: {data_dir}")
            return False, self.errors, self.warnings

        # 检查标注文件
        if not os.path.exists(label_file):
            self.errors.append(f"标注文件不存在: {label_file}")
            return False, self.errors, self.warnings

        # 读取标注文件
        try:
            with open(label_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            self.errors.append(f"无法读取标注文件: {str(e)}")
            return False, self.errors, self.warnings

        if len(lines) == 0:
            self.errors.append("标注文件为空")
            return False, self.errors, self.warnings

        # 验证每一行
        valid_count = 0
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) != 2:
                self.errors.append(f"第 {line_num} 行格式错误: 应为 '图片路径\\t表格HTML'")
                continue

            img_path, html = parts

            # 检查图片文件
            full_img_path = os.path.join(data_dir, img_path)
            if not os.path.exists(full_img_path):
                self.errors.append(f"第 {line_num} 行: 图片不存在 {img_path}")
                continue

            # 验证图片可读
            try:
                img = Image.open(full_img_path)
                img.verify()
            except Exception as e:
                self.errors.append(f"第 {line_num} 行: 图片无法读取 {img_path} - {str(e)}")
                continue

            # 检查 HTML 格式
            if not html.strip().startswith("<html>") or not html.strip().endswith("</html>"):
                self.warnings.append(f"第 {line_num} 行: HTML 格式可能不正确")

            if "<table>" not in html or "</table>" not in html:
                self.errors.append(f"第 {line_num} 行: HTML 中缺少 <table> 标签")
                continue

            valid_count += 1

        if valid_count == 0:
            self.errors.append("没有有效的标注数据")
            return False, self.errors, self.warnings

        self.warnings.append(f"共 {len(lines)} 行，有效 {valid_count} 行")
        return len(self.errors) == 0, self.errors, self.warnings

    def validate(self, model_type, data_dir, label_file):
        """统一验证接口"""
        if model_type == "det":
            return self.validate_detection_dataset(data_dir, label_file)
        elif model_type == "rec":
            return self.validate_recognition_dataset(data_dir, label_file)
        elif model_type == "table":
            return self.validate_table_dataset(data_dir, label_file)
        else:
            return False, [f"不支持的模型类型: {model_type}"], []


if __name__ == "__main__":
    # 测试验证器
    validator = DatasetValidator()

    # 测试检测数据集
    success, errors, warnings = validator.validate(
        "det",
        "./datasets/detection/train_images",
        "./datasets/detection/train.txt",
    )
    print(f"检测数据集验证: {'通过' if success else '失败'}")
    if errors:
        print("错误:", errors)
    if warnings:
        print("警告:", warnings)
