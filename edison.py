from __future__ import print_function, unicode_literals
import os, re, sys
import webbrowser, urllib, time
try:
    import requests
    import soundcloud
except ImportError:
    raise ImportError('Error importing one of the important libraries.'
        'Please install it.')

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
            raise IOError('Could not connect.')


    def download_text_posts(self, post):
        print('Downloading text post #',post['id'],'...')
        try:
            self.new_post = open('%s.rst' % post['slug'], 'wb')
        except IOError:
            raise IOError("Impossible to create new post.")

        self.Npost = """.. link: %s\r
.. description: %s\r
.. tags: %s\r
.. date: %s\r
.. title: %s\r
.. slug: %s\r
.. type: text\r
\r
%s""" % (str(post['slug']), post['title'],
                ['' if len(post['tags']) <= 0 else post['tags']][0][0],
                post['date'], post['title'],
                post['slug'], re.sub('<[^<]+?>', '', post['body']))

        self.new_post.write(self.Npost.encode("utf-8"))
        self.new_post.close()
        print('Post #',post['id'],' completed!')


    def download_image_posts(self, post):
        print('Downloading image post #',post['id'],'...')

        image_posts = ''

        if (len(post['photos']) == 1):
            self.image = post['photos'][0]['original_size']['url']
            self.image_name, self.image_extension = os.path\
                            .splitext(self.image)

            self.image_name = re.sub('tumblr_.*_[0-9]+.*', '', self.image_name)
            self.image_name = self.image_name.split('/')[-2]
            self.output = self.image_name + self.image_extension

            urllib.urlretrieve(self.image, '%s' % (self.output))

            image_posts = '\r.. image:: %s' % self.output

            try:
                self.new_post = open('%s.rst' % post['id'], 'wb')
            except IOError:
                raise IOError("Impossible to create new post.")

            self.Npost = """.. link: %s\r
.. description: %s\r
.. tags: \r
.. date: %s\r
.. title: %s\r
.. slug: %s\r
.. type: text\r
\r
%s\r

%s""" % (post['slug'], post['slug'],
                post['date'], post['id'],
                post['id'], image_posts,
                post['caption'])
            self.new_post.write(self.Npost.encode("utf-8"))
            self.new_post.close()

        if (len(post['photos']) > 1):
            for photoset in post['photos']:
                self.image = photoset['original_size']['url']
                self.image_name, self.image_extension = os.path\
                                .splitext(self.image)

                # This one's cleaner than the original filename
                self.image_name = re.sub('tumblr_.*_[0-9]+.*', '',
                                    self.image_name)
                self.image_name = self.image_name.split('/')[-2]
                self.output = self.image_name + self.image_extension

                urllib.urlretrieve(self.image, '%s' % (self.output))        

                image_posts += '\r.. image:: %s' % '/galleries/' + self.output

            try:
                self.new_post = open('%s.rst' % post['id'], 'wb')
            except IOError:
                raise IOError("Impossible to create new post.")

            self.Npost = """.. link: %s\r
.. description: %s\r
.. tags: \r
.. date: %s\r
.. title: %s\r
.. slug: %s\r
.. type: text\r
\r
%s\r

%s""" % (post['slug'], post['slug'],
                post['date'], post['id'],
                post['id'], image_posts,
                post['caption'])

            self.new_post.write(self.Npost)
            self.new_post.close()


        print('Post #',post['id'],' completed!')


    def audio_from_tumblr(self, post):
        """
        THIS FUNCIONALITY IS COMPLETELY EXPERIMENTAL!!!
        USE ONLY FOR TESTING PURPOSES!!!
        """
        self.audio_name, self.audio_extension = os.path\
                            .splitext(post['audio_url'])
        print(self.audio_name)
        self.audio_name = str(post['id'])
        print(self.audio_name)
        self.output_audio = self.audio_name + self.audio_extension
        urllib.urlretrieve(post['audio_url'], self.output_audio)

        client = soundcloud.Client(
            client_id='',
            client_secret='',
        )
        webbrowser.open(urlclient.authorize_url())

        track = client.post('/tracks', track={
            'title': post['title'],
            'asset_data': open(self.output_audio, 'rb')
        })

    def audio_from_soundcloud(self, post):
        print('Downloading audio post #',post['id'],'...')
        current_url = re.findall(r'[0-9]+', post['audio_url'])[0]
        slug_name = re.sub(r'\s+', '-', post['track_name'])

        try:
            self.new_post = open('%s.rst' % slug_name, 'wb')
        except IOError:
            raise IOError("Impossible to create new post.")

        if (post['caption'] != ''):
            self.Npost = """.. link: %s\r
.. description: %s\r
.. tags: \r
.. date: %s\r
.. title: %s\r
.. slug: %s\r
.. type: text\r
\r
.. soundcloud:: %s\r

%s""" % (slug_name, slug_name,
                post['date'], post['id'],
                post['track_name'], current_url,
                post['caption'])

        else:
            self.Npost = """.. link: %s\r
.. description: %s\r
.. tags: \r
.. date: %s\r
.. title: %s\r
.. slug: %s\r
.. type: text\r
\r
.. soundcloud:: %s""" % (slug_name, slug_name,
                post['date'], post['id'],
                post['track_name'], current_url)
        self.new_post.write(self.Npost.encode("utf-8"))
        self.new_post.close()

        print('Post #',post['id'],' completed!')

    def download_audio_posts(self, post):
        if (post['audio_type'] == 'soundcloud'):
            self.audio_from_soundcloud(post)

    def download_video_posts(self, post):
        print('Downloading video post #',post['id'],'...')
        youtubeID = re.findall(
            "#(?<=v=)[a-zA-Z0-9-]+(?=&)|(?<=v\/)[^&\n]" \
            + "+(?=\?)|(?<=v=)[^&\n]+|(?<=youtu.be/)[^&\n]+#",
            post['permalink_url'])
        isYoutube = False
        if len(youtubeID) > 0:
            video_id = youtubeID[0]
            isYoutube = True
        try:
            self.new_post = open('%s.rst' % post['id'], 'wb')
        except IOError:
            raise IOError("Impossible to create new post.")
        if not isYoutube:
            self.Npost = """.. link: %s\r
.. description: %s\r
.. tags: \r
.. date: %s\r
.. title: %s\r
.. slug: %s\r
.. type: text\r
\r

%s""" % (post['id'], post['id'],
                post['date'], post['permalink_url'],
                post['id'], post['caption'])

        elif (post['caption'] != ''):
            self.Npost = """.. link: %s\r
.. description: %s\r
.. tags: \r
.. date: %s\r
.. title: %s\r
.. slug: %s\r
.. type: text\r
\r
.. youtube:: %s\r

%s""" % (post['id'], post['id'],
                post['date'], post['permalink_url'],
                post['id'], video_id,
                post['caption'])

        else:
            self.Npost = """.. link: %s\r
.. description: %s\r
.. tags: \r
.. date: %s\r
.. title: %s\r
.. slug: %s\r
.. type: text\r
\r
.. youtube:: %s""" % (post['id'], post['permalink_url'],
                post['date'], post['id'],
                post['id'], video_id)

        self.new_post.write(self.Npost)
        self.new_post.close()

        print('Post #',post['id'],' completed!')

    def download_all_posts(self, site, key, folder="tumblr/"):
        self.start(site, key)
        if not os.path.exists(folder):
            os.makedirs(folder)
            os.chdir(folder)
        else:
            os.chdir(folder)
        self.posts = requests.get('http://api.tumblr.com' \
            '/v2/blog/%s.tumblr.com/posts/?api_key=%s' % (site, key))
        if (self.posts.status_code == 200):
            self.posts = self.posts.json()
            self.total_posts = self.posts['response']['total_posts']
            self.posts_content = self.posts['response']['posts']
            self.index = 0
            while (self.index != self.total_posts):
                self.current_post = self.posts_content[self.index]
                if (self.current_post['type'] == 'video'):
                    self.download_video_posts(self.current_post)
                if (self.current_post['type'] == 'audio'):
                    self.download_audio_posts(self.current_post)
                if (self.current_post['type'] == 'photo'):
                    self.download_image_posts(self.current_post)
                if (self.current_post['type'] == 'text'):
                    self.download_text_posts(self.current_post)
                self.index = self.index + 1

        self.new_post.write(self.Npost.encode("utf-8"))
        self.new_post.close()

        print('Post #',post['id'],' completed!')

    def download_all_posts(self, site, key, folder="tumblr/"):
        self.start(site, key)
        if not os.path.exists(folder):
            os.makedirs(folder)
            os.chdir(folder)
        else:
            os.chdir(folder)
        self.posts = requests.get('http://api.tumblr.com' \
            '/v2/blog/%s.tumblr.com/posts/?api_key=%s' % (site, key))
        if (self.posts.status_code == 200):
            self.posts = self.posts.json()
            self.total_posts = self.posts['response']['total_posts']
            self.posts_content = self.posts['response']['posts']
            self.index = 0
            while (self.index != self.total_posts):
                self.current_post = self.posts_content[self.index]
                if (self.current_post['type'] == 'video'):
                    self.download_video_posts(self.current_post)
                if (self.current_post['type'] == 'audio'):
                    self.download_audio_posts(self.current_post)
                if (self.current_post['type'] == 'photo'):
                    self.download_image_posts(self.current_post)
                if (self.current_post['type'] == 'text'):
                    self.download_text_posts(self.current_post)
                self.index = self.index + 1
