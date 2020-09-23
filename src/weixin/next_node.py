#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
import json
from config import setting
from bson.objectid import ObjectId
import app_helper

db = setting.db_web

# 从指定节点返回后续节点，与js交互
url = ('/wx/next_node')


def find_child(node_id, include_me='0'): # 参数node_id是ObjectId实例
    r1 = db.nodes.find_one({'_id': node_id})
    if r1 is None:
        return [] # node_id 错误

    #if r1['text'][0]=='@': # 跳转到页面
    #    r2 = db.pages.find_one({'page_code':r1['text'][1:]})
    #    if r2 is None:
    #        return [] # 跳转页面不存在
    #    return find_child(ObjectId(r2['start_node']))

    me = []

    if include_me=='1': # 包含自己
        if r1['text'][0]=='0': # 起始节点
            r3 = db.pages.find_one({'_id':ObjectId(r1['page_id'])}) 
            # 检查也没是否有rich_text内容，如果有，且没有规则树，加到起始节点的内容里
            if len(r3.get('rich_text','').strip())>0 and len(r1['child'])==0: 
                r1['node_prop']=r3['rich_text']
            elif len(r1['child'])==1: # 是起始节点，且只有一个子节点，则不显示初始节点
                r2 = db.nodes.find_one({'_id': ObjectId(r1['child'][0])})
                if r2:
                    r1 = r2
        me.append(r1)

    child = []

    for i in r1['child']: # 检查子节点
        r3 = db.nodes.find_one({'_id': ObjectId(i)})
        if r3 is None:
            continue

        if r3['node_type']==0 and r3['text'][0]!='@': #如果是虚节点，且不是跳转节点，进一步处理
            child.extend(find_child(ObjectId(i)))
        else:
            child.append(r3)

    child = sorted(child, key=lambda s: s['position']['y'])

    return me + child


class handler:        
    # 返回指定node的下一层节点，返回json格式
    def POST(self):
        web.header("Content-Type", "application/json")

        param = web.input(session_id='', node_id='', include_me='0') # include_me == 1 同时返回当前节点数据

        print param

        if param.session_id=='':
            return json.dumps({'ret' : -1, 'msg' : 'session参数错误'})

        uname = app_helper.wx_logged(param.session_id)
        if uname is None:
            return json.dumps({'ret' : -2, 'msg' : '无效的session_id'})

        if param.node_id=='':
            return json.dumps({'ret':-2, 'msg':'参数错误'})

        ret_data = []

        child_data = find_child(ObjectId(param['node_id']), param.include_me)

        for i in child_data:
            ret_data.append({
                '_id'      : str(i['_id']),
                'text'     : i['text'],
                'position' : i['position'],
                'child'    : i['child'],
                'node_prop'     : i.get('node_prop',''), # 节点属性 2018－08-14
                'node_weight'   : i.get('node_weight','1'), # 节点权重 2018－08-14
            })

        print ret_data
        
        return json.dumps({'ret':0,'data':ret_data})


