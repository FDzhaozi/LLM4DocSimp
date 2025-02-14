from easse.sari import corpus_sari
import os
import json

from Database.select_target import query_word_freq, query_sims, query_freq
from Evaluate.calc_ch_level import readability
from Evaluate.calc_d_sari import D_SARIsent
from Evaluate.easse.easse.fkgl import corpus_fkgl
from Methods.para_aspect import seg_to_chunks
from Methods.sentence_aspect import seg_to_sens, calc_complex_sen_frequency
from Methods.word_aspect import seg_words, judge_complex_char, query_char_level, query_word_level, get_words_sim


def calculate_sari(raw_text: str, model_text: str, ref_text: list):
    # Calculate SARI
    macro_sari, res_sari = corpus_sari(orig_sents=[raw_text], sys_sents=[model_text], refs_sents=ref_text)
    ref_text = [i[0] for i in ref_text]
    # result_d_sari = D_SARIsent(raw_text, model_text, ref_text)[0]
    # sententces = seg_to_sens(raw_text)
    # print(sententces)

    return macro_sari, res_sari


def calculate_ch_read(raw_text: str, model_text: str, ref_text: list):
    raw_level = readability(raw_text, lang='chinese')
    sys_level = readability(model_text, lang='chinese')
    ref1_level = readability(ref_text[0], lang='chinese')
    ref2_level = readability(ref_text[1], lang='chinese')
    ref3_level = readability(ref_text[2], lang='chinese')

    return raw_level, sys_level, ref1_level, ref2_level, ref3_level


def seg_to_paras(text):
    paragraphs = text.split('\n')
    # 删除空段落
    paragraphs = [i for i in paragraphs if i != '']
    return paragraphs


from Utiles.configs import load_config, get_work_path

config_path = r"../Utiles/config.yml"
work_path = get_work_path()
config = load_config(config_path)
hanzi_hsk_path = os.path.join(work_path, config['hanzi_hsk_path'])
ci_hsk_path = work_path + config['ci_hsk_path']
freq_db_path = work_path + config['freq_db_path']
word_freq_db_path = work_path + config['word_freq_db_path']
sim_db_path = work_path + config['sim_db_path']

# def judge_zi_ci(text):
#     all_zi = 0
#     all_ci = 0
#
#     hsk_zi = 0
#     freq_zi = 0
#
#     hsk_ci = 0
#     freq_ci = 0  # 简单词的词频，越高越好
#     sim_ci = 0
#
#     sent_nums = 0
#     paras = seg_to_paras(text)
#     para_nums = len(paras)
#
#     chunks = seg_to_chunks(text)
#     for chunk in chunks:
#         sent_nums += len(seg_to_sens(chunk))
#         char_and_word = seg_words([chunk])
#         complex_chars = set()
#         for char in char_and_word[0]:
#             if len(char) == 1:
#                 punctuation = set('，。、；：？！“”‘’（）《》【】')
#                 if char in punctuation:
#                     continue
#                 all_zi += 1
#                 if '\u4e00' <= char <= '\u9fff':
#                     level = query_char_level(char, hanzi_hsk_path)
#                     if level is None:
#                         hsk_zi += 1
#                     db_name = freq_db_path
#                     freq = query_freq(db_name, char)
#                     if freq is None:
#                         freq_zi += 1
#                     else:
#                         freq = float(freq["char_freq"])
#                         if freq > 98.5:
#                             freq_zi += 1
#                 print("char: ", char)
#             elif 1 < len(char) < 5:
#                 all_ci += 1
#                 level = query_word_level(char)
#                 if level is None:
#                     hsk_ci += 1
#                 result = query_word_freq(word_freq_db_path, char)
#                 if result is None:
#                     pass
#                 elif result["freq"] > 100:
#                     freq_ci += 1
#                 sim = query_sims(sim_db_path, char)
#                 if sim is None:
#                     word, sim = get_words_sim(char)
#                     if sim is None:
#                         sim = 0
#                     else:
#                         sim = float(sim)
#                 else:
#                     sim = float(sim["sim_value"])
#                 if sim < 0.14:
#                     sim_ci += 1
#                 print("word: ", char)
#     avg_zi_hsk = hsk_zi / all_zi
#     avg_zi_freq = freq_zi / all_zi
#     avg_ci_hsk = hsk_ci / all_ci
#     avg_ci_freq = freq_ci / all_ci
#     avg_ci_sim = sim_ci / all_ci
#     avg_sents_per_para = sent_nums / para_nums
#     return [avg_zi_hsk, avg_zi_freq, avg_ci_hsk, avg_ci_freq, avg_ci_sim, avg_sents_per_para]


