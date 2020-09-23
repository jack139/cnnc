#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 删除目录（目录必须为空）

url = ('/plat/dir_remove')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'DATA_MODIFY'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(page_id='', parent_id='')

        if user_data.page_id == '': 
            return render.info('参数错误！')  

        db_obj=db.pages.find({'parent_id':user_data.page_id})
        if db_obj.count()>0:
            return render.info('只能删除空的目录！')

        db.pages.delete_one({'_id':ObjectId(user_data.page_id), 'page_type':1})

        return render.info('成功删除！', '/plat/pages?parent_id='+user_data['parent_id'])

