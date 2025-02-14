import os
import re

import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
import csv


def read_file_as_string(file_path: str, encoding: str = 'utf-8') -> str:
    """
    Read the content of a file and return it as a string.

    Parameters:
    file_path (str): The path to the file.
    encoding (str): The encoding of the file. Default is 'utf-8'.

    Returns:
    str: The content of the file as a string.
    """
    with open(file_path, 'r', encoding=encoding) as file:
        content = file.read()
    return content


def chinese_character_count(s: str) -> int:
    """
    Count the number of Chinese characters in a string.

    Parameters:
    s (str): The input string.

    Returns:
    int: The count of Chinese characters.
    """
    count = 0
    for char in s:
        if '\u4e00' <= char <= '\u9fff':
            count += 1
    return count


def get_webpage_content(url):
    try:
        # 使用requests库获取网页内容
        full_url = "http://www.5156edu.com" + url
        response = requests.get(full_url)
        response.raise_for_status()  # 如果响应状态码不是200，则抛出HTTPError异常

        # 手动设置编码为GB2312
        response.encoding = 'gb2312'

        # 使用BeautifulSoup解析网页
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.prettify()
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.exceptions.ConnectionError as conn_err:
        return f"Connection error occurred: {conn_err}"
    except requests.exceptions.Timeout as timeout_err:
        return f"Timeout error occurred: {timeout_err}"
    except requests.exceptions.RequestException as req_err:
        return f"An error occurred: {req_err}"


def extract_urls(s):
    # 使用正则表达式匹配所有的网址
    urls = re.findall(r'href="(.*?)"', s)
    return urls


def process_files(path, type_name, output_file):
    # 检查输出文件是否存在，决定写入模式
    mode = 'a' if os.path.exists(output_file) else 'w'

    # 遍历指定路径下的所有文件
    for filename in os.listdir(path):
        if filename.endswith('.txt'):
            file_path = os.path.join(path, filename)

            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            content = content.strip()  # 去除首尾空白
            content = content.replace(' ', '')  # 去除特殊空格
            # 创建要写入的数据
            data = {
                "type": type_name,
                "raw_content": content
            }

            # 将数据写入JSON文件
            with open(output_file, mode, encoding='utf-8') as outfile:
                json.dump(data, outfile, ensure_ascii=False)
                outfile.write('\n')  # 每条数据后添加换行，以便多次追加

            # 后续写入都使用追加模式
            mode = 'a'

    print(f"处理完成，结果已保存到 {output_file}")


def process_csv(input_file, type_name, output_file):
    # 检查输出文件是否存在，决定写入模式
    mode = 'a' if os.path.exists(output_file) else 'w'

    # 打开并读取CSV文件
    with open(input_file, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)

        # 遍历CSV文件的每一行
        for row in csv_reader:
            # 假设CSV文件只有一列，如果有多列，可能需要调整这里
            content = row[0] if row else ""
            content = content.strip()  # 去除首尾空白
            content = content.replace(' ', '')  # 去除特殊空格
            # 创建要写入的数据
            data = {
                "type": type_name,
                "raw_content": content
            }

            # 将数据写入JSON文件
            with open(output_file, mode, encoding='utf-8') as outfile:
                json.dump(data, outfile, ensure_ascii=False)
                outfile.write('\n')  # 每条数据后添加换行，以便多次追加

            # 后续写入都使用追加模式
            mode = 'a'

    print(f"处理完成，结果已保存到 {output_file}")


def multi_rows_csv_to_json(csv_file_path, json_file_path):
    # Initialize a list to store the data
    data_list = []

    # Open and read the CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # Extract the required columns
            required_data = {
                # 级别 音节 代表字
                "level": row["级别"],
                "grammar_item": row["语法项目"],
                "category": row["类别"],
                "sub_category": row["细目"],
                "content": row["语法内容"]
            }
            data_list.append(required_data)

    # Write the list to the JSON file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data_list, json_file, ensure_ascii=False, indent=4)

    print(f"Data from {csv_file_path} has been written to {json_file_path}")


