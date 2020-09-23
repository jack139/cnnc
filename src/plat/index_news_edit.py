#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
from datetime import datetime
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 聊天机器人规则编辑

url = ('/plat/index_news_edit')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'TALKBOT'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(news_id='')

        news_data = { 'news_id' : 'n/a' }

        if user_data.news_id != '': 
            db_obj=db.index_news.find_one({'_id':ObjectId(user_data.news_id)})
            if db_obj!=None:
                # 已存在的obj
                news_data = db_obj
                news_data['news_id']=news_data['_id']

        return render.index_news_edit(helper.get_session_uname(), helper.get_privilege_name(), news_data )


    def POST(self):
        if not helper.logged(helper.PRIV_USER, 'TALKBOT'):
            raise web.seeother('/')
        render = helper.create_render()
        user_data=web.input(news_id='', news_title='')

        news_title = user_data.news_title.strip()
        if news_title=='':
            return render.info('标题不能为空！')  

        # 排除同名
        find_condition = {
            'news_title'  : news_title,
        }

        if user_data['news_id']=='n/a': # 新建
            news_id = None
            message = '新建'
        else:
            news_id = ObjectId(user_data['news_id'])
            message = '修改'
            find_condition['_id'] = { '$ne' : news_id}  # 排除自己

        r1 = db.index_news.find_one(find_condition)
        if r1 is not None:
            return render.info('标题已存在，不能重复！')  


        try:
            update_set={
                'news_title'  : news_title,
                'news_type'   : int(user_data['news_type']), 
                'news_link'   : user_data['news_link'].strip(),
                'news_text'   : user_data['news_text'],
                'available'  : int(user_data['available']),
                'last_tick'  : datetime.now(), 
            }
        except ValueError:
            return render.info('请在相应字段输入数字！')

        if news_id is None:
            update_set['history'] = [(helper.time_str(), helper.get_session_uname(), message)]
            r2 = db.index_news.insert_one(update_set)
            
            #内容文本则需更新news_link指向自己
            if int(user_data['news_type']) == 2:
                news_id = r2.inserted_id
                db.index_news.update_one({'_id':news_id}, {'$set':{'news_link':'/ui/index_news?news_id='+str(news_id)}})
        else:
            db.index_news.update_one({'_id':news_id}, {
                '$set'  : update_set,
                '$push' : {
                    'history' : (helper.time_str(), helper.get_session_uname(), message), 
                }  # 纪录操作历史
            })

        return render.info('成功保存！', '/plat/index_news')
