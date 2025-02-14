from easse.sari import corpus_sari
import os
import json

from Evaluate.calc_ch_level import readability
from Evaluate.calc_d_sari import D_SARIsent
from Evaluate.easse.easse.fkgl import corpus_fkgl
from Methods.para_aspect import seg_to_chunks
from Methods.sentence_aspect import seg_to_sens, calc_complex_sen_frequency
from Methods.word_aspect import seg_words


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

    avg_sys_macro_sari = [0, 0, 0]
    avg_sys_res_sari = 0
    avg_sys_read = 0
    avg_sys_read_l1 = 0
    avg_sys_read_l2 = 0
    avg_sys_complex_sent_freq = 0
    avg_sys_para_nums = 0

    count = 0
    avg_chars = 0
    avg_words = 0
    avg_sents = 0
    avg_paras = 0

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

        count += 1
        punctuation = set('，。、；：？！“”‘’（）《》【】')
        raw_text_without_punc = ''.join([i for i in ref_text_3 if i not in punctuation])
        avg_chars += len(raw_text_without_punc)
        chunks = seg_to_chunks(ref_text_3)
        for chunk in chunks:
            sens = seg_to_sens(chunk)
            avg_sents += len(sens)
            words = seg_words([chunk])[0]
            avg_words += len(words)
        paras = seg_to_paras(ref_text_3)
        avg_paras += len(paras)

    avg_chars /= count
    avg_words /= count
    avg_paras /= count
    avg_sents /= count

    print('avg_chars:', avg_chars)
    print('avg_words:', avg_words)
    print('avg_sents:', avg_sents)
    print('avg_paras:', avg_paras)
    print('count:', count)


if __name__ == '__main__':
    base_path = r'D:\Code\Ch_Doc_Simp_Dataset\Eval_Docs'
    read_and_print_contents(base_path)
