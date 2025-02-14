# 语法
import hanlp

from Methods.word_aspect import seg_words


def seg_to_sens(chunk):
    sents_generator = hanlp.utils.rules.split_sentence(chunk)
    return list(sents_generator)


def dp_tree(sentences):
    seg_words_sentences = seg_words(sentences)
    dp = hanlp.load(hanlp.pretrained.dep.CTB9_DEP_ELECTRA_SMALL)
    doc = dp(seg_words_sentences)
    return doc


# 参考了HSK的语法等级划分标准, 依存句法分析
def sentence_difficulty_dep(dep_tree):
    # 计算句子长度
    sentence_length = len(dep_tree)

    # 计算最大依存深度
    max_depth = max(find_depth(node, dep_tree) for node in dep_tree)

    # 检查复杂结构
    complex_structures = sum(1 for node in dep_tree if node['deprel'] in ['rcmod', 'conj', 'ccomp', 'xcomp'])

    # 计算得分
    score = sentence_length + max_depth * 2 + complex_structures * 3

    # 根据得分确定难度等级
    if score < 15:
        return "简单"
    elif score < 30:
        return "中等"
    else:
        return "复杂"


def find_depth(node, dep_tree):
    if node['head'] == 0:
        return 0
    parent = next(n for n in dep_tree if n['id'] == node['head'])
    return 1 + find_depth(parent, dep_tree)


# 成分句法分析
def sentence_complexity_con(tree):
    # 句子长度
    sentence_length = len(tree.leaves())

    # 树的深度
    tree_depth = tree.height()

    # 从句数量
    clause_count = len([t for t in tree.subtrees() if t.label() in ['IP', 'CP']])

    # NP和VP的数量
    np_vp_count = len([t for t in tree.subtrees() if t.label() in ['NP', 'VP']])

    # 特殊结构数量(这里以并列结构为例)
    special_structure_count = len([t for t in tree.subtrees() if t.label() == 'ADVP'])

    # 计算复杂度得分
    complexity_score = (sentence_length * 0.1 +
                        tree_depth * 0.2 +
                        clause_count * 0.3 +
                        np_vp_count * 0.2 +
                        special_structure_count * 0.2)

    # 根据得分划分难度等级
    if complexity_score < 5:
        return "简单", complexity_score
    elif complexity_score < 10:
        return "中等", complexity_score
    else:
        return "复杂", complexity_score


nlp = hanlp.pipeline().append(hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH), output_key='tok') \
    .append(hanlp.load(hanlp.pretrained.pos.CTB9_POS_ELECTRA_SMALL), input_key='tok', output_key='pos') \
    .append(hanlp.load(hanlp.pretrained.constituency.CTB9_CON_FULL_TAG_ELECTRA_SMALL), input_key='tok',
            output_key='con')


def sentence_difficulty_con(sentence):
    doc = nlp(sentence)
    tree = doc['con']
    difficulty, score = sentence_complexity_con(tree)
    return difficulty


def weighted_difficulty(dep_difficulty, con_difficulty):
    # 定义难度等级到数值的映射
    difficulty_map = {
        "简单": 1,
        "中等": 2,
        "复杂": 3
    }

    # 将难度等级转换为数值
    dep_score = difficulty_map[dep_difficulty]

    con_score = difficulty_map[con_difficulty]


    # 计算加权平均分数（五五开）
    weighted_score = (dep_score * 0.5) + (con_score * 0.5)
    print(f"加权分数: {weighted_score}")
    if dep_difficulty == "复杂" and con_difficulty == "复杂":
        return "复杂"

    # 根据加权分数确定最终难度等级
    if weighted_score < 2.5:
        return "简单"
    else:
        return "中等"



def calc_complex_sen_frequency(doc):
    sentences_dptrees_list = []
    result = seg_to_sens(doc)
    sent_nums = len(result)
    dp_trees = dp_tree(result)
    complex_sen_count = 0
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
            complex_sen_count += 1
    complex_sen_frequency = complex_sen_count / sent_nums
    return complex_sen_frequency

