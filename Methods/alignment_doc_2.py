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


def start_align_pipeline(raw_path, simp_path):
    # 读取source_json_path中的json文件,两个键，type和raw_content
    doc_num = 0
    # 随机打乱
    seed = 44
    random.seed(seed)

    with open(raw_path, 'r', encoding='utf-8') as file:
        raw_text = file.read()

    with open(simp_path, 'r', encoding='utf-8') as file:
        simp_text = file.read()

    raw_text_list = raw_text.split("\n\n")
    simp_text_list = simp_text.split("\n\n")

    json_list = []

    for raw, simp in zip(raw_text_list, simp_text_list):
        json_list.append({"raw_content": raw, "ref_content": simp})

    # 打乱列表中的元素顺序
    random.shuffle(json_list)

    # 打印加载的JSON内容长度
    print(f"Loaded {len(json_list)} items from the input file.")

    # 读取
    for item in json_list:
        print(f"raw_content: {item['raw_content'][:500]}")
        print("====================================")
        print(f"ref_content: {item['ref_content'][:500]}")
        print("====================================")
        doc_num += 1

        if doc_num < 14:
            continue
        # 将doc_num的值保存在当前目录下的doc_num.txt文件中,不存在则创建，存在则追加
        with open('align_doc_num.txt', 'r+', encoding='utf-8') as file:
            # 如果文件中的某一行已经有了doc_num的值，则不再写入
            content = file.read()
            if str(doc_num) not in content.split('\n'):
                file.write(str(doc_num) + '\n')
                print(f"doc_num: {doc_num}")
            else:
                continue

        # 读取raw_content键的值
        doc_content = item['raw_content']
        paragraphs = doc_content.split('\n')
        if len(paragraphs[0]) <= 25:
            doc_name = paragraphs[0]
        else:
            doc_name = paragraphs[0][:25]
        chars_to_replace = r'[ :：;；。，,！!]'
        # 使用正则表达式替换所有指定的字符为下划线
        doc_name = re.sub(chars_to_replace, '_', doc_name)
        doc_type = 'Align'

        ver_1_doc = full_pipeline(doc_content, doc_name, version=1, type=doc_type, ref=item['ref_content'])
        ver_2_doc = full_pipeline(ver_1_doc, doc_name, version=2, type=doc_type)
        ver_3_doc = full_pipeline(ver_2_doc, doc_name, version=3, type=doc_type)


if __name__ == '__main__':
    # alis_text = read_file_as_string(
    #     r"D:\桌面\ch_doc_dataset\成-青\成-青数据集\成-青原文数据\成人完整版\1\√爱丽丝漫游奇境记_刘易斯·卡罗尔_TXT小说天堂.txt")
    # chapters = seg_alis(alis_text)
    # for chapter in chapters:
    #     print(chapter)
    #     print()
    #
    # print(len(chapters))
    # 11

    # simp_path = r"D:\桌面\ch_doc_dataset\成-青\成-青数据集\成-青原文数据\成人完整版\1\√木偶奇遇记_.txt"
    # simp_text = read_file_as_string(simp_path)
    # chapters = seg_chapter(simp_text)
    # for chapter in chapters:
    #     print(chapter)
    #     print()
    #
    # print(len(chapters))

    path1 = r"D:\桌面\ch_doc_dataset\原著.txt"
    path2 = r"D:\桌面\ch_doc_dataset\青少.txt"
    # with open(path1, 'r', encoding='utf-8') as file:
    #     text1 = file.read()
    # with open(path2, 'r', encoding='utf-8') as file:
    #     text2 = file.read()
    #
    # text1_list = text1.split("\n\n")
    # text2_list = text2.split("\n\n")
    # print(len(text1_list))
    # print(len(text2_list))
    #
    # for text1, text2 in zip(text1_list, text2_list):
    #     print(text1)
    #     print("-----------------")
    #     print(text2)
    #     print("=====================================")

    start_align_pipeline(path1, path2)
