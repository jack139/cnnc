#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 自动回复规则

url = ('/plat/bayes')

PAGE_SIZE = 30

#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'TALKBOT'):
            raise web.seeother('/')
        user_data=web.input(page='0', rule_name='')
        render = helper.create_render()

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  

        conditions ={}

        rule_name = user_data.rule_name.strip()
        if rule_name!='':
            conditions = {
                '$or' : [
                    {'key_word'  : { '$regex' : u'%s.*'%(rule_name.replace('*','\\*').replace('?','\\?')), '$options' : 'i' }},
                    {'reply'     : { '$regex' : u'%s.*'%(rule_name.replace('*','\\*').replace('?','\\?')), '$options' : 'i' }},
                    {'rule_name' : { '$regex' : u'%s.*'%(rule_name.replace('*','\\*').replace('?','\\?')), '$options' : 'i' }},
                ]
            }


        # 分页获取数据
        db_sku = db.bayes.find(conditions,
            sort=[ ('available', -1), ('rule_name', 1) ],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE
        
        return render.bayes(helper.get_session_uname(), helper.get_privilege_name(), db_sku,
            range(0, num), rule_name, int(user_data['page']))
