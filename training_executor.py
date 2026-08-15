"""
训练执行器
启动训练进程、实时捕获日志、解析训练指标
"""
import os
import re
import subprocess
import threading
import queue
from pathlib import Path


class TrainingExecutor:
    """训练执行器"""

    def __init__(self, log_callback=None, metric_callback=None):
        """
        Args:
            log_callback: 日志回调函数 callback(log_text, log_type)
            metric_callback: 指标回调函数 callback(epoch, loss, acc, lr)
        """
        self.log_callback = log_callback
        self.metric_callback = metric_callback
        self.process = None
        self.is_running = False
        self.log_queue = queue.Queue()

    def start_training(self, config_path, gpu_id="0"):
        """
        启动训练

        Args:
            config_path: 配置文件路径
            gpu_id: GPU 设备 ID

        Returns:
            bool: 是否成功启动
        """
        if self.is_running:
            if self.log_callback:
                self.log_callback("训练已在运行中", "warning")
            return False

        # 检查配置文件
        if not os.path.exists(config_path):
            if self.log_callback:
                self.log_callback(f"配置文件不存在: {config_path}", "error")
            return False

        # 检查训练脚本
        train_script = Path(__file__).parent / "training" / "tools" / "train.py"
        if not train_script.exists():
            if self.log_callback:
                self.log_callback(f"训练脚本不存在: {train_script}", "error")
                self.log_callback("请先复制 PaddleOCR 训练模块到 training/ 目录", "error")
            return False

        # 构建训练命令
        cmd = [
            "python",
            str(train_script),
            "-c",
            config_path,
            "-o",
            f"Global.use_gpu=True",
            f"Global.device=gpu:{gpu_id}",
        ]

        if self.log_callback:
            self.log_callback(f"启动训练命令: {' '.join(cmd)}", "info")

        try:
            # 启动训练进程
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
            )

            self.is_running = True

            # 启动日志读取线程
            log_thread = threading.Thread(target=self._read_logs, daemon=True)
            log_thread.start()

            # 启动日志处理线程
            process_thread = threading.Thread(target=self._process_logs, daemon=True)
            process_thread.start()

            if self.log_callback:
                self.log_callback("训练已启动", "success")

            return True

        except Exception as e:
            if self.log_callback:
                self.log_callback(f"启动训练失败: {str(e)}", "error")
            self.is_running = False
            return False

    def stop_training(self):
        """停止训练"""
        if not self.is_running:
            if self.log_callback:
                self.log_callback("训练未在运行", "warning")
            return False

        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

            self.is_running = False

            if self.log_callback:
                self.log_callback("训练已停止", "info")

            return True

        return False

    def _read_logs(self):
        """读取训练日志（后台线程）"""
        if not self.process:
            return

        try:
            for line in iter(self.process.stdout.readline, ""):
                if not line:
                    break
                self.log_queue.put(line.strip())

            # 等待进程结束
            self.process.wait()
            self.is_running = False

            if self.log_callback:
                if self.process.returncode == 0:
                    self.log_callback("训练完成", "success")
                else:
                    self.log_callback(f"训练异常退出 (返回码: {self.process.returncode})", "error")

        except Exception as e:
            if self.log_callback:
                self.log_callback(f"读取日志失败: {str(e)}", "error")
            self.is_running = False

    def _process_logs(self):
        """处理训练日志（后台线程）"""
        # 正则表达式匹配训练日志
        # 示例: [2024/01/01 12:00:00] epoch: 1, iter: 100, loss: 0.5, acc: 0.95, lr: 0.001
        pattern = re.compile(
            r"epoch:\s*(\d+).*?loss:\s*([\d.]+).*?(?:acc|accuracy):\s*([\d.]+).*?lr:\s*([\d.e-]+)",
            re.IGNORECASE,
        )

        while self.is_running or not self.log_queue.empty():
            try:
                log_line = self.log_queue.get(timeout=0.5)

                # 输出日志
                if self.log_callback:
                    self.log_callback(log_line, "info")

                # 解析训练指标
                match = pattern.search(log_line)
                if match and self.metric_callback:
                    epoch = int(match.group(1))
                    loss = float(match.group(2))
                    acc = float(match.group(3))
                    lr = float(match.group(4))
                    self.metric_callback(epoch, loss, acc, lr)

            except queue.Empty:
                continue
            except Exception as e:
                if self.log_callback:
                    self.log_callback(f"处理日志失败: {str(e)}", "error")

    def is_training(self):
        """检查是否正在训练"""
        return self.is_running


if __name__ == "__main__":
    # 测试训练执行器
    def log_callback(text, log_type):
        print(f"[{log_type.upper()}] {text}")

    def metric_callback(epoch, loss, acc, lr):
        print(f"Epoch: {epoch}, Loss: {loss:.4f}, Acc: {acc:.4f}, LR: {lr:.6f}")

    executor = TrainingExecutor(log_callback=log_callback, metric_callback=metric_callback)

    # 启动训练
    config_path = "./training/configs/det/custom_config.yml"
    if executor.start_training(config_path, gpu_id="0"):
        print("训练已启动，按 Ctrl+C 停止...")
        try:
            while executor.is_training():
                import time

                time.sleep(1)
        except KeyboardInterrupt:
            print("\n停止训练...")
            executor.stop_training()
