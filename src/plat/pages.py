#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import web
from bson.objectid import ObjectId
from config import setting
import helper

db = setting.db_web

# 页面管理

url = ('/plat/pages')

PAGE_SIZE = 30

# 返回目录里所有问题节点的数量
def count_question(parent_id):
    question = 0
    r2 = db.pages.find({'parent_id':str(parent_id)})
    for i in r2:
        if i['page_type']==0: # 普通页面
            r3 = db.nodes.find({'page_id':str(i['_id']), 'node_question':True})
            question += r3.count()
        else: # 目录
            question += count_question(i['_id'])
    return question

#  -------------------
class handler:  
    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'DATA_MODIFY'):
            raise web.seeother('/')
        user_data=web.input(page='0',parent_id='')
        render = helper.create_render()

        if not user_data['page'].isdigit():
            return render.info('参数错误！')  

        last_dir_id = ''
        last_dir_name = ''
        if user_data['parent_id']!='':
            db_obj=db.pages.find_one({'_id':ObjectId(user_data.parent_id)})
            if db_obj:
                last_dir_id = str(db_obj['parent_id'])
                last_dir_name = db_obj['dir_name']

        # 分页获取数据
        db_sku = db.pages.find({'parent_id' : user_data['parent_id']},
            sort=[ ('available', -1), ('weight', 1), ('page_type', -1) ],
            limit=PAGE_SIZE,
            skip=int(user_data['page'])*PAGE_SIZE
        )

        data = []

        for i in db_sku:
            if i.get('page_type', 0)==0: # 普通页面
                r2 = db.nodes.find({'page_id':str(i['_id']), 'node_question':True})
                i['node_question'] = r2.count()
            else: # 目录
                i['node_question'] = count_question(i['_id'])
            data.append(i)

        num = db_sku.count()
        if num%PAGE_SIZE>0:
            num = num / PAGE_SIZE + 1
        else:
            num = num / PAGE_SIZE
        
        return render.pages(helper.get_session_uname(), helper.get_privilege_name(), data,
            range(0, num), user_data['parent_id'], last_dir_id, last_dir_name, int(user_data['page']))
