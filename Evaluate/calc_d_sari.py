from __future__ import division

import random
import re
from collections import Counter
from easse.sari import corpus_sari
import sys

from nltk.tokenize import word_tokenize
import nltk

import math




def ReadInFile(filename):
    with open(filename) as f:
        lines = f.readlines()

        lines = [x.strip() for x in lines]

    return lines


def D_SARIngram(sgrams, cgrams, rgramslist, numref):
    rgramsall = [rgram for rgrams in rgramslist for rgram in rgrams]

    rgramcounter = Counter(rgramsall)

    sgramcounter = Counter(sgrams)

    sgramcounter_rep = Counter()

    for sgram, scount in sgramcounter.items():
        sgramcounter_rep[sgram] = scount * numref

    cgramcounter = Counter(cgrams)

    cgramcounter_rep = Counter()

    for cgram, ccount in cgramcounter.items():
        cgramcounter_rep[cgram] = ccount * numref

    # KEEP

    keepgramcounter_rep = sgramcounter_rep & cgramcounter_rep

    keepgramcountergood_rep = keepgramcounter_rep & rgramcounter

    keepgramcounterall_rep = sgramcounter_rep & rgramcounter

    keeptmpscore1 = 0

    keeptmpscore2 = 0

    for keepgram in keepgramcountergood_rep:
        keeptmpscore1 += keepgramcountergood_rep[keepgram] / keepgramcounter_rep[keepgram]

        keeptmpscore2 += keepgramcountergood_rep[keepgram] / keepgramcounterall_rep[keepgram]

        # print "KEEP", keepgram, keepscore, cgramcounter[keepgram], sgramcounter[keepgram], rgramcounter[keepgram]

    keepscore_precision = 0

    if len(keepgramcounter_rep) > 0:
        keepscore_precision = keeptmpscore1 / len(keepgramcounter_rep)

    keepscore_recall = 0

    if len(keepgramcounterall_rep) > 0:
        keepscore_recall = keeptmpscore2 / len(keepgramcounterall_rep)

    keepscore = 0

    if keepscore_precision > 0 or keepscore_recall > 0:
        keepscore = 2 * keepscore_precision * keepscore_recall / (keepscore_precision + keepscore_recall)

    # DELETION

    delgramcounter_rep = sgramcounter_rep - cgramcounter_rep

    delgramcountergood_rep = delgramcounter_rep - rgramcounter

    delgramcounterall_rep = sgramcounter_rep - rgramcounter

    deltmpscore1 = 0

    deltmpscore2 = 0

    for delgram in delgramcountergood_rep:
        deltmpscore1 += delgramcountergood_rep[delgram] / delgramcounter_rep[delgram]

        deltmpscore2 += delgramcountergood_rep[delgram] / delgramcounterall_rep[delgram]

    delscore_precision = 0

    if len(delgramcounter_rep) > 0:
        delscore_precision = deltmpscore1 / len(delgramcounter_rep)

    delscore_recall = 0

    if len(delgramcounterall_rep) > 0:
        delscore_recall = deltmpscore1 / len(delgramcounterall_rep)

    delscore = 0

    if delscore_precision > 0 or delscore_recall > 0:
        delscore = 2 * delscore_precision * delscore_recall / (delscore_precision + delscore_recall)

    # ADDITION

    addgramcounter = set(cgramcounter) - set(sgramcounter)

    addgramcountergood = set(addgramcounter) & set(rgramcounter)

    addgramcounterall = set(rgramcounter) - set(sgramcounter)

    addtmpscore = 0

    for addgram in addgramcountergood:
        addtmpscore += 1

    addscore_precision = 0

    addscore_recall = 0

    if len(addgramcounter) > 0:
        addscore_precision = addtmpscore / len(addgramcounter)

    if len(addgramcounterall) > 0:
        addscore_recall = addtmpscore / len(addgramcounterall)

    addscore = 0

    if addscore_precision > 0 or addscore_recall > 0:
        addscore = 2 * addscore_precision * addscore_recall / (addscore_precision + addscore_recall)

    return (keepscore, delscore_precision, addscore)


def count_length(ssent, csent, rsents):
    input_length = len(ssent.split(" "))

    output_length = len(csent.split(" "))

    reference_length = 0

    for rsent in rsents:
        reference_length += len(rsent.split(" "))

    reference_length = int(reference_length / len(rsents))

    return input_length, reference_length, output_length


