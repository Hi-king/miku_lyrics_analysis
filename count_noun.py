#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MeCab
import sys
import argparse
import gensim
import collections


parser = argparse.ArgumentParser()
parser.add_argument("wordsfilenames", nargs="+")
parser.add_argument("--top", type=int, default=10)
args = parser.parse_args()

##################################################
## corpus 
##################################################
def get_word_vec(filename):
    document = []
    for line in open(filename):
        linevec = line.rstrip().split(",")
        if linevec[1] == "名詞":
            document.append(linevec[0])
    return document

def word_count(words, top=10):
    word_dict = collections.defaultdict(int)
    for word in words:
        word_dict[word] += 1
    return sorted(word_dict.items(), key=lambda x: x[1])[-top:]


words = [word for filename in args.wordsfilenames for word in get_word_vec(filename)]

for w, c in word_count(words, args.top):
    print w, c

exit(0)


stoplist = set('て に を は が も だ の よ この あの あなた ・ 「 」 な ？ 、 . 君 僕 た 私 ！ で （ ） ない . 。'.split())
texts = [[line.rstrip() for line in open(filename) if not line.rstrip() in stoplist] for filename in args.wordsfilenames]

refined_filenames = [filename for filename,line in zip(args.wordsfilenames, texts) if line]
texts = [line for line in texts if line]


#word_index_dict = dict([(item, i) for i, item in enumerate(wordlist)])
dictionary = gensim.corpora.Dictionary(texts)
print(dictionary)

raw_corpus = [dictionary.doc2bow(text) for text in texts]
tfidf = gensim.models.TfidfModel(raw_corpus)

tfidf_corpus = [tfidf[item] for item in raw_corpus]




##################################################
## nearest
##################################################
tfidf_index = gensim.similarities.SparseMatrixSimilarity(tfidf_corpus, num_features=1000)
query = tfidf_corpus[0]
print refined_filenames[0]

N = 5
print "og"
similars = tfidf_index[query]
print "sim"
ordered = sorted(enumerate(similars), key= lambda item: -item[1])
print "ord"
topn = [refined_filenames[item[0]] for item in ordered[:N]]
worstn = [refined_filenames[item[0]] for item in ordered[-N:]]

print topn
print worstn
exit(0)


##################################################
## lda
##################################################
lda = gensim.models.LdaModel(corpus=tfidf_corpus, id2word=dictionary, num_topics=10)

print lda.num_topics

words = [[item[1] for item in lda.show_topic(i, topn=100)] for i in xrange(10)]
counts = collections.defaultdict(int)
for line in words:
    for word in line: counts[word]+=1
uniquewords = set(w for w,c in counts.items() if c==1)
for line in words:
    print ' '.join([word for word in line if word in uniquewords])
#lda.printTopic(0)

## each document vector
