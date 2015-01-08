from __future__ import print_function, unicode_literals
from edison import Edison
import json

# Use for personal use, do not push with this on True
DEBUG = False

def main():

    try:
        if DEBUG == True:
            config_file = open('config_dev.json')
        else:
            config_file = open('config.json')
    except IOError:
        print("Couldn't open the config file.")

    config = json.load(config_file)

    convert = Edison()

    print('Welcome to Edison! The Tumblr to Nikola converter\n')
    print('Once its done, remember to move the files to their respective folder')
    print('\n\n')

    blog_url = raw_input('Insert blog URL (without the .tumblr.com): ')
    print('\n\n')

    convert.download_all_posts(blog_url, config['settings']['API_KEY'])

    print("\n\nDone! Enjoy your Nikola website!")

if __name__ == "__main__":
    main()