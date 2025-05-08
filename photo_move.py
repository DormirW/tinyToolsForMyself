import os
import shutil
from datetime import datetime


def copy_files_by_type(src_dir, dst_dir, file_extension):
    """
    将指定路径中的指定类型文件复制到目标路径。
    如果目标路径不存在，则自动创建。

    :param src_dir: 源目录路径
    :param dst_dir: 目标目录路径
    :param file_extension: 文件扩展名（如 '.txt' 或 '.jpg'）
    """

    cnt = 0

    # 遍历源目录及其子目录
    for root, _, files in os.walk(src_dir):
        for file in files:
            # 检查文件扩展名
            if file.endswith(file_extension):
                src_file_path = os.path.join(root, file)

                # 获取文件创建时间
                creation_time = os.path.getctime(src_file_path)
                # 转换为 datetime 对象
                creation_date = datetime.fromtimestamp(creation_time)
                # 格式化为 YYYYMMDD
                data_str = creation_date.strftime('%Y%m%d')
                dst_str = dst_dir.replace("data_str", data_str)
                dst_file_path = os.path.join(dst_str, file)

                # 确保目标目录存在
                if not os.path.exists(dst_str):
                    os.makedirs(dst_str)

                if os.path.exists(dst_file_path):
                    print(f"文件已存在，跳过: {dst_file_path}")
                    continue

                # 复制文件
                shutil.copy2(src_file_path, dst_file_path)
                cnt += 1

    print(f"{file_extension}类型文件已移动： {src_dir} -> {dst_dir}, 共{cnt}项")


def nikon_z50_files_move():
    # 源目录
    src_directory = r"G:\DCIM"

    # 移动raw格式文件
    dst_directory = r"F:\Photos\NIKON_Z50\data_str\RAW"
    file_type = ".NEF"
    copy_files_by_type(src_directory, dst_directory, file_type)

    # 移动jpg格式文件
    dst_directory = r"F:\PHOTOS\NIKON_Z50\data_str\JPEG"
    file_type = ".JPG"
    copy_files_by_type(src_directory, dst_directory, file_type)

    # 移动mov格式文件
    dst_directory = r"F:\PHOTOS\NIKON_Z50\data_str\MOV"
    file_type = ".MOV"
    copy_files_by_type(src_directory, dst_directory, file_type)

    print("Nikon z50 files have been all done")


def dji_pokect3_files_move():
    # 源目录
    src_directory = r"G:\DCIM"

    # 移动raw格式文件
    # dst_directory = r"F:\Photos\DJI_POCKET3\data_str\RAW"
    # file_type = ".NEF"
    # copy_files_by_type(src_directory, dst_directory, file_type)

    # 移动JPG格式文件
    dst_directory = r"F:\Photos\DJI_POCKET3\data_str\JPEG"
    file_type = ".JPG"
    copy_files_by_type(src_directory, dst_directory, file_type)

    # 移动LRF格式文件
    dst_directory = r"F:\Photos\DJI_POCKET3\data_str\PREVIEW"
    file_type = ".LRF"
    copy_files_by_type(src_directory, dst_directory, file_type)

    # 移动MP4格式文件
    dst_directory = r"F:\Photos\DJI_POCKET3\data_str\MOV"
    file_type = ".MP4"
    copy_files_by_type(src_directory, dst_directory, file_type)

    print("Dji pocket3 files have been all done")


if __name__ == "__main__":
    if os.path.exists(r"G:\NIKON_Z50_FLAG"):
        print(f"检测到nikon z50存储卡插入，开始处理文件...")
        nikon_z50_files_move()

    if os.path.exists(r"G:\DJI_POCKET3_FLAG"):
        print(f"检测到dji pocket3存储卡插入，开始处理文件...")
        dji_pokect3_files_move()
