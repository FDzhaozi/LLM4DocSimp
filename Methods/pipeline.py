# 简化一篇文章。  初次、中次、末次
import json
import os
import random
import re
import sys

from LLMs.qwen_api import simp_aiml_qwen_api
from Methods.para_aspect import seg_to_chunks, simp_para_prompt
from Methods.sentence_aspect import seg_to_sens, dp_tree, sentence_difficulty_dep, sentence_difficulty_con, \
    weighted_difficulty, simp_sentence_prompt
from Methods.word_aspect import simp_char_prompt, judge_complex_char, simp_word_prompt, judge_complex_words
from Utiles.configs import get_work_path, load_config
from Utiles.format_output import extract_json_from_string, write_to_json, remove_square_brackets

# 将原文和对应三个等级保存在同一文件下面的三个txt文件。除此之外，还应该有汉字、词汇的简化数据保存为json, 语法的简化保存为json, 整个段落的简化保存为json。
# 在第一级简化开始前，应用命名实体识别技术，将人名、地名、机构名、专有名词等识别出来，不必进行简化（只需在原文中标注该词的类别即可。）


config_path = r"../Utiles/config.yml"
work_path = get_work_path()
config = load_config(config_path)
output_json_path = work_path + config['output_json_path']
source_json_path = work_path + config['source_json_path']


def simp_char_pip(doc: str, version: int = 1, re_check_max_round: int = 3, output_json_path: str = None,
                  type: str = "News"):
    chunks = seg_to_chunks(doc)
    final_doc = ""
    chunk_num = 0
    for chunk in chunks:
        ban_list = []
        chunk_num += 1
        prompt = simp_char_prompt(chunk, version)
        if prompt is None:
            print("无复杂字，不需要在字符级别上简化")
            simp_chunk = chunk
        else:
            need_recheck = True
            re_check_round = 0
            json_ext_round = 0
            # while need_recheck:
            result = simp_aiml_qwen_api(prompt)
            if result is None:
                print("调用API失败")
                return None
            if json_ext_round >= 3:
                # 终止整个程序
                print("超过最大json解析次数，停止程序")
                sys.exit(1)

            print(f"简化结果：{result}")
            json_result = extract_json_from_string(result)
            if json_result is None:
                simp_chunk = chunk
                print("json解析失败")
            else:
                simp_chunk = json_result["simplified_text"]
                simp_chunk = remove_square_brackets(simp_chunk)
                json_result["simplified_text"] = simp_chunk
                print(f"简化结果：{simp_chunk}")
                print(f"复杂字简化结果json：{json_result}")
                # # 重复检查生成的替换结果中是否还有复杂词，注释，实际效果不好。
                # for key, value in json_result["substitutions"].items():
                #     print(f"key: {key}, value: {value}")
                #     # 如果键值对中的值是复杂字,则将该字典加入ban_list
                #     if judge_complex_char(value, version):
                #         ban_list.append({key: value})
                # re_check_round += 1
                # if len(ban_list) == 0:
                #     print("无复杂字，不需要进行重复生成")
                #     need_recheck = False
                #     json_result["original"] = chunk
                #     all_results.append(json_result)
                #     continue
                # if re_check_round >= re_check_max_round:
                #     print("超过最大重复次数，停止重复")
                #     need_recheck = False
                #     json_result["original"] = chunk
                #     all_results.append(json_result)
                #     continue
                print("复杂字简化完成")
                print("复杂字简化结果：")
                json_result["version"] = version
                json_result["original"] = chunk
                json_result["chunk_num"] = chunk_num
                json_result["type"] = type
                write_to_json(output_json_path, json_result)
        final_doc += simp_chunk + "\n\n"

    return final_doc


def add_brackets_to_keys(chunk, ner_dict, abbre_dict):
    # 合并两个字典
    edited_abbre_dict = {}
    for key, value in abbre_dict.items():
        edited_abbre_dict[key] = abbre_dict[key]["full_form"]
    all_dicts = {**ner_dict, **edited_abbre_dict}

    # 对字典的键进行排序，确保按长度降序，以避免短键替换长键的问题
    sorted_keys = sorted(all_dicts.keys(), key=len, reverse=True)

    # 使用正则表达式替换字典键，并在其后添加括号及对应的值
    for key in sorted_keys:
        # 替换前确保key不是另一个键的子串
        pattern = r'{}'.format(re.escape(key))
        chunk = re.sub(pattern, '{}({})'.format(key, all_dicts[key]), chunk)

    return chunk


