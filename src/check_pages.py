#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, os
from bson.objectid import ObjectId
import helper

db = helper.db


if __name__ == "__main__":

	r1 = db.pages.find()

	for i in r1:
		if i.get('parent_id','')=='':
			#print 'BLANK parent: ', i['_id']
			continue

		r2 = db.pages.find_one({'_id':ObjectId(i['parent_id'])})
		if r2 is None:
			print 'MISS parent: ', i['_id'], i['parent_id'], i['page_code']

