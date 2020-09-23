#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web, json, time
from config import setting
from bson.objectid import ObjectId
import helper

db = setting.db_web

url = ('/plat/json_map')

# 取得指定页面的节点数据
class handler:        
    def POST(self):
        web.header('Content-Type', 'application/json')

        if not helper.logged(helper.PRIV_USER,'DATA_MODIFY'):
            return json.dumps({'ret':-1, 'msg':'没有权限'})

        param = web.input(page_id='')

        r1 = db.pages.find_one({'_id': ObjectId(param['page_id'])})
        if r1 is None:
            return json.dumps({'ret':-2, 'msg':'page_id参数错误'})

        r2 = db.nodes.find({'page_id':param['page_id']})

        print 'page_id', param['page_id']

        data = []

        for i in r2:
            #print i

            # 查找纠错内容
            node_question = i.get('node_question', False)
            node_correct = []
            if node_question:
                r4 = db.correct.find({'node_id' : str(i['_id']), 'status' : 'WAIT'})
                for j in r4:
                    node_correct.append({
                        'time_t' : j['time_t'],
                        'note'   : j['note']
                    })

            data.append({
                '_id'      : str(i['_id']),
                'text'     : i['text'],
                'position' : i['position'],
                'child'    : i['child'],
                'node_prop'     : i.get('node_prop',''), # 节点属性 2018－08-14
                'node_weight'   : i.get('node_weight','1'), # 节点权重 2018－08-14
                'node_question' : { 
                    'check'   : node_question, # 节点是否有疑问 2018－08-14
                    'correct' : node_correct,  # 用户提供的纠错内容 2019-02-12
                },
            })

        r3 = db.connect.find({'page_id':param['page_id']})

        data2 = []

        for i in r3:
            #print i
            data2.append({
                'source'   : i['source'],
                'target'   : i['target'],
                'vertices' : i['vertices'],
            })

        # 返回
        return json.dumps({'ret' : 0, 'data' : data, 'connect' : data2})
