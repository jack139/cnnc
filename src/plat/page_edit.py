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

# 页面信息编辑

url = ('/plat/page_edit')

class handler:

    def GET(self):
        if not helper.logged(helper.PRIV_USER, 'DATA_MODIFY'):
            raise web.seeother('/')

        render = helper.create_render()
        user_data = web.input(page_id='', parent_id='')

        page_data = { 'page_id' : 'n/a', 'parent_id' : user_data['parent_id']}

        if user_data.page_id != '': 
            db_obj=db.pages.find_one({'_id':ObjectId(user_data.page_id)})
            if db_obj!=None:
                # 已存在的obj
                page_data = db_obj
                page_data['page_id']=page_data['_id']
        else:
            # 获取所在目录的版本信息
            version = ''
            if page_data['parent_id']!='':
                parent_id = page_data['parent_id']
                while True:
                    print parent_id
                    r7 = db.pages.find_one({'_id':ObjectId(parent_id)})
                    if r7 is None:
                        break

                    if r7['parent_id']!='':
                        parent_id = r7['parent_id']
                    else:
                        if r7['page_type']==1:
                            version = r7['dir_note']
                        break
            page_data['version'] = version

        # 生成目录树清单
        dir_list = {}
        r2 = db.pages.find({'page_type':1})
        for x in r2:
            dir_list[str(x['_id'])] = {
                'parent_id' : x['parent_id'],
                'dir_name'  : x['dir_name'],
                'path'      : x['dir_name'],
            }

        for i in dir_list.keys():
            x = dir_list[i]
            parent = x['parent_id']
            while(parent!=''):
                x['path'] = dir_list[parent]['dir_name'] + '/' + x['path']
                parent = dir_list[parent]['parent_id']
            x['path'] = '/' + x['path']

        #print dir_list

        dir_list[''] = {
            'path' : '/'
        }

        dir_list2 = sorted(dir_list.items(), key=lambda s: s[1]['path'])

        print dir_list2

        return render.page_edit(helper.get_session_uname(), helper.get_privilege_name(), 
            page_data, dir_list2)


    def POST(self):
        if not helper.logged(helper.PRIV_USER, 'DATA_MODIFY'):
            raise web.seeother('/')
        render = helper.create_render()
        user_data=web.input(page_id='',page_code='', page_name='', parent_id='', rich_text='')

        page_code = user_data.page_code.strip().upper() # page_code都是用大写字母
        if page_code=='':
            return render.info('页面编码不能为空！')  

        # 排除同名, 只比较在使用的，忽略停用的 2019-03-20
        find_condition = {'page_code' : page_code, 'version' : user_data['version'], 'available' : 1 }

        if user_data['page_id']=='n/a': # 新建
            page_id = None
            message = '新建'
        else:
            page_id = ObjectId(user_data['page_id'])
            message = '修改'
            find_condition['_id'] = { '$ne' : page_id} # 排除自己

        r1 = db.pages.find_one(find_condition)
        if r1 is not None:
            return render.info('页面编码已存在，不能重复！')  

        try:
            update_set={
                'page_code'   : page_code,
                'page_name'   : user_data['page_name'],
                'version'     : user_data['version'],
                'available'   : int(user_data['available']),
                'last_tick'   : int(time.time()),  # 更新时间戳
                'first_page'  : int(user_data['first_page']),
                'parent_id'   : user_data['parent_id'],
                'rich_text'   : '' if user_data['rich_text']=='<br>' else user_data['rich_text'], # 去除只有<br>的内容 2019-02-12
                'weight'      : int(user_data['weight']),
                'page_type'   : 0,
            }
        except ValueError:
            return render.info('请在相应字段输入数字！')

        if page_id is None:
            update_set['history'] = [(helper.time_str(), helper.get_session_uname(), message)]
            r2 = db.pages.insert_one(update_set)

            # 新建页面，插入起始节点
            r3 = db.nodes.insert_one({
                'page_id'   : str(r2.inserted_id),
                'node_type' : 0,
                'parent'    : [],
                'child'     : [],
                'text'      : '0',
                'position'  : {'y': 175, 'x': 50},  # 节点在页面的位置
            })

            # 在页面记录起始节点
            db.pages.update_one({'_id':r2.inserted_id}, {'$set':{'start_node':str(r3.inserted_id)}})

        else:
            db.pages.update_one({'_id':page_id}, {
                '$set'  : update_set,
                '$push' : {
                    'history' : (helper.time_str(), helper.get_session_uname(), message), 
                }  # 纪录操作历史
            })

        return render.info('成功保存！', '/plat/pages?parent_id='+user_data['parent_id'])