def simp_word_pip(doc: str, version: int = 1, re_check_max_round: int = 1, output_json_path: str = None,
                  type: str = "News"):
    chunks = seg_to_chunks(doc)
    final_doc = ""
    chunk_num = 0
    for chunk in chunks:
        ban_list = []
        chunk_num += 1
        prompt, ner_dict, abbre_dict = simp_word_prompt(chunk, version)
        if prompt is None:
            print("无复杂词，不需要在词汇级别上简化")
            print("将命名实体和缩写词进行替换....")
            json_result = {"original": chunk}
            chunk = add_brackets_to_keys(chunk, ner_dict, abbre_dict)
            json_result["substitutions"] = {**ner_dict, **abbre_dict}
            json_result["simplified_text"] = chunk
            print(json_result)
            print("========================")
            simp_chunk = chunk

        else:
            # need_recheck = True
            # re_check_round = 0
            json_ext_round = 0
            # while need_recheck:
            result = simp_aiml_qwen_api(prompt)
            if result is None:
                print("调用API失败")
                return None

            json_result = extract_json_from_string(result)
            if json_result is None:
                simp_chunk = chunk
                print("无法解析json结果")
            else:
                print(f"复杂词简化结果json：{json_result}")
                simplified_text = json_result["simplified_text"]
                simplified_text = remove_square_brackets(str(simplified_text))
                json_result["simplified_text"] = simplified_text

                print(f"复杂词简化结果json：{json_result}")
                # for key, value in json_result["substitutions"].items():
                #     print(f"key: {key}, value: {value}")
                #     # 如果键值对中的值仍是复杂词,则将该字典加入ban_list
                #     if judge_complex_word(value, version):
                #         ban_list.append({key: value})

                # 重复检查生成的替换结果中是否还有复杂词，注释，实际效果不好。
                # need_words = judge_complex_words(json_result["substitutions"].values(), version)
                # # 根据need_words找到对应的键值对
                # need_dict = {}
                # for key, value in json_result["substitutions"].items():
                #     if value in need_words:
                #         need_dict[key] = value
                #
                # if len(need_dict) > 0:
                #     for key, value in need_dict.items():
                #         ban_list.append({key: value})
                #
                # re_check_round += 1
                # if len(ban_list) == 0:
                #     print("无复杂词，不需要进行重复生成")
                #     need_recheck = False
                #     json_result["original"] = chunk
                #     all_results.append(json_result)
                #     continue
                # if re_check_round >= re_check_max_round:
                #     print("超过最大重复次数，停止重复")
                #     need_recheck = False
                #     json_result["original"] = chunk
                #     all_results.append(json_result)
                #     continue
                json_result["original"] = chunk
                json_result["version"] = version
                print("将命名实体和缩写词进行替换....")
                simplified_text = add_brackets_to_keys(simplified_text, ner_dict, abbre_dict)
                print(f"使用到的命名实体：{ner_dict}")
                print(f"使用到的缩写词：{abbre_dict}")
                json_result["simplified_text"] = simplified_text
                json_result["chunk_num"] = chunk_num
                json_result["type"] = type
                print("复杂词简化完成")
                simp_chunk = simplified_text
                write_to_json(output_json_path, json_result)
        final_doc += simp_chunk + "\n\n"

    return final_doc


