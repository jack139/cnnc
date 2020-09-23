#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 删除tnm规则

url = ('/plat/tnm_remove')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'TNM_DATA'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(rule_id='')

        if user_data.rule_id == '': 
            return render.info('参数错误！')  

        db.tnm.delete_one({'_id':ObjectId(user_data.rule_id)})

        return render.info('成功删除！', '/plat/tnm')