def sentence_number(csent, rsents):
    output_sentence_number = len(nltk.sent_tokenize(csent))

    reference_sentence_number = 0

    for rsent in rsents:
        reference_sentence_number += len(nltk.sent_tokenize(rsent))

    reference_sentence_number = int(reference_sentence_number / len(rsents))

    return reference_sentence_number, output_sentence_number


def D_SARIsent(ssent, csent, rsents):
    numref = len(rsents)

    s1grams = ssent.lower().split(" ")

    c1grams = csent.lower().split(" ")

    s2grams = []

    c2grams = []

    s3grams = []

    c3grams = []

    s4grams = []

    c4grams = []

    r1gramslist = []

    r2gramslist = []

    r3gramslist = []

    r4gramslist = []

    for rsent in rsents:

        r1grams = rsent.lower().split(" ")

        r2grams = []

        r3grams = []

        r4grams = []

        r1gramslist.append(r1grams)

        for i in range(0, len(r1grams) - 1):

            if i < len(r1grams) - 1:
                r2gram = r1grams[i] + " " + r1grams[i + 1]

                r2grams.append(r2gram)

            if i < len(r1grams) - 2:
                r3gram = r1grams[i] + " " + r1grams[i + 1] + " " + r1grams[i + 2]

                r3grams.append(r3gram)

            if i < len(r1grams) - 3:
                r4gram = r1grams[i] + " " + r1grams[i + 1] + " " + r1grams[i + 2] + " " + r1grams[i + 3]

                r4grams.append(r4gram)

        r2gramslist.append(r2grams)

        r3gramslist.append(r3grams)

        r4gramslist.append(r4grams)

    for i in range(0, len(s1grams) - 1):

        if i < len(s1grams) - 1:
            s2gram = s1grams[i] + " " + s1grams[i + 1]

            s2grams.append(s2gram)

        if i < len(s1grams) - 2:
            s3gram = s1grams[i] + " " + s1grams[i + 1] + " " + s1grams[i + 2]

            s3grams.append(s3gram)

        if i < len(s1grams) - 3:
            s4gram = s1grams[i] + " " + s1grams[i + 1] + " " + s1grams[i + 2] + " " + s1grams[i + 3]

            s4grams.append(s4gram)

    for i in range(0, len(c1grams) - 1):

        if i < len(c1grams) - 1:
            c2gram = c1grams[i] + " " + c1grams[i + 1]

            c2grams.append(c2gram)

        if i < len(c1grams) - 2:
            c3gram = c1grams[i] + " " + c1grams[i + 1] + " " + c1grams[i + 2]

            c3grams.append(c3gram)

        if i < len(c1grams) - 3:
            c4gram = c1grams[i] + " " + c1grams[i + 1] + " " + c1grams[i + 2] + " " + c1grams[i + 3]

            c4grams.append(c4gram)

    (keep1score, del1score, add1score) = D_SARIngram(s1grams, c1grams, r1gramslist, numref)

    (keep2score, del2score, add2score) = D_SARIngram(s2grams, c2grams, r2gramslist, numref)

    (keep3score, del3score, add3score) = D_SARIngram(s3grams, c3grams, r3gramslist, numref)

    (keep4score, del4score, add4score) = D_SARIngram(s4grams, c4grams, r4gramslist, numref)

    avgkeepscore = sum([keep1score, keep2score, keep3score, keep4score]) / 4

    avgdelscore = sum([del1score, del2score, del3score, del4score]) / 4

    avgaddscore = sum([add1score, add2score, add3score, add4score]) / 4

    input_length, reference_length, output_length = count_length(ssent, csent, rsents)

    reference_sentence_number, output_sentence_number = sentence_number(csent, rsents)

    if output_length >= reference_length:

        LP_1 = 1

    else:

        LP_1 = math.exp((output_length - reference_length) / output_length)

    if output_length > reference_length:

        LP_2 = math.exp((reference_length - output_length) / max(input_length - reference_length, 1))

    else:

        LP_2 = 1

    SLP = math.exp(-abs(reference_sentence_number - output_sentence_number) / max(reference_sentence_number,
                                                                                  output_sentence_number))

    avgkeepscore = avgkeepscore * LP_2 * SLP * 100

    avgaddscore = avgaddscore * LP_1 * 100

    avgdelscore = avgdelscore * LP_2 * 100

    finalscore = (avgkeepscore + avgdelscore + avgaddscore) / 3

    return finalscore, avgkeepscore, avgdelscore, avgaddscore


