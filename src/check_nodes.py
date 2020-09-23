#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, os
from bson.objectid import ObjectId
import helper

db = helper.db

node_stack = []
history = []

def find_child(node_id, include_me='0'): # 参数node_id是ObjectId实例
	r1 = db.nodes.find_one({'_id': node_id})
	if r1 is None:
		return [] # node_id 错误

	#if r1['text'][0]=='@': # 跳转到页面
	#    r2 = db.pages.find_one({'page_code':r1['text'][1:]})
	#    if r2 is None:
	#        return [] # 跳转页面不存在
	#    return find_child(ObjectId(r2['start_node']))

	child = []

	if include_me=='1': # 包含自己
		if r1['text'][0]=='0': # 起始节点
			r3 = db.pages.find_one({'_id':ObjectId(r1['page_id'])}) # 检查也没是否有rich_text内容，如果有，加到起始节点的内容里
			if len(r3.get('rich_text','').strip())>0:
				r1['node_prop']=r3['rich_text']
			elif len(r1['child'])==1: # 是起始节点，且只有一个子节点，则不显示初始节点
				r2 = db.nodes.find_one({'_id': ObjectId(r1['child'][0])})
				if r2:
					r1 = r2
		child.append(r1)

	for i in r1['child']: # 检查子节点
		r3 = db.nodes.find_one({'_id': ObjectId(i)})
		if r3 is None:
			continue

		if r3['node_type']==0 and r3['text'][0]!='@': #如果是虚节点，且不是跳转节点，进一步处理
			child.extend(find_child(ObjectId(i)))
		else:
			child.append(r3)

	return child


def check_nodes():
	current = node_stack.pop()

	find_child(current, '1')

	r2 = db.nodes.find_one({'_id': ObjectId(current)})
	if r2 is None:
		print 'Error: cannot find node ', current
	else:
		#print current, r2['text'].encode('utf-8')
		for x in r2['child']:
			if x not in history:
				node_stack.append(x)
				history.append(x)


if __name__ == "__main__":
	'''
	r1 = db.pages.find({'available':0, 'page_type':0})
	#r1 = db.pages.find({'_id':ObjectId('5c0d01923c33c05c0b6383ee')})

	for i in r1:
		print i['page_code'], i['page_name']
		node_stack.append(i['start_node'])
		history.append(i['start_node'])

		n = 0
		while len(node_stack)>0:
			n += 1
			if n>100:
				print 'Warning: too many!'
				print node_stack
				node_stack=[]
			else:
				check_nodes()

	'''

	r1 = db.nodes.find()
	for x in r1:
		idd = str(x['_id'])
		if (idd in x.get('parent',[])) or (idd in x.get('child',[])):
			r2 = db.pages.find_one({'_id':ObjectId(x['page_id'])})
			print 'ERROR: ', idd, x['text'], r2['_id'], r2['page_code'], r2['page_name']
