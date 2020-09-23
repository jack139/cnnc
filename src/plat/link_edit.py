#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
#from libs import pos_func
import helper

db = setting.db_web

# 页面连接信息编辑

url = ('/plat/link_edit')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'DATA_MODIFY'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(page_id='', parent_id='')

        page_data = { 'page_id' : 'n/a', 'parent_id' : user_data['parent_id'] }

        if user_data.page_id != '': 
            db_obj=db.pages.find_one({'_id':ObjectId(user_data.page_id)})
            if db_obj!=None:
                # 已存在的obj
                page_data = db_obj
                page_data['page_id']=page_data['_id']

        return render.link_edit(helper.get_session_uname(), helper.get_privilege_name(), 
            page_data)


    def POST(self):
        if not helper.logged(helper.PRIV_USER, 'DATA_MODIFY'):
            raise web.seeother('/')
        render = helper.create_render()
        user_data=web.input(page_id='', link_name='', link_note='', link_page_code='', parent_id='')

        link_name = user_data.link_name.strip()
        if link_name=='':
            return render.info('页面链接名不能为空！')  

        # 排除同名
        find_condition = {
            'parent_id'  : user_data['parent_id'],
            'link_name'  : link_name,
        }

        if user_data['page_id']=='n/a': # 新建
            page_id = None
            message = '新建'
        else:
            page_id = ObjectId(user_data['page_id'])
            message = '修改'
            find_condition['_id'] = { '$ne' : page_id}  # 排除自己

        r1 = db.pages.find_one(find_condition)
        if r1 is not None:
            return render.info('页面链接名已存在，不能重复！')  


        try:
            update_set={
                'link_name'   : link_name,
                'link_note'   : user_data['link_note'],
                'link_page_code' : user_data['link_page_code'].upper().strip(),
                'page_type'   : 2,
                'available'   : int(user_data['available']),
                'weight'      : int(user_data['weight']),
                'parent_id'   : user_data['parent_id'],
                'last_tick'   : int(time.time()),  # 更新时间戳
            }
        except ValueError:
            return render.info('请在相应字段输入数字！')

        if page_id is None:
            update_set['history'] = [(helper.time_str(), helper.get_session_uname(), message)]
            r2 = db.pages.insert_one(update_set)
        else:
            db.pages.update_one({'_id':page_id}, {
                '$set'  : update_set,
                '$push' : {
                    'history' : (helper.time_str(), helper.get_session_uname(), message), 
                }  # 纪录操作历史
            })

        return render.info('成功保存！', '/plat/pages?parent_id='+user_data['parent_id'])
