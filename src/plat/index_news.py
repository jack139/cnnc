#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 聊天机器人回复规则

url = ('/plat/index_news')

PAGE_SIZE = 30

#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'TALKBOT'):
            raise web.seeother('/')
        user_data=web.input(page='0', news_title='')
        render = helper.create_render()

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  

        conditions ={}

        news_title = user_data.news_title.strip()
        if news_title!='':
            conditions = {
                {'news_title'  : { '$regex' : u'%s.*'%(news_title.replace('*','\\*').replace('?','\\?')), '$options' : 'i' }},
            }

        # 分页获取数据
        db_sku = db.index_news.find(conditions,
            sort=[ ('available', -1), ('news_title', 1) ],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE
        
        return render.index_news(helper.get_session_uname(), helper.get_privilege_name(), db_sku,
            range(0, num), news_title, int(user_data['page']))
