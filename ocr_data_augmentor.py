#!/usr/bin/env python3
"""
OCR 数据增强器
支持检测和识别数据集的增强
"""
import warnings
warnings.filterwarnings('ignore')

import os
import shutil
import cv2
import tqdm
import numpy as np
import albumentations as A
from PIL import Image
from pathlib import Path
from typing import List, Tuple


class OCRDataAugmentor:
    """OCR 数据增强器"""

    # 图片文件扩展名
    IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif')

    def __init__(self, dataset_root: str, model_type: str = "det", aug_count: int = 5):
        """
        Args:
            dataset_root: 数据集根目录
            model_type: 模型类型 (det/rec/table)
            aug_count: 每张图片增强的数量
        """
        self.dataset_root = Path(dataset_root)
        self.model_type = model_type
        self.aug_count = aug_count

        # 源目录和目标目录
        self.train_images_dir = self.dataset_root / "train_images"
        self.val_images_dir = self.dataset_root / "val_images"
        self.train_label = self.dataset_root / "train.txt"
        self.val_label = self.dataset_root / "val.txt"

        # 增强后的目录
        self.aug_train_images_dir = self.dataset_root / "train_images_aug"
        self.aug_val_images_dir = self.dataset_root / "val_images_aug"
        self.aug_train_label = self.dataset_root / "train_aug.txt"
        self.aug_val_label = self.dataset_root / "val_aug.txt"

        # 数据增强策略
        self.transform = self._build_transform()

    def _build_transform(self):
        """构建数据增强策略"""
        if self.model_type == "det":
            # 检测模型：需要保持文本框坐标
            return A.Compose([
                A.OneOf([
                    A.Affine(scale=(0.8, 1.2), translate_percent=(-0.1, 0.1), rotate=(-5, 5), p=0.5),
                    A.Perspective(scale=(0.05, 0.1), p=0.3),
                    A.ElasticTransform(alpha=50, sigma=5, p=0.2),
                ], p=0.5),

                A.OneOf([
                    A.GaussNoise(var_limit=(10, 50), p=0.3),
                    A.ISONoise(color_shift=(0.01, 0.05), intensity=(0.1, 0.5), p=0.3),
                    A.ImageCompression(quality_lower=60, quality_upper=100, p=0.3),
                ], p=0.4),

                A.OneOf([
                    A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.5),
                    A.RandomGamma(gamma_limit=(80, 120), p=0.3),
                    A.CLAHE(clip_limit=2.0, p=0.3),
                ], p=0.5),

                A.OneOf([
                    A.Blur(blur_limit=3, p=0.3),
                    A.MotionBlur(blur_limit=3, p=0.3),
                    A.GaussianBlur(blur_limit=3, p=0.3),
                ], p=0.3),
            ], p=1.0)

        elif self.model_type == "rec":
            # 识别模型：不需要保持坐标，可以更激进
            return A.Compose([
                A.OneOf([
                    A.Affine(scale=(0.7, 1.3), translate_percent=(-0.15, 0.15), rotate=(-10, 10), shear=(-5, 5), p=0.5),
                    A.Perspective(scale=(0.05, 0.15), p=0.4),
                    A.ElasticTransform(alpha=100, sigma=10, p=0.3),
                ], p=0.6),

                A.OneOf([
                    A.GaussNoise(var_limit=(10, 80), p=0.4),
                    A.ISONoise(color_shift=(0.01, 0.1), intensity=(0.1, 0.8), p=0.4),
                    A.ImageCompression(quality_lower=50, quality_upper=100, p=0.4),
                ], p=0.5),

                A.OneOf([
                    A.RandomBrightnessContrast(brightness_limit=0.3, contrast_limit=0.3, p=0.5),
                    A.RandomGamma(gamma_limit=(70, 130), p=0.4),
                    A.CLAHE(clip_limit=3.0, p=0.4),
                    A.ToGray(p=0.2),
                ], p=0.6),

                A.OneOf([
                    A.Blur(blur_limit=5, p=0.4),
                    A.MotionBlur(blur_limit=5, p=0.4),
                    A.GaussianBlur(blur_limit=5, p=0.4),
                ], p=0.4),
            ], p=1.0)

        else:  # table
            # 表格模型：类似检测模型
            return A.Compose([
                A.OneOf([
                    A.Affine(scale=(0.9, 1.1), translate_percent=(-0.05, 0.05), rotate=(-3, 3), p=0.5),
                    A.Perspective(scale=(0.02, 0.08), p=0.3),
                ], p=0.4),

                A.OneOf([
                    A.GaussNoise(var_limit=(5, 30), p=0.3),
                    A.ImageCompression(quality_lower=70, quality_upper=100, p=0.3),
                ], p=0.3),

                A.OneOf([
                    A.RandomBrightnessContrast(brightness_limit=0.15, contrast_limit=0.15, p=0.5),
                    A.CLAHE(clip_limit=2.0, p=0.3),
                ], p=0.4),
            ], p=1.0)

    def validate_dataset(self) -> Tuple[bool, List[str]]:
        """验证数据集格式"""
        errors = []

        if not self.train_images_dir.exists():
            errors.append(f"训练图片目录不存在: {self.train_images_dir}")

        if not self.train_label.exists():
            errors.append(f"训练标签文件不存在: {self.train_label}")

        if not self.val_images_dir.exists():
            errors.append(f"验证图片目录不存在: {self.val_images_dir}")

        if not self.val_label.exists():
            errors.append(f"验证标签文件不存在: {self.val_label}")

        return len(errors) == 0, errors

    def augment_single_image(self, image_path: Path, label_line: str, output_dir: Path, aug_labels: List[str]) -> int:
        """
        增强单张图片

        Args:
            image_path: 图片路径
            label_line: 标签行（格式：相对路径\t标注内容）
            output_dir: 输出目录
            aug_labels: 增强后的标签列表（用于收集）

        Returns:
            成功增强的数量
        """
        try:
            # 解析标签行
            parts = label_line.strip().split('\t')
            if len(parts) < 2:
                return 0

            rel_path = parts[0]
            annotation = '\t'.join(parts[1:])

            # 读取图片
            image = Image.open(image_path).convert('RGB')
            image_np = np.array(image)

            # 获取文件名和扩展名
            file_stem = image_path.stem
            file_ext = image_path.suffix

            success_count = 0

            for i in range(self.aug_count):
                try:
                    # 应用数据增强
                    transformed = self.transform(image=image_np)
                    aug_image = transformed['image']

                    # 生成新文件名
                    new_filename = f"{file_stem}_aug{i:03d}{file_ext}"
                    new_image_path = output_dir / new_filename

                    # 保存增强后的图片
                    cv2.imwrite(str(new_image_path), cv2.cvtColor(aug_image, cv2.COLOR_RGB2BGR))

                    # 添加标签（相对路径保持一致）
                    new_rel_path = str(Path(rel_path).parent / new_filename)
                    aug_labels.append(f"{new_rel_path}\t{annotation}\n")

                    success_count += 1

                except Exception as e:
                    print(f"  增强 {image_path.name} 第 {i} 次失败: {str(e)}")
                    continue

            return success_count

        except Exception as e:
            print(f"  处理 {image_path.name} 失败: {str(e)}")
            return 0

    def augment_dataset(self, split: str = "train") -> Tuple[int, int]:
        """
        增强数据集

        Args:
            split: 数据集划分 (train/val)

        Returns:
            (原始数量, 增强后总数量)
        """
        if split == "train":
            images_dir = self.train_images_dir
            label_file = self.train_label
            output_dir = self.aug_train_images_dir
            output_label = self.aug_train_label
        else:
            images_dir = self.val_images_dir
            label_file = self.val_label
            output_dir = self.aug_val_images_dir
            output_label = self.aug_val_label

        # 创建输出目录
        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 读取标签文件
        with open(label_file, 'r', encoding='utf-8') as f:
            label_lines = f.readlines()

        print(f"\n开始增强 {split} 数据集，共 {len(label_lines)} 张图片...")

        aug_labels = []
        original_count = 0
        augmented_count = 0

        for label_line in tqdm.tqdm(label_lines):
            # 解析图片路径
            parts = label_line.strip().split('\t')
            if len(parts) < 2:
                continue

            rel_path = parts[0]
            image_path = images_dir / Path(rel_path).name

            if not image_path.exists():
                print(f"  警告: 图片不存在 {image_path}")
                continue

            # 复制原始图片和标签
            shutil.copy(image_path, output_dir / image_path.name)
            aug_labels.append(label_line)
            original_count += 1

            # 增强图片
            count = self.augment_single_image(image_path, label_line, output_dir, aug_labels)
            augmented_count += count

        # 保存增强后的标签文件
        with open(output_label, 'w', encoding='utf-8') as f:
            f.writelines(aug_labels)

        total_count = original_count + augmented_count

        print(f"\n{split} 数据集增强完成:")
        print(f"  原始数量: {original_count}")
        print(f"  增强数量: {augmented_count}")
        print(f"  总数量: {total_count}")
        print(f"  图片保存在: {output_dir}")
        print(f"  标签保存在: {output_label}")

        return original_count, total_count

    def augment_all(self) -> dict:
        """增强所有数据集"""
        # 验证数据集
        valid, errors = self.validate_dataset()
        if not valid:
            print("数据集验证失败:")
            for error in errors:
                print(f"  - {error}")
            return None

        print("=" * 60)
        print(f"OCR 数据增强器")
        print(f"模型类型: {self.model_type}")
        print(f"每张图片增强数量: {self.aug_count}")
        print("=" * 60)

        # 增强训练集
        train_orig, train_total = self.augment_dataset("train")

        # 增强验证集
        val_orig, val_total = self.augment_dataset("val")

        print("\n" + "=" * 60)
        print("数据增强完成!")
        print("=" * 60)
        print(f"训练集: {train_orig} -> {train_total} (增加 {train_total - train_orig})")
        print(f"验证集: {val_orig} -> {val_total} (增加 {val_total - val_orig})")
        print(f"总计: {train_orig + val_orig} -> {train_total + val_total} (增加 {train_total + val_total - train_orig - val_orig})")

        return {
            "train_original": train_orig,
            "train_total": train_total,
            "val_original": val_orig,
            "val_total": val_total,
        }


if __name__ == "__main__":
    # 测试
    augmentor = OCRDataAugmentor(
        dataset_root="./datasets/recognition",
        model_type="rec",
        aug_count=5
    )

    augmentor.augment_all()
