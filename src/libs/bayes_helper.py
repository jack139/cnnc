#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from numpy import *
from bson.objectid import ObjectId
import jieba
from talkbot_lib import jieba_dictionary
from config import setting
import helper

db = setting.db_web


def loadDataFromDB():
    postingList = []
    classVec = []
    r1 = db.bayes.find({'available':1})
    for x in r1:
        postingList.append(x['key_word'].strip())
        classVec.append(str(x['_id']))
    postingList2 = []
    for x in postingList:
        postingList2.append(textParse(x))
    return postingList2,classVec


def createVocabList(dataSet):
    vocabSet = set([])  #create empty set
    for document in dataSet:
        vocabSet = vocabSet | set(document) #union of the two sets,
    return list(vocabSet)


def trainNB2(trainMatrix,trainCategory):
    numTrainDocs = len(trainMatrix)
    numWords = len(trainMatrix[0])
    pAbusive = {}
    pNum = {}
    pDenom = {}
    pVect = {}

    for c in trainCategory:
        pAbusive[c] = 0
        #pNum[c] = ones(numWords)
        #pDenom[c] = 2.0
        pNum[c] = zeros(numWords)
        pDenom[c] = 0.0

    for i in range(numTrainDocs):
        c = trainCategory[i]
        pAbusive[c] += 1
        pNum[c] += trainMatrix[i]
        pDenom[c] += sum(trainMatrix[i])

    for c in pAbusive.keys():
        pAbusive[c] = pAbusive[c]/float(numTrainDocs)
        #pVect[c] = log(pNum[c]/pDenom[c])
        pVect[c] = pNum[c]/pDenom[c]

    return pVect,pAbusive


def classifyNB2(vec2Classify, pVec, pClass):
    print vec2Classify
    p = {}
    for c in pClass:
        p[c] = sum(vec2Classify * pVec[c]) + log(pClass[c])
    return p

    
def bagOfWords2VecMN(vocabList, inputSet): # 字符串匹配 
    returnVec = [0]*len(vocabList)
    for word in inputSet:
        for x in vocabList:
            #if x.lower() in word.lower(): # 转换为小写比较
            if x.lower() == word.lower(): # 转换为小写比较 --- 严格匹配，
                print vocabList.index(x)
                returnVec[vocabList.index(x)] += 1
    return returnVec

#def bagOfWords2VecMN_jieba(vocabList, inputSet):  # 使用jieba分词匹配  -- 用于匹配
#    returnVec = [0]*len(vocabList)
#    for word in inputSet:
#        for x in vocabList:
#            word_cut = jieba.cut(word.lower()) # 转换为小写比较
#            #print ' '.join([x for x in word_cut]).encode('utf-8')
#            if x.lower() in word_cut:
#                print vocabList.index(x)
#                returnVec[vocabList.index(x)] += 1
#    return returnVec

def textParse(bigString):    #输入为 unicode, #输出 is word list
    import re
    listOfTokens = re.split(u'(，|。|！|,|\!|\.|？|\?)', bigString)
    return [tok.strip() for tok in listOfTokens if len(tok.strip()) > 1] 


def trainToDB():
    try:
        listOPosts,listClasses = loadDataFromDB()
        myVocabList = createVocabList(listOPosts)
        trainMat=[]
        for postinDoc in listOPosts:
            trainMat.append(bagOfWords2VecMN(myVocabList, postinDoc))
        pV,pAb = trainNB2(array(trainMat),array(listClasses))

        for x in pV.keys():
            pV[x] = pV[x].tolist()

        db.bayes_data.update_one({'train_data' : 'train_data'}, { '$set' : {
            'pV'        : pV,
            'pAb'       : pAb,
            'vocabList' : myVocabList,
            'time_t'    : helper.time_str(),
        }}, upsert=True)

        return True

    except:
        print 'ERROR: train and save data to DB fail.'
        return None



def loadTrainData():
    r2 = db.bayes_data.find_one({'train_data' : 'train_data'})
    if r2 is None:
        return None, None, None
    pV = r2['pV']

    for x in pV.keys():
        pV[x] = array(pV[x])

    return pV, r2['pAb'], r2['vocabList']


def textParse_jieba(bigString):    #输入为 unicode, #输出 is word list, jieba 版本
    #import re
    #listOfTokens = re.split(u'(，|。|！|,|\!|\.|？|\?)', bigString)
    word_cut = jieba.cut(bigString.lower())
    return [tok.strip() for tok in word_cut if len(tok.strip()) > 1] 

def getReply(testString):
    jieba_dictionary.refreshDict()
    
    pV,pAb,myVocabList = loadTrainData()
    if pV is None:
        print 'ERROR: load trainning data fail.'
        return None

    #print pV
    #print pAb
    #print myVocabList

    testEntry = textParse_jieba(testString)
    print ' '.join(testEntry).encode('utf-8')
    thisDoc = array(bagOfWords2VecMN(myVocabList, testEntry))
    if sum(thisDoc)==0:
        print 'INFO: no match key word.'
        return None

    #print testEntry

    result = classifyNB2(thisDoc,pV,pAb)
    result_class = list(result.keys())[list(result.values()).index(max(result.values()))]
    #print result

    r3 = db.bayes.find_one({'_id':ObjectId(result_class)})
    if r3 is None:
        print 'ERROR: cannot find rule', result_class
        return None
    else:
        if r3['reply_type']==1: # 返回链接
            r4 = db.pages.find_one({'dir_name' : r3['reply'], 'available' : 1})
            if r4 is None:
                r5 = db.pages.find_one({'page_code' : r3['reply'].upper(), 'available' : 1})
                if r5 is None:
                    print 'ERROR: cannot find page name or page code', result_class
                    return None
                else: # 显示页面
                    show_name = r5['page_name']
                    show_link = 'http:///wx/init_doct?page_id='+str(r5['_id'])
            else:  # 显示目录
                show_name = r4['dir_name']
                show_link = 'http:///wx/init_cate2?parent_id='+str(r4['_id'])

            return {
                'rule_id'    : result_class,
                'reply_type' : 'link',
                'reply'      : show_link,
                'title'      : show_name,
            }
        elif r3['reply_type']==2: # 返回URL
            reply_list = r3['reply'].split('|')
            return {
                'rule_id'    : result_class,
                'reply_type' : 'link',
                'reply'      : reply_list[1] if len(reply_list)>1 else 'http:///wx/init_cate2',
                'title'      : reply_list[0],
            }
        else:
            # 返回文本信息
            q = [x.strip() for x in r3['reply'].split('|') if len(x.strip())>0]
            if len(q)>1: # 如果多个则随机返回
                import random
                reply_txt = random.sample(q, 1)[0] 
            else:
                reply_txt = r3['reply']
            return {
                'rule_id'    : result_class,
                'reply_type' : 'text',
                'reply'      : reply_txt
            }

