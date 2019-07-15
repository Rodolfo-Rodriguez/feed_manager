
import os, sys

class Config:

	PROJECT_ROOT_DIR = '/home/ubuntu/develop/feed_manager'

	PROJECT_DB_DIR = 'database'
	PROJECT_DB_FILENAME = 'radio.db'
	SQLITE_DATABASE_FILE = ''

	PROJECT_CSV_DIR = 'database/csv_data'

	FLASK_IMG_DIR = '/static/images'

	PROJECT_RADIOS_IMG_DIR = 'app/static/images/radios'
	PROJECT_PODCASTS_IMG_DIR = 'app/static/images/podcasts'
	PROJECT_ARTIST_IMG_DIR = 'app/static/images/artist'
	PROJECT_ALBUM_IMG_DIR = 'app/static/images/albums'
	PROJECT_FEED_DIR = 'app/static/feeds'

        FEED_IMG_BASE_URL = 'http://feeds.the2rods.com/static/images/podcasts'

	PODCAST_BASE_URL = '/static/Podcast'

	PLAYLIST_DIR = '/Playlists'
	PODCAST_FEED_FILE = '.podcast_feed.rss'
	DOWNLOADED_EPISODES_FILE = '.downloaded_episodes.txt'
	BASE_URI = 'USB/WD-500'

	DEFAULT_SERVER_NAME = 'none'
	DEFAULT_SERVER_PORT = '0'
	DEFAULT_SERVER_TYPE = 'NC'
	
	MPD_SERVERS = ["rune-1", "rune-2"]

	SERVER_NAMES = {
		"none":"NC",
		"rune-1":"MPD-Office",
		"cxn":"CXN" 
	}
	
	SERVER_PORTS = { 
		"none":"0",
		"rune-1":"6600",
		"cxn":"8050"
	}
			
	CXN_ID = '9ffd0730-00fb-455b-aa2f-8fc8df0c268f'

	SOCIAL_SITES = ['twitter', 'instagram', 'youtube', 'spotify', 'apple', 'soundcloud']

	TIMEZONES = {
                'Uruguay':-3, 
		'Argentina':-3, 
		'Chile':-4, 
		'Spain':7, 
		'Brazil':2, 
		'USA':1, 
		'Peru':0,
		'Australia':15, 
		'UK':6,
		'Italy':7,
		'Poland': 7,
		'Switzerland': 7,
		'Greece':8 
        }

	BOOKMARK_MAX = 20
	DEFAULT_VOLUME = 50

	def __init__(self):

		self.SQLITE_DATABASE = "sqlite:///{}".format(os.path.join(self.PROJECT_ROOT_DIR, self.PROJECT_DB_DIR, self.PROJECT_DB_FILENAME))
