#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
import json
from config import setting

db = setting.db_web

# 点击次数

url = ('/wx/click_count')

class handler:  
    def POST(self):
        web.header('Content-Type', 'application/json')
        param = web.input()

        r = db.sys_refs.find_one({'name' : 'click_count'},{'c':1})

        # 返回
        return json.dumps({'ret' : 0, 'data' : {
            'c' : '{:,}'.format(int(r['c'])) if r else '0',
        }})
