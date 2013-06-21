from __future__ import print_function
import os
import sys
import urllib
import time
try:
	import requests
	import simplejson
	from simplejson.compat import StringIO
except ImportError:
	print('Error importing one of the important libraries. Please install it.')
	sys.exit(1)

class Edison(object):
	"""docstring for Edison"""

	def start(self, site, key):
		self.req = requests.get('http://api.tumblr.com/' \
		'v2/blog/%s/info?api_key=%s' % (site, key))
		if (self.req.status_code == 200):
			self.req = self.req.json()
			self.req = simplejson.loads(simplejson.dumps(self.req))
			return self.req
		else:
			print('Error of status %s: %s'\
					% (self.req['meta']['status'], self.req['meta']['msg']))
			sys.exit(1)

	def fetch_all_posts(self, site, key,
						limit=0):
		if (limit == 0):
			self.posts = requests.get('http://api.tumblr.com/' \
				'v2/blog/%s/posts/?api_key=%s' % (site, key))
		else:
				self.posts = requests.get('http://api.tumblr.com/' \
					'v2/blog/%s/posts/?api_key=%s&limit=%d' % (site, key, limit))
		self.posts = simplejson.loads(simplejson.dumps(self.posts.json()))
		self.posts = self.posts['response']['posts']
		return self.posts

	def make_ReST(self, text):
		try:
			from html2rest import html2rest
		except ImportError:
			return "Impossible to convert."
			sys.exit(1)

		if (text != ''):
			text = html2rest(text, "utf-8", StringIO)
			return text

	def make_Nikola_imgPost(self, post_index, total, folder='tumblr/'):
		self.index = 0
		while (self.index != total):
			self.post = post_index[self.index]
			self.image = self.post['photos'][0]['original_size']['url']
			self.image_name, self.image_extension = os.path\
				.splitext(self.image)
			# The original filename does not exist, the Tumblr hash is
			# quite shitty and I prefer to use the timestamp
			self.image_name = self.post['reblog_key']
			self.output = folder + self.image_name\
								 + self.image_extension
			urllib.urlretrieve(self.image, '%s' % (self.output))
			try:
				self.new_post = open('%s.txt' % self.post['id'], 'wb')
			except IOError:
				return "Impossible to create new post."
				sys.exit(1)

			self.Npost = """.. link: %s
.. description: %s 
.. tags: %s
.. date: %s
.. title: %s
.. slug: %s

.. Image:: %s
%s""" % (self.post['id'], self.post['caption'],
			self.post['tags'], self.post['date'],
			self.post['id'], self.post['slug'],
			self.output, self.post['caption'])
			self.post_path = folder + 'stories/'
			if not os.path.exists(self.post_path):
				os.makedirs(self.post_path)			
			self.new_post.write(folder + self.Npost)
			self.new_post.close()
			# With this timer the code should be able
			# to avoid Tumblr's shutdown on its own API
			time.sleep(3)
			self.index = self.index + 1

	def fetch_image_posts(self, site, key, limit=0,
						  folder='tumblr/'):
		if not os.path.exists(folder):
			os.makedirs(folder)

		self.img_posts = requests.get('http://api.tumblr.com/'\
			'v2/blog/%s/posts?api_key=%s&type=photo' % (site, key))

		if (limit != 0):
			self.img_posts = requests.get('http://api.tumblr.com/'\
				'v2/blog/%s/posts?api_key=%s&type=photo&limit=' \
				% (site, key, self.img_posts['response']['total_posts']))
			self.img_posts = simplejson.loads(simplejson\
				.dumps(self.img_posts.json()))
			self.make_Nikola_imgPost(self.img_posts['response']['posts'],
									 20, folder) # Tumblr's default load
		self.make_Nikola_imgPost(self.img_posts['response']['posts'],
								 limit, folder)

	def make_Nikola_textPost(self, post_index, total, folder='tumblr/'):
		if (total == 0):
			return "Nothing to import."
		elif (total == 1):
			try:
				self.new_post = open('%s.txt' % post_index['title'], 'wb')
			except IOError:
				return "Impossible to create new post."
				sys.exit(1)

			if(post_index['title'] != ''):
				self.Npost = """.. link: %s
.. description: %s 
.. tags: %s
.. date: %s
.. title: %s
.. slug: %s

%s""" % (self.post['title'], self.post['caption'],
				self.post['tags'], self.post['date'],
				self.post['id'], self.post['slug'],
				make_ReST(self.post['body']))

			self.post_path = folder + 'stories/'
			if not os.path.exists(self.post_path):
				os.makedirs(self.post_path)			
			self.new_post.write(folder + self.Npost)
			self.new_post.close()
		else:
			self.index = 0
			while (self.index != total):
				try:
					self.new_post = open('%s.txt' % post_index['title'], 'wb')
				except IOError:
					return "Impossible to create new post."
					sys.exit(1)

				if(post_index['title'] != ''):
					self.Npost = """.. link: %s
.. description: %s 
.. tags: %s
.. date: %s
.. title: %s
.. slug: %s

%s""" % (self.post['title'], self.post['caption'],
					self.post['tags'], self.post['date'],
					self.post['id'], self.post['slug'],
					make_ReST(self.post['body']))

				self.post_path = folder + 'stories/'
				if not os.path.exists(self.post_path):
					os.makedirs(self.post_path)			
				self.new_post.write(folder + self.Npost)
				self.new_post.close()
				# With this timer the code should be able
				# to avoid Tumblr's shutdown on its own API
				time.sleep(3)
				self.index = self.index + 1

	def fetch_text_posts(self, site, key, get_type, limit=0,
						 folder='tumblr/'):
		"""
			Note that this function works on text, quote, link and chat
			all at one. It won't download images inside the posts but it
			will link them directly, which might be changed in the future
			after Nikola supports a basic image uploading system, or the
			user might as well do it manually.
		"""
		self.text_posts = requests.get('http://api.tumblr.com/'\
				'v2/blog/%s/posts?api_key=%s&type=%s' % (site, key, get_type))
		self.text_posts = simplejson.loads(simplejson\
						  .dumps(self.text_posts.json()))
		self.total_posts = self.text_posts['response']['total_posts']
		if (limit != 0):
			self.text_posts = requests.get('http://api.tumblr.com/'\
				'v2/blog/%s/posts?api_key=%s&type=%s&limit'\
				% (site, key, get_type,
				   self.text_posts['response']['total_posts']))
		self.text_posts = simplejson.loads(simplejson\
						  .dumps(self.text_posts.json()))
		self.all_text_posts = self.text_posts['response']['posts'][0]
		self.make_Nikola_textPost(self.all_text_posts, self.total_posts)