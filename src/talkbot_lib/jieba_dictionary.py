#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import jieba
from config import setting

db = setting.db_web

last_update = 0

#jieba.add_word('人民广场',freq=5,tag='n')
#jieba.suggest_freq(('上海市','浦东新区'),tune=True)

def textParse(bigString):    #输入为 unicode, #输出 is word list
    import re
    listOfTokens = re.split(u'(，|。|！|,|\!|\.|？|\?)', bigString)
    return [tok.strip() for tok in listOfTokens if len(tok) > 1]   # 过滤掉了单个字的关键词

def loadBayesKeyword():
    # 从关键词装入字典
    postingList = []
    r1 = db.bayes.find({'available':1})
    for x in r1:
        #postingList.append(x['key_word'].strip())
        postingList.extend(textParse(x['key_word'].strip()))
    #postingList2 = []
    #for x in postingList:
    #    postingList2.extend(textParse(x))
    return list(set(postingList))

def refreshDict(force=False):
    if not force:
        global last_update
        r2 = db.sys_refs.find_one({'name' : 'dict_update'})
        if r2:
            if r2['last_tick']==last_update: # 检查是否需要刷新词库
                return
            else:
                last_update=r2['last_tick']

    # 刷新词库
    print '................ Refresh JIEBA Dictionary ......'
    jieba.user_word_tag_tab.clear()
    word_list = loadBayesKeyword()
    for i in word_list:
        jieba.add_word(i, freq=200, tag='n')

def showDict():
    for i in jieba.user_word_tag_tab.keys():
        print(i.encode('utf-8'))
    print 'Dictionary:', len(jieba.user_word_tag_tab)