def simp_sentences_pip(doc, version: int = 1, output_json_path: str = None, type: str = "News"):
    chunks = seg_to_chunks(doc)
    final_doc = ""
    chunk_num = 0
    for chunk in chunks:
        chunk_num += 1
        sentences_dptrees_list = []
        result = seg_to_sens(chunk)
        dp_trees = dp_tree(result)
        simp_chunk = ""
        for sentence, dep_tree in zip(result, dp_trees):
            sentences_dptrees_list.append((sentence, dep_tree))
            print(sentence)

            difficulty_level_dep = sentence_difficulty_dep(dep_tree)
            print(f"依存句法难度: {difficulty_level_dep}")

            difficulty_level_con = sentence_difficulty_con(sentence)
            print(f"成分句法难度: {difficulty_level_con}")

            difficulty_level = weighted_difficulty(difficulty_level_dep, difficulty_level_con)
            print(f"综合难度: {difficulty_level}")
            if difficulty_level == "复杂":
                print("复杂句子，需要简化")
                simp_sen_prompt = simp_sentence_prompt(sentence)
                result = simp_aiml_qwen_api(simp_sen_prompt)
                if result is None:
                    print("调用API失败")
                    return None
                json_result = extract_json_from_string(result)
                if json_result is None:
                    print("无法解析json结果")
                    simplified_text = sentence

                else:
                    print(f"复杂句子简化结果：{json_result}")
                    simplified_text = json_result["simplified_text"]
                    simplified_text = remove_square_brackets(simplified_text)
                    json_result["simplified_text"] = simplified_text
                    print(f"简化后的句子：{simplified_text}")
                    json_result["original"] = sentence
                    json_result["version"] = version
                    json_result["chunk_num"] = chunk_num
                    json_result["type"] = type
                    write_to_json(output_json_path, json_result)
                simp_chunk += simplified_text
            else:
                simp_chunk += sentence
        final_doc += simp_chunk + "\n\n"

    return final_doc


def simp_paras_pip(doc, version: int = 1, output_json_path: str = None, type: str = "News"):
    chunks = seg_to_chunks(doc)
    final_doc = ""
    chunk_num = 0
    for chunk in chunks:
        simp_chunk = ""
        chunk_num += 1
        prompt = simp_para_prompt(chunk, version)
        if prompt is None:
            simp_chunk = chunk
        else:
            result = simp_aiml_qwen_api(prompt)
            if result is None:
                print("调用API失败")
                return None
            json_result = extract_json_from_string(result)
            if json_result is None:
                print("无法解析json结果")
                simp_chunk = chunk
            else:
                simp_chunk = json_result["simplified_text"]
                simp_chunk = remove_square_brackets(simp_chunk)
                json_result["simplified_text"] = simp_chunk
                json_result["original"] = chunk
                json_result["version"] = version
                json_result["chunk_num"] = chunk_num
                json_result["type"] = type
                write_to_json(output_json_path, json_result)
                print(f"简化后的段落：{simp_chunk}")

        final_doc += simp_chunk + "\n\n"

    return final_doc


