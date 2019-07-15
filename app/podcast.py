
import os, sys
import urllib2
import xml.etree.cElementTree as ET
import wget
import eyed3
import datetime

from mpd import MPDClient

from flask import url_for

from .models import Podcast
from . import CONFIG

####################################################################################
# Podcast Info
####################################################################################

class PodcastInfo:
	feed_file = ''
	down_ep_file = ''
	podcast = None
	items_list = []
	down_episodes = []
	pod_uri = ''
	mpd_client = MPDClient()
	server_name = CONFIG.DEFAULT_SERVER_NAME
	server_port = CONFIG.DEFAULT_SERVER_PORT

	def __init__(self,podcast):
		self.podcast = podcast
		self.feed_file = os.path.join(podcast.pod_dir, CONFIG.PODCAST_FEED_FILE)
		self.down_ep_file = os.path.join(podcast.pod_dir, CONFIG.DOWNLOADED_EPISODES_FILE)
		self.pod_uri = CONFIG.BASE_URI + podcast.pod_dir

	def update_feed(self):

		if os.path.isfile(self.feed_file):
			os.remove(self.feed_file)
		
		wget.download(self.podcast.feed_url, self.feed_file)    	


	def update_items_list(self):

		if not(os.path.isfile(self.feed_file)):		
			wget.download(self.podcast.feed_url, self.feed_file)    	

		tree = ET.parse(self.feed_file)
		root = tree.getroot()
		channel = root[0]
		self.items_list = channel.findall('item')


	def episode_list(self):

		episodes_list = []
		track_num = 1

		for item in self.items_list:
			item_title = item.find('title').text
			
			item_pub_date = (item.find('pubDate').text).split(' ')
			item_pub_date = '{} {} {} {} {}'.format(item_pub_date[0], item_pub_date[1],item_pub_date[2],item_pub_date[3], item_pub_date[4])
			
			item_url = item.find('enclosure').get('url')
			item_length = item.find('enclosure').get('length')
			item_length_txt = str(int(item.find('enclosure').get('length')) / 1000 / 1000) + ' MB'

			item_desc = item.find('description').text
			if item_desc:
				if len(item_desc) > 120:
					item_desc = item_desc[0:120]


			if item_desc:
				if '<p>' in item_desc:
					item_desc = item_desc.split('<p>')[1].split('</p>')[0]
			else:
				item_desc = ''

			item_down = 'No'

			episodes_list.append({'track':track_num,'title':item_title,'description':item_desc,'pubdate':item_pub_date,'downloaded':item_down, 'url':item_url, 'length':item_length})
			
			track_num = track_num + 1

		return episodes_list

	def update_mpd_db(self):

		self.mpd_client.connect(self.server_name, self.server_port)
		self.mpd_client.update(self.pod_uri)
		self.mpd_client.close()
		self.mpd_client.disconnect()

	def remove_from_downloaded(self,ep_filename):

		self.down_episodes = [line.rstrip('\n') for line in open(self.down_ep_file)]

		down_ep_f = open(self.down_ep_file,'w')

		for ep_url in self.down_episodes:
			if not(ep_filename in ep_url):
				down_ep_f.write(ep_url + '\n')

		down_ep_f.close()


	def tag_file(self,file_name,title_tag):

		audio = eyed3.load(file_name)
		audio.initTag()
		audio.tag.title = unicode(title_tag)
		audio.tag.artist = unicode(self.podcast.name)
		audio.tag.save()

	def episode_file_tags(self, episode):

		audio_file = os.path.join(self.podcast.pod_dir, episode.local_file)

		audio = eyed3.load(audio_file)
		title = audio.tag.title
		artist = audio.tag.artist

		return [title, artist]


	def write_episode_file_tags(self, episode, title_tag):

		audio_file = os.path.join(self.podcast.pod_dir, episode.local_file)
		
		audio = eyed3.load(audio_file)

		audio.initTag()
		audio.tag.title = unicode(title_tag)
		audio.tag.album = unicode(self.podcast.name)
		audio.tag.artist = unicode(self.podcast.name)
		audio.tag.save()

		self.update_mpd_db()
	
	def download_episode(self,track_num):
		
		self.down_episodes = [line.rstrip('\n') for line in open(self.down_ep_file)]
		self.update_items_list()

		down_ep_f = open(self.down_ep_file,'a')

		item = self.items_list[int(track_num) - 1]
		
		item_url = item.find('enclosure').get('url')
		item_title = item.find('title').text
		item_pub_date = item.find('pubDate').text
				
		if not(item_url in self.down_episodes):
			ep_file = item_url.split('/')[-1]
			if '.mp3' in ep_file:
				ep_file = ep_file.split('.mp3')[0] + '.mp3'
			pod_ep_name = self.podcast.pod_dir + '/' + ep_file

			download_manager.down_redirect_url = url_for('podcast.podcast_show', id=self.podcast.id)
			download_manager.download(item_url, pod_ep_name)

			down_ep_f.write(item_url + '\n')

			## Re-Tag File

			if self.podcast.retag:				
				pub_date_d = int(item_pub_date.split(' ')[1])
				pub_date_mn = item_pub_date.split(' ')[2]
				pub_date_y = int(item_pub_date.split(' ')[3])

				pub_date_m = datetime.datetime.strptime(pub_date_mn, '%b').month

				pub_date = datetime.date(pub_date_y, pub_date_m, pub_date_d)
				pub_date_txt = pub_date.strftime('%Y.%m.%d')

				title_tag = pub_date_txt + ' - ' + item_title
			else:
				title_tag = item_title

			if '.mp3' in ep_file:
				self.tag_file(pod_ep_name,title_tag)
				
		down_ep_f.close()

		self.update_mpd_db()


	def download_episode_from_url(self,url,title):
		
		self.down_episodes = [line.rstrip('\n') for line in open(self.down_ep_file)]
		self.update_items_list()

		down_ep_f = open(self.down_ep_file,'a')

		if not(url in self.down_episodes):
			ep_file = url.split('/')[-1]
			if '.mp3' in ep_file:
				ep_file = ep_file.split('.mp3')[0] + '.mp3'
			pod_ep_name = self.podcast.pod_dir + '/' + ep_file

			download_manager.down_redirect_url = url_for('podcast.podcast_show', id=self.podcast.id)
			download_manager.download(url, pod_ep_name)

			down_ep_f.write(url + '\n')
				
			## Re-Tag File

			if '.mp3' in ep_file:
				self.tag_file(pod_ep_name,title)

		down_ep_f.close()

		self.update_mpd_db()


	def download_episode_file(self, episode):
				
		item_url = episode.url
		item_title = episode.title
		item_pub_date = episode.pub_date

		episode_data = {}
				
		if not(episode.downloaded):

			ep_file = item_url.split('/')[-1]
			if '.mp3' in ep_file:
				ep_file = ep_file.split('.mp3')[0] + '.mp3'
			pod_ep_name = self.podcast.pod_dir + '/' + ep_file
			
			episode_data['local_file'] = ep_file

			download_manager.down_redirect_url = url_for('podcast.podcast_show', id=self.podcast.id)
			download_manager.download(item_url, pod_ep_name)

			episode_data['file_size'] = download_manager.down_file_size	

			## Re-Tag File

			if self.podcast.retag:				
				pub_date_txt = episode.pub_date.split('-')[0]

				title_tag = pub_date_txt + ' - ' + item_title
			else:
				title_tag = item_title

			if '.mp3' in ep_file:
				self.tag_file(pod_ep_name,title_tag)
				
		self.update_mpd_db()

		return episode_data


	def add_episode_to_feed(self, title, url, pub_date, description=''):
		
		feed_filename = os.path.basename(self.podcast.feed_url)
		local_feed_file = os.path.join(CONFIG.PROJECT_ROOT_DIR, CONFIG.PROJECT_FEED_DIR, feed_filename)

		image_filename = feed_filename.split('.')[0]
		
		tree = ET.parse(local_feed_file)
		root = tree.getroot()
		channel = root[0]
		items_list = channel.findall('item')

		pub_date_txt = datetime.datetime.now().strftime("%a %d %b %Y %H:%M:%S")

		feed_f = open(local_feed_file,'w')

		item_text = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{}</title>
    <link>https://www.the2rods.com</link>
    <image>
    	<url>http://feeds.the2rods.com/image/{}</url>
        <title>{}</title>
        <link>http://www.the2rods.com</link>
    </image>
    <description>{}</description>
    <pubDate>"{}"</pubDate>\n""".format(self.podcast.name, image_filename, self.podcast.name, self.podcast.description, pub_date_txt)

		feed_f.write(item_text)

		item_text = """
	<item>
		<title>{}</title>
		<pubDate>{}</pubDate>
		<description>{}</description>
		<enclosure url="{}" length="0" type="audio/mpeg"/>
		<guid>{}</guid>
	</item>\n""".format(title, pub_date, description, url, url)

		feed_f.write(item_text)

		for item in items_list:
			item_url = item.find('enclosure').get('url')
			item_title = item.find('title').text
			item_desc = item.find('description').text
			item_pub_date = item.find('pubDate').text

			item_text = """
	<item>
		<title>{}</title>
		<pubDate>{}</pubDate>
		<description>{}</description>
		<enclosure url="{}" length="0" type="audio/mpeg"/>
		<guid>{}</guid>
	</item>\n""".format(item_title, item_pub_date, item_desc, item_url, item_url)

			feed_f.write(item_text)

		feed_f.write("\n</channel></rss>")

		feed_f.close()

		self.update_feed()


	def clear_feed(self):
		
		feed_filename = os.path.basename(self.podcast.feed_url)
		local_feed_file = os.path.join(CONFIG.PROJECT_ROOT_DIR, CONFIG.PROJECT_FEED_DIR, feed_filename)

		image_filename = feed_filename.split('.')[0]
		
		pub_date_txt = datetime.datetime.now().strftime("%a %d %b %Y %H:%M:%S")

		feed_f = open(local_feed_file,'w')

		item_text = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
  <channel>
    <title>{}</title>
    <link>https://www.the2rods.com</link>
    <image>
    	<url>http://feeds.the2rods.com/image/{}</url>
        <title>{}</title>
        <link>http://www.the2rods.com</link>
    </image>
    <description>{}</description>
    <pubDate>"{}"</pubDate>
</channel></rss>""".format(self.podcast.name, image_filename, self.podcast.name, self.podcast.description, pub_date_txt)

		feed_f.write(item_text)

		feed_f.close()

		self.update_feed()

	def create_feed(self):
		
		feed_filename = os.path.basename(self.podcast.internal_feed_url) + '.rss'
		local_feed_file = os.path.join(CONFIG.PROJECT_ROOT_DIR, CONFIG.PROJECT_FEED_DIR, feed_filename)

		pub_date_txt = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S")

		feed_f = open(local_feed_file,'w')

		item_text = """<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
  <channel>
    <atom:link href="http://feeds.the2rods.com/static/feeds/{}" rel="self" type="application/rss+xml" />
    <title>{}</title>
    <link>{}</link>
    <image>
    	<url>http://feeds.the2rods.com/static/images/podcasts/{}</url>
        <title>{}</title>
        <link>{}</link>
    </image>
    <description>{}</description>
    <pubDate>{} GMT</pubDate>\n""".format(
                feed_filename, 
                self.podcast.name, 
                self.podcast.web_url, 
                self.podcast.image, 
                self.podcast.name, 
                self.podcast.web_url, 
                self.podcast.description, 
                pub_date_txt
                )

		feed_f.write(item_text)
                
                self.podcast.episode_list.sort(key=lambda x: x.pub_date, reverse=True)
		for episode in self.podcast.episode_list:

			item_text = """
	<item>
		<title>{}</title>
		<pubDate>{} GMT</pubDate>
		<description>{}</description>
		<enclosure url="{}" length="{}" type="audio/mpeg"/>
		<guid>{}</guid>
                <itunes:duration>{}</itunes:duration>
	</item>\n""".format(
                        episode.title,
                        episode.pub_date_feed_txt(), 
                        episode.description, 
                        episode.url, 
                        episode.audio_size, 
                        episode.url,
                        episode.audio_time
                        )

			feed_f.write(item_text)

		feed_f.write("\n</channel></rss>")

		feed_f.close()

		self.update_feed()
		#self.upload_feed_to_server()

	def upload_feed_to_server(self):

		feed_filename = os.path.basename(self.podcast.feed_url) + '.rss'
		upload_cmd = '/home/ubuntu/bin/upload_feed.sh {}'.format(feed_filename)
		os.system(upload_cmd)

	def upload_image_to_server(self):

		upload_cmd = '/home/ubuntu/bin/upload_image.sh {}'.format(self.podcast.image)
		os.system(upload_cmd)

	def episode_url(self,track_num):
		
		self.update_items_list()

		item = self.items_list[int(track_num) - 1]
		
		item_url = item.find('enclosure').get('url')

		return item_url


	def create_init_files(self):

		if not(os.path.exists(self.podcast.pod_dir)):
			os.mkdir(self.podcast.pod_dir)
			
			with open(self.down_ep_file, 'a'):
				os.utime(self.down_ep_file, None)


	def delete_episode_file(self, episode):

		ep_file = self.podcast.pod_dir + '/' + episode.local_file

		if os.path.exists(ep_file):
			os.remove(ep_file)

		self.update_mpd_db()


