#!/usr/bin/env python
import requests
import re
import sys

class Endomondo:
	session = requests.Session()
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:26.0) Gecko/20100101 Firefox/26.0'}
	url_init = "https://www.endomondo.com/access"
	url_base = "http://endomondo.com"
	email = ""
	password = ""
	path = ""
	
	def __init__(self, email, password):
		self.email = email 
		self.password = password
		self.session.headers.update(self.headers)

	def get_url(self, url):
		return self.session.get(url)

	def login(self):
		content = self.get_url(self.url_init)
		m = re.search('action="([^"]+)" ', content.text)
		url_login = self.url_init + m.group(1)
		self.session.headers.update({'referer': self.url_init})
		post_data = {'signInButton':'x','rememberMe':'on','email':self.email,'password':self.password}
		self.session.post(url_login,data=post_data)

	def get_workout(self, url):
		content = self.get_url(url)
		m = re.search('<a class="enabled button export" .*(\?wicket[^\']+)\'.*>',content.text)
		url_export = ""
		try:
			url_export = self.url_base + m.group(1)
		except:
			#print ("ERROR: No export button")
			return None
		m = re.search('<div class="date-time">([^<]+)<.div>',content.text)
		datetime = m.group(1)
		print(datetime)
		content = self.get_url(url_export)
		m = re.search('(\?wicket[^"]+GpxLink[^"]+)',content.text)
		url_return = self.url_base+m.group(1)
		return {'url':url_return, 'datetime':datetime}

	def save_workout(self, download_url, file_path):
		with open(file_path, 'wb') as handle:
			request = self.session.get(download_url, stream=True)
			for block in request.iter_content(1024):
				if not block:
					break
				handle.write(block)

	def save_workouts(self):
		content = self.get_url("http://www.endomondo.com/workouts/list/")
		pages = re.findall('(\?wicket[^"]+).*? title="[^"]+">[0-9]+<\/a>',content.text)
		workout_url_list = []
		pages.append("/workouts/list/")
		for page in pages:
			content = self.get_url(self.url_base+page)
			workout_list = re.split('<input type="checkbox" name="pageContainer',content.text)
			for workout in workout_list:
				re.purge()
				c = re.search('<span>[0-9]{4}-[0-9]{2}-[0-9]{2}</span>',workout)
				if(type(c) != type(None)):
					i = re.search('<td id="[^"]+" onclick="var wcall=.*?(\?wicket[^\']+)',workout)
					try:
						url = self.get_workout(self.url_base+i.group(1))
						self.save_workout(url['url'],self.path+url['datetime']+".gpx")
					except:
						print("ERROR")
						pass
		return workout_url_list


if(len(sys.argv) == 3):
	endo = Endomondo(sys.argv[1],sys.argv[2])
	print(sys.argv[1]+" "+sys.argv[2])
	endo.login()
	endo.save_workouts()
elif(len(sys.argv) == 4):
	endo = Endomondo(sys.argv[1],sys.argv[2])
	endo.path = sys.argv[3]
	endo.login()
	endo.save_workouts()
else:
	print("Usage: ./export.py email password path_to_save(optional)")
