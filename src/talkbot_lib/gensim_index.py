#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# jieba gensim 测试

#from numpy import *
import jieba
#import gensim

from talkbot_lib import corpus_lib
#from talkbot_lib import jieba_dictionary

#jieba_dictionary.refreshDict()


def index_from_file():
    string=corpus_lib.corpus_from_file()

    print('\nTexts:')
    texts=[]
    for sentence in string:
        sentence_list=[ word for word in jieba.cut(sentence) ]
        texts.append(sentence_list)

    for i in texts:
        print(' '.join([x for x in i]))

    from gensim import corpora, models, similarities

    # From Strings to Vectors

    dictionary = corpora.Dictionary(texts)
    dictionary.save(corpus_lib.OUTPUT_PATH+'/gensimbot2.dict')  # store the dictionary, for future reference
    print(dictionary)

    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize(corpus_lib.OUTPUT_PATH+'/gensimbot2.mm', corpus)  # store to disk, for later use
    #print('\nCorpus:')
    #print(corpus)

    # Transformation interface

    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=200)
    lsi.save(corpus_lib.OUTPUT_PATH+'/gensimbot2.lsi')

    index = similarities.MatrixSimilarity(lsi[corpus])  # transform corpus to LSI space and index it
    index.save(corpus_lib.OUTPUT_PATH+'/gensimbot2.index')

    return True



def index_from_db(db):
    string=corpus_lib.corpus_from_db(db)

    print('\nTexts:')
    texts=[]
    for sentence in string:
        sentence_list=[ word for word in jieba.cut(sentence) ]
        texts.append(sentence_list)

    #for i in texts:
    #    print(' '.join([x for x in i]))

    from gensim import corpora, models, similarities

    # From Strings to Vectors

    dictionary = corpora.Dictionary(texts)
    dictionary.save(corpus_lib.OUTPUT_PATH+'/gensimbot.dict')  # store the dictionary, for future reference
    print(dictionary)

    corpus = [dictionary.doc2bow(text) for text in texts]
    corpora.MmCorpus.serialize(corpus_lib.OUTPUT_PATH+'/gensimbot.mm', corpus)  # store to disk, for later use
    #print('\nCorpus:')
    #print(corpus)

    # Transformation interface

    lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=200)
    lsi.save(corpus_lib.OUTPUT_PATH+'/gensimbot.lsi')

    index = similarities.MatrixSimilarity(lsi[corpus])  # transform corpus to LSI space and index it
    index.save(corpus_lib.OUTPUT_PATH+'/gensimbot.index')

    return True

