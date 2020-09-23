#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
from bson.objectid import ObjectId
from config import setting
import app_helper

db = setting.db_web

url = ('/wx/doct')

# - 规则树页面
class handler:      
    def POST(self):
        web.header('Content-Type', 'application/json')
        param=web.input(session_id='', page_id='', page_code='')

        print param

        if param.session_id=='':
            return json.dumps({'ret' : -1, 'msg' : 'session参数错误'})

        uname = app_helper.wx_logged(param.session_id)
        if uname is None:
            return json.dumps({'ret' : -2, 'msg' : '无效的session_id'})

        if param['page_id']=='' and param['page_code']=='':
            return json.dumps({'ret' : -3, 'msg' : '参数错误'})

        if len(param['page_code'])>0:
            r1 = db.pages.find_one({
                'page_code' : param['page_code'].upper(),
                #'page_type' : 0,
                'available' : 1
            }, { 'history' : 0 })
            if r1 is None:
                r1 = db.pages.find_one({
                    'page_code' : param['page_code'].upper()+'#1',  # 加 '#1' 再试一次
                    #'page_type' : 0,
                    'available' : 1
                }, { 'history' : 0 })
                if r1 is None:
                    return json.dumps({'ret' : -4, 'msg' : '页面不可用！'})
        else:
            r1 = db.pages.find_one({'_id': ObjectId(param['page_id'])},{ 'history' : 0 })
            if r1 is None:
                return json.dumps({'ret' : -4, 'msg' : '页面不可用！'})

        r1['_id'] = str(r1['_id'])

        r2 = db.nodes.find_one({'_id':ObjectId(r1['start_node'])})
        if r2 is None:
            return json.dumps({'ret' : -5, 'msg' : '页面数据错误！'})

        if len(r2.get('child',[]))>0:
            r1['type'] = 'map'  # 显示规则树
        else:
            r1['type'] = 'text'  # 显示纯文本

        # 返回
        return json.dumps({'ret' : 0, 'data' : {
            'data' : r1,
        }})

