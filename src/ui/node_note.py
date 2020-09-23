#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
from config import setting
from bson.objectid import ObjectId
import helper

db = setting.db_web

# 返回指定注释内容
url = ('/ui/node_note')


class handler:        
    # 返回指定note_code的注释，返回json格式
    def POST(self):
        web.header("Content-Type", "application/json")
        #if not helper.logged(helper.PRIV_USER, 'DOCTOR_USE'):
        #    return json.dumps({'ret':-1,'msg':'无访问权限'})

        param = web.input(note_code='')

        if param.note_code=='':
            return json.dumps({'ret':-1, 'msg':'参数错误'})

        r2 = db.notes.find_one({'note_code':param['note_code'].upper()}) # 索引编码大写
        if r2 is None:
            return json.dumps({'ret':-1, 'msg':'未找到注释内容！'})

        ret_data = {
            'note_code' : r2['note_code'],
            'content'   : r2['note_content'],
        }

        return json.dumps({'ret':0,'data':ret_data})


