#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
import web
import time
from bson.objectid import ObjectId
from config import setting
from libs import page_helper
import helper

db = setting.db_web

# 目录信息编辑

url = ('/plat/dir_edit')

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


        # 生成目录树清单
        dir_list = {}
        r2 = db.pages.find({'page_type':1})
        for x in r2:
            dir_list[str(x['_id'])] = {
                'parent_id' : x['parent_id'],
                'dir_name'  : x['dir_name'],
                'path'      : x['dir_name'],
                'version'   : x.get('version',''),
            }

        for i in dir_list.keys():
            x = dir_list[i]
            parent = x['parent_id']
            while(parent!=''):
                x['path'] = dir_list[parent]['dir_name'] + '/' + x['path']
                parent = dir_list[parent]['parent_id']
            x['path'] = '/' + x['path'] + '(' + x['version'] + ')'

        #print dir_list

        dir_list[''] = {
            'path' : '/'
        }

        dir_list2 = sorted(dir_list.items(), key=lambda s: s[1]['path'])

        print dir_list2

        return render.dir_edit(helper.get_session_uname(), helper.get_privilege_name(), 
            page_data, dir_list2)


    def POST(self):
        if not helper.logged(helper.PRIV_USER, 'DATA_MODIFY'):
            raise web.seeother('/')
        render = helper.create_render()
        user_data=web.input(page_id='', dir_name='', dir_note='', parent_id='')

        dir_name = user_data.dir_name.strip()
        if dir_name=='':
            return render.info('目录名不能为空！')  

        if user_data['page_id']==user_data['parent_id']:
            return render.info('目录位置不能是自己！')  

        dir_note = user_data['dir_note'].strip()

        # 排除同目录同名
        find_condition = {
            'parent_id' : user_data['parent_id'],
            'dir_name'  : dir_name,
            'dir_note'  : dir_note, 
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
            return render.info('目录名已存在，不能重复！')  


        try:
            update_set={
                'dir_name'   : dir_name,
                'dir_note'   : dir_note, # 版本信息
                'page_type'  : 1,
                'available'  : int(user_data['available']),
                'weight'     : int(user_data['weight']),
                'parent_id'  : user_data['parent_id'],
                'last_tick'  : int(time.time()),  # 更新时间戳
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

            # 更新所有此目录下页面信息 2018-10-20
            page_helper.dir_update(str(page_id), 
                {
                    'version'   : dir_note,
                    'available' : int(user_data['available']),
                }
            )

        return render.info('成功保存！', '/plat/pages?parent_id='+user_data['parent_id'])