def main():
    # ssent = "marengo is a town in and the county seat of iowa county , iowa , united states . it has served as the county seat since august 1845 , even though it was not incorporated until july 1859 . the population was 2,528 in the 2010 census , a decline from 2,535 in 2000 ."
    #
    # csent1 = "in the US . 2,528 in 2010 ."
    # csent2 = "marengo is a city in iowa , the US . it has served as the county seat since august 1845 , even though it was not incorporated . the population was 2,528 in the 2010 census , a decline from 2,535 in 2010 ."
    # csent3 = "marengo is a town in iowa . marengo is a town in the US . in the US . the population was 2,528 . the population in the 2010 census ."
    # csent4 = "marengo is a town in iowa , united states . in 2010 , the population was 2,528 ."
    # rsents = ["marengo is a city in iowa in the US . the population was 2,528 in 2010 ."]
    #
    # print(D_SARIsent(ssent, csent1, rsents))
    # print(D_SARIsent(ssent, csent2, rsents))
    # print(D_SARIsent(ssent, csent3, rsents))
    # print(D_SARIsent(ssent, csent4, rsents))

    src_path = "data/d-wiki/test.src"
    tgt_path = "data/d-wiki/test.tgt"
    # 打开src和tgt文件
    src_file = open(src_path, "r", encoding="utf-8")
    tgt_file = open(tgt_path, "r", encoding="utf-8")
    # 读取src和tgt文件
    src_lines = src_file.readlines()
    tgt_lines = tgt_file.readlines()
    # 关闭src和tgt文件
    src_file.close()
    tgt_file.close()
    # 读取src和tgt文件的行数
    src_lines_num = len(src_lines)
    tgt_lines_num = len(tgt_lines)
    print("src_lines_num: ", src_lines_num)
    print("tgt_lines_num: ", tgt_lines_num)
    # 随机生成0-8000中的10个整数，以此作为src和tgt的索引，提取出src和tgt的句子,设置随机种子
    # random.seed(44)
    # random_index = random.sample(range(0, src_lines_num), 10)
    random_index = [2152, 5824, 4611, 5507, 6521, 3245, 6702, 4871, 4520, 1267]
    print("random_index: ", random_index)
    sari = 0
    keep_sari = 0
    add_sari = 0
    del_sari = 0
    d_sari = 0
    keep_d_sari = 0
    add_d_sari = 0
    del_d_sari = 0
    nums = 0
    for i in random_index:
        print("src: ", src_lines[i])
        print("src word num: ", len(word_tokenize(src_lines[i])))
        print("tgt: ", tgt_lines[i])
        print("tgt word num: ", len(word_tokenize(tgt_lines[i])))

        text = f"""Please simplify the article I provided, using three operations: adding word, deleting word, and retaining word.
        Raw:"{src_lines[i]}"
        Simplified:"""
        d = {"role": "user", "content": text}
        messages = [{"role": "system", "content": """"""}, d]
        simp_text = askChatGPT(messages)
        print("gpt gen:", simp_text)
        result_d_sari = D_SARIsent(src_lines[i], simp_text, [tgt_lines[i]])
        result_sari = corpus_sari([src_lines[i]], [simp_text], [[tgt_lines[i]]])
        print("d_sari: ", result_d_sari[0])
        print("keep_d_sari: ", result_d_sari[1])
        print("del_d_sari: ", result_d_sari[2])
        print("add_d_sari: ", result_d_sari[3])
        print("sari: ", result_sari[1])
        print("keep_sari: ", result_sari[0][1])
        print("del_sari: ", result_sari[0][2])
        print("add_sari: ", result_sari[0][0])
        nums += 1
        d_sari += result_d_sari[0]
        keep_d_sari += result_d_sari[1]
        del_d_sari += result_d_sari[2]
        add_d_sari += result_d_sari[3]
        sari += result_sari[1]
        keep_sari += result_sari[0][1]
        del_sari += result_sari[0][2]
        add_sari += result_sari[0][0]
        print("--------------------------------------------------")
    print("avg d_sari: ", d_sari / nums)
    print("avg keep_d_sari: ", keep_d_sari / nums)
    print("avg del_d_sari: ", del_d_sari / nums)
    print("avg add_d_sari: ", add_d_sari / nums)
    print("--------------------")
    print("avg sari: ", sari / nums)
    print("avg keep_sari: ", keep_sari / nums)
    print("avg del_sari: ", del_sari / nums)
    print("avg add_sari: ", add_sari / nums)

    # ssent =
    # csent1 =
    # rsents = [""]

    # print(D_SARIsent(ssent, csent1, rsents))
    # print(corpus_sari([ssent], [csent1], [rsents]))


