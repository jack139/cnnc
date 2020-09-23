#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

# jieba gensim 测试
import re, random
from bson.objectid import ObjectId
import jieba
from gensim import corpora, models, similarities
from talkbot_lib import jieba_dictionary
from talkbot_lib.corpus_lib import OUTPUT_PATH
from config import setting

db = setting.db_web

dictionary = lsi = index = answer_id = None
last_update = 0

#answer = []
#with open(OUTPUT_PATH+'/answer.txt', 'r') as f:
#    while True:
#        line = f.readline()
#        if not line:
#            break
#        answer.append(line.strip())    
#
#print 'Answer TXT file: ', len(answer)

def load_data():
    global dictionary, lsi, index, answer_id

    answer_id = []
    with open(OUTPUT_PATH+'/answer_id.txt', 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            answer_id.append(line.strip())    

    print 'Answer_id TXT file: ', len(answer_id)

    # Transformation interface
    dictionary = corpora.Dictionary.load(OUTPUT_PATH+'/gensimbot.dict')
    lsi = models.LsiModel.load(OUTPUT_PATH+'/gensimbot.lsi')
    index = similarities.MatrixSimilarity.load(OUTPUT_PATH+'/gensimbot.index')
    print 'Loaded gensim data.'

#def qa_bot(doc):
#    jieba_dictionary.refreshDict()
#
#        
#    doc = doc if type(doc)==type(u'') else doc.decode('utf-8') # 转换为unicode
#    doc = re.sub(u'[!?.,！？。，]', u'', doc)
#    doc = [ word for word in jieba.cut(doc) ] # 分词
#    #print ' '.join(doc)
#    vec_bow = dictionary.doc2bow(doc)
#    vec_lsi = lsi[vec_bow]  # convert the query to LSI space
#    #print('\nvec_lsi:')
#    #print(vec_lsi)
#
#    sims = index[vec_lsi]  # perform a similarity query against the corpus
#    #print(list(enumerate(sims)))  # print (document_number, document_similarity) 2-tuples
#
#    sims = sorted(enumerate(sims), key=lambda item: -item[1])
#    #print('\nResult:')
#    #print(sims)  # print sorted (document number, similarity score) 2-tuples
#
#    # 对相似度一样的，随机返回答案
#    sim_count = 0
#    sim_value = sims[0][1]
#
#    print sims[:10]
#
#    if sim_value>0:
#        for i in sims:
#            if i[1]<sim_value:
#                break
#            sim_count += 1
#        sim_reply = answer[sims[random.randint(0,sim_count)][0]]
#    else:
#        sim_reply = '让我想想如何回答 ...'
#
#    return sim_reply


def qa_bot_db(doc):
    # 检查是否刷新数据
    global last_update
    r2 = db.sys_refs.find_one({'name' : 'talkbot_update'})
    if r2:
        if r2['last_tick']>last_update: # 检查是否需要刷新词库
            last_update=r2['last_tick']
            print '................ Refresh talkbot data ......'
            load_data()

    # 刷新字典
    jieba_dictionary.refreshDict()
    
    doc = doc if type(doc)==type(u'') else doc.decode('utf-8') # 转换为unicode
    doc = re.sub(u'[!?.,！？。，]', u'', doc)
    doc = [ word for word in jieba.cut(doc) ] # 分词
    #print ' '.join(doc)
    vec_bow = dictionary.doc2bow(doc)
    vec_lsi = lsi[vec_bow]  # convert the query to LSI space
    #print('\nvec_lsi:')
    #print(vec_lsi)

    sims = index[vec_lsi]  # perform a similarity query against the corpus
    #print(list(enumerate(sims)))  # print (document_number, document_similarity) 2-tuples

    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    #print('\nResult:')
    #print(sims)  # print sorted (document number, similarity score) 2-tuples

    # 对相似度一样的，随机返回答案
    sim_count = 0
    sim_value = sims[0][1]

    print sims[:10]

    if sim_value>0:
        for i in sims:
            if i[1]<sim_value:
                break
            sim_count += 1
        reply_id = answer_id[sims[random.randint(0,sim_count-1)][0]]
        
        print 'reply_id: ', reply_id, sim_count

        # 从数据库中取回复内容，多个时随机取
        r2=db.talkbot.find_one({'_id':ObjectId(reply_id)})
        if r2:
             q = [x.strip() for x in r2['reply'].split('|') if len(x.strip())>0]
             if len(q)>0:
                sim_reply = random.sample(q, 1)[0]
                return sim_reply

    # 随机默认回答
    r3 = db.talkbot.find_one({'_id':ObjectId('5d1c9b9e3c33c0474e14c224')})
    if r3:
        q = [x.strip() for x in r3['reply'].split('|') if len(x.strip())>0]
        if len(q)>0:
            sim_reply = random.sample(q, 1)[0]
            return sim_reply

    # 固定默认回答
    sim_reply = '让我想想如何回答 ...'
    return sim_reply

load_data()
