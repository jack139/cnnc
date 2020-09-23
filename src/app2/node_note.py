#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
from config import setting
from bson.objectid import ObjectId
import app_helper

db = setting.db_web

# 返回指定注释内容
url = ('/app2/note')


class handler:        
    # 返回指定note_code的注释，返回json格式
    @app_helper.ex_check_sign(['app_id','tick','note_code','version'], 'TNM') 
    def POST(self):
        web.header("Content-Type", "application/json")

        param = web.input(note_code='', version='')
        #print param

        if param.note_code=='':
            return json.dumps({'ret':-4, 'msg':'无效的note_code'})

        # 先指定版本查找，未找到则不指定版本，只按索引号找 2019-02-02
        r2 = db.notes.find_one({'note_code':param['note_code'].upper(), 'version' : param['version']}) # 索引编码大写,
        if r2 is None:
            print 'NOT FOUND NOTE with version'
            r2 = db.notes.find_one({'note_code':param['note_code'].upper()}) # 索引编码大写
            if r2 is None:
                print 'NOT FOUND NOTE'
                return json.dumps({'ret':-5, 'msg':'未找到注释内容！'})

        app_helper.log_app_api('external', 'node_note', param)

        ret_data = {
            'note'   : r2['note_content'],
        }

        return json.dumps({'ret':0,'data':ret_data})


