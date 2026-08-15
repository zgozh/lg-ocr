"""
训练配置生成器
根据模型类型和用户参数生成 PaddleOCR 训练配置文件
"""
import os
import yaml
from pathlib import Path


class TrainingConfigGenerator:
    """训练配置生成器"""

    def __init__(self):
        self.config_templates_dir = Path(__file__).parent / "training" / "configs"

    def generate_det_config(
        self,
        train_data_dir,
        train_label,
        val_data_dir,
        val_label,
        pretrained_model=None,
        epoch_num=500,
        batch_size=8,
        learning_rate=0.001,
        save_model_dir="./trained_models/det",
    ):
        """生成检测模型配置"""
        config = {
            "Global": {
                "use_gpu": True,
                "epoch_num": epoch_num,
                "log_smooth_window": 20,
                "print_batch_step": 10,
                "save_model_dir": save_model_dir,
                "save_epoch_step": 50,
                "eval_batch_step": [0, 2000],
                "cal_metric_during_train": False,
                "pretrained_model": pretrained_model if pretrained_model else None,
                "checkpoints": None,
                "save_inference_dir": None,
                "use_visualdl": True,
                "infer_img": None,
                "save_res_path": "./output/det_results.txt",
            },
            "Architecture": {
                "model_type": "det",
                "algorithm": "DB",
                "Transform": None,
                "Backbone": {
                    "name": "ResNet",
                    "layers": 50,
                    "dcn_stage": [False, True, True, True],
                },
                "Neck": {"name": "DBFPN", "out_channels": 256},
                "Head": {"name": "DBHead", "k": 50},
            },
            "Loss": {"name": "DBLoss", "balance_loss": True, "main_loss_type": "DiceLoss", "alpha": 5, "beta": 10, "ohem_ratio": 3},
            "Optimizer": {
                "name": "Adam",
                "beta1": 0.9,
                "beta2": 0.999,
                "lr": {"name": "Cosine", "learning_rate": learning_rate, "warmup_epoch": 2},
                "regularizer": {"name": "L2", "factor": 0.0001},
            },
            "PostProcess": {"name": "DBPostProcess", "thresh": 0.3, "box_thresh": 0.6, "max_candidates": 1000, "unclip_ratio": 1.5},
            "Metric": {"name": "DetMetric", "main_indicator": "hmean"},
            "Train": {
                "dataset": {
                    "name": "SimpleDataSet",
                    "data_dir": train_data_dir,
                    "label_file_list": [train_label],
                    "ratio_list": [1.0],
                    "transforms": [
                        {"DecodeImage": {"img_mode": "BGR", "channel_first": False}},
                        {"DetLabelEncode": None},
                        {"IaaAugment": {"augmenter_args": [{"type": "Fliplr", "args": {"p": 0.5}}]}},
                        {"EastRandomCropData": {"size": [640, 640], "max_tries": 50, "keep_ratio": True}},
                        {"MakeBorderMap": {"shrink_ratio": 0.4, "thresh_min": 0.3, "thresh_max": 0.7}},
                        {"MakeShrinkMap": {"shrink_ratio": 0.4, "min_text_size": 8}},
                        {"NormalizeImage": {"scale": "1./255.", "mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225], "order": "hwc"}},
                        {"ToCHWImage": None},
                        {"KeepKeys": {"keep_keys": ["image", "threshold_map", "threshold_mask", "shrink_map", "shrink_mask"]}},
                    ],
                },
                "loader": {"shuffle": True, "drop_last": False, "batch_size_per_card": batch_size, "num_workers": 4},
            },
            "Eval": {
                "dataset": {
                    "name": "SimpleDataSet",
                    "data_dir": val_data_dir,
                    "label_file_list": [val_label],
                    "transforms": [
                        {"DecodeImage": {"img_mode": "BGR", "channel_first": False}},
                        {"DetLabelEncode": None},
                        {"DetResizeForTest": None},
                        {"NormalizeImage": {"scale": "1./255.", "mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225], "order": "hwc"}},
                        {"ToCHWImage": None},
                        {"KeepKeys": {"keep_keys": ["image", "shape", "polys", "ignore_tags"]}},
                    ],
                },
                "loader": {"shuffle": False, "drop_last": False, "batch_size_per_card": 1, "num_workers": 2},
            },
        }

        return config

    def generate_rec_config(
        self,
        train_data_dir,
        train_label,
        val_data_dir,
        val_label,
        pretrained_model=None,
        epoch_num=500,
        batch_size=128,
        learning_rate=0.001,
        save_model_dir="./trained_models/rec",
        character_dict_path=None,
    ):
        """生成识别模型配置"""
        # 使用绝对路径的字符字典
        if character_dict_path is None:
            import os
            character_dict_path = os.path.abspath("./training/ppocr/utils/ppocr_keys_v1.txt")

        config = {
            "Global": {
                "use_gpu": True,
                "epoch_num": epoch_num,
                "log_smooth_window": 20,
                "print_batch_step": 10,
                "save_model_dir": save_model_dir,
                "save_epoch_step": 50,
                "eval_batch_step": [0, 2000],
                "cal_metric_during_train": True,
                "pretrained_model": pretrained_model if pretrained_model else None,
                "checkpoints": None,
                "save_inference_dir": None,
                "use_visualdl": True,
                "infer_img": None,
                "character_dict_path": character_dict_path,
                "max_text_length": 25,
                "infer_mode": False,
                "use_space_char": True,
                "save_res_path": "./output/rec_results.txt",
            },
            "Architecture": {
                "model_type": "rec",
                "algorithm": "SVTR_LCNet",
                "Transform": None,
                "Backbone": {"name": "PPLCNetV3", "scale": 0.95},
                "Neck": {
                    "name": "SequenceEncoder",
                    "encoder_type": "svtr",
                    "dims": 120,
                    "depth": 2,
                    "hidden_dims": 120,
                    "use_guide": True,
                },
                "Head": {"name": "CTCHead", "fc_decay": 0.00001},
            },
            "Loss": {"name": "CTCLoss"},
            "Optimizer": {
                "name": "AdamW",
                "beta1": 0.9,
                "beta2": 0.999,
                "epsilon": 1.0e-8,
                "weight_decay": 0.05,
                "no_weight_decay_name": "bias LayerNorm.bias LayerNorm.weight",
                "one_dim_param_no_weight_decay": True,
                "lr": {"name": "Cosine", "learning_rate": learning_rate, "warmup_epoch": 2},
            },
            "PostProcess": {"name": "CTCLabelDecode"},
            "Metric": {"name": "RecMetric", "main_indicator": "acc"},
            "Train": {
                "dataset": {
                    "name": "SimpleDataSet",
                    "data_dir": train_data_dir,
                    "label_file_list": [train_label],
                    "ratio_list": [1.0],
                    "transforms": [
                        {"DecodeImage": {"img_mode": "BGR", "channel_first": False}},
                        {"RecAug": None},
                        {"CTCLabelEncode": None},
                        {"RecResizeImg": {"image_shape": [3, 48, 320]}},
                        {"KeepKeys": {"keep_keys": ["image", "label", "length"]}},
                    ],
                },
                "loader": {"shuffle": True, "drop_last": True, "batch_size_per_card": batch_size, "num_workers": 4},
            },
            "Eval": {
                "dataset": {
                    "name": "SimpleDataSet",
                    "data_dir": val_data_dir,
                    "label_file_list": [val_label],
                    "transforms": [
                        {"DecodeImage": {"img_mode": "BGR", "channel_first": False}},
                        {"CTCLabelEncode": None},
                        {"RecResizeImg": {"image_shape": [3, 48, 320]}},
                        {"KeepKeys": {"keep_keys": ["image", "label", "length"]}},
                    ],
                },
                "loader": {"shuffle": False, "drop_last": False, "batch_size_per_card": 64, "num_workers": 2},
            },
        }

        return config

    def generate_table_config(
        self,
        train_data_dir,
        train_label,
        val_data_dir,
        val_label,
        pretrained_model=None,
        epoch_num=400,
        batch_size=32,
        learning_rate=0.001,
        save_model_dir="./trained_models/table",
    ):
        """生成表格识别模型配置"""
        # 使用绝对路径的字符字典
        import os
        character_dict_path = os.path.abspath("./training/ppocr/utils/dict/table_structure_dict.txt")

        config = {
            "Global": {
                "use_gpu": True,
                "epoch_num": epoch_num,
                "log_smooth_window": 20,
                "print_batch_step": 10,
                "save_model_dir": save_model_dir,
                "save_epoch_step": 50,
                "eval_batch_step": [0, 2000],
                "cal_metric_during_train": True,
                "pretrained_model": pretrained_model if pretrained_model else None,
                "checkpoints": None,
                "save_inference_dir": None,
                "use_visualdl": True,
                "infer_img": None,
                "save_res_path": "./output/table_results.txt",
                "max_text_length": 500,
                "max_elem_length": 800,
                "max_cell_num": 500,
                "character_dict_path": character_dict_path,
            },
            "Architecture": {
                "model_type": "table",
                "algorithm": "SLANet",
                "Backbone": {"name": "PPLCNet", "scale": 1.0},
                "Neck": {"name": "CSPPAN", "out_channels": 96},
                "Head": {
                    "name": "SLAHead",
                    "hidden_size": 256,
                    "max_text_length": 500,
                    "loc_reg_num": 4,
                },
            },
            "Loss": {"name": "SLALoss"},
            "Optimizer": {
                "name": "Adam",
                "beta1": 0.9,
                "beta2": 0.999,
                "lr": {"name": "Cosine", "learning_rate": learning_rate, "warmup_epoch": 2},
                "regularizer": {"name": "L2", "factor": 0.0},
            },
            "PostProcess": {"name": "TableLabelDecode"},
            "Metric": {"name": "TableMetric", "main_indicator": "acc"},
            "Train": {
                "dataset": {
                    "name": "PubTabDataSet",
                    "data_dir": train_data_dir,
                    "label_file_list": [train_label],
                    "transforms": [
                        {"DecodeImage": {"img_mode": "BGR", "channel_first": False}},
                        {"TableLabelEncode": None},
                        {"TableBoxEncode": None},
                        {"ResizeTableImage": {"max_len": 488}},
                        {"NormalizeImage": {"scale": "1./255.", "mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225], "order": "hwc"}},
                        {"PaddingTableImage": {"size": [488, 488]}},
                        {"ToCHWImage": None},
                        {"KeepKeys": {"keep_keys": ["image", "structure", "bboxes", "bbox_masks", "shape"]}},
                    ],
                },
                "loader": {"shuffle": True, "drop_last": True, "batch_size_per_card": batch_size, "num_workers": 4},
            },
            "Eval": {
                "dataset": {
                    "name": "PubTabDataSet",
                    "data_dir": val_data_dir,
                    "label_file_list": [val_label],
                    "transforms": [
                        {"DecodeImage": {"img_mode": "BGR", "channel_first": False}},
                        {"TableLabelEncode": None},
                        {"TableBoxEncode": None},
                        {"ResizeTableImage": {"max_len": 488}},
                        {"NormalizeImage": {"scale": "1./255.", "mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225], "order": "hwc"}},
                        {"PaddingTableImage": {"size": [488, 488]}},
                        {"ToCHWImage": None},
                        {"KeepKeys": {"keep_keys": ["image", "structure", "bboxes", "bbox_masks", "shape"]}},
                    ],
                },
                "loader": {"shuffle": False, "drop_last": False, "batch_size_per_card": 16, "num_workers": 2},
            },
        }

        return config

    def save_config(self, config, output_path):
        """保存配置到 YAML 文件"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        return output_path

    def generate_and_save(self, model_type, params, output_path):
        """生成并保存配置文件"""
        if model_type == "det":
            config = self.generate_det_config(**params)
        elif model_type == "rec":
            config = self.generate_rec_config(**params)
        elif model_type == "table":
            config = self.generate_table_config(**params)
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")

        return self.save_config(config, output_path)


if __name__ == "__main__":
    # 测试配置生成
    generator = TrainingConfigGenerator()

    # 生成检测模型配置
    det_params = {
        "train_data_dir": "./datasets/detection/train_images",
        "train_label": "./datasets/detection/train.txt",
        "val_data_dir": "./datasets/detection/val_images",
        "val_label": "./datasets/detection/val.txt",
        "epoch_num": 500,
        "batch_size": 8,
        "learning_rate": 0.001,
    }
    det_config_path = generator.generate_and_save("det", det_params, "./training/configs/det/custom_config.yml")
    print(f"检测模型配置已生成: {det_config_path}")

    # 生成识别模型配置
    rec_params = {
        "train_data_dir": "./datasets/recognition/train_images",
        "train_label": "./datasets/recognition/train.txt",
        "val_data_dir": "./datasets/recognition/val_images",
        "val_label": "./datasets/recognition/val.txt",
        "epoch_num": 500,
        "batch_size": 128,
        "learning_rate": 0.001,
    }
    rec_config_path = generator.generate_and_save("rec", rec_params, "./training/configs/rec/custom_config.yml")
    print(f"识别模型配置已生成: {rec_config_path}")

    # 生成表格模型配置
    table_params = {
        "train_data_dir": "./datasets/table/train_images",
        "train_label": "./datasets/table/train.txt",
        "val_data_dir": "./datasets/table/val_images",
        "val_label": "./datasets/table/val.txt",
        "epoch_num": 400,
        "batch_size": 32,
        "learning_rate": 0.001,
    }
    table_config_path = generator.generate_and_save("table", table_params, "./training/configs/table/custom_config.yml")
    print(f"表格模型配置已生成: {table_config_path}")
