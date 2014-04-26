
import requests
import xml.etree.ElementTree as ET

def api(**options):
	appname  = options['appname']
	apptoken = options['apptoken']
	return Api({'X-appname': appname, 'X-token': apptoken})

class Api:
	"""
		Root of all evil.
	"""
	def __init__(self, headers):
		self.headers = headers

	def user(self, **options):
		username = options['username']
		password = options['password']
		r = requests.post('https://auth.dtu.dk/dtu/mobilapp.jsp', { 'username': username, 'password': password })
		LIMITEDPASSWORD = ET.fromstring(r.text)[0].attrib['Password']
		return CurrentUser((username, LIMITEDPASSWORD), self.headers)


class CurrentUser:
	"""
		Logged in user.
	"""
	
	__BASEURL = 'https://www.campusnet.dtu.dk/data/CurrentUser'

	def __init__(self, auth, headers):
		self.auth 	 = auth
		self.headers = headers

	def courses(self):
		xml = requests.get(self.__BASEURL + '/Elements', auth=self.auth, headers=self.headers).text.encode('utf-8')
		courses = [group for group in ET.fromstring(xml).findall('Grouping') if group.attrib['Name'] == 'Courses'][0]
		for element in courses: yield Element(self.auth, self.headers, element.attrib['Id'], element.attrib['Name'])	

	def groups(self):
		xml = requests.get(self.__BASEURL + '/Elements', auth=self.auth, headers=self.headers).text.encode('utf-8')
		groups = [group for group in ET.fromstring(xml).findall('Grouping') if group.attrib['Name'] == 'Groups'][0]
		for element in groups: yield Element(self.auth, self.headers, element.attrib['Id'], element.attrib['Name'])

class Element:
	"""
		A course or a group.
	"""

	def __init__(self, auth, headers, id, name):
		self.auth 		= auth
		self.headers 	= headers
		self.id 		= id
		self.name   	= name
		self.__BASEURL 	= 'https://www.campusnet.dtu.dk/data/CurrentUser/Elements/%s' % id

	def fs(self):
		xml = requests.get(self.__BASEURL + '/Files', auth=self.auth, headers=self.headers).text.encode('utf-8')
		return self.__fs(ET.fromstring(xml))

	def __fs(self, node):
		folder = Folder(node.attrib['Name'], node.attrib['Id'])
		folder.folders = [self.__fs(child) for child in node if child.tag == 'Folder']
		folder.files   = [File(self.auth, self.headers, self.id, child) for child in node if child.tag == 'File']
		return folder 

class Folder:
	"""
		A folder.
	"""

	def __init__(self, name, id):
		self.name 		= name
		self.id 		= id

	def pprint(self):
		self.__pprint(0)

	def __pprint(self, index):
		print ' ' * index * 4, '>', self.name
		for folder in self.folders: folder.__pprint(index + 1)
		for file in self.files: print ' ' * (index + 1) * 4, '*', file.name

	def file(self, id):
		return [file for file in self.files if file.id == id][0]

	def folder(self, id):
		return [folder for folder in self.folders if folder.id == id][0]

class File:
	"""
		A file.
	"""
	def __init__(self, auth, headers, elementId, node):
		self.auth = auth
		self.headers = headers
		self.id      = node.attrib['Id']
		self.name    = node.attrib['Name']
		self.__BASEURL = 'https://www.campusnet.dtu.dk/data/CurrentUser/Elements/%s/Files/%s' % (elementId, node.attrib['Id'])
		self.elementId = elementId
		self.versions  = [FileVersion(self.auth, self.headers, elementId, node.attrib['Id'], child.attrib['Version']) for child in node if child.tag == 'FileVersion']

	def bytes(self):
		params = {'serviceUsername': self.auth[0], 'servicePassword': self.auth[1]}
		return requests.get(self.__BASEURL + '/Bytes', auth=self.auth, headers=self.headers, params=params).content

	def version(self, version):
		return [fileVersion for fileVersion in self.versions if fileVersion.version == version][0]

class FileVersion:
	"""
		A version of a file.
	"""
	def __init__(self, auth, headers, id, fileId, version):
		self.auth 		= auth
		self.headers 	= headers
		self.version 	= version
		self.__BASEURL 	= 'https://www.campusnet.dtu.dk/data/CurrentUser/Elements/%s/Files/%s/Versions/%s' % (id, fileId, version)

	def bytes(self):
		params = {'serviceUsername': self.auth[0], 'servicePassword': self.auth[1]}
		return requests.get(self.__BASEURL + '/Bytes', auth=self.auth, headers=self.headers, params=params).content

