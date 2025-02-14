from easse.sari import corpus_sari

from Evaluate.easse.easse.fkgl import corpus_fkgl

# result = corpus_sari(orig_sents=["About 95 species are currently accepted.", "The cat perched on the mat."],
#             sys_sents=["About 95 you now get in.", "Cat on mat."],
#             refs_sents=[["About 95 species are currently known.", "The cat sat on the mat."],
#                         ["About 95 species are now accepted.", "The cat is on the mat."],
#                         ["95 species are now accepted.", "The cat sat."]])
#
#
# print(result)

origin = [
    "marengo is a town in and the county seat of iowa county , iowa , united states .it has served as the county seat since august 1845 , even though it was not incorporated until july 1859 . the population was 2,528 in the 2010 census , a decline from 2,535 in 2000 ."]
ref = ["marengo is a city in iowa in the US . the population was 2,528 in 2010 ."]
sys_simp1 = ["in the US . 2,528 in 2010 ."]
sys_simp2 = [
    "marengo is a city in iowa , the US . it has served as the county seat since august 1845 , even though it was not incorporated . the population was 2,528 in the 2010 census , a decline from 2,535 in 2010 ."]
sys_simp3 = [
    "marengo is a town in iowa . marengo is a town in the US . in the US . the population was 2,528 . the population in the 2010 census ."]
sys_simp4 = ["marengo is a town in iowa , united states . in 2010 , the population was 2,528 ."]


#  [add_score, keep_score, del_score],(add_score + keep_score + del_score) / 3
macro1, res1 = corpus_sari(orig_sents=origin, sys_sents=sys_simp1, refs_sents=[ref])
macro2, res2 = corpus_sari(orig_sents=origin, sys_sents=sys_simp2, refs_sents=[ref])
macro3, res3 = corpus_sari(orig_sents=origin, sys_sents=sys_simp3, refs_sents=[ref])
macro4, res4 = corpus_sari(orig_sents=origin, sys_sents=sys_simp4, refs_sents=[ref])

print(macro1, res1)
print(macro2, res2)
print(macro3, res3)
print(macro4, res4)

fkgl = corpus_fkgl(origin+ref+sys_simp1+sys_simp2+sys_simp3+sys_simp4)
print(fkgl)


# if __name__ == '__main__':
#  pass
