from easse.sari import corpus_sari
import os
import json

from Evaluate.calc_ch_level import readability
from Evaluate.calc_d_sari import D_SARIsent
from Evaluate.easse.easse.fkgl import corpus_fkgl
from Methods.sentence_aspect import seg_to_sens, calc_complex_sen_frequency


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

def read_and_print_contents(base_path):
    # 获取所有子文件夹列表
    subfolders = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]

    # avg_raw_macro_sari = [0, 0, 0]
    # avg_raw_res_sari = 0
    # avg_ref_macro_sari = [0, 0, 0]
    # avg_ref_res_sari = 0
    # avg_raw_read = 0
    # avg_raw_read_l1 = 0
    # avg_raw_read_l2 = 0
    # avg_ref1_read = 0
    # avg_ref1_read_l1 = 0
    # avg_ref1_read_l2 = 0
    # avg_ref2_read = 0
    # avg_ref2_read_l1 = 0
    # avg_ref2_read_l2 = 0
    # avg_ref3_read = 0
    # avg_ref3_read_l1 = 0
    # avg_ref3_read_l2 = 0
    #
    # avg_raw_complex_sent_freq = 0
    # avg_ref1_complex_sent_freq = 0
    # avg_ref2_complex_sent_freq = 0
    # avg_ref3_complex_sent_freq = 0

    # avg_ref1_macro_sari = [0, 0, 0]
    # avg_ref1_res_sari = 0
    # avg_ref2_macro_sari = [0, 0, 0]
    # avg_ref2_res_sari = 0
    # avg_ref3_macro_sari = [0, 0, 0]
    # avg_ref3_res_sari = 0
    #
    # avg_raw_para_nums = 0
    # avg_ref1_para_nums = 0
    # avg_ref2_para_nums = 0
    # avg_ref3_para_nums = 0

    avg_sys_macro_sari = [0, 0, 0]
    avg_sys_res_sari = 0
    avg_sys_read = 0
    avg_sys_read_l1 = 0
    avg_sys_read_l2 = 0
    avg_sys_complex_sent_freq = 0
    avg_sys_para_nums = 0

    count = 0

    # 逐个处理每个子文件夹
    for folder in subfolders:
        folder_path = os.path.join(base_path, folder)
        title = folder

        # 初始化变量
        raw_text = ''
        ref_text_1 = ''
        ref_text_2 = ''
        ref_text_3 = ''
        char_json = []
        word_json = []
        sent_json = []
        para_json = []

        # 读取文件内容
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)

            if filename == 'raw.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    raw_text = file.read()
            elif filename == 'ref_1.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    ref_text_1 = file.read()
            elif filename == 'ref_2.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    ref_text_2 = file.read()
            elif filename == 'ref_3.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    ref_text_3 = file.read()
            elif filename == 'char.json':
                with open(file_path, 'r', encoding='utf-8') as file:
                    char_json = json.load(file)
            elif filename == 'word.json':
                with open(file_path, 'r', encoding='utf-8') as file:
                    word_json = json.load(file)
            elif filename == 'sent.json':
                with open(file_path, 'r', encoding='utf-8') as file:
                    sent_json = json.load(file)
            elif filename == 'para.json':
                with open(file_path, 'r', encoding='utf-8') as file:
                    para_json = json.load(file)

        # 读取ver1, ver2, ver3文件夹下的中间文档

        for ver_folder in ['ver1', 'ver2', 'ver3']:
            ver_folder_path = os.path.join(folder_path, ver_folder)
            if os.path.isdir(ver_folder_path):
                for ver_file in os.listdir(ver_folder_path):
                    ver_file_path = os.path.join(ver_folder_path, ver_file)
                    with open(ver_file_path, 'r', encoding='utf-8') as file:
                        print(f"{ver_folder} - {ver_file}")
                        if ver_folder == 'ver1' and ver_file == 'ver1_char.txt':
                            count += 1
                            # macro_sari, res_sari = calculate_sari(
                            #     raw_text, file.read(),
                            #     [[ref_text_1], [ref_text_2],
                            #      [ref_text_3]])
                            #
                            # raw_macro_sari, raw_res_sari = calculate_sari(
                            #     raw_text, raw_text,
                            #     [[ref_text_1], [ref_text_2],
                            #      [ref_text_3]])
                            #
                            # ref1_macro_sari, ref1_res_sari = calculate_sari(
                            #     raw_text, ref_text_1,
                            #     [[ref_text_1], [ref_text_2],
                            #      [ref_text_3]])
                            #
                            # ref2_macro_sari, ref2_res_sari = calculate_sari(
                            #     raw_text, ref_text_2,
                            #     [[ref_text_1], [ref_text_2],
                            #      [ref_text_3]])
                            #
                            # ref3_macro_sari, ref3_res_sari = calculate_sari(
                            #     raw_text, ref_text_3,
                            #     [[ref_text_1], [ref_text_2],
                            #      [ref_text_3]])
                            #
                            # print(f"ref1_macro_sari: {ref1_macro_sari}")
                            # print(f"ref2_macro_sari: {ref2_macro_sari}")
                            # print(f"ref3_macro_sari: {ref3_macro_sari}")
                            # print(f"ref1_res_sari: {ref1_res_sari}")
                            # print(f"ref2_res_sari: {ref2_res_sari}")
                            # print(f"ref3_res_sari: {ref3_res_sari}")
                            #
                            # ref_macro_sari = [(a + b + c) / 3 for a, b, c in zip(ref1_macro_sari, ref2_macro_sari, ref3_macro_sari)]
                            # ref_res_sari = (ref1_res_sari + ref2_res_sari + ref3_res_sari) / 3
                            #
                            #
                            #
                            # raw_level_all, sys_level_all, ref1_level_all, ref2_level_all, ref3_level_all = calculate_ch_read(
                            #     raw_text, file.read(),
                            #     [ref_text_1, ref_text_2, ref_text_3])
                            #
                            # print(f"Raw Level: {raw_level_all}")
                            # print(f"Sys Level: {sys_level_all}")
                            # print(f"Ref1 Level: {ref1_level_all}")
                            # print(f"Ref2 Level: {ref2_level_all}")
                            # print(f"Ref3 Level: {ref3_level_all}")
                            #
                            # raw_level = raw_level_all["readability3"]
                            # raw_level_l1 = raw_level_all["readability1"]
                            # raw_level_l2 = raw_level_all["readability2"]
                            #
                            # ref1_level = ref1_level_all["readability3"]
                            # ref1_level_l1 = ref1_level_all["readability1"]
                            # ref1_level_l2 = ref1_level_all["readability2"]
                            #
                            # ref2_level = ref2_level_all["readability3"]
                            # ref2_level_l1 = ref2_level_all["readability1"]
                            # ref2_level_l2 = ref2_level_all["readability2"]
                            #
                            # ref3_level = ref3_level_all["readability3"]
                            # ref3_level_l1 = ref3_level_all["readability1"]
                            # ref3_level_l2 = ref3_level_all["readability2"]
                            #
                            #
                            # avg_raw_macro_sari = [a + b for a, b in zip(avg_raw_macro_sari, raw_macro_sari)]
                            # avg_raw_res_sari += raw_res_sari
                            # avg_ref_macro_sari = [a + b for a, b in zip(avg_ref_macro_sari, ref_macro_sari)]
                            # avg_ref_res_sari += ref_res_sari

                            # avg_ref1_macro_sari = [a + b for a, b in zip(avg_ref1_macro_sari, ref1_macro_sari)]
                            # avg_ref1_res_sari += ref1_res_sari
                            # avg_ref2_macro_sari = [a + b for a, b in zip(avg_ref2_macro_sari, ref2_macro_sari)]
                            # avg_ref2_res_sari += ref2_res_sari
                            # avg_ref3_macro_sari = [a + b for a, b in zip(avg_ref3_macro_sari, ref3_macro_sari)]
                            # avg_ref3_res_sari += ref3_res_sari

                            # avg_raw_read += raw_level
                            # avg_raw_read_l1 += raw_level_l1
                            # avg_raw_read_l2 += raw_level_l2
                            # avg_ref1_read += ref1_level
                            # avg_ref1_read_l1 += ref1_level_l1
                            # avg_ref1_read_l2 += ref1_level_l2
                            # avg_ref2_read += ref2_level
                            # avg_ref2_read_l1 += ref2_level_l1
                            # avg_ref2_read_l2 += ref2_level_l2
                            # avg_ref3_read += ref3_level
                            # avg_ref3_read_l1 += ref3_level_l1
                            # avg_ref3_read_l2 += ref3_level_l2
                            #
                            #
                            # print(f"Macro SARI: {macro_sari}")
                            # print(f"SARI: {res_sari}")
                            # print(f"Raw Macro SARI: {raw_macro_sari}")
                            # print(f"Raw SARI: {raw_res_sari}")
                            # print(f"Ref Macro SARI: {ref_macro_sari}")
                            # print(f"Ref SARI: {ref_res_sari}")
                            #
                            # avg_raw_complex_sent_freq += calc_complex_sen_frequency(raw_text)
                            # avg_ref1_complex_sent_freq += calc_complex_sen_frequency(ref_text_1)
                            # avg_ref2_complex_sent_freq += calc_complex_sen_frequency(ref_text_2)
                            # avg_ref3_complex_sent_freq += calc_complex_sen_frequency(ref_text_3)

                            # raw_paras = seg_to_paras(raw_text)
                            # avg_raw_para_nums += len(raw_paras)
                            # ref1_paras = seg_to_paras(ref_text_1)
                            # avg_ref1_para_nums += len(ref1_paras)
                            # ref2_paras = seg_to_paras(ref_text_2)
                            # avg_ref2_para_nums += len(ref2_paras)
                            # ref3_paras = seg_to_paras(ref_text_3)
                            # avg_ref3_para_nums += len(ref3_paras)
                            sys_text = file.read()
                            #print(f"Sys Text: {sys_text}")


                            macro_sari, res_sari = calculate_sari(
                                raw_text, sys_text,
                                [[ref_text_1], [ref_text_2],
                                 [ref_text_3]])

                            avg_sys_macro_sari = [a + b for a, b in zip(avg_sys_macro_sari, macro_sari)]
                            avg_sys_res_sari += res_sari

                            raw_level_all, sys_level_all, ref1_level_all, ref2_level_all, ref3_level_all = calculate_ch_read(
                                    raw_text, sys_text,
                                    [ref_text_1, ref_text_2, ref_text_3])
                            sys_level = sys_level_all["readability3"]
                            sys_level_l1 = sys_level_all["readability1"]
                            sys_level_l2 = sys_level_all["readability2"]
                            avg_sys_read += sys_level
                            avg_sys_read_l1 += sys_level_l1
                            avg_sys_read_l2 += sys_level_l2

                            avg_sys_complex_sent_freq += calc_complex_sen_frequency(sys_text)

                            sys_paras = seg_to_paras(sys_text)
                            avg_sys_para_nums += len(sys_paras)





                            print('-' * 50)

    # avg_raw_macro_sari = [a / count for a in avg_raw_macro_sari]
    # avg_raw_res_sari /= count
    # avg_ref_macro_sari = [a / count for a in avg_ref_macro_sari]
    # avg_ref_res_sari /= count
    # avg_raw_read /= count
    # avg_raw_read_l1 /= count
    # avg_raw_read_l2 /= count
    # avg_ref1_read /= count
    # avg_ref1_read_l1 /= count
    # avg_ref1_read_l2 /= count
    # avg_ref2_read /= count
    # avg_ref2_read_l1 /= count
    # avg_ref2_read_l2 /= count
    # avg_ref3_read /= count
    # avg_ref3_read_l1 /= count
    # avg_ref3_read_l2 /= count
    #
    # avg_raw_complex_sent_freq /= count
    # avg_ref1_complex_sent_freq /= count
    # avg_ref2_complex_sent_freq /= count
    # avg_ref3_complex_sent_freq /= count

    # avg_ref1_macro_sari = [a / count for a in avg_ref1_macro_sari]
    # avg_ref1_res_sari /= count
    # avg_ref2_macro_sari = [a / count for a in avg_ref2_macro_sari]
    # avg_ref2_res_sari /= count
    # avg_ref3_macro_sari = [a / count for a in avg_ref3_macro_sari]
    # avg_ref3_res_sari /= count
    #
    # avg_raw_para_nums /= count
    # avg_ref1_para_nums /= count
    # avg_ref2_para_nums /= count
    # avg_ref3_para_nums /= count

    avg_sys_macro_sari = [a / count for a in avg_sys_macro_sari]
    avg_sys_res_sari /= count
    avg_sys_read /= count
    avg_sys_read_l1 /= count
    avg_sys_read_l2 /= count
    avg_sys_complex_sent_freq /= count
    avg_sys_para_nums /= count




    # print(f"Raw Macro SARI: {avg_raw_macro_sari}")
    # print(f"Raw SARI: {avg_raw_res_sari}")
    # print(f"Ref Macro SARI: {avg_ref_macro_sari}")
    # print(f"Ref SARI: {avg_ref_res_sari}")
    # print(f"Raw Read: {avg_raw_read}")
    # print(f"Raw Read L1: {avg_raw_read_l1}")
    # print(f"Raw Read L2: {avg_raw_read_l2}")
    # print(f"Ref1 Read: {avg_ref1_read}")
    # print(f"Ref1 Read L1: {avg_ref1_read_l1}")
    # print(f"Ref1 Read L2: {avg_ref1_read_l2}")
    # print(f"Ref2 Read: {avg_ref2_read}")
    # print(f"Ref2 Read L1: {avg_ref2_read_l1}")
    # print(f"Ref2 Read L2: {avg_ref2_read_l2}")
    # print(f"Ref3 Read: {avg_ref3_read}")
    # print(f"Ref3 Read L1: {avg_ref3_read_l1}")
    # print(f"Ref3 Read L2: {avg_ref3_read_l2}")
    #
    # print(f"Raw Complex Sent Freq: {avg_raw_complex_sent_freq}")
    # print(f"Ref1 Complex Sent Freq: {avg_ref1_complex_sent_freq}")
    # print(f"Ref2 Complex Sent Freq: {avg_ref2_complex_sent_freq}")
    # print(f"Ref3 Complex Sent Freq: {avg_ref3_complex_sent_freq}")

    # print(f"Ref1 Macro SARI: {avg_ref1_macro_sari}")
    # print(f"Ref1 SARI: {avg_ref1_res_sari}")
    # print(f"Ref2 Macro SARI: {avg_ref2_macro_sari}")
    # print(f"Ref2 SARI: {avg_ref2_res_sari}")
    # print(f"Ref3 Macro SARI: {avg_ref3_macro_sari}")
    # print(f"Ref3 SARI: {avg_ref3_res_sari}")
    #
    # print(f"Raw Para Num: {avg_raw_para_nums}")
    # print(f"Ref1 Para Num: {avg_ref1_para_nums}")
    # print(f"Ref2 Para Num: {avg_ref2_para_nums}")
    # print(f"Ref3 Para Num: {avg_ref3_para_nums}")

    print(f"Sys Macro SARI: {avg_sys_macro_sari}")
    print(f"Sys SARI: {avg_sys_res_sari}")
    print(f"Sys Read: {avg_sys_read}")
    print(f"Sys Read L1: {avg_sys_read_l1}")
    print(f"Sys Read L2: {avg_sys_read_l2}")
    print(f"Sys Complex Sent Freq: {avg_sys_complex_sent_freq}")
    print(f"Sys Para Num: {avg_sys_para_nums}")


    print("count: ", count)


    print('-' * 50)

    # 打印内容
    print(f"Title: {title}")

        # print(f"Raw Text: {raw_text}...")
        # print(f"Ref Text 1: {ref_text_1}...")
        # print(f"Ref Text 2: {ref_text_2}...")
        # print(f"Ref Text 3: {ref_text_3}...")
        # print(f"Char JSON: {char_json}")
        # print(f"Word JSON: {word_json}")
        # print(f"Sent JSON: {sent_json}")
        # print(f"Para JSON: {para_json}")
        # print('-' * 50)


if __name__ == '__main__':
    base_path = r'D:\Code\Ch_Doc_Simp_Dataset\Eval_Docs'
    read_and_print_contents(base_path)
