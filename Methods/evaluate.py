import os
import random
import re

from Methods.pipeline import full_pipeline
from Utiles.preprocess import read_file_as_string


def seg_chapter(text, delimiter="\n\n"):
    text_list = text.split(delimiter)
    # 删除空白片段
    text_list = [seg for seg in text_list if seg.strip()]
    return text_list


def seg_alis(text):
    # Split the text by '\n'
    segments = text.split('\n')
    # 删除空白片段
    segments = [seg for seg in segments if seg.strip()]

    # Filter out segments that contain both "小" and "说"
    filtered_segments = [seg for seg in segments if not ("小" in seg and "说" in seg)]

    chapters = []
    current_chapter = []

    for seg in filtered_segments:
        # Check if the segment contains both 'w' (case-insensitive) and '.'
        if any(char in seg for char in ['w', 'W']):
            # If current chapter has content, add it to the list of chapters
            if current_chapter:
                chapters.append('\n'.join(current_chapter))
                current_chapter = []
        else:
            current_chapter.append(seg)

    # Add the last chapter if it has content
    if current_chapter:
        chapters.append('\n'.join(current_chapter))

    return chapters


def del_none_rows(text):
    text_list = text.split("\n")
    text_list = [seg for seg in text_list if seg.strip()]
    text = "\n".join(text_list)
    return text


def start_evl_pipeline(base_path):
    # 获取所有子文件夹列表
    subfolders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]

    # 按照数字序号排序子文件夹
    subfolders.sort(key=lambda x: int(x.split('-')[0]))

    # 逐个处理每个子文件夹
    for folder in subfolders:
        # 解析子文件夹的标题
        num = folder.split('-', 1)[0]
        title = folder.split('-', 1)[1]

        # 构建子文件夹的完整路径
        folder_path = os.path.join(base_path, folder)

        # 初始化变量
        original_text = ''
        simplified_text_1 = ''
        simplified_text_2 = ''
        simplified_text_3 = ''

        # 读取每个文件的内容
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if filename == '原著-白话.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    original_text = file.read()
            elif filename == '简化一.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    simplified_text_1 = file.read()
            elif filename == '简化二.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    simplified_text_2 = file.read()
            elif filename == '简化三.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    simplified_text_3 = file.read()
        # # 输出变量内容或进行进一步处理
        # print(f"Title: {title}")
        # print(f"Original Text: {original_text[:100]}...")  # 输出原文的前100个字符作为示例
        # print(f"Simplified Text 1: {simplified_text_1[:100]}...")  # 输出简化1的前100个字符作为示例
        # print(f"Simplified Text 2: {simplified_text_2[:100]}...")  # 输出简化2的前100个字符作为示例
        # print(f"Simplified Text 3: {simplified_text_3[:100]}...")  # 输出简化3的前100个字符作为示例
        # print('-' * 50)  # 分隔线

        doc_content = original_text
        ref_list = [simplified_text_1, simplified_text_2, simplified_text_3]
        doc_name = title
        doc_type = 'Evl_西游记'

        ver_1_doc = full_pipeline(doc_content, doc_name, version=1, type=doc_type, ref=ref_list)
        ver_2_doc = full_pipeline(ver_1_doc, doc_name, version=2, type=doc_type)
        ver_3_doc = full_pipeline(ver_2_doc, doc_name, version=3, type=doc_type)


if __name__ == '__main__':
    path = r"D:\桌面\西游记(完整)"
    start_evl_pipeline(path)
