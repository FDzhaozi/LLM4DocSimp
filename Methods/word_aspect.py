import json
import re
from string import punctuation

import hanlp
from transformers import BertTokenizer, BertForMaskedLM, BertModel
import torch
from modelscope.hub.snapshot_download import snapshot_download
from gensim.models import KeyedVectors
from scipy.spatial.distance import cosine

# 在第一级简化开始前，应用命名实体识别技术，将人名、地名、机构名、专有名词等识别出来，不必进行简化（只需在原文中标注该词的类别即可。）
# HSK大纲（高等以上，五级到高等，三级到四级，一二级不需再简化）、频率（98.5以上、80到98.5,70-80，70以下不需再简化）；综合影响大模型的输出（因LLM不能或不容易训练or微调，故在其推理阶段优化模型输出）
# 对于一些不常见的字或者词或者成语，词表中可能没有，这时候可以接入互联网查询，避免大模型的幻觉。
# 最后一级的简化，需要特别prompt说明，即使汉字和词语简单常见，也可能需要简化，比如可能存在特殊含义或者特殊用法，例如“是夜”，“是”和“夜”都是常见字，但是“是夜”这个词组的意思可能不是很好理解。
# 在评估阶段，可以使用HSK的xx词xx比率、频率、相似度-复杂度作为指标来评价简化质量的分级。(长度、 FKGL、音节、笔画等等，中文论文 。。)


# 不管是字替换还是词替换，都要声明不能直接替换，而是要在上下文中进行合理替换再加修整，确保原文的含义不变和通顺流畅。
# 不管是字替换还是词替换，要增加一个参数，该参数可以启动简化性确保，因为替换后的字或词也有可能是复杂词，需要对齐进行循环检测，直到满足简化性要求。（如果生成的替换字或者词仍然被鉴定为复杂词，那么在下一轮的对大模型的请求中需要额外声明不可以生成上述被鉴定为复杂词的那个词）。
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from concurrent.futures import ThreadPoolExecutor, as_completed

from Database.select_target import query_freq, query_abbre, query_idiom, query_word, query_ci, query_level, \
    insert_into_sims, query_sims, query_word_freq


from Utiles.configs import load_config, get_work_path

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH= 'https://file.hankcs.com/hanlp/tok/coarse_electra_small_20220616_012050.zip'
# Electra (Clark et al. 2020) small model trained on coarse-grained CWS corpora. Its performance is P: 98.34% R: 98.38% F1: 98.36% which is much higher than that of MTL model
# Clark K., Luong M., Le Q., & Manning C. ELECTRA: pre-training text encoders as discriminators rather than generators. In ICLR. 2020. URL: https://openreview.net/pdf?id=r1xMH1BtvB.
tok = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH, devices=device)

config_path = r"../Utiles/config.yml"
work_path = get_work_path()
config = load_config(config_path)
hanzi_hsk_path = work_path + config['hanzi_hsk_path']
ci_hsk_path = work_path + config['ci_hsk_path']
freq_db_path = work_path + config['freq_db_path']
abbre_db_path = work_path + config['abbre_db_path']
ci_db_path = work_path + config['cis_db_path']
idiom_db_path = work_path + config['idioms_db_path']
level_db_path = work_path + config['level_db_path']
word_freq_db_path = work_path + config['word_freq_db_path']
ch_word2vec_path = config['ch_word2vec_bin_path']
sim_db_path = work_path + config['sim_db_path']


def download_model(model_name: str, cache_dir: str = None, revision: str = None):
    model_dir = snapshot_download(model_name, cache_dir=cache_dir, revision=revision)
    return model_dir


def seg_words(sentences: list[str]):
    # 用于分词的模型

    result = tok(sentences)
    return result


def seg_to_sens(chunk):
    sents_generator = hanlp.utils.rules.split_sentence(chunk)
    return list(sents_generator)

ner_pipeline = pipeline(Tasks.named_entity_recognition, 'damo/nlp_raner_named-entity-recognition_chinese-base-generic')


def ner_words(text: str, threshold: float = 0.15):
    type_dict = {"GPE": "地名", "LOC": "地名", "ORG": "机构名", "PER": "人名"}
    ner_dict = {}
    result = ner_pipeline(text)
    if result is not None:
        for entry in result['output']:
            if entry["prob"] > threshold:
                ner_dict[entry["span"]] = type_dict[entry["type"]]
    return ner_dict


