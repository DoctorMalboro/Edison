from __future__ import print_function, unicode_literals
import os
import re
import sys
import urllib
import time
try:
	import requests
	import simplejson
except ImportError:
	print('Error importing one of the important libraries. Please install it.')
	sys.exit(1)

class Edison(object):
	"""docstring for Edison"""

	def start(self, site, key):
		self.meta = requests.get('http://api.tumblr.com/' \
		'v2/blog/%s.tumblr.com/info?api_key=%s' % (site, key))
		if (self.meta.status_code == 200):
			self.meta = self.meta.json()
			print('Blog title: ', self.meta['response']['blog']['title'],\
				'\nBlog name: ', self.meta['response']['blog']['name'], \
				'\nBlog URL: ', self.meta['response']['blog']['url'], \
				'\nStarting Conversion....\n\n')
		else:
			print('Error!')
			sys.exit(1)


	def download_text_posts(self, post):
		print('Downloading text post #',post['id'],'...')
		try:
			self.new_post = open('%s.txt' % post['slug'], 'wb')
		except IOError:
			return "Impossible to create new post."
			sys.exit(1)

		self.Npost = """.. link: %s\r
.. description: %s\r
.. tags: %s\r
.. date: %s\r
.. title: %s\r
.. slug: %s\r
\r
%s""" % (str(post['slug']), post['title'],
				['' if len(post['tags']) <= 0 else post['tags']][0][0],
				post['date'], post['id'],
				post['slug'], re.sub('<[^<]+?>', '', post['body']).decode())

		self.new_post.write(self.Npost)
		self.new_post.close()
		print('Post #',post['id'],' completed!')


	def download_image_posts(self, post):
		print('Downloading image post #',post['id'],'...')
		if (len(post['photos']) == 1):
			self.image = post['photos'][0]['original_size']['url']
			self.image_name, self.image_extension = os.path\
							.splitext(self.image)

			# This one's cleaner than the original filename
			self.image_name = re.sub('tumblr_.*_[0-9]+.*', '', self.image_name)
			self.image_name = self.image_name.split('/')[-2]
			self.output = self.image_name + self.image_extension

			urllib.urlretrieve(self.image, '%s' % (self.output))

		if (len(post['photos']) > 1):
			for photoset in post['photos']:
				self.image = photoset['original_size']['url']
				self.image_name, self.image_extension = os.path\
								.splitext(self.image)

				# This one's cleaner than the original filename
				self.image_name = re.sub('tumblr_.*_[0-9]+.*', '', self.image_name)
				self.image_name = self.image_name.split('/')[-2]
				self.output = self.image_name + self.image_extension

				urllib.urlretrieve(self.image, '%s' % (self.output))				

		print('Post #',post['id'],' completed!')


	def download_all_posts(self, site, key, folder="tumblr/"):
		if not os.path.exists(folder):
			os.makedirs(folder)
			os.chdir(folder)
		else:
			os.chdir(folder)
		self.start(site, key)
		self.posts = requests.get('http://api.tumblr.com' \
			'/v2/blog/%s.tumblr.com/posts/?api_key=%s' % (site, key))
		if (self.posts.status_code == 200):
			self.posts = self.posts.json()
			self.total_posts = self.posts['response']['total_posts']
			self.posts_content = self.posts['response']['posts']
			self.index = 0
			while (self.index != self.total_posts):
				self.current_post = self.posts_content[self.index]
				if (self.current_post['type'] == 'photo'):
					self.download_image_posts(self.current_post)
				if (self.current_post['type'] == 'text'):
					self.download_text_posts(self.current_post)
				self.index = self.index + 1