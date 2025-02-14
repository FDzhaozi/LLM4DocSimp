from Methods.word_aspect import get_words_sim, ner_words


def test_get_words_sim():
    score = get_words_sim("不知不觉")
    print(score)

    score = get_words_sim("值得")
    print(score)

    score = get_words_sim("喜悦")
    print(score)

    score = get_words_sim("纶巾")
    print(score)

    score = get_words_sim("叱咤风云")
    print(score)

    score = get_words_sim("沁人心脾")
    print(score)

    score = get_words_sim("草船借箭")
    print(score)

    score = get_words_sim("独具匠心")
    print(score)

    score = get_words_sim("峨眉")
    print(score)

    score = get_words_sim("轻快")
    print(score)

    score = get_words_sim("萧瑟")
    print(score)

    score = get_words_sim("蝇营狗苟")
    print(score)

    score = get_words_sim("沆瀣一气")
    print(score)

def test_ner():
    doc = """很早，很早以前，我就相信这个传说，而且，相信它必定是真实的。
据说，南宋绍兴年间，抗金名将岳飞在北伐途中路过诸葛亮的故里――隆中。是夜，他借宿于草庐。秋风萧瑟，月白窗前，勾起他激荡难已的家国之思。剪亮烛光，展读武侯留下的《出师表》，他，不觉泪湿征衫，于是便力运千钧，笔走龙蛇，用遒劲而潇洒的行草，一口气录下了这篇感人肺腑的表文。从此，将军的墨宝就与丞相的文章交相辉映，流颂四海……
每当我踏进成都武候祠，仰望那高悬在大殿内的岳公的木刻手迹，心情总是十分激动。有的人活着，等同死去；有的人长眠九泉，却永远活在我们心中。上下五千年，纵横一万里，在中国这块古老的土地上，奔驰过多少盘马弯弓、叱咤风云的英雄好汉！可是，能够真正属于历史而不朽者，复有几人？我以为，诸葛亮恰恰是这样一位值得后世景仰的伟大人物。
在故乡锦城的游览胜地中，武候祠乃是一个值得去的地方。每次度假归来或出差经过，哪怕只有短短的三两天，我几乎总要带着几分思古的向慕之心去走一走，而回回都能增强我对历史的洞察力，获得某种新的精神升华。"""
    result = ner_words(doc)
    print(result)

if __name__ == '__main__':
    test_get_words_sim()
    # test_ner()