if __name__ == '__main__':
    pass
    # import nltk
    #
    # nltk.download()
    # main()

    # raw_news = read_txt(
    #     r"D:\Dataset\newsela_article_corpus_with_scripts_2016-01-29.1\newsela_article_corpus_2016-01-29\articles\abercrombie-headscarves.en.0.txt")
    # # result = add_sent_bracket(text)
    # # print(stat_sen_nums(text))
    # # print(result)
    # ref_news1 = read_txt(
    #     r"D:\Dataset\newsela_article_corpus_with_scripts_2016-01-29.1\newsela_article_corpus_2016-01-29\articles\abercrombie-headscarves.en.1.txt")
    # ref_news2 = read_txt(
    #     r"D:\Dataset\newsela_article_corpus_with_scripts_2016-01-29.1\newsela_article_corpus_2016-01-29\articles\abercrombie-headscarves.en.2.txt")
    # ref_news3 = read_txt(
    #     r"D:\Dataset\newsela_article_corpus_with_scripts_2016-01-29.1\newsela_article_corpus_2016-01-29\articles\abercrombie-headscarves.en.3.txt")
    # ref_news4 = read_txt(
    #     r"D:\Dataset\newsela_article_corpus_with_scripts_2016-01-29.1\newsela_article_corpus_2016-01-29\articles\abercrombie-headscarves.en.4.txt")

    #     simp_text = """Abercrombie & Fitch, a popular fashion retailer, has agreed to change its dress code policy after being sued for discrimination by two women in the San Francisco Bay Area. The settlement, announced on Monday, includes better protections for Muslim women who wear headscarves, according to lawyers representing one of the plaintiffs, Hani Khan.
    # Khan was fired from her job in 2010 at an Abercrombie-owned store in San Mateo because she refused to take off her hijab. Abercrombie had strict rules about how its employees should look, including at its Hollister Co. stores, which were also involved in the lawsuits.
    # Khan, a recent graduate of the University of California, Davis, said she was surprised by Abercrombie's policies and worried that similar things could happen to others. She decided to stand up for her rights.
    # Abercrombie will pay $48,000 in back pay and compensatory damages to Khan and $21,000 to the other plaintiff, Halla Banafa, who was denied a job at a Hollister Co. store in Milpitas because she wore a hijab.
    # At a news conference, Khan said that the last 3 1/2 years had been a "roller coaster," but that fighting for her rights was worth it. She said it was surprising and shocking to be fired for doing nothing wrong. However, she was happy with the outcome.
    # Khan had been allowed to wear her hijab while working as a stock clerk at Hollister in Hillsdale Shopping Center, where she was initially hired in 2009. But a few months later, she was fired when a visiting district manager objected to her appearance.
    # The Equal Employment Opportunity Commission filed a lawsuit against Abercrombie in 2011, claiming it had violated Title VII of the Civil Rights Act, which prevents religious discrimination in the workplace. U.S. District Court Judge Yvonne Gonzalez Rogers ruled in Khan's favor on Sept. 3, which led to a trial to decide damages. However, the parties settled before the trial, and Abercrombie did not admit wrongdoing.
    # Last week, U.S. District Court Judge Edward Davila approved a settlement for both women in which Abercrombie agreed to accommodate religious attire unless it created an "undue hardship" for the company. Attorneys for the women said Abercrombie would have a hard time proving such a hardship. Two federal judges rejected Abercrombie's claims that the plaintiffs' hijabs were harmful to the company's operation.
    # Under the three-year decree, Abercrombie will also establish an appeal process for employees who are denied accommodations for religious attire and retrain its managers on the company's policy on headscarves. Abercrombie said in a statement that it was happy to put these "very old matters" behind it and that it did not discriminate based on religion.
    # The cases involving Khan and Banafa are the latest in a string of controversies for Abercrombie, which has faced discrimination lawsuits in the past. CEO Mike Jeffries's comments in a 2006 interview that the company is "exclusionary" and that his clothes are only for "cool" and "attractive" kids also caused controversy.
    # Abercrombie operates over 900 stores in the United States, with more than half of them under the Hollister brand. A spokesperson for the Council on American-Islamic Relations, which represented Khan, said that Abercrombie's policy changes would be monitored for three years. After that, the company will no longer have to follow the decree, but attorneys will continue to watch the company closely."""
    # result_d_sari = D_SARIsent(raw_news, simp_text, [ref_news1, ref_news2, ref_news3, ref_news4])
    # result_sari = corpus_sari([raw_news], [simp_text], [[ref_news1], [ref_news2], [ref_news3], [ref_news4]])
    # print("d_sari:", result_d_sari)
    # print("sari:", result_sari)
    # print(stat_sen_nums(raw_news))
    #     raw_news = "in minnesota , youth hockey has long had a reputation for competitiveness , but now , youth basketball might be catching up ."
    #     ref_news1 = "minnesota is famous for competitive youth hockey ."
    #     ref_news2 = "in minnesota , youth hockey has long been reputation for competitiveness ."
    #     ref_news3 = "in minnesota , youth hockey has long been known for competitiveness ."
    #     #simp_text = doc_simp_gpt(raw_news)
    #     prompt = """Please complete the task of simplifying the text, while keeping the meaning of the sentence unchanged and referring to the context, and try to provide a more user-friendly and readable simplified version.
    # raw：in minnesota , youth hockey has long had a reputation for competitiveness , but now , youth basketball might be catching up .
    # simple："""
    #     simp_text = askChatGPT(prompt)

    # simp_text = plan_simp3(raw_news)
    #
    # result_d_sari = D_SARIsent(raw_news, simp_text, [ref_news1, ref_news2, ref_news3, ref_news4])
    # result_sari = corpus_sari([raw_news], [ref_news1], [[ref_news1], [ref_news2], [ref_news3], [ref_news4]])
    # print("d_sari:", result_d_sari)
    # print("sari:", result_sari)
    # print("原文档句子数：", stat_sen_nums(raw_news))
    # print("简化文档句子数：", stat_sen_nums(simp_text))
    # print("参考1句子数：", stat_sen_nums(ref_news1))
    # print("参考2句子数：", stat_sen_nums(ref_news2))
    # print("参考3句子数：", stat_sen_nums(ref_news3))
    # print("参考4句子数：", stat_sen_nums(ref_news4))
    # print("原文档单词数：", stat_word_nums(raw_news))
    # print("简化文档单词数：", stat_word_nums(simp_text))
    # print("参考1单词数：", stat_word_nums(ref_news1))
    # print("参考2单词数：", stat_word_nums(ref_news2))
    # print("参考3单词数：", stat_word_nums(ref_news3))
    # print("参考4单词数：", stat_word_nums(ref_news4))
    # print(simp_text)

    # # raw :  890 words
    # # gpt3.5: 160   dsari 23  sari 30
    # # gpt4: 252     dsari 24  sari 35
    # # claude+: 272 dsari 24  sari 35
    # # claude+ force rewrite: 504 dsari 28  sari 40
    # # chatbot:  704  dsari 27  sari 39
    #
    # raw = "Simone ’s mixture of jazz , blues , and classical music in her performances at the bar earned her a small , but loyal , fan base ."
    # # simp = "Simone played jazz, blues, and classical music at a bar and gained a small group of loyal fans."  #  直接简化57  60
    # simp = "Her performances at the bar earned her a small but loyal fan base."   #  带上下文   抽取出简化后的对应句子   39  29
    #
    # ref = "Simone played jazz, blues, and classical music at the bar and gained a small but dedicated group of fans."   #  9  12
    # result_sari = corpus_sari([raw], [simp], [[ref]])
    # print("sari:", result_sari)
    # result_dsari = D_SARIsent(raw, simp, [ref])
    # print("dsari:", result_dsari)
