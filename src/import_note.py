#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, time, os
import helper

db = helper.db

cnt = 0
wrn = 0


def process_file(file_name, action):
	global cnt, wrn

	f = open(file_name)


	while True:
		line = f.readline().strip()
		if not line:
			break

		#line2 = line.decode('gbk').encode('utf-8').split('\t') # for windows / Office export
		line2 = line.split('\t') # for deepin linux / WPS export

		if len(line2)>3 or len(line2)<3:
			print 'WARNING: ', file_name, line2
			wrn += 1

		if action=='do':
			note_code = line2[0].strip().upper()
			version = line2[1].strip()

			r1 = db.notes.find_one({'note_code' : note_code, 'version' : version})
			if r1: # 有重复
				print 'WARNING REPEAT: ', file_name, note_code
				wrn +=1
				continue

			

			line3 = line2[2].strip()
			line3 = line3[1:] if line3[0]=='"' else line3
			line3 = line3[:-1] if line3[-1]=='"' else line3

			update_set={
				'note_code'   : note_code,
				'version'     : version,
				'note_content': line3,
				'last_tick'   : int(time.time()),  # 更新时间戳
				'weight'      : 1,
				'history'     : [(helper.time_str(), 'import_note.py', '导入')]
			}
			r2 = db.notes.insert_one(update_set)
			#print update_set

		cnt += 1

	f.close()


if __name__ == "__main__":
	if len(sys.argv)<3:
		print "usage: python %s <dir_name> <try|do>" % sys.argv[0]
		sys.exit(2)

	dir_name = sys.argv[1]
	action = sys.argv[2]

	for i in os.listdir(dir_name):
		process_file(dir_name+'/'+i, action)

	print 'cnt=', cnt, '\twrn=', wrn
