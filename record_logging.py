import os
import logging
from datetime import datetime

# 创建日志目录（自动处理权限和路径）
log_dir = "logging"
os.makedirs(log_dir, exist_ok=True)
os.chmod(log_dir, 0o755)  # 设置可读写权限

# 生成日期格式文件名（避免非法字符）
current_date = datetime.now().strftime("%Y-%m-%d")  # 格式示例：2025-05-09
log_filename = os.path.join(log_dir, f"{current_date}.log")  # 输出路径：logging/2025-05-09.log

# 初始化日志记录器
logger = logging.getLogger("FileCopyLogger")
logger.setLevel(logging.INFO)  # 设置日志级别

# 配置日志格式（包含时间戳、操作类型和详情）
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"  # 日志行内的时间格式
)

# 创建文件处理器（追加模式）
file_handler = logging.FileHandler(
    filename=log_filename,
    mode='a',  # 追加写入模式
    encoding='utf-8'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 添加控制台输出
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def log_operation_results(dev: str, result: dict):
    # 记录汇总信息
    logger.info(
        f"设备: {dev} "
        f"{result['file_type']}类型文件操作完成 | 总数: {result['total_files']} "
        f"成功: {len(result['copied'])} "
        f"跳过: {len(result['skipped'])} "
        f"失败: {len(result['failed'])}"
    )

    # 记录失败详情（错误级别）
    for src_path, error in result["failed"]:
        logger.error(f"文件复制失败: {src_path} | 错误: {error}")

    # 记录哈希校验问题（警告级别）
    for src_path in result["hash_mismatch"]:
        logger.warning(f"哈希校验失败: {src_path}")