def query_char_level(char: str, json_path: str):
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for entry in data:
            if entry["word"] == char:
                return entry["level"]
    return None


def query_words_level(words: list[str]):
    result_dict = {}
    for word in words:
        result_dict[word] = query_level(level_db_path, word)
    return result_dict


def query_word_level(word: str):
    return query_level(level_db_path, word)

def sta_words_standard(json_path):
    # Initialize counters
    total_words = 0
    unique_levels = set()

    # Read the JSON file
    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

        # Iterate through each entry in the JSON data
        for entry in data:
            total_words += 1  # Increment total word count
            unique_levels.add(entry["level"])  # Add level to set of unique levels

    # Print the statistics
    print(f"Total number of words: {total_words}")
    print(f"Total number of unique levels: {len(unique_levels)}")
    # char:3149 {'一级', '二级', '三级', '四级', '五级', '六级', '高等'}'
    # word:11092 {'一级', '二级', '三级', '四级', '五级', '六级', '高等'}
    print(f"Types of levels: {unique_levels}")


# ver1 只处理超纲字，定义为不在HSK大纲中的字或者字频超过98.5%的字
# ver2 处理HSK大纲中五级以上的字，或者字频在80%到98.5%之间的字
# ver3 处理HSK大纲中三级以上的字，或者字频在50%到80%之间的字
# ver1-3是递进关系，越来越严格的简化要求，更高级的版本包含了低级版本的要求，即高级简化版本的输入是上一级简化版本的输出。
def judge_complex_char(char: str, version: int = 1):
    db_name = freq_db_path
    # 确保char是单个字符
    # 长度为一且不是标点符号
    if len(char) == 1:
        if '\u4e00' <= char <= '\u9fff':
            pass
        else:
            return False
    else:
        return False
    freq = query_freq(db_name, char)
    if freq is None:
        return True
    else:
        freq = float(freq["char_freq"])

    # print(freq)
    level = query_char_level(char, hanzi_hsk_path)
    if version == 1:
        if level is None or freq > 98.5:
            return True
    elif version == 2:
        if level in ["五级", "六级", "高等"] or 80 < freq < 98.5:
            return True
    elif version == 3:
        if level in ["三级", "四级"] or 70 < freq < 80:
            return True
    else:
        return False
    return False


# ver1 只处理超纲词语，超纲词和成语定义为不在HSK大纲中的词汇,或者与“的”字的嵌入距离过远的词和成语（定义为相似度在14%以下的）
# ver2 处理HSK大纲中五级以上的词，或者相似度在14%到18%之间的词
# ver3 处理HSK大纲中三级以上的词，或者相似度在18%到22%之间的词，相似度20%以上的认为不需要简化
# (均为经验值，可以根据实际情况调整)
# ver1-3是递进关系，越来越严格的简化要求，更高级的版本包含了低级版本的要求，即高级简化版本的输入是上一级简化版本的输出。

# 和char不同，词语（bi-gram，tri-gram等）的数目繁多，也难以找寻完整的词频数据库，因此这里使用了一个简化的方法，即通过词语的相似度来判断词语的复杂度，此外使用一个不够完整的bi-gram词频数据库来过滤掉词频很高的常用词语。
def fiter_simp_words(words: list[str], freq: int = 100):
    for word in words:
        result = query_word_freq(word_freq_db_path, word)
        if result is None:
            continue
        if result["freq"] > freq:
            words.remove(word)
            print(f"词语{word}的词频为{result['freq']}，超过了设定的阈值{freq}，已被过滤")
    return words


