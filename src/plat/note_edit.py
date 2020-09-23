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

# 注释信息编辑

url = ('/plat/note_edit')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'DATA_MODIFY'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(note_id='')

        note_data = { 'note_id' : 'n/a'}

        if user_data.note_id != '': 
            db_obj=db.notes.find_one({'_id':ObjectId(user_data.note_id)})
            if db_obj!=None:
                # 已存在的obj
                note_data = db_obj
                note_data['note_id']=note_data['_id']

        return render.note_edit(helper.get_session_uname(), helper.get_privilege_name(), 
            note_data)


    def POST(self):
        if not helper.logged(helper.PRIV_USER, 'DATA_MODIFY'):
            raise web.seeother('/')
        render = helper.create_render()
        user_data=web.input(note_id='',note_code='', note_content='')

        note_code = user_data.note_code.strip().upper() # note_code 都是用大写字母
        if note_code=='':
            return render.info('索引编码不能为空！')  
        
        version = user_data.version.strip()

        # 排除同名
        find_condition = {'note_code' : note_code, 'version': version }

        if user_data['note_id']=='n/a': # 新建
            note_id = None
            message = '新建'
        else:
            note_id = ObjectId(user_data['note_id'])
            message = '修改'
            find_condition['_id'] = { '$ne' : note_id} # 排除自己

        r1 = db.notes.find_one(find_condition)
        if r1 is not None:
            return render.info('索引编码已存在，不能重复！')  

        try:
            update_set={
                'note_code'   : note_code,
                'version'     : version, # 版本说明  2018-10-18
                'note_content': user_data['note_content'],
                'last_tick'   : int(time.time()),  # 更新时间戳
                'weight'      : int(user_data['weight']),
            }
        except ValueError:
            return render.info('请在相应字段输入数字！')

        if note_id is None:
            update_set['history'] = [(helper.time_str(), helper.get_session_uname(), message)]
            r2 = db.notes.insert_one(update_set)
        else:
            db.notes.update_one({'_id':note_id}, {
                '$set'  : update_set,
                '$push' : {
                    'history' : (helper.time_str(), helper.get_session_uname(), message), 
                }  # 纪录操作历史
            })

        return render.info('成功保存！', '/plat/notes')
