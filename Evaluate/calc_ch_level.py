# 计算文本可读性
import re
import jieba
import cntext as ct
import numpy as np
STOPWORDS_zh = ct.load_pkl_dict(file='STOPWORDS.pkl')['STOPWORDS']['chinese']
STOPWORDS_en = ct.load_pkl_dict(file='STOPWORDS.pkl')['STOPWORDS']['english']
ADV_words = ct.load_pkl_dict(file='ADV_CONJ.pkl')['ADV']
CONJ_words = ct.load_pkl_dict(file='ADV_CONJ.pkl')['CONJ']

# 中文分词
def cn_seg_sent(text):
    #split the chinese text into sentences
    text = re.sub('([。！；？;\?])([^”’])', "[[end]]", text)  # 单字符断句符
    text = re.sub('([。！？\?][”’])([^，。！？\?])', "[[end]]", text)
    text = re.sub('\s', '', text)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    return text.split("[[end]]")

def readability(text, zh_advconj=None, lang='chinese'):
    """
    text readability, the larger the indicator, the higher the complexity of the article and the worse the readability.
    :param text: text string
    :param zh_advconj Chinese conjunctions and adverbs, receive list data type. By default, the built-in dictionary of cntext is used
    :param language: "chinese" or "english"; default is "chinese"
    ------------
    【English readability】english_readability = 4.71 x (characters/words) + 0.5 x (words/sentences) - 21.43；
    【Chinese readability】  Refer 【徐巍,姚振晔,陈冬华.中文年报可读性：衡量与检验[J].会计研究,2021(03):28-44.】
                 readability1  ---每个分句中的平均字数
                 readability2  ---每个句子中副词和连词所占的比例
                 readability3  ---参考Fog Index， readability3=(readability1+readability2)×0.5
                 以上三个指标越大，都说明文本的复杂程度越高，可读性越差。
    """
    if lang=='english':
        text = text.lower()
        #将浮点数、整数替换为num
        text = re.sub('\d+\.\d+|\.\d+', 'num', text)
        num_of_characters = len(text)
        #英文分词
        rgx = re.compile("(?:(?:[^a-zA-Z]+')|(?:'[^a-zA-Z]+))|(?:[^a-zA-Z']+)")
        num_of_words = len(re.split(rgx, text))
        #分句
        num_of_sentences = len(re.split('(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text))
        ari = (
                4.71 * (num_of_characters / num_of_words)
                + 0.5 * (num_of_words / num_of_sentences)
                - 21.43
        )
        return {"readability": ari}
    if lang=='chinese':
        if zh_advconj:
            adv_conj_words = zh_advconj
        else:
            adv_conj_words = set(ADV_words + CONJ_words)
        zi_num_per_sent = []
        adv_conj_ratio_per_sent = []
        text = re.sub('\d+\.\d+|\.\d+', 'num', text)
        #【分句】
        sentences = cn_seg_sent(text)
        for sent in sentences:
            adv_conj_num = 0
            zi_num_per_sent.append(len(sent))
            words = list(jieba.cut(sent))
            for w in words:
                if w in adv_conj_words:
                    adv_conj_num+=1
            adv_conj_ratio_per_sent.append(adv_conj_num/(len(words)+1))
        readability1 = np.mean(zi_num_per_sent)
        readability2 = np.mean(adv_conj_ratio_per_sent)
        readability3 = (readability1+readability2)*0.5
        return {'readability1': readability1,
                'readability2': readability2,
                'readability3': readability3}


if __name__ == '__main__':
    text1 = "我是个小孩子，我想快快乐乐地成长，慢慢长大。"
    text2 = '赵客缦胡缨，吴钩霜雪明。银鞍照白马，飒沓如流星。十步杀一人，千里不留行。事了拂衣去，深藏身与名。闲过信陵饮，脱剑膝前横。将炙啖朱亥，持觞劝侯嬴。三杯吐然诺，五岳倒为轻。眼花耳热后，意气素霓生。救赵挥金槌，邯郸先震惊。千秋二壮士，烜赫大梁城。纵死侠骨香，不惭世上英。谁能书阁下，白首太玄经。'
    print(readability(text1, lang='chinese'))
    print(readability(text2, lang='chinese'))