def judge_complex_words(words: list[str], version: int = 1):
    words = fiter_simp_words(words)
    levels_dict = query_words_level(words)
    need_words = []
    have_sim_dict = {}
    for word in words:
        sim = query_sims(sim_db_path, word)
        if sim is None:
            need_words.append(word)
        else:
            sim_score = sim["sim_value"]
            print(f"数据库中检索到词语{word}的相似度为{sim_score}")
            have_sim_dict[word] = sim_score
    word_pairs = [(word, "我的") for word in need_words]
    with ThreadPoolExecutor(max_workers=8) as executor:
        # 提交任务到线程池
        future_to_word = {executor.submit(get_words_sim, word, base_word): (word, base_word) for word, base_word
                          in word_pairs}

        # 处理结果
        for future in as_completed(future_to_word):
            word, base_word = future_to_word[future]
            try:
                word, sim = future.result()
                print(f"词语{word}与{base_word}的相似度为{sim}")
                if sim is None:
                    continue
                else:
                    sim = float(sim)
                    have_sim_dict[word] = sim
                    # 将sim保留两位插入数据库
                    insert_into_sims(sim_db_path, word, sim)
            except Exception as exc:
                print(f"{base_word}, {word} generated an exception: {exc}")
                continue

    # if sim_score is None:
    #     return False
    # if version == 1:
    #     if level is None or sim_score < 0.10:
    #         return True
    # elif version == 2:
    #     if level in ["五级", "六级", "高等"] or 0.1 < sim_score < 0.15:
    #         return True
    # elif version == 3:
    #     if level in ["三级", "四级"] or 0.15 < sim_score < 0.25:
    #         return True
    # else:
    #     return False

    need_simp_words = []
    for word in words:
        if word not in have_sim_dict.keys():
            continue
        if version == 1:
            print(f"词语 {word} 的HSK等级为{levels_dict[word]}，相似度为{have_sim_dict[word]}")
            if levels_dict[word] is None and have_sim_dict[word] < 0.14:
                need_simp_words.append(word)
        elif version == 2:
            if levels_dict[word] in ["五级", "六级", "高等"] or 0.14 < have_sim_dict[word] < 0.18:
                need_simp_words.append(word)
                print(f"需要进行二级简化的词语{word}")
        elif version == 3:
            if levels_dict[word] in ["三级", "四级"] or 0.18 < have_sim_dict[word] < 0.22:
                need_simp_words.append(word)
                print(f"需要进行三级简化的词语{word}")

    return need_simp_words


def find_explanation(word: str):
    print(f"正在检索{word}的解释...")
    if len(word) == 4:  # 成语
        explanation = query_idiom(idiom_db_path, word)
        if explanation:
            explanation = explanation['explanation']
        else:
            return None
    else:  # 词语
        explanation = query_ci(ci_db_path, word)
        if explanation:
            explanation = explanation['explanation']
        else:
            return None

    return explanation


# 不同于词语和成语，单个汉字往往还有多种解释，所以这里让模型自己根据上下文生成合适的替代和完成替代，而不进行RAG增强，避免引入幻觉（RAG带来幻觉相关论文。）
def simp_char_prompt(text: str, version: int = 1, ban_list: list[str] = None):
    char_and_word = seg_words([text])
    complex_chars = set()
    for char in char_and_word[0]:
        if len(char) == 1:
            if '\u4e00' <= char <= '\u9fff':
                if judge_complex_char(char, version):
                    # print(f"请简化{char}")
                    complex_chars.add(char)
    complex_chars = list(complex_chars)
    if len(complex_chars) == 0:
        return None
    prompt = f"""请对给定的中文文本进行简化处理，主要针对复杂字和生僻字。你的任务是：
    1. 阅读我给出的原始文本和其中蕴含的复杂字和生僻字。
    2. 在保持原文含义的前提下，通过删除或替换这些字来简化文本。
    3. 以JSON格式输出结果，包含以下两个键：
       - "substitutions": 提供每个复杂字或生僻字及其替换表达（如果是删除则提供一个空字符串）。
       - "simplified_text": 最终简化后的完整文本。

    请确保简化后的文本保持原意，同时提高可读性。

    示例输入：[右手，拈着人们熟悉的那把羽毛扇，头戴纶巾，又像是置身于东吴万千军中，从容不迫。]
    复杂字：["拈", "纶"]

    示例输出：
    ```json
    {{
    "substitutions": {{"拈": "拿", "纶": "丝"}},
    "simplified_text": "右手，拿着人们熟悉的那把羽毛扇，头上戴着丝巾，又像是置身于东吴万千军中，从容不迫。"
    }}
    ```
   

请根据以上说明处理下面的文本：
原始文本：[{text}]\n
复杂字：{complex_chars}\n
(请注意，simplified_text的文本中不一定只需要生硬的替换，可以根据上下文进行调整以确保言语通顺。但是与复杂字无关的的文章其余部分千万不要修改！否则会影响文本的简化等级。)
"""
    # if len(complex_chars) > 0 and ban_list is not None:
    #     prompt += f"提示：请注意避免使用以下替换(因为先前的尝试表明这样的替换字同样是复杂字)：{ban_list}\n"
    return prompt