# 缓存查询结果
char_cache = {}
word_cache = {}


def judge_zi_ci(text):
    all_zi = 0
    all_ci = 0

    hsk_zi = 0
    freq_zi = 0

    hsk_ci = 0
    freq_ci = 0
    sim_ci = 0

    sent_nums = 0
    paras = seg_to_paras(text)
    para_nums = len(paras)

    punctuation = set('，。、；：？！“”‘’（）《》【】')
    chunks = seg_to_chunks(text)

    for chunk in chunks:
        sent_nums += len(seg_to_sens(chunk))
        char_and_word = seg_words([chunk])
        for char in char_and_word[0]:
            if len(char) == 1:
                if char in punctuation:
                    continue
                all_zi += 1
                if '\u4e00' <= char <= '\u9fff':
                    if char not in char_cache:
                        level = query_char_level(char, hanzi_hsk_path)
                        freq = query_freq(freq_db_path, char)
                        char_cache[char] = (level, freq)
                    else:
                        level, freq = char_cache[char]

                    if level is None:
                        hsk_zi += 1
                    if freq is None or float(freq["char_freq"]) > 98.5:
                        freq_zi += 1
            elif 1 < len(char) < 5:
                all_ci += 1
                if char not in word_cache:
                    level = query_word_level(char)
                    result = query_word_freq(word_freq_db_path, char)
                    sim = query_sims(sim_db_path, char)
                    word_cache[char] = (level, result, sim)
                else:
                    level, result, sim = word_cache[char]

                if level is None:
                    hsk_ci += 1
                if result and result["freq"] > 100:
                    freq_ci += 1
                if sim is None:
                    word, sim = get_words_sim(char)
                    sim = float(sim) if sim else 0
                else:
                    sim = float(sim["sim_value"])
                if sim < 0.14:
                    sim_ci += 1

    avg_zi_hsk = hsk_zi / all_zi if all_zi else 0
    avg_zi_freq = freq_zi / all_zi if all_zi else 0
    avg_ci_hsk = hsk_ci / all_ci if all_ci else 0
    avg_ci_freq = freq_ci / all_ci if all_ci else 0
    avg_ci_sim = sim_ci / all_ci if all_ci else 0
    avg_sents_per_para = sent_nums / para_nums if para_nums else 0

    return [avg_zi_hsk, avg_zi_freq, avg_ci_hsk, avg_ci_freq, avg_ci_sim, avg_sents_per_para]


