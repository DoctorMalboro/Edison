from __future__ import print_function, unicode_literals
from edison import Edison


def main():

	convert = Edison()

	print('Welcome to Edison! The Tumblr to Nikola converter\n')
	print('Once its done, remember to move the files to their respective folder')
	print('\n\n')

	blog_url = raw_input('Insert blog URL (without the .tumblr.com): ')
	print('\n\n')

	convert.download_all_posts(blog_url, '')

	print("\n\nDone! Enjoy your Nikola website!")

if __name__ == "__main__":
	main()