def simp_word_prompt(text: str, version: int = 1, ban_list: list[str] = None):
    """生成简化词语的提示,复杂词不会包括ner_dict中的词和abbre_dict中的词，因为这些词已经被识别为地名、机构名、人名或缩写词，不需要简化。
    但是这些词被返回是需要后续要替换掉原文中的原始词（加入NER识别结果和缩写词识别结果）。
    Returns:
        prompt: str, 提示文本
        ner_dict: dict, NER识别结果
        abbre_dict: dict, 缩写词识别结果
        """
    char_and_word = seg_words([text])
    # 过滤掉已被NER识别为地名、机构名、人名的词
    ner_dict = {}
    sentences = seg_to_sens(text)
    for sentence in sentences:
        if len(sentence) > 500:
            continue
        ner_dict.update(ner_words(sentence))
    char_and_word_without_ner = char_and_word[0] - ner_dict.keys()
    # 过滤掉缩写词
    abbre_dict = {}
    for word in char_and_word_without_ner:
        full_form = query_abbre(abbre_db_path, word)
        if full_form:
            abbre_dict[word] = full_form
    char_and_word_without_ner_and_abbre = char_and_word_without_ner - abbre_dict.keys()
    # 过滤掉单个字符以及各种标点符号
    punctuation = set('，。、；：？！“”‘’（）《》【】')
    char_and_word_without_ner_and_abbre = [word for word in char_and_word_without_ner_and_abbre if
                                           len(word) != 1 and not any(char in word for char in punctuation)]
    # complex_words = set()
    # for word in char_and_word_without_ner_and_abbre:
    #     if len(word) != 1:  # 确保不是单个字符
    #         # 确保不包含任何标点符号
    #         if not any(char in word for char in punctuation):
    #             if judge_complex_word(word, version):
    #                 complex_words.add(word)
    # complex_words = list(complex_words)

    need_simp_words = list(set(judge_complex_words(char_and_word_without_ner_and_abbre, version)))
    if len(need_simp_words) == 0:
        return None, ner_dict, abbre_dict
    complex_words_with_explanation = {}
    for complex_word in need_simp_words:
        print(f"复杂词：{complex_word}")
        explanation = find_explanation(complex_word)
        if explanation:
            complex_words_with_explanation[complex_word] = explanation
        else:
            # complex_words_with_explanation[complex_word] = "暂无解释"
            pass
    prompt = f"""请对给定的中文文本进行简化处理，主要针对复杂词和成语。你的任务是：
    1. 阅读我给出的原始文本和其中蕴含的复杂词和成语及其相关解释。
    2. 在保持原文含义的前提下，通过删除或替换这些词来简化文本。
    3. 以JSON格式输出结果，包含以下两个键：
       - "substitutions": 提供每个复杂词或成语及其替换表达（如果是删除则提供一个空字符串）。
       - "simplified_text": 最终简化后的完整文本。

    请确保简化后的文本保持原意，同时提高可读性。

    示例输入：[右手，拿着人们熟悉的那把羽毛扇，头戴纶巾，又像是置身于东吴万千军中，从容不迫。]
    复杂词及其解释：[{{"纶巾": "1.冠名。古代用青色丝带做的头巾。一说配有青色丝带的头巾。相传三国蜀诸葛亮在军中服用，故又称诸葛巾。", "从容不迫": "从容不慌不忙，很镇静；不迫不急促。不慌不忙，沉着镇定。"}}]

    示例输出：
    ```json
    {{
  "substitutions": {{
    "纶巾": "丝头巾",
    "从容不迫": "沉着镇定"
     }},
  "simplified_text": "右手，拿着人们熟悉的那把羽毛扇，头上戴着丝头巾，又像是置身于东吴万千军中，表现得沉着镇定。"
    }}
    ```

请根据以上说明处理下面的文本：
原始文本：[{text}]\n
复杂词及其解释：[{complex_words_with_explanation}]\n
(请注意，simplified_text的文本中不一定只使用生硬的替换，可以根据上下文进行调整以确保言语通顺。但是，与我提供的复杂词无关的文章其余部分千万不要修改！否则会影响文本的简化等级。)

"""
    # if len(need_simp_words) > 0 and ban_list is not None:
    #     prompt += f"提示：请注意避免使用以下替换(因为先前的尝试表明这样的替换词同样是复杂词)：{ban_list}\n"
    return prompt, ner_dict, abbre_dict


