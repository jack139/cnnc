#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, copy
from bson.objectid import ObjectId
import helper
from config import setting

db = setting.db_web

# 修改目录版本时，更新所有此目录下页面版本信息
# 修改目录可用状态时，更新所有此目录下页面可用状态
def dir_update(dir_id, update_set):
    if dir_id=='':
        return

    db.pages.update_one({'_id':ObjectId(dir_id), 'page_type':1}, {'$set':update_set})

    r1 = db.pages.find({'parent_id' : dir_id})
    for i in r1:
        if i['page_type']==1: # 目录
            dir_update(str(i['_id']), update_set)
        else:
            db.pages.update_one({'_id':i['_id']}, {'$set':update_set})                

    return

# 复制页面node
def nodes_copy(source_page, start_node, target_page):
    ref = {}
    r2 = db.nodes.find({'page_id':source_page})
    for i in r2:
        c = i.copy()
        old_id = str(c.pop('_id'))
        c['page_id'] = target_page
        target_id = db.nodes.insert_one(c)
        target_id = str(target_id.inserted_id)
        # 建立新旧节点对照
        ref[old_id] = target_id

    # 复制 connect
    r3 = db.connect.find({'page_id':source_page})
    for i in r3:
        c = i.copy()
        c.pop('_id')
        c['page_id'] = target_page
        c['source'] = ref[c['source']] # 转换为心的node_id
        c['target'] = ref[c['target']] # 转换为心的node_id
        target_id = db.connect.insert_one(c)
        #target_id = str(target_id.inserted_id)

    # 整理新复制node 的 parent 和 child
    r4 = db.nodes.find({'page_id':target_page})
    for i in r4:
        new_parent = [ref[x] for x in i['parent']]
        new_child = [ref[x] for x in i['child']]
        db.nodes.update_one({'_id':i['_id']}, {'$set':{
            'parent' : new_parent,
            'child'  : new_child,
        }})

    # 更新新页面的 start_node
    db.pages.update_one({'_id':ObjectId(target_page)}, {'$set':{'start_node':ref[start_node]}})


# 复制目录
def dir_copy(source_dir, target_id=''):
    if source_dir=='':
        return None

    if target_id=='':
        r0 = db.pages.find_one({'_id' : ObjectId(source_dir)})    
        if r0 is None:
            return None

        if r0['page_type']!=1: # 不是目录，不复制
            return None

        c = r0.copy()
        c.pop('_id')
        c['dir_name'] = c['dir_name']+u'（副本）'
        c['available'] = 0
        c['history'] = [(helper.time_str(), 'dir copy', 'dir copy')]
        target_id = db.pages.insert_one(c)
        target_id = str(target_id.inserted_id)

    r1 = db.pages.find({'parent_id' : source_dir})
    for i in r1:
        c = i.copy()
        c.pop('_id')
        c['parent_id'] = target_id
        c['available'] = 0
        c['history'] = [(helper.time_str(), 'copy', 'copy')]
        d = db.pages.insert_one(c)
        d = str(d.inserted_id)

        if i['page_type']==1: # 目录
            dir_copy(str(i['_id']), d)
        elif i['page_type']==0: # 页面，拷贝nodes
            nodes_copy(str(i['_id']), i['start_node'], d)

    return target_id