def simp_sentence_prompt(sentence):
    prompt = f"""请对给定的中文文本进行简化处理，主要针对复杂句子。你的任务是：
        1. 在保持原文含义的前提下，通过拆解、组合、调整语序等方式，对复杂句子结构进行简化。
        2. 请注意，你只需要简化句子的结构，而至于汉字、词汇等内容相关的要素不可以修改。
        3. 以JSON格式输出结果，包含以下两个键值对：
           - "simp_type": 提供针对复杂句子结构的简化方式，从【拆分，组合，调整语序，转换句式】中选择一个或多个。
           - "simplified_text": 最终简化后的完整文本。
        请确保简化后的文本保持原意，同时提高可读性。

        示例输入：
        [虽然天气预报说今天会下雨，但是早上起来的时候却发现阳光明媚，这使得他决定还是去公园散步，不过他还是带上了雨伞以防万一。]

        示例输出：
        ```json
        {{
        "simp_type": ["拆分", "调整语序"],
        "simplified_text": "早上起来的时候发现阳光明媚，尽管天气预报说今天会下雨。他决定去公园散步，不过他还是带上了雨伞以防万一。"
        }}
        ```
    请根据以上说明处理下面的文本：
    原始文本：[{sentence}]\n
    """
    return prompt


if __name__ == '__main__':
    chunk = """据说，南宋绍兴年间，抗金名将岳飞在北伐途中路过诸葛亮的故里――隆中。是夜，他借宿于草庐。秋风萧瑟，月白窗前，勾起他激荡难已的家国之思。剪亮烛光，展读武侯留下的《出师表》，他，不觉泪湿征衫，于是便力运千钧，笔走龙蛇，用遒劲而潇洒的行草，一口气录下了这篇感人肺腑的表文。从此，将军的墨宝就与丞相的文章交相辉映，流颂四海……
    文档简化(Document Simplification,DS)任务是在尽量保持一篇文章的原本含义不改变的情况下，将其按照不同的级别进行简化，使其更加简洁易懂[1]。文档简化是一种典型的序列到序列任务，这类似于机器翻译[]、文档摘要[]。文档简化因其可以提高文本可读性的特征，对于学生[2]、非母语人士[3]、认知障碍人士[4]等人群的阅读学习活动具有重要意义。
先前的工作专注于文档简化的子任务，例如词汇简化[5]、句子简化[6]等。而在实际应用中，文字内容往往是以文档形式出现的，因此针对文档级别的简化是更为常见和重要的。此外，针对文档简化的研究主要集中在英语上[]，而中文相关的研究非常匮乏，其主要原因有两个：第一，中文语言结构的复杂性较高，句子结构和词汇用法灵活多变，给文档简化带来了额外的挑战[]。第二，相比于英文，中文的简化资源（如简化文本对、语料库等）更为稀缺[]。
值得庆幸的是，关于中文文本可读性评估的研究正在逐步兴起[---]，该研究主要包括如何制定不同等级的文本可读性标准以及如何利用这样的标准评估中文文本的可读性，这为中文文档简化提供了理论基础和方法指导。此外，随着人工智能技术的发展，采用智能化方法（例如大语言模型）来辅助甚至代替人工来完成一些复杂数据处理工作成为主流趋势[-]，这为中文文档简化提供了技术支持，能够尽可能地降低人力和财力的投入。
著名的英文文档简化数据集Newsela[]是人类专家根据蓝思(Lexile)可读性分级[]编纂出来的（其中每篇原始文档基本对应4个不同等级的简化版本），借鉴于此，本文提出了一种基于规则增强大语言模型的中文文档分级简化框架(Rule-enhanced Large Language Model for Chinese Document Grading Simplification, RLCDGS)。
RLCDGS采用的规则即不同层面（包括字、词、句、段）以及不同等级（分为一级、二级、三级）的文本可读性标准和一些对应的外部知识库，从待简化文本中按照可读性标准筛选出其中的待简化因素，再从外部知识库中检索出待简化因素对应的知识，将待简化因素和对应的知识动态地构建为提示模板输入给大语言模型，则可以从大语言模型的输出中提取出相关的简化因素并最终拼合为特定等级的简化版本。该框架的运行过程中仅通过制定特定规则来指导和增强大语言模型进行文档简化的能力，不需要使用额外的训练数据、不涉及对模型的参数调整。这种方法可以有效缓解文档简化任务的成本颇高和质量不可控问题。
本文首先收集和对齐了一个带有多个参考简化版本的平行数据集，在该数据集上对RLCDGS进行了评估，然后又使用RLCDGS针对不同类别（包括名家短篇、新闻报道、小说章节、维基百科）的原始文档进行了简化与评估。"""
    # chunk = """HanLP是面向生产环境的自然语言处理工具包。
    # 晓美焰来到北京立方庭参观自然语义科技公司。
    # 徐先生还具体帮助他确定了把画雄鹰、松鼠和麻雀作为主攻目标。
    # 剑桥分析公司多位高管对卧底记者说，他们确保了唐纳德·特朗普在总统大选中获胜。
    # 萨哈夫说，伊拉克将同联合国销毁伊拉克大规模杀伤性武器特别委员会继续保持合作。"""
    calc_complex_sen_frequency(chunk)