def full_pipeline(doc, doc_name, version: int = 1, type: str = "News", ref=None):
    doc_root_path = output_json_path + type + '_' + doc_name
    # 判断该文件夹是否存在，不存在则创建
    if not os.path.exists(doc_root_path):
        os.makedirs(doc_root_path)
    char_out_path = doc_root_path + '/' + 'char.json'
    word_out_path = doc_root_path + '/' + 'word.json'
    sent_out_path = doc_root_path + '/' + 'sent.json'
    para_out_path = doc_root_path + '/' + 'para.json'
    raw_doc_path = doc_root_path + '/' + 'raw.txt'
    if ref is not None:
        if len(ref) == 3:
            ref_1 = ref[0]
            ref_2 = ref[1]
            ref_3 = ref[2]
            ref_1_doc_path = doc_root_path + '/' + 'ref_1.txt'
            ref_2_doc_path = doc_root_path + '/' + 'ref_2.txt'
            ref_3_doc_path = doc_root_path + '/' + 'ref_3.txt'
            with open(ref_1_doc_path, 'w', encoding='utf-8') as f:
                f.write(ref_1)
            with open(ref_2_doc_path, 'w', encoding='utf-8') as f:
                f.write(ref_2)
            with open(ref_3_doc_path, 'w', encoding='utf-8') as f:
                f.write(ref_3)
        else:
            ref_doc_path = doc_root_path + '/' + 'ref.txt'
            with open(ref_doc_path, 'w', encoding='utf-8') as f:
                f.write(ref)
    doc_root_ver_path = doc_root_path + '/' + 'ver' + str(version)
    if not os.path.exists(doc_root_ver_path):
        os.makedirs(doc_root_ver_path)
    # ver_para_doc_path = doc_root_ver_path + '/' + 'ver' + str(version) + '_para.txt'
    # ver_para_sent_doc_path = doc_root_ver_path + '/' + 'ver' + str(version) + '_para_sent.txt'
    # ver_para_sent_word_doc_path = doc_root_ver_path + '/' + 'ver' + str(version) + '_para_sent_word.txt'
    # ver_para_sent_word_char_doc_path = doc_root_ver_path + '/' + 'ver' + str(version) + '_para_sent_word_char.txt'

    ver_char_doc_path = doc_root_ver_path + '/' + 'ver' + str(version) + '_char.txt'
    ver_char_word_doc_path = doc_root_ver_path + '/' + 'ver' + str(version) + '_char_word.txt'
    ver_char_word_sent_doc_path = doc_root_ver_path + '/' + 'ver' + str(version) + '_char_word_sent.txt'
    ver_char_word_sent_para_doc_path = doc_root_ver_path + '/' + 'ver' + str(version) + '_char_word_sent_para.txt'

    # 保存原文, 若文件已存在则不保存
    if not os.path.exists(raw_doc_path):
        with open(raw_doc_path, 'w', encoding='utf-8') as file:
            file.write(doc)

    # # para 级别简化
    # simp_para_doc = simp_paras_pip(doc, version=version, output_json_path=para_out_path, type=type)
    # with open(ver_para_doc_path, 'w', encoding='utf-8') as file:
    #     file.write(simp_para_doc)
    #
    # # para + sent 级别简化
    # simp_para_sent_doc = simp_sentences_pip(simp_para_doc, version=version, output_json_path=sent_out_path, type=type)
    # with open(ver_para_sent_doc_path, 'w', encoding='utf-8') as file:
    #     file.write(simp_para_sent_doc)
    #
    # # para + sent + word 级别简化
    # simp_para_sent_word_doc = simp_word_pip(simp_para_sent_doc, version=version, output_json_path=word_out_path,
    #                                         type=type)
    # with open(ver_para_sent_word_doc_path, 'w', encoding='utf-8') as file:
    #     file.write(simp_para_sent_word_doc)
    #
    # # para + sent + word + char 级别简化
    # simp_para_sent_word_char_doc = simp_char_pip(simp_para_sent_word_doc, version=version,
    #                                              output_json_path=char_out_path, type=type)
    # with open(ver_para_sent_word_char_doc_path, 'w', encoding='utf-8') as file:
    #     file.write(simp_para_sent_word_char_doc)

    # char 级别简化
    simp_char_doc = simp_char_pip(doc, version=version, output_json_path=char_out_path, type=type)
    with open(ver_char_doc_path, 'w', encoding='utf-8') as file:
        file.write(simp_char_doc)

    # char + word 级别简化
    simp_char_word_doc = simp_word_pip(simp_char_doc, version=version, output_json_path=word_out_path, type=type)

    with open(ver_char_word_doc_path, 'w', encoding='utf-8') as file:
        file.write(simp_char_word_doc)

    # char + word + sent 级别简化
    simp_char_word_sent_doc = simp_sentences_pip(simp_char_word_doc, version=version, output_json_path=sent_out_path,
                                                 type=type)
    with open(ver_char_word_sent_doc_path, 'w', encoding='utf-8') as file:
        file.write(simp_char_word_sent_doc)

    # char + word + sent + para 级别简化
    simp_char_word_sent_para_doc = simp_paras_pip(simp_char_word_sent_doc, version=version,
                                                  output_json_path=para_out_path, type=type)
    with open(ver_char_word_sent_para_doc_path, 'w', encoding='utf-8') as file:
        file.write(simp_char_word_sent_para_doc)

    return simp_char_word_sent_para_doc


