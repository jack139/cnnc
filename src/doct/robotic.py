#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
from config import setting
from bson.objectid import ObjectId
import helper

db = setting.db_web

# 从指定节点返回后续节点，与js交互
url = ('/doct/robotic')


def find_child(node_id): # 参数node_id是ObjectId实例
    r1 = db.nodes.find_one({'_id': node_id})
    if r1 is None:
        return [] # node_id 错误

    if r1['text'][0]=='@': # 跳转到页面
        r2 = db.pages.find_one({'page_code':r1['text'][1:]})
        if r2 is None:
            return [] # 跳转页面不存在

        return find_child(ObjectId(r2['start_node']))

    child = []
    for i in r1['child']: # 检查子节点
        r3 = db.nodes.find_one({'_id': ObjectId(i)})
        if r3 is None:
            continue

        if r3['node_type']==0: #如果是虚节点，进一步处理
            child.extend(find_child(ObjectId(i)))
        else:
            child.append(r3)

    return child


class handler:        
    def GET(self):
        if not helper.logged(helper.PRIV_USER,'DOCTOR_USE'):
            raise web.seeother('/')

        render = helper.create_render()
        param=web.input(page_id='')

        r1 = db.pages.find_one({'_id': ObjectId(param['page_id'])})
        if r1 is None:
            return json.dumps({'ret':-2, 'msg':'page_id参数错误'})

        return render.robotic(helper.get_session_uname(), helper.get_privilege_name(), r1)


    # 返回指定node的下一层节点，返回json格式
    def POST(self):
        web.header("Content-Type", "application/json")
        if not helper.logged(helper.PRIV_USER, 'DOCTOR_USE'):
            return json.dumps({'ret':-1,'msg':'无访问权限'})

        param = web.input(node_id='')

        if param.node_id=='':
            return json.dumps({'ret':-1, 'msg':'参数错误'})

        child_data = find_child(ObjectId(param['node_id']))

        page_code_dict={}
        ret_data = []
        for i in child_data:
            if not page_code_dict.has_key(i['page_id']): # 获取节点的page_code
                r1 = db.pages.find_one({'_id':ObjectId(i['page_id'])})
                page_code_dict[i['page_id']]=r1['page_code']

            ret_data.append({
                'node_id'   : str(i['_id']),
                'text'      : i['text'],
                'page_code' : page_code_dict[i['page_id']],
            })

        return json.dumps({'ret':0,'data':ret_data})


