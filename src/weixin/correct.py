#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
from config import setting
from bson.objectid import ObjectId
import app_helper

db = setting.db_web

# 我要纠错
url = ('/wx/correct')


class handler:        
    # 返回指定note_code的注释，返回json格式
    def POST(self):
        web.header("Content-Type", "application/json")

        param = web.input(session_id='', node_id='', correct_note='', source="cnnc")
        print param

        if param.session_id=='':
            return json.dumps({'ret' : -1, 'msg' : 'session参数错误'})

        uname = app_helper.wx_logged(param.session_id)
        if uname is None:
            return json.dumps({'ret' : -2, 'msg' : '无效的session_id'})

        if param.node_id=='':
            return json.dumps({'ret':-2, 'msg':'参数错误'})

        db.correct.insert_one({
            'node_id' : param['node_id'],
            'note'    : param['correct_note'],
            'openid'  : uname['openid'],
            'time_t'  : app_helper.time_str(), # 提交时间
            'status'  : 'WAIT', # WAIT 等待处理，PASS 接受，NOGO 拒绝
            'source'  : param['source'], # 2019-10-29, 区分来源
        })

        if param['source']=='tnm':
            r2 = db.tnm.update_one({ '_id' : ObjectId(param['node_id'])} , {'$set' : {'node_question' : True} })
        else:
            r2 = db.nodes.update_one({ '_id' : ObjectId(param['node_id'])} , {'$set' : {'node_question' : True} })
        print r2.matched_count, r2.modified_count

        return json.dumps({'ret':0,'data':{}})


