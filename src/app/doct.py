#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
from bson.objectid import ObjectId
from config import setting
import app_helper

db = setting.db_web

url = ('/app/document')

# - 规则树页面
class handler:     
    @app_helper.ex_check_sign(['app_id','tick','page_id_or_code']) 
    def POST(self):
        web.header('Content-Type', 'application/json')
        param=web.input(page_id_or_code='')

        #print param

        if param['page_id_or_code']=='':
            return json.dumps({'ret' : -4, 'msg' : '无效的page_id_or_code'})

        if len(param['page_id_or_code'])<20: # _id长度为24
            r1 = db.pages.find_one({
                'page_code' : param['page_id_or_code'].upper(),
                #'page_type' : 0,
                'available' : 1
            }, { 'history' : 0 })
            if r1 is None:
                r1 = db.pages.find_one({
                    'page_code' : param['page_id_or_code'].upper()+'#1',  # 加 '#1' 再试一次
                    #'page_type' : 0,
                    'available' : 1
                }, { 'history' : 0 })
                if r1 is None:
                    return json.dumps({'ret' : -7, 'msg' : '页面不可用！'})
        else:
            real_page_id = app_helper.realid(param['page_id_or_code']) # 恢复原始id
            if real_page_id is None:
                return json.dumps({'ret' : -4, 'msg' : '无效的page_id'})

            r1 = db.pages.find_one({'_id': ObjectId(real_page_id)},{ 'history' : 0 })
            if r1 is None:
                return json.dumps({'ret' : -7, 'msg' : '页面不可用！'})

        r1['_id'] = str(r1['_id'])

        if not r1.has_key('start_node'):
            return json.dumps({'ret' : -5, 'msg' : '页面类型错误！'})

        r2 = db.nodes.find_one({'_id':ObjectId(r1['start_node'])})
        if r2 is None:
            return json.dumps({'ret' : -6, 'msg' : '页面数据错误！'})

        if len(r2.get('child',[]))>0:
            r1['type'] = 'map'  # 显示规则树
        else:
            r1['type'] = 'text'  # 显示纯文本

        app_helper.log_app_api('external', 'document', param)

        # 返回
        return json.dumps({'ret' : 0, 'data' : {
                'gid'        : app_helper.randomid(r1['_id']),
                'type'       : r1['type'],
                'title'      : r1['page_name'],
                'page_code'  : r1['page_code'],
                'start_node' : app_helper.randomid(r1['start_node']),
                'text'       : r1['rich_text'],
            } 
        })

