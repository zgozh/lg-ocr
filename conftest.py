"""pytest 根配置：将项目根目录加入 sys.path，使 tests/ 可直接导入根模块。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
