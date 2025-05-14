import os
import piexif
from collections import defaultdict
import csv
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, LogLocator, MaxNLocator
import mplcursors
import pandas as pd


def get_jpg_files(root_dir):
    jpg_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith('.jpg'):
                jpg_files.append(os.path.join(root, file))
    return jpg_files


def extract_focal_lengths(file_paths):
    focal_data = defaultdict(int)
    for path in file_paths:
        try:
            exif_dict = piexif.load(path)
            exif_tags = exif_dict.get('Exif', {})

            # 提取实际焦距（单位：mm）
            focal_pair = exif_tags.get(piexif.ExifIFD.FocalLength, (0, 1))
            focal = focal_pair[0] / focal_pair[1] if focal_pair[1] != 0 else 0

            # 优先使用等效35mm焦距（若存在）
            focal_35mm = exif_tags.get(piexif.ExifIFD.FocalLengthIn35mmFilm)
            if focal_35mm:
                focal = focal_35mm

            if focal > 0:
                focal_data[round(focal, 1)] += 1  # 保留一位小数分组
        except Exception as e:
            print(f"Error processing {path}: {e}")
    return focal_data


def save_to_csv(data, output_path):
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Focal Length (mm)', 'Count'])
        for focal, count in sorted(data.items()):
            writer.writerow([focal, count])


def plot_distribution(focal_data, output_image, log_scale=False, interactive=True):
    """绘制带防重叠坐标的焦段分布图

    Parameters:
        focal_data (dict): 焦距统计字典 {焦距(mm): 数量}
        output_image (str): 输出图片路径
        log_scale (bool): 是否启用Y轴对数刻度(默认False)
        interactive (bool): 是否启用交互式提示(默认True)
    """
    # 展开原始数据点
    focals = []
    for focal, count in focal_data.items():
        focals.extend([focal] * count)

    # 创建画布
    plt.figure(figsize=(16, 8))  # 增大画布宽度[3,4](@ref)
    ax = plt.gca()

    # 绘制直方图
    n, bins, patches = plt.hist(
        focals,
        bins=50,
        edgecolor='white',
        alpha=0.7,
        histtype='stepfilled'
    )

    # 对数坐标轴设置
    if log_scale:
        ax.set_yscale('log')
        ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=15))
        ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=(0.2, 0.4, 0.6, 0.8)))
    else:
        ax.yaxis.set_major_locator(MaxNLocator(nbins=10))  # 限制Y轴刻度数量[3](@ref)
        ax.yaxis.set_minor_locator(MultipleLocator(1))

    # X轴防重叠优化
    ax.xaxis.set_major_locator(MaxNLocator(nbins=20))  # 智能控制刻度数量[3](@ref)
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    plt.xticks(
        rotation=45,
        ha='right',
        fontsize=10,
        fontweight='light'  # 细体字减少视觉拥挤[4,7](@ref)
    )

    # 格式美化
    plt.style.use('seaborn-v0_8')
    plt.rcParams.update({
        'font.family': 'Arial',
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'xtick.major.pad': 12  # 增加标签与轴线间距[7](@ref)
    })

    # 标签设置
    plt.title('Focal Length Distribution of Nikon Z50', fontsize=14, pad=20)
    plt.xlabel('Focal Length (mm)', fontsize=12, labelpad=15)  # 增加标签偏移[7](@ref)
    plt.ylabel('Image Count (log scale)' if log_scale else 'Image Count',
               fontsize=12, labelpad=10)

    # 网格增强
    ax.grid(which='major', axis='both', linestyle='--', alpha=0.7)
    ax.grid(which='minor', axis='x', linestyle=':', alpha=0.4)

    # 动态布局优化
    plt.tight_layout(pad=3)  # 增加边距防止标签截断[1,2](@ref)

    # 交互式数据提示
    if interactive:
        cursor = mplcursors.cursor(patches, hover=True)

        @cursor.connect("add")
        def on_add(sel):
            sel.annotation.set(
                text=f"Focal: {bins[sel.target.index]:.1f}mm\n"
                     f"Count: {n[sel.target.index]:.0f}",
                bbox=dict(
                    boxstyle="round,pad=0.5",
                    fc="white",
                    ec="gray",
                    lw=1,
                    alpha=0.9
                ),
                position=(50, 30)  # 固定提示框位置[7](@ref)
            )
            sel.annotation.arrowprops = None

    plt.savefig(output_image, dpi=300, bbox_inches='tight')
    plt.close()


# 从csv文件中读出焦距数据
def read_focal_data_from_csv(file_path):
    df = pd.read_csv(file_path)
    focal_data = {row['Focal Length (mm)']: row['Count'] for _, row in df.iterrows()}
    return focal_data


if __name__ == "__main__":
    # 主程序
    root_dir = r"F:\Photos\NIKON_Z50"
    output_csv = r'.\statistics\focal_stats.csv'
    output_plot = r'.\statistics\focal_distribution.png'

    # 执行流程
    # jpg_files = get_jpg_files(root_dir)
    # focal_stats = extract_focal_lengths(jpg_files)
    # save_to_csv(focal_stats, output_csv)
    # print(f"Focal length statistics saved to {output_csv}")
    # 读取csv数据
    # focal_stats = read_focal_data_from_csv(output_csv)
    df = pd.read_csv(output_csv)
    df['Focal Length (mm)'] = df['Focal Length (mm)'].astype(float)
    df['Count'] = df['Count'].astype(int)

    # 2. 数据转换
    focal_stats = df.set_index('Focal Length (mm)')['Count'].to_dict()
    # 生成标准线性坐标图
    plot_distribution(focal_stats, r'.\statistics\linear_plot.png',
                      log_scale=False, interactive=True)

    # 生成对数坐标图
    plot_distribution(focal_stats, r'.\statistics\log_plot.png',
                      log_scale=True, interactive=True)
