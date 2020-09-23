#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 删除聊天规则

url = ('/plat/index_news_remove')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'TALKBOT'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(news_id='')

        if user_data.news_id == '': 
            return render.info('参数错误！')  

        db.index_news.delete_one({'_id':ObjectId(user_data.news_id)})

        return render.info('成功删除！', '/plat/index_news')