def process_text_file(input_file, type_name, output_file):
    # 检查输出文件是否存在，决定写入模式
    mode = 'a' if os.path.exists(output_file) else 'w'

    article_count = 0
    current_article = []
    is_article = False

    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if article_count == 1000:
                print(f"已找到 {article_count} 篇文章，停止处理")
                break
            if line.startswith('<CHAPTER'):
                # 新文章的开始
                is_article = True
                current_article = []
            elif line == '</CHAPTER>':
                # 文章结束，保存文章
                if is_article and current_article:
                    article_content = ' '.join(current_article)
                    content = article_content.strip()  # 去除首尾空白
                    content = article_content.replace(' ', '')  # 去除特殊空格
                    char_count = chinese_character_count(content)
                    if char_count > 1800:
                        continue
                    content = content.replace('﻿', '')  # 去除特殊字符\
                    # print(f"文章长度：{char_count}")
                    data = {
                        "type": type_name,
                        "raw_content": content
                    }
                    with open(output_file, mode, encoding='utf-8') as outfile:
                        json.dump(data, outfile, ensure_ascii=False)
                        outfile.write('\n')

                    article_count += 1
                    mode = 'a'  # 确保后续写入使用追加模式
                is_article = False
                current_article = []
            elif is_article:
                # 文章内容，添加到当前文章
                current_article.append(line)

    print(f"处理完成，共找到 {article_count} 篇文章")
    print(f"结果已保存到 {output_file}")
    return article_count


def xls_to_json(xls_file_path, json_file_path):
    # Load the xls file
    df = pd.read_excel(xls_file_path, header=5)  # 5th row as header (0-indexed)

    # Select only the required columns
    df_selected = df[["汉字", "累计频率(%)"]]

    # Convert the DataFrame to a list of dictionaries
    data_list = df_selected.to_dict(orient='records')

    # Write the list to the JSON file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data_list, json_file, ensure_ascii=False, indent=4)

    print(f"Data from {xls_file_path} has been written to {json_file_path}")


def optimize_json_format(input_file, output_file):
    # 读取原始JSON文件
    with open(input_file, 'r', encoding='utf-8') as file:
        data = []
        for line in file:
            try:
                item = json.loads(line.strip())
                data.append(item)
            except json.JSONDecodeError:
                print(f"Warning: 跳过无效的JSON行: {line.strip()}")

    # 将优化后的数据写入新文件
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    print(f"JSON格式优化完成。优化后的文件保存为: {output_file}")
    print(f"共处理 {len(data)} 条数据。")


def process_abbre_txt_file(txt_file_path, json_file_path):
    # Initialize an empty dictionary to store the abbreviation and full form

    # Open and read the txt file
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            # Skip lines starting with 'n:'
            if line.startswith('n:'):
                continue

            # Split the line at ':' to separate abbreviation and full form
            split_line = line.split(':')
            if len(split_line) == 2:
                abbreviation = split_line[0].strip()
                full_form = split_line[1].strip()

                # Remove any non-Chinese characters from the full form
                full_form_cleaned = ''.join(filter(lambda char: '\u4e00' <= char <= '\u9fff', full_form))

                # Add the abbreviation and cleaned full form
                data = {
                    "abbreviation": abbreviation,
                    "full_form": full_form_cleaned
                }
                with open(json_file_path, 'a', encoding='utf-8') as outfile:
                    json.dump(data, outfile, ensure_ascii=False)
                    outfile.write('\n')

    print(f"Processed {txt_file_path} and wrote to {json_file_path}")


# Uncommenting the following line to run the main function
# main()

def load_newsela_doc(
        path=os.path.abspath(os.path.join(os.getcwd(), "..")) + r"\data\newsela\articles\\",
        nums=1, random_seed=10):
    # 读取path下的所有文件
    file_list = os.listdir(path)
    # 构造正则表达式，找到所有以“0.txt”结尾的文件名
    pattern = re.compile(r'.*0.txt')
    raw_file_list = list(filter(lambda x: pattern.match(x), file_list))
    # 拿到当前文件后面的4个文件（根据在file_list中的索引）
    doc_list = []
    for file in raw_file_list:
        index = file_list.index(file)
        temp_list = file_list[index:index + 5]
        # 检查temp_list中的文件名前缀是否一致
        prefix = file.split('-')[0]
        if len(temp_list) < 5:
            continue
        else:
            flag = 0
            for i in range(1, 5):
                if prefix != temp_list[i].split('-')[0]:
                    print("文件名前缀不一致！")
                    flag = 1
            if flag == 1:
                continue
        if len(temp_list) == 5:
            doc_list.append(temp_list)
    # 随机生成nums个随机数
    np.random.seed(random_seed)
    if nums > len(doc_list):
        nums = len(doc_list)
    random_index = np.random.randint(0, len(doc_list), nums)
    # 从list中取出对应的数据
    doc_list = np.array(doc_list)[random_index]
    # print(doc_list.shape)
    # print(doc_list)
    # 读取对应的文件内容
    content_list = []
    for i in range(len(doc_list)):
        temp_list = []
        for j in range(len(doc_list[i])):
            with open(path + doc_list[i][j], 'r', encoding='utf-8') as f:
                temp_list.append(f.read())
        content_list.append(temp_list)
    return doc_list, content_list


if __name__ == '__main__':
    pass