def read_and_print_contents(base_path):
    # 获取所有子文件夹列表
    subfolders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
    raw_data = [0, 0, 0, 0, 0, 0]
    avg_sys_data_1_1 = [0, 0, 0, 0, 0, 0]
    avg_sys_data_1_2 = [0, 0, 0, 0, 0, 0]
    avg_sys_data_1_3 = [0, 0, 0, 0, 0, 0]
    avg_sys_data_1_4 = [0, 0, 0, 0, 0, 0]
    avg_sys_data_2_1 = [0, 0, 0, 0, 0, 0]
    avg_sys_data_2_2 = [0, 0, 0, 0, 0, 0]
    avg_sys_data_2_3 = [0, 0, 0, 0, 0, 0]
    avg_sys_data_2_4 = [0, 0, 0, 0, 0, 0]
    avg_sys_data_3_1 = [0, 0, 0, 0, 0, 0]
    avg_sys_data_3_2 = [0, 0, 0, 0, 0, 0]
    avg_sys_data_3_3 = [0, 0, 0, 0, 0, 0]
    avg_sys_data_3_4 = [0, 0, 0, 0, 0, 0]

    count = 0

    chars = 0
    words = 0
    sents = 0
    paras = 0



    # 逐个处理每个子文件夹
    for folder in subfolders:
        folder_path = os.path.join(base_path, folder)
        title = folder
        print(f"处理文件夹：{title}")
        if not title.startswith("Novel"):
            continue

        # 读取文件内容
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            if filename == 'raw.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    raw_text = file.read()
                    count += 1
                    chars += len(raw_text)
                    for word in seg_words([raw_text])[0]:
                        if len(word) > 1:
                            words += 1
                    sents += len(seg_to_sens(raw_text))
                    paras += len(seg_to_paras(raw_text))

                    # raw_score = judge_zi_ci(raw_text)
                    # raw_data = [a + b for a, b in zip(raw_data, raw_score)]

    #     # 读取ver1, ver2, ver3文件夹下的中间文档
    #
    #     for ver_folder in ['ver1', 'ver2', 'ver3']:
    #         ver_folder_path = os.path.join(folder_path, ver_folder)
    #         if os.path.isdir(ver_folder_path):
    #             for ver_file in os.listdir(ver_folder_path):
    #                 ver_file_path = os.path.join(ver_folder_path, ver_file)
    #                 with open(ver_file_path, 'r', encoding='utf-8') as file:
    #                     print(f"{ver_folder} - {ver_file}")
    #                     if ver_folder == 'ver1' and ver_file == 'ver1_char.txt':
    #                         count += 1
    #                         sys_text = file.read()
    #                         sys_score = judge_zi_ci(sys_text)
    #                         avg_sys_data_1_1 = [a + b for a, b in zip(avg_sys_data_1_1, sys_score)]
    #                     elif ver_folder == 'ver1' and ver_file == 'ver1_char_word.txt':
    #                         sys_text = file.read()
    #                         sys_score = judge_zi_ci(sys_text)
    #                         avg_sys_data_1_2 = [a + b for a, b in zip(avg_sys_data_1_2, sys_score)]
    #                     elif ver_folder == 'ver1' and ver_file == 'ver1_char_word_sent.txt':
    #                         sys_text = file.read()
    #                         sys_score = judge_zi_ci(sys_text)
    #                         avg_sys_data_1_3 = [a + b for a, b in zip(avg_sys_data_1_3, sys_score)]
    #                     elif ver_folder == 'ver1' and ver_file == 'ver1_char_word_sent_para.txt':
    #                         sys_text = file.read()
    #                         sys_score = judge_zi_ci(sys_text)
    #                         avg_sys_data_1_4 = [a + b for a, b in zip(avg_sys_data_1_4, sys_score)]
    #                     elif ver_folder == 'ver2' and ver_file == 'ver2_char.txt':
    #                         sys_text = file.read()
    #                         sys_score = judge_zi_ci(sys_text)
    #                         avg_sys_data_2_1 = [a + b for a, b in zip(avg_sys_data_2_1, sys_score)]
    #                     elif ver_folder == 'ver2' and ver_file == 'ver2_char_word.txt':
    #                         sys_text = file.read()
    #                         sys_score = judge_zi_ci(sys_text)
    #                         avg_sys_data_2_2 = [a + b for a, b in zip(avg_sys_data_2_2, sys_score)]
    #                     elif ver_folder == 'ver2' and ver_file == 'ver2_char_word_sent.txt':
    #                         sys_text = file.read()
    #                         sys_score = judge_zi_ci(sys_text)
    #                         avg_sys_data_2_3 = [a + b for a, b in zip(avg_sys_data_2_3, sys_score)]
    #                     elif ver_folder == 'ver2' and ver_file == 'ver2_char_word_sent_para.txt':
    #                         sys_text = file.read()
    #                         sys_score = judge_zi_ci(sys_text)
    #                         avg_sys_data_2_4 = [a + b for a, b in zip(avg_sys_data_2_4, sys_score)]
    #                     elif ver_folder == 'ver3' and ver_file == 'ver3_char.txt':
    #                         sys_text = file.read()
    #                         sys_score = judge_zi_ci(sys_text)
    #                         avg_sys_data_3_1 = [a + b for a, b in zip(avg_sys_data_3_1, sys_score)]
    #                     elif ver_folder == 'ver3' and ver_file == 'ver3_char_word.txt':
    #                         sys_text = file.read()
    #                         sys_score = judge_zi_ci(sys_text)
    #                         avg_sys_data_3_2 = [a + b for a, b in zip(avg_sys_data_3_2, sys_score)]
    #                     elif ver_folder == 'ver3' and ver_file == 'ver3_char_word_sent.txt':
    #                         sys_text = file.read()
    #                         sys_score = judge_zi_ci(sys_text)
    #                         avg_sys_data_3_3 = [a + b for a, b in zip(avg_sys_data_3_3, sys_score)]
    #                     elif ver_folder == 'ver3' and ver_file == 'ver3_char_word_sent_para.txt':
    #                         sys_text = file.read()
    #                         sys_score = judge_zi_ci(sys_text)
    #                         avg_sys_data_3_4 = [a + b for a, b in zip(avg_sys_data_3_4, sys_score)]
    #
    # raw_data = [a / count for a in raw_data]
    # avg_sys_data_1_1 = [a / count for a in avg_sys_data_1_1]
    # avg_sys_data_1_2 = [a / count for a in avg_sys_data_1_2]
    # avg_sys_data_1_3 = [a / count for a in avg_sys_data_1_3]
    # avg_sys_data_1_4 = [a / count for a in avg_sys_data_1_4]
    # mean_list_1 = [(a + b + c + d) / 4 for a, b, c, d in
    #                zip(avg_sys_data_1_1, avg_sys_data_1_2, avg_sys_data_1_3, avg_sys_data_1_4)]
    # avg_sys_data_2_1 = [a / count for a in avg_sys_data_2_1]
    # avg_sys_data_2_2 = [a / count for a in avg_sys_data_2_2]
    # avg_sys_data_2_3 = [a / count for a in avg_sys_data_2_3]
    # avg_sys_data_2_4 = [a / count for a in avg_sys_data_2_4]
    # mean_list_2 = [(a + b + c + d) / 4 for a, b, c, d in
    #                zip(avg_sys_data_2_1, avg_sys_data_2_2, avg_sys_data_2_3, avg_sys_data_2_4)]
    # avg_sys_data_3_1 = [a / count for a in avg_sys_data_3_1]
    # avg_sys_data_3_2 = [a / count for a in avg_sys_data_3_2]
    # avg_sys_data_3_3 = [a / count for a in avg_sys_data_3_3]
    # avg_sys_data_3_4 = [a / count for a in avg_sys_data_3_4]
    # mean_list_3 = [(a + b + c + d) / 4 for a, b, c, d in
    #                zip(avg_sys_data_3_1, avg_sys_data_3_2, avg_sys_data_3_3, avg_sys_data_3_4)]
    #
    # print(f"Raw: {raw_data}")
    # print(f"Sys CI 1_1: {avg_sys_data_1_1}")
    # print(f"Sys CI 1_2: {avg_sys_data_1_2}")
    # print(f"Sys CI 1_3: {avg_sys_data_1_3}")
    # print(f"Sys CI 1_4: {avg_sys_data_1_4}")
    # print(f"Sys CI 2_1: {avg_sys_data_2_1}")
    # print(f"Sys CI 2_2: {avg_sys_data_2_2}")
    # print(f"Sys CI 2_3: {avg_sys_data_2_3}")
    # print(f"Sys CI 2_4: {avg_sys_data_2_4}")
    # print(f"Sys CI 3_1: {avg_sys_data_3_1}")
    # print(f"Sys CI 3_2: {avg_sys_data_3_2}")
    # print(f"Sys CI 3_3: {avg_sys_data_3_3}")
    # print(f"Sys CI 3_4: {avg_sys_data_3_4}")
    # print(f"Mean CI 1: {mean_list_1}")
    # print(f"Mean CI 2: {mean_list_2}")
    # print(f"Mean CI 3: {mean_list_3}")
    # print("count: ", count)

    # print(f"Raw Text: {raw_text}...")
    # print(f"Ref Text 1: {ref_text_1}...")
    # print(f"Ref Text 2: {ref_text_2}...")
    # print(f"Ref Text 3: {ref_text_3}...")
    # print(f"Char JSON: {char_json}")
    # print(f"Word JSON: {word_json}")
    # print(f"Sent JSON: {sent_json}")
    # print(f"Para JSON: {para_json}")
    # print('-' * 50)

    print(f"count: {count}")
    print(f"avg chars: {chars/count}")
    print(f"avg words: {words/count}")
    print(f"avg sents: {sents/count}")
    print(f"avg paras: {paras/count}")


if __name__ == '__main__':
    base_path = r'D:\Code\Ch_Doc_Simp_Dataset\Output_Docs'
    read_and_print_contents(base_path)