def start_pipeline(input_path):
    # 读取source_json_path中的json文件,两个键，type和raw_content
    doc_num = 0
    # 随机打乱
    seed = 44
    random.seed(seed)

    with open(input_path, 'r', encoding='utf-8') as file:
        source_json = json.load(file)

    # 检查加载的JSON内容是否为列表，如果不是则抛出异常
    if not isinstance(source_json, list):
        raise ValueError("The loaded JSON content is not a list.")

    # 打乱列表中的元素顺序
    random.shuffle(source_json)

    # 打印加载的JSON内容长度
    print(f"Loaded {len(source_json)} items from the input file.")

    # 读取
    for doc in source_json:
        doc_num += 1

        # 将doc_num的值保存在当前目录下的doc_num.txt文件中,不存在则创建，存在则追加

        with open('doc_num.txt', 'r+', encoding='utf-8') as file:
            # 如果文件中的某一行已经有了doc_num的值，则不再写入
            content = file.read()
            if str(doc_num) not in content:
                file.write(str(doc_num) + '\n')
            else:
                print("文章已存在......")
                continue

        # 读取raw_content键的值
        doc_type = doc['type']
        doc_content = doc['raw_content']
        paragraphs = doc_content.split('\n')
        if len(paragraphs[0]) <= 25:
            doc_name = paragraphs[0]
        else:
            doc_name = paragraphs[0][:25]
        chars_to_replace = r'[ :：;；。，,！!]'
        # 使用正则表达式替换所有指定的字符为下划线
        doc_name = re.sub(chars_to_replace, '_', doc_name)
        # 非法字符列表
        invalid_chars = '<>:"/\\|?*'
        # 替换非法字符为下划线
        for char in invalid_chars:
            doc_name = doc_name.replace(char, '_')

        ver_1_doc = full_pipeline(doc_content, doc_name, version=1, type=doc_type)
        ver_2_doc = full_pipeline(ver_1_doc, doc_name, version=2, type=doc_type)
        ver_3_doc = full_pipeline(ver_2_doc, doc_name, version=3, type=doc_type)


# def process_document(document, output_dir):
#     # 保存原文
#     with open(os.path.join(output_dir, "original.txt"), 'w', encoding='utf-8') as file:
#         file.write(document)
#
#     # 分句
#     sentences = seg_sentences(document)
#
#     # 保存初次简化
#     simplified = simplify_sentences(sentences, level=1)
#     with open(os.path.join(output_dir, "level1.txt"), 'w', encoding='utf-8') as file:
#         for sent in simplified:
#             file.write(sent + '\n')
#
#     # 保存中次简化
#     simplified = simplify_sentences(sentences, level=2)
#     with open(os.path.join(output_dir, "level2.txt"), 'w', encoding='utf-8') as file:
#         for sent in simplified:
#             file.write(sent + '\n')
#
#     # 保存末次简化
#     simplified = simplify_sentences(sentences, level=3)
#     with open(os.path.join(output_dir, "level3.txt"), 'w', encoding='utf-8') as file:
#         for sent in simplified:
#             file.write(sent + '\n')
#
#     # 保存汉字简化数据
#     json_path = os.path.join(output_dir, "hanzi.json")
#     sta_words_standard(json_path)
#
#     # 保存词汇简化数据
#     json_path = os.path.join(output_dir, "words.json")
#     sta_words_standard(json_path)
#
#     # 保存语法简化数据
#     json_path = os.path.join(output_dir, "grammar.json")
#     sta_grammar_standard(json_path)
#
#     # 保存整个段落简化数据
#     json_path = os.path.join(output_dir, "paragraph.json")
#     sta_paragraph_standard(json_path)
#
#     print(f"处理完成，结果已保存到 {output_dir}")


if __name__ == '__main__':
    start_pipeline(source_json_path)
    # name = {'蔡国强': '人名', '中国': '地名'}
    # abbre = {'警力': {'abbreviation': '警力', 'full_form': '警务力量'},
    #                 '创意': {'abbreviation': '创意', 'full_form': '创新意识'},
    #                 '团队': {'abbreviation': '团队', 'full_form': '共青团和少先队'}}
    # text = "蔡国强是中国的一位科学家，他在创意团队中发挥着重要作用。"
    # print(add_brackets_to_keys(text, name, abbre))




