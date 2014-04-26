from __future__ import print_function
from collections import defaultdict
import cnapi
import os
import time

APPNAME  = 'SYCN'
APPTOKEN = '7f4655b9-609e-4220-88c3-db38433b8c50'

DATAFILE = '%s/.cnsync'
TEMPFILE = '%s/.cnsync_tmp'
LOGFILE  = '%s/cnsync.log'
LINETEMPLATE = '%s/%s/%s\n'

d = defaultdict(int)

# append content to file
def append(file, content):
	with open(file, 'a+') as f:
		f.write(content)
		f.close()

# write bytes to file
def wb(file, bytes):
	with open(file, 'wb') as f:
		f.write(bytes)
		f.close()

def update(dir, eid, folder):
	if not os.path.exists(dir): os.makedirs(dir)
	for file in folder.files:
		latestVersion = max([int(fileVersion.version) for fileVersion in file.versions])
		ourVersion    = d[eid + '/' + file.id]
		if ourVersion < latestVersion: 
			wb(dir + '/' + file.name, file.bytes())
			print('%s - %s is updated to version %s' % (time.strftime('%c'), file.name, latestVersion), file=open(LOGFILE % ROOT, 'a+'))
		append((TEMPFILE % ROOT), (LINETEMPLATE % (eid, file.id, str(latestVersion))))
	for subfolder in folder.folders: update(dir + '/' + subfolder.name, eid, subfolder)

def task():
	# read current versions of the files from .cnsync file in ROOT
	if not os.path.isfile(DATAFILE % ROOT): 
		open(DATAFILE % ROOT, 'w')
	with open((DATAFILE % ROOT), 'r') as f:
		lines = f.readlines()
		for line in lines: 
			eid, fid, v = line[:-1].split('/')
			d[eid + '/' + fid] = int(v)
		user = cnapi.api(appname=APPNAME, apptoken=APPTOKEN).user(username=USERNAME, password=PASSWORD)
		for course in user.courses(): update(ROOT + '/Courses/' + course.name, course.id, course.fs())
		for group in user.groups(): update(ROOT + '/Groups/' + group.name, group.id, group.fs())

	# clean out
	os.remove(DATAFILE % ROOT)
	os.rename(TEMPFILE % ROOT, DATAFILE % ROOT)

if __name__ == '__main__':
	config = {}
	execfile('cnsync.conf', config)

	# find username, password and ROOT folder from config file
	global ROOT, USERNAME, PASSWORD
	ROOT 	 = config['ROOT_FOLDER']
	USERNAME = config['USERNAME']
	PASSWORD = config['PASSWORD']
	INTERVAL = int(config['INTERVAL'])

	while INTERVAL > 0: task(), time.sleep(INTERVAL * 60)
	task()	