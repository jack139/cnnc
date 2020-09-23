#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 负责tnm规则

url = ('/plat/tnm_copy')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'TNM_DATA'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(rule_id='')

        if user_data.rule_id == '': 
            return render.info('参数错误！')  

        r1 = db.tnm.find_one({'_id':ObjectId(user_data.rule_id)})
        if r1 is None:
        	return render.info('rule_id错误！')  

        r1.pop('_id')
        r1['tnm_name'] = r1['tnm_name'] + ' - ' + helper.my_rand(4).upper()
        r1['available'] = 0

        r1['history'] = [(helper.time_str(), helper.get_session_uname(), '复制')]
        r2 = db.tnm.insert_one(r1)

        return render.info('复制成功！复制后的病种名为：'+r1['tnm_name'].encode('utf-8'), '/plat/tnm')

