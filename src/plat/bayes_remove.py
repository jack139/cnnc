#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 删除规则

url = ('/plat/bayes_remove')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'TALKBOT'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(rule_id='')

        if user_data.rule_id == '': 
            return render.info('参数错误！')  

        db.bayes.delete_one({'_id':ObjectId(user_data.rule_id)})

        # 刷新分词字典
        db.sys_refs.update_one({'name' : 'dict_update'}, {'$set' : {'last_tick' : int(time.time())}}, upsert=True)

        return render.info('成功删除！', '/plat/bayes')

