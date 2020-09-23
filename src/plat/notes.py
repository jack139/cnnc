#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 注释管理

url = ('/plat/notes')

PAGE_SIZE = 30

#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'DATA_MODIFY'):
            raise web.seeother('/')
        user_data=web.input(page='0', note_code='')
        render = helper.create_render()

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  

        conditions ={}

        note_code = user_data.note_code.strip()
        if note_code!='':

            conditions['note_code'] = { '$regex' : u'%s.*'%(note_code.replace('*','\\*').replace('?','\\?')), '$options' : 'i' }

        # 分页获取数据
        db_sku = db.notes.find(conditions,
            sort=[ ('weight', 1) ],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE
        
        return render.notes(helper.get_session_uname(), helper.get_privilege_name(), db_sku,
            range(0, num), note_code, int(user_data['page']))
