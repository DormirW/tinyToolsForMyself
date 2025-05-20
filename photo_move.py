import os
import shutil
import hashlib
from tqdm import tqdm
from datetime import datetime
from record_logging import log_operation_results


def _compute_file_hash(file_path: str, algorithm: str = "sha256") -> str:
    """计算文件的哈希值（支持大文件处理）"""
    hash_obj = hashlib.new(algorithm)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def _generate_target_path(
        source_root: str,
        target_root: str,
        preserve_dirs: list,
        src_path: str
) -> str:
    """统一生成目标路径（同时用于复制和校验阶段）"""
    relative_path = os.path.relpath(os.path.dirname(src_path), source_root)
    path_segments = os.path.normpath(relative_path).split(os.sep)

    # 匹配首个保留目录
    target_subdir = target_root
    for preserve_dir in preserve_dirs:
        if preserve_dir in path_segments:
            dir_index = path_segments.index(preserve_dir)
            target_subdir = os.path.join(target_root, *path_segments[dir_index:])
            break

    # 获取文件创建时间
    creation_time = os.path.getctime(src_path)
    # 转换为 datetime 对象
    creation_date = datetime.fromtimestamp(creation_time)
    # 格式化为 YYYYMMDD
    data_str = creation_date.strftime('%Y%m%d')
    target_subdir = target_subdir.replace("data_str", data_str)
    os.makedirs(target_subdir, exist_ok=True)

    return os.path.join(target_subdir, os.path.basename(src_path))


def enhanced_file_copy(
        source_root: str,
        target_root: str,
        preserve_dirs: list,
        file_suffix: str,
        overwrite: bool = False,
        hash_algorithm: str = "sha256"
) -> dict:
    """
    增强型文件复制函数，支持多目录结构保留和完整性校验

    :param source_root: 源目录根路径
    :param target_root: 目标目录根路径
    :param preserve_dirs: 需要保留结构的目录列表（如["D","F"]）
    :param file_suffix: 目标文件后缀（如".B"）
    :param overwrite: 是否覆盖已存在文件
    :param hash_algorithm: 哈希校验算法（md5/sha1/sha256）
    :return: 包含操作结果的字典
    """
    result = {
        "file_type": file_suffix,
        "total_files": 0,
        "copied": [],
        "skipped": [],
        "failed": [],
        "hash_mismatch": []
    }

    print(f"开始复制{file_suffix}文件...")

    # 预扫描所有符合条件的文件
    file_list = []
    for root, _, files in os.walk(source_root):
        for file in files:
            if file.endswith(file_suffix):
                file_list.append((root, file))
    result["total_files"] = len(file_list)

    # 带进度条的复制过程
    with tqdm(total=result["total_files"], desc="复制进度", unit="file") as pbar:
        for root, file in file_list:
            src_path = os.path.join(root, file)
            dest_path = _generate_target_path(
                source_root=source_root,
                target_root=target_root,
                preserve_dirs=preserve_dirs,
                src_path=src_path
            )

            try:
                # 文件存在性检查
                if os.path.exists(dest_path):
                    if overwrite:
                        shutil.copy2(src_path, dest_path)
                        result["copied"].append(src_path)
                    else:
                        result["skipped"].append(src_path)
                else:
                    shutil.copy2(src_path, dest_path)
                    result["copied"].append(src_path)
            except Exception as e:
                result["failed"].append((src_path, str(e)))

            pbar.update(1)

    # 哈希校验
    with tqdm(total=len(result["copied"]), desc="校验进度", unit="file") as pbar:
        for src_path in result["copied"]:
            dest_path = _generate_target_path(
                source_root=source_root,
                target_root=target_root,
                preserve_dirs=preserve_dirs,
                src_path=src_path
            )

            try:
                # 检验文件存在性
                if not os.path.exists(dest_path):
                    raise FileNotFoundError(f"目标文件不存在: {dest_path}")

                src_hash = _compute_file_hash(src_path, hash_algorithm)
                dest_hash = _compute_file_hash(dest_path, hash_algorithm)

                if src_hash != dest_hash:
                    result["hash_mismatch"].append(src_path)
            except Exception as e:
                result["failed"].append((src_path, f"Hash校验失败: {str(e)}"))

            pbar.update(1)

    return result


def result_dump(result: dict):
    """
    将操作结果输出
    """
    print(f"总文件数: {result['total_files']}")
    print(f"成功复制: {len(result['copied'])}")
    print(f"跳过文件: {len(result['skipped'])}")
    print(f"哈希不一致: {len(result['hash_mismatch'])}")
    print(f"失败文件: {len(result['failed'])}")


