#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, os
import helper

db = helper.db


# 删除指定文件夹内容

# 删除页面node
def nodes_remove(source_page, action='try'):
    ref = {}
    r2 = db.nodes.find({'page_id':source_page})
    print 'node:    ', r2.count()
    for i in r2:
        if action=='do':
            db.nodes.delete_one({'_id':i['_id']})
        #print 'node:', i['_id']

    # 删除 connect
    r3 = db.connect.find({'page_id':source_page})
    print 'connect: ', r3.count()
    for i in r3:
        if action=='do':
            db.connect.delete_one({'_id':i['_id']})
        #print 'connect:', i['_id']


# 删除目录
def dir_empty(source_dir, action='try'):
    if source_dir=='':
        return None

    r1 = db.pages.find({'parent_id' : source_dir})
    for i in r1:
        if i['page_type']==1: # 目录
            print '--> ', i['dir_name']
            dir_empty(str(i['_id']), action)            
        else:
            print '   ', i['page_code']
            nodes_remove(str(i['_id']), action)

        if action=='do':
            db.pages.delete_one({'_id':i['_id']})



if __name__ == "__main__":
    if len(sys.argv)<3:
        print "usage: python %s <dir_id> <try|do>" % sys.argv[0]
        sys.exit(2)

    dir_id = sys.argv[1]
    action = sys.argv[2]

    dir_empty(dir_id, action)