# 计算概率


# D:\Dataset\model\

# # 加载预训练的中文BERT模型和分词器
# model_name = "bert-base-chinese"
# tokenizer = BertTokenizer.from_pretrained(model_name, cache_dir="../bert-base-chinese")
# model = BertForMaskedLM.from_pretrained(model_name, cache_dir="../bert-base-chinese")


# # 利用词向量之间的余弦相似度或欧氏距离来量化词语之间的差异。与更常见的词汇相比，不常见或复杂的词汇在向量空间中可能更孤立。
# model_id = "iic/nlp_gte_sentence-embedding_chinese-large"
# # model_id = "iic/gte_Qwen2-7B-instruct"
# pipeline_se = pipeline(Tasks.sentence_embedding,
#                        model=model_id,
#                        sequence_length=512)


# def get_words_sim(word, base_word="我的", model_id="iic/nlp_gte_sentence-embedding_chinese-large"):
#     # 初始化pipeline
#     # model_id = "iic/nlp_gte_sentence-embedding_chinese-large"
#     # pipeline_se = pipeline(Tasks.sentence_embedding,
#     #                        model=model_id,
#     #                        sequence_length=512)
#
#     # 准备输入
#     inputs = {
#         "source_sentence": [base_word],
#         "sentences_to_compare": [word]
#     }
#
#     # 获取结果
#     result = pipeline_se(input=inputs)
#
#     return result["scores"][0]

def get_words_sim(word, base_word="我的"):
    # "Directional Skip-Gram: Explicitly Distinguishing Left and Right Context for Word Embeddings",

    # path = r"D:\Dataset\model\tencent-ailab-embedding-zh-d200-v0.2.0-s\tencent-ailab-embedding-zh-d200-v0.2.0-s\tencent-ailab-embedding-zh-d200-v0.2.0-s\\"
    # file = 'tencent-ailab-embedding-zh-d200-v0.2.0-s.txt'
    # model = KeyedVectors.load_word2vec_format(path + file, binary=False)
    # model.save(path + 'Tencent_AILab_ChineseEmbedding.bin')

    try:
        model = KeyedVectors.load(ch_word2vec_path)
        sim = model.similarity(base_word, word)
        print(f"词语  {word}  与  {base_word}  的相似度为{sim}")
    except KeyError:
        sim = None

    # from fasttext import load_model
    #
    # # 加载预训练的FastText模型
    # fasttext_model = load_model(ch_word2vec_path)
    #
    # # 计算相似度
    # sim = fasttext_model.similarity(base_word, word)

    return word, sim