def nikon_z50_files_move():
    # 源目录
    src_directory = r"G:\DCIM"
    dev = "NIKON Z50"

    # 移动raw格式文件
    dst_directory = r"F:\Photos\NIKON_Z50\data_str\RAW"
    file_type = ".NEF"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=[],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    # 移动jpg格式文件
    dst_directory = r"F:\PHOTOS\NIKON_Z50\data_str\JPEG"
    file_type = ".JPG"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=["PANORAMA", "HYPERLAPSE"],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    # 移动mov格式文件
    dst_directory = r"F:\PHOTOS\NIKON_Z50\data_str\MOV"
    file_type = ".MOV"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=[],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    print("Nikon z50 files have been all done!")


def sony_a7c2_files_move():
    # 源目录
    src_directory = r"G:\DCIM"
    dev = "SONY A7C2"

    # 移动raw格式文件
    dst_directory = r"F:\Photos\SONY_A7C2\data_str\RAW"
    file_type = ".ARW"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=[],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    # 移动jpg格式文件
    dst_directory = r"F:\PHOTOS\SONY_A7C2\data_str\JPEG"
    file_type = ".JPG"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=["PANORAMA", "HYPERLAPSE"],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    # 源目录
    src_directory = r"G:\PRIVATE"

    # 移动mov格式文件
    dst_directory = r"F:\PHOTOS\SONY_A7C2\data_str\VIDEO"
    file_type = ".MP4"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=[],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    # 移动xml格式文件
    dst_directory = r"F:\PHOTOS\SONY_A7C2\data_str\XML"
    file_type = ".XML"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=[],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    print("Sony a7c2 files have been all done!")


def dji_pokect3_files_move():
    # 源目录
    src_directory = r"G:\DCIM"
    dev = "DJI POCKET3"

    # 移动raw格式文件
    dst_directory = r"F:\Photos\DJI_POCKET3\data_str\RAW"
    # file_type = ".NEF"
    # copy_files_by_type(src_directory, dst_directory, file_type)

    # 移动JPG格式文件
    dst_directory = r"F:\Photos\DJI_POCKET3\data_str\JPEG"
    file_type = ".JPG"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=["PANORAMA", "HYPERLAPSE"],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    # 移动LRF格式文件
    dst_directory = r"F:\Photos\DJI_POCKET3\data_str\PREVIEW"
    file_type = ".LRF"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=[],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    # 移动MP4格式文件
    dst_directory = r"F:\Photos\DJI_POCKET3\data_str\MOV"
    file_type = ".MP4"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=[],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    print("Dji pocket3 files have been all done!")


def dji_flip_files_move():
    # 源目录
    src_directory = r"G:\DCIM"
    dev = "DJI FLIP"

    # 移动MP4格式文件
    dst_directory = r"F:\Photos\DJI_FLIP\data_str\MOV"
    file_type = ".MP4"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=[],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    # 移动音频文件
    dst_directory = r"F:\Photos\DJI_FLIP\data_str\AUDIO"
    file_type = ".m4a"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=[],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    # 移动raw格式文件
    dst_directory = r"F:\Photos\DJI_FLIP\data_str\RAW"
    file_type = ".DNG"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=["PANORAMA", "HYPERLAPSE"],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    # 移动JPG格式文件
    dst_directory = r"F:\Photos\DJI_FLIP\data_str\JPEG"
    file_type = ".JPG"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=["PANORAMA", "HYPERLAPSE"],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    # 移动SRT格式文件
    dst_directory = r"F:\Photos\DJI_FLIP\data_str\SRT"
    file_type = ".SRT"
    r = enhanced_file_copy(
        source_root=src_directory,
        target_root=dst_directory,
        preserve_dirs=[],
        file_suffix=file_type,
        overwrite=False,
        hash_algorithm="sha256"
    )
    log_operation_results(dev, r)

    print("Dji flip files have been all done!")


if __name__ == "__main__":
    if os.path.exists(r"G:\NIKON_Z50_FLAG"):
        print(f"检测到nikon z50存储卡插入，开始处理文件...")
        nikon_z50_files_move()

    if os.path.exists(r"G:\SONY_A7C2_FLAG"):
        print(f"检测到sony a7c2存储卡插入，开始处理文件...")
        sony_a7c2_files_move()

    if os.path.exists(r"G:\DJI_POCKET3_FLAG"):
        print(f"检测到dji pocket3存储卡插入，开始处理文件...")
        dji_pokect3_files_move()

    if os.path.exists(r"G:\DJI_FLIP_FLAG"):
        print(f"检测到dji flip存储卡插入，开始处理文件...")
        dji_flip_files_move()

    os.system("pause")
