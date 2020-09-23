#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import os, time

# 装入语料库

#from numpy import *
#import jieba
#import gensim

CORPUS_PATH = 'data/chinese'
OUTPUT_PATH = 'data/output'

# 从yml文件装入语料库
def corpus_from_file():
    question = []
    answer = []

    for i in os.listdir(CORPUS_PATH):
        filename = CORPUS_PATH+'/'+i
        f = open(filename)
        tmp_q = tmp_a = None
        while True:
            line = f.readline()
            if not line:
                break

            prefix = line[:4]
            if prefix!='- - ' and prefix!='  - ': # 不是数据行
                print line
                continue

            if prefix=='- - ':
                tmp_q = line[4:]
            else:
                if tmp_q is None:
                    tmp_q = line[4:]
                    tmp_a = None
                else:
                    tmp_a = line[4:]

            if (tmp_q is not None) and (tmp_a is not None):
                question.append(tmp_q.strip())
                answer.append(tmp_a.strip())
                tmp_q = tmp_a = None 

        #break # for test
        f.close()

    f = open(OUTPUT_PATH+'/answer.txt','w')

    for i in xrange(len(question)):
        print question[i], '--->', answer[i]
        f.write(answer[i]+'\n')

    f.close()

    print len(question), len(answer)

    return question

# 从db装入语料库
def corpus_from_db(db):
    question = []
    answer = []

    r1 = db.talkbot.find({'available':1})
    for i in r1:
        q = [x.strip() for x in i['question'].split('|') if len(x.strip())>0]
        question.extend(q)
        answer.extend([str(i['_id'])]*len(q))

    f = open(OUTPUT_PATH+'/answer_id.txt','w')

    for i in xrange(len(question)):
        #print question[i], '--->', answer[i]
        f.write(answer[i]+'\n')

    f.close()

    print len(question), len(answer)

    return question

# 将yml格式文件导入db
def corpus_from_file_to_db(db):
    question = []
    answer = []

    for i in os.listdir(CORPUS_PATH):
        filename = CORPUS_PATH+'/'+i
        f = open(filename)
        tmp_q = tmp_a = None
        while True:
            line = f.readline()
            if not line:
                break

            prefix = line[:4]
            if prefix!='- - ' and prefix!='  - ': # 不是数据行
                print line
                continue

            if prefix=='- - ':
                tmp_q = line[4:]
            else:
                if tmp_q is None:
                    tmp_q = line[4:]
                    tmp_a = None
                else:
                    tmp_a = line[4:]

            if (tmp_q is not None) and (tmp_a is not None):
                question.append(tmp_q.strip())
                answer.append(tmp_a.strip())
                tmp_q = tmp_a = None 

        #break # for test
        f.close()

    for i in xrange(len(question)):
        print question[i], '--->', answer[i]
        rule_name = 'rule_%04d' % i

        update_set={
            'rule_name'  : rule_name,
            'question'   : question[i], 
            'reply'      : answer[i],
            'reply_type' : 0,
            'available'  : 1,
            'last_tick'  : int(time.time()),  # 更新时间戳
        }

        db.talkbot.insert_one(update_set)

    print len(question), len(answer)