if __name__ == '__main__':
    # s1 = "和清华大学化学系曹小平教授约定的采访时间是上午10时，身高1.84米的曹教授早早就在门口等候。谈起31年前赴美留学的经历，他如数家珍，信手拈来。"
    # s2 = "所以，及早注意到美国某些大学“宰”人的现象，非常值得留学生和家长的重视。"
    # sentences = [s1, s2]
    # result = seg_words(sentences)
    # for char_word in result:
    #     print(char_word)
    #     print()

    # json_path = "HSK_standard/汉字.json"
    # sta_words_standard(json_path)
    # json_path = "HSK_standard/词语.json"
    # sta_words_standard(json_path)

    # # 使用示例
    # base_word = "的"
    # words_to_compare = ["量子", "今天", "耄耋", "的", "苹果"]
    #
    # for word in words_to_compare:
    #     similarity = get_words_sim(word, base_word)
    #     print(f"词语 '{word}' 与 '{base_word}' 的相似度: {similarity:.4f}")
    #     complexity = 1 - similarity
    #     print(f"词语 '{word}' 的复杂度分数: {complexity:.4f}")

    #     doc = """1、我很重要毕淑敏
    # # 当我说出“我很重要”这句话的时候，颈项后面掠过一阵战栗。我知道这是把自己的额头裸露在弓箭之下了，心灵极容易被别人的批判洞伤。许多年来，没有人敢在光天化日之下表示自己“很重要”。我们从小受到的教育都是――“我不重要”。
    # # 作为一名普通士兵，与辉煌的胜利相比，我不重要。
    # # 作为一个单薄的个体，与浑厚的集体相比，我不重要。
    # # 作为一位奉献型的女性，与整个家庭相比，我不重要。
    # # 作为随处可见的人的一分子，与宝贵的物质相比，我们不重要。
    # # 我们――简明扼要地说，就是每一个单独的“我”――到底重要还是不重要?
    # # 我是由无数星辰日月草木山川的精华汇聚而成的。只要计算一下我们一生吃进去多少谷物，饮下了多少清水，才凝聚成一具美轮美奂的躯体，我们一定会为那数字的庞大而惊讶。平日里，我们尚要珍惜一粒米、一叶菜，难道可以对亿万粒菽粟亿万滴甘露濡养出的万物之灵，掉以丝毫的轻心吗?
    # # 当我在博物馆里看到北京猿人窄小的额和前凸的吻时，我为人类原始时期的粗糙而黯然。他们精心打制出的石器，用今天的目光看来不过是极简单的玩具。如今很幼小的孩童，就能熟练地操纵语言，我们才意识到已经在进化之路上前进了多远。我们的头颅就是一部历史，无数祖先进步的痕迹储存于脑海深处。我们是一株亿万年苍老树干上最新萌发的绿叶，不单属于自身，更属于土地。人类的精神之火，是连绵不断的链条，作为精致的一环，我们否认了自身的重要，就是推卸了一种神圣的承诺。
    # # 回溯我们诞生的过程，两组生命基因的嵌合，更是充满了人所不能把握的偶然性。我们每一个个体，都是机遇的产物。
    # # 常常遥想，如果是另一个男人和另一个女人，就绝不会有今天的我……
    # # 即使是这一个男人和这一个女人，如果换了一个时辰相爱，也不会有此刻的我……
    # # 即使是这一个男人和这一个女人在这一个时辰，由于一片小小落叶或是清脆鸟啼的打搅，依然可能不会有如此的我……
    # # 一种令人怅然以至走入恐惧的想象，像雾霭一般不可避免地缓缓升起，模糊了我们的来路和去处，令人不得不断然打住思绪。"""

    doc = """很早，很早以前，我就相信这个传说，而且，相信它必定是真实的。
据说，南宋绍兴年间，抗金名将岳飞在北伐途中路过诸葛亮的故里――隆中。是夜，他借宿于草庐。秋风萧瑟，月白窗前，勾起他激荡难已的家国之思。剪亮烛光，展读武侯留下的《出师表》，他，不觉泪湿征衫，于是便力运千钧，笔走龙蛇，用遒劲而潇洒的行草，一口气录下了这篇感人肺腑的表文。从此，将军的墨宝就与丞相的文章交相辉映，流颂四海……
每当我踏进成都武候祠，仰望那高悬在大殿内的岳公的木刻手迹，心情总是十分激动。有的人活着，等同死去；有的人长眠九泉，却永远活在我们心中。上下五千年，纵横一万里，在中国这块古老的土地上，奔驰过多少盘马弯弓、叱咤风云的英雄好汉！可是，能够真正属于历史而不朽者，复有几人？我以为，诸葛亮恰恰是这样一位值得后世景仰的伟大人物。
在故乡锦城的游览胜地中，武候祠乃是一个值得去的地方。每次度假归来或出差经过，哪怕只有短短的三两天，我几乎总要带着几分思古的向慕之心去走一走，而回回都能增强我对历史的洞察力，获得某种新的精神升华。
祠堂位处城市的南梢，东连万里桥；西头，与数里外杜甫草堂的那片茂林修竹悠然相望。确切地说，他本当称为“汉昭烈庙”或“惠陵”。因为，这里不仅供奉有蜀汉昭烈皇帝刘备的灵位，而且青冢巍然，埋葬者先主并甘、吴二夫人的遗骸。武乡侯的祠堂，不过是帝庙旁的一个配享。丞相的墓地，远在陕西的定军山下。然而，一代一代的人们还是爱把这里叫做武候祠。
推开祠庙前那两扇沉厚的暗红漆的大门，一条青砖步道便直贯而入，将庭院中分为二。道旁，夹峙着古碑数通。右边一块唐碑，高可丈五，碑帽镌有华美的云纹，距今业已一千一百余岁。油黑的碑面上，铭刻着一篇褒颂诸葛亮的文字，作者是中唐名相裴度。由柳公绰（书法大师柳公权之兄）书丹，工匠鲁健执刀勒石。因文章、书法、刻字均佳，谷有“三绝碑”之称。砖道左侧一碑立于明朝，碑身拙厚，驮于龟趺之上，碑文详述了祠庙的来历和变迁。
武候祠的建立也曾有过一番波折。据《三国志》裴注引《襄阳记》云：“亮初亡，所在各求为立庙，朝议以礼秩不听，百姓遂因时节私祭之于道陌上。言事者或以为可听立庙于成都者，后主不从。步兵校尉习隆、中书郎向充等共上表曰：‘……亮德范遐迩，功盖季世，王室之不坏，实斯人是赖……‘于是始从之。’”后魏将军钟会征蜀，亦“祭亮之庙”。
替高人义士立享祠，在汉代本属常见的事。诸葛亮一腔公忠，匡扶两朝，无疑是蜀汉的头号功臣；且先主刘备临死前，托孤于白帝，嘱刘禅兄弟以父礼事丞相；丞相殉国后，后主却公然违背民意，吞吞吐吐，始终不肯在都城替武侯立祠，其人心性如此，千载之下，尚令人齿冷！
首先在成都为武侯建祠的倒是农民的领袖李特、李雄父子。当时，李氏率饥民攻占蜀都，推翻了西晋王朝在四川的腐朽统治。后来，东晋大将桓温逐兵入蜀，以百倍的疯狂焚毁了成都，却独独不敢把武候祠烧去。
比起昏庸的阿斗，桓温毕竟要聪明一些。
岁月如流，武候祠也屡屡迁址。明初，朱元璋的儿子朱椿来蜀就藩，决定把祠基移往锦江南岸的惠陵近旁，与刘备庙合祭，以示“君臣一体”。此后，又经历了数百年的损毁修葺，便成为现今这样的规模。
从小爱读杜诗，每当读到《蜀相》，吟味“丞相祠堂何处寻，锦官城外柏森森。映阶碧草自春色，隔叶黄鹂空好音”的名句，一颗心，往往会沉浸到那种极其清幽庄穆的氛围中去。那么，今日的武候祠外，是否还有几许杜甫当年的古意呢？
绕过文臣武将塑像长廊，穿过先主正殿，就来到诸葛殿前。每逢四月春深，庭中香花扑鼻，草木葳蕤，分外怡人。站在庭前举目环顾，但见左钟右鼓，前亭后榭，布局精巧，错落有致。走完回廊，跨过石桥，刻通向桂荷楼，楼前自然是碧水一潭。到了秋天，这里荷叶田田，丹桂飘馨，另有一番情趣。小楼外侧，有亭翼然。亭中置石琴一架，不免使人联想起罗贯中《三国演义》第九十五回“武侯弹琴退仲达”的场面。也许，在月色皎好的夜晚，丞相魂兮南来，还会在亭中抚琴清操一曲，向陵墓中的先主娓娓述说当年隆中晤对的知遇之恩……
诸葛殿高大而宏敞。飞檐凌空，气势不凡。门外有细砂石栏，有纹铁香炉，有历代名流题下的楹联。门楣上，迎面一幅巨匾，灿然书写着四个闪金的大字――“名垂宇宙”。
他，安详地坐在堂上。金身玉面，黑髯飘拂，神采奕奕，气宇轩昂。左手扶膝，似在深心运筹北伐大计；右手，拈着人们熟悉的那把羽毛扇，又像是置身于东吴万千军中，从容不迫，舌战群儒……
肃立在他的雕像前，我每每浮想联翩。
诸葛亮不是历史的幸运儿，他那灭魏吞吴的宏愿始终未能实现。他也不是完人，更不是小说中那个踏罡步斗、呼风唤雨的神仙。论才学，他稍逊庞统；比奇谋，他不如法正（这在史书上都有记载），同时更没有关、张之辈值得夸耀的资历。可是，为什么千百年来他却得到那样多的同情、敬佩与爱戴？
他生于群雄并起的炎汉季世，待到刘皇叔三顾频繁之际，曹阿瞒早已横扫诸袁，奄有了北方的大部，碧眼儿也坐稳了江东。人们常常扼腕叹息，叹息他随逢明主却未获天时。然而，即使这样，他还是竭尽人谋，提出取荆州、定西川、三分天下而后联吴伐魏的正确战略。殊不料彝陵一败，先主崩殂，在极度的艰难困苦之中，他毅然挑起军国重担，坚持北伐，直到�}志以殁。
北伐中原利耶弊耶？那是研究者们的事情。历史最怕的是假设。可是，有一些事实却是无法抹煞的。
――他平定南中，夷心归化；
他发展农桑，境内安康；
他厉行法制，贵贱无欺；
他严勒军纪，众口皆碑。
至于他本人，则廉洁奉公，惟有一些薄田和桑树供子弟读书、生活，而自己则不增一寸生财，“随身衣食，悉仰于官”，真可谓两袖清风！临终前，他拒绝厚葬，并指定要埋在汉中前线，他要亲眼看见大汉的旌旗插向长安、插向中原……
“其身正，不令而行；其身不正，虽令不行。”心中有人民，人民才会为他的事业去奋斗、去效死，这真是一条万古不变的至理！
在南中，各族人民怀念他，亲切地唤他“孔明老爹”；鼓称“诸葛鼓”，他带兵翻过的大山，后人取名“相公岭”。到处都有他的遗迹，在湖北，在陕西，在甘肃，在四川。剑阁有“武侯坡”，勉县有“读书台”，长江有“水八阵”……成都西北郊有一处地名叫“九里堤”，现在已经寻找不到什么痕迹了，当年却有一条坚实的大堤，挡住府河的激流，保护了大量的良田。而九里堤人们又称为“诸葛堤”。不管这个说法是否有依据，实际上，他已经成为一个德范万世的表率，已经化为一座石的雕像，或者，一颗植根于人民心田的枝叶常青的大树……
于是，我又想起那挺立在武候祠前的古柏。
古柏崔嵬，黛色参天，环卫着汉家君臣的英灵，向来往的游人投下如盖的春荫。我经常留连于古柏下，伸出手，去抚摸它青铜一般坚泽的表皮，久久不忍离去。某日，一位在树荫下舞剑的老人向我走来，莞尔一笑道：
“喜欢这大树么？”
我点点头。
“可晓得它的故事？”
我不觉茫然。
老者捋捋白雪似的长须，向我一一道来。
有一年，嘉靖皇帝忽然想在北京城里修建乾清宫，于是下令各地搜献大木奇材。有个贪官鬼迷心窍，竟然打起武候祠前那一行柏树的主意。他假借祭祠之名封闭了祠院大门，命人砍伐。哪知一斧下去，猛然间风云四合，飞来无数鸦鸟，绕柏怒噪，直扑人面。砍树的衙役被赶得东奔西跑，那官员想溜，早被鸟儿们追上，叼去乌纱帽，狠狠地啄去，啄瞎了他一双狗眼！
真有这样的事情么？
“嗨！”见我信疑参半，老人竟认真起来，涨红了脸，手一指，说：
“看看去！那棵柏树上，还留下斧头印子呢！”
说罢，愤愤地将剑塞向剑鞘，扭头便去。
我不知道我是否找到了斧头印，但却再也无法忘记白胡子老人讲的这个故事。虽然它和岳飞题写《出师表》一样，仅仅是个传说，我却敢断定，它，必定也是千真万确的。
（作者：刘征泰）"""

    pass
