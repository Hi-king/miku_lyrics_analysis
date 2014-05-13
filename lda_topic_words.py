#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import gensim
import collections


parser = argparse.ArgumentParser()
parser.add_argument("wordsfilenames", nargs="+")
parser.add_argument("--top", type=int, default=10)
parser.add_argument("-L1", action='store_true')
parser.add_argument("-k", type=int, default=3)
parser.add_argument("--stopwords")
args = parser.parse_args()

def get_word_vec(filename, is_L1=False, stopwords=()):
    document = []
    for line in open(filename):
        linevec = line.rstrip().split(",")
        if linevec[1] == "名詞" and (not linevec[0] in stopwords):
            document.append(linevec[0])
    if is_L1:
        return list(set(document))
    else:
        return document

def word_count(words, top=10):
    word_dict = collections.defaultdict(int)
    for word in words:
        word_dict[word] += 1
    return sorted(word_dict.items(), key=lambda x: x[1])[-top:]


## corpus
stopwords = set([line.rstrip() for line in open(args.stopwords)]) if args.stopwords else ()
raw_documents = [[word for word in get_word_vec(filename, args.L1, stopwords)] for filename in args.wordsfilenames]
documents = [document for document in raw_documents if document]
words = [word for document in documents for word in document]
dictionary = gensim.corpora.Dictionary(documents)
raw_corpus = [dictionary.doc2bow(document) for document in documents]
tfidf = gensim.models.TfidfModel(raw_corpus, id2word=dictionary, normalize=True)
tfidf_corpus = [tfidf[word] for word in raw_corpus]

## nearest neighbor
#valid_filenames = [args.wordsfilenames[i] for i in xrange(len(args.wordsfilenames)) if raw_documents[i]]
#tfidf_index = gensim.similarities.SparseMatrixSimilarity(tfidf_corpus, num_features=1000)
#print("Nearest Neighbor")
#target_id = 370
#neigbors = sorted(tfidf_index[tfidf_corpus[target_id]], key=lambda item: item[1])[-3:]
#print(",".join([target_id]+neigbors))

## lsa
lsa = gensim.models.LsiModel(corpus=tfidf_corpus, id2word=dictionary, num_topics=args.k)
print("LSA: %d topics from %d lyrics" % (lsa.num_topics, len(documents)))
print("##### topic words top %d" % args.top)
words = [[item[1] for item in lsa.show_topic(i, topn=args.top)] for i in xrange(args.k)]
counts = collections.defaultdict(int)
for line in words:
    print ' '.join(line)
    for word in line: counts[word]+=1

## lda
lda = gensim.models.LdaModel(corpus=tfidf_corpus, id2word=dictionary, num_topics=args.k, iterations=100)

## print
print("LDA: %d topics from %d lyrics" % (lda.num_topics, len(documents)))
print("##### topic words top %d" % args.top)
words = [[item[1] for item in lda.show_topic(i, topn=args.top)] for i in xrange(args.k)]
counts = collections.defaultdict(int)
for line in words:
    print ' '.join(line)
    for word in line: counts[word]+=1
print("##### unique topic words top %d" % args.top)
uniquewords = set(w for w,c in counts.items() if c==1)
for line in words:
    print ' '.join([word for word in line if word in uniquewords])

print lda.print_topic(0)

exit(0)
