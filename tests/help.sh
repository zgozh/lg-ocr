# # 安装torch
# pip install torch torchvision --index-url https://download.pytorch.org/whl/cu129
# # 卸载才能正常使用paddle
# pip uninstall torch torchvision

# 安装paddle-gpu
python -m pip install paddlepaddle-gpu==3.1.1 -i https://www.paddlepaddle.org.cn/packages/stable/cu129/
# # 安装paddle-cpu
# python -m pip install paddlepaddle==3.1.1
# 安装paddleocr
python -m pip install "paddleocr[all]"
# 
pip install -r requirements.txt
# 环境
conda activate ppocr

# 文本识别
## 训练
python tools/train.py -c configs/rec/PP-OCRv5/PP-OCRv5_server_rec.yml -o Global.pretrained_model=./pdparams/PP-OCRv5_server_rec_pretrained.pdparams
## 测试集评估
python tools/eval.py -c configs/rec/PP-OCRv5/PP-OCRv5_server_rec.yml -o Global.pretrained_model=output/PP-OCRv5_server_rec/latest.pdparams
## 模型导出
python tools/export_model.py -c configs/rec/PP-OCRv5/PP-OCRv5_server_rec.yml -o Global.pretrained_model=output/PP-OCRv5_server_rec/latest.pdparams Global.save_inference_dir="./infer/PP-OCRv5_server_rec_infer/"

# 文本检测
## 训练
python tools/train.py -c configs/det/PP-OCRv5/PP-OCRv5_server_det.yml -o Global.pretrained_model=./pdparams/PP-OCRv5_server_det_pretrained.pdparams
## 测试集评估
python tools/eval.py -c configs/det/PP-OCRv5/PP-OCRv5_server_det.yml -o Global.pretrained_model=output/PP-OCRv5_server_det/latest.pdparams
## 模型导出
python tools/export_model.py -c configs/det/PP-OCRv5/PP-OCRv5_server_det.yml -o Global.pretrained_model=output/PP-OCRv5_server_det/latest.pdparams Global.save_inference_dir="./infer/PP-OCRv5_server_det_infer/"

# 表格识别 SLANeXt_wired
## 训练
python tools/train.py -c configs/table/SLANeXt_wired.yml -o Global.pretrained_model=./pdparams/SLANeXt_wired_pretrained.pdparams
## 测试集评估
python tools/eval.py -c configs/table/SLANeXt_wired.yml -o Global.pretrained_model=output/SLANeXt_wired/latest.pdparams
## 模型导出
python tools/export_model.py -c configs/table/SLANeXt_wired.yml -o Global.pretrained_model=output/SLANeXt_wired/latest.pdparams Global.save_inference_dir="./infer/SLANeXt_wired_infer/"


# # 表格识别 SLANeXt_wireless
# ## 训练
# python tools/train.py -c configs/table/SLANeXt_wireless.yml -o Global.pretrained_model=./pdparams/SLANeXt_wireless_pretrained.pdparams
# ## 测试集评估
# python tools/eval.py -c configs/table/SLANeXt_wireless.yml -o Global.pretrained_model=output/SLANeXt_wireless/latest.pdparams
# ## 模型导出
# python tools/export_model.py -c configs/table/SLANeXt_wireless.yml -o Global.pretrained_model=output/SLANeXt_wireless/latest.pdparams Global.save_inference_dir="./infer/SLANeXt_wireless_infer/"

# # 表格识别 SLANet_plus
# ## 训练
# python tools/train.py -c configs/table/SLANet_plus.yml -o Global.pretrained_model=./pdparams/SLANet_plus_pretrained.pdparams
# ## 测试集评估
# python tools/eval.py -c configs/table/SLANet_plus.yml -o Global.pretrained_model=output/SLANet_plus/latest.pdparams
# ## 模型导出
# python tools/export_model.py -c configs/table/SLANet_plus.yml -o Global.pretrained_model=output/SLANet_plus/latest.pdparams Global.save_inference_dir="./infer/SLANet_plus_infer/"
