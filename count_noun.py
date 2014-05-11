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
parser.add_argument("-L1", action='store_true')
args = parser.parse_args()

def get_word_vec(filename, is_L1=False):
    document = []
    for line in open(filename):
        linevec = line.rstrip().split(",")
        if linevec[1] == "名詞":
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


words = [word for filename in args.wordsfilenames for word in get_word_vec(filename, args.L1)]

for w, c in word_count(words, args.top):
    print w, c

exit(0)
