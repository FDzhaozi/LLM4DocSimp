import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde

from Utiles.preprocess import load_newsela_doc, read_file_as_string
# from matplotlib import font_manager
# font_path = 'C:\Windows\Fonts\simsunb.ttf'  # 替换为你的字体文件路径
# font_manager.fontManager.addfont(font_path)
plt.rcParams['font.family'] = ['SimHei']  # 设置字体为黑体

def calculate_compression_ratio(original_texts, simplified_texts):
    """
    Calculate the compression ratio for a list of original and simplified text pairs.

    Parameters:
    - original_texts: List of strings, representing the original texts.
    - simplified_texts: List of strings, representing the simplified texts.

    Returns:
    - List of compression ratios.
    """
    ratios = []
    for original, simplified in zip(original_texts, simplified_texts):
        original_length = len(original)
        simplified_length = len(simplified)
        ratio = simplified_length / original_length
        ratios.append(ratio)
    return ratios


def plot_compression_ratios(ratios):
    """
    Plot the distribution of compression ratios using kernel density estimation.

    Parameters:
    - ratios: List of compression ratios.
    """
    # Calculate the density
    density = gaussian_kde(ratios)
    xs = np.linspace(0, 1, 200)
    density.covariance_factor = lambda: .25
    density._compute_covariance()

    # Plotting
    plt.figure(figsize=(8, 6))
    plt.plot(xs, density(xs))
    plt.title('MDDS', fontsize=18)
    plt.xlabel('压缩比', fontsize=16)
    plt.ylabel('概率密度', fontsize=16)
    plt.grid(True)
    plt.savefig('mdds_compression_ratios.png')
    plt.show()



# Example usage
# 示例数据集
# original_texts_example = [
#     "This is an example of a longer text that needs to be simplified.",
#     "Another example of a text that will be made simpler.",
#     "Here is a third example, which is quite long and complex.",
#     "Short text.",
#     "A longer text that will be reduced in length significantly."
# ]
#
# simplified_texts_example = [
#     "This is a short version of the text.",
#     "Another simple text.",
#     "Third example, made simpler.",
#     "Short.",
#     "Much shorter version."
# ]
#
# # 计算压缩比率
# ratios_example = calculate_compression_ratio(original_texts_example, simplified_texts_example)
#
# # 绘制压缩比率分布图
# plot_compression_ratios(ratios_example)

if __name__ == '__main__':
    # path = r"D:\Dataset\newsela_share_2020\newsela_share_2020\documents\articles\\"
    # doc_list, content_list = load_newsela_doc(path, nums=2000)
    # raw_doc_list = []
    # simplified_doc_list = []
    # for doc_content in content_list:
    #     raw_doc = doc_content[0]
    #     simplified_doc = doc_content[-1]
    #     raw_doc_list.append(raw_doc)
    #     simplified_doc_list.append(simplified_doc)
    #
    # ratios = calculate_compression_ratio(raw_doc_list, simplified_doc_list)
    # plot_compression_ratios(ratios)

    path = r"../Output_Docs/"
    raw_doc_list = []
    simplified_doc_list = []
    for subdir, dirs, files in os.walk(path):
        for dir_name in dirs:
            # 检查是否存在名为"ver3"的子文件夹
            if dir_name == "ver3":
                raw_path = os.path.join(subdir, "raw.txt")
                ver3_path = os.path.join(subdir, dir_name, "ver3_char_word_sent_para.txt")

                # 读取raw.txt文件
                raw_doc = read_file_as_string(raw_path)

                # 读取ver3_char_word_sent_para.txt文件
                simplified_doc = read_file_as_string(ver3_path)

                raw_doc_list.append(raw_doc)
                simplified_doc_list.append(simplified_doc)

    ratios = calculate_compression_ratio(raw_doc_list, simplified_doc_list)
    plot_compression_ratios(ratios)


