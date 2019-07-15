
import os, sys
import urllib2
from BeautifulSoup import BeautifulSoup as BS
import datetime

####################################################################################
# Podcast Info
####################################################################################

class FeedManager:

	month_abr = {
		'ene':'Jan',
		'feb':'Feb',
		'mar':'Mar',
		'abr':'Apr',
		'may':'May',
		'jun':'Jun',
		'jul':'Jul',
		'ago':'Aug',
		'sep':'Sep',
		'oct':'Oct',
		'nov':'Nov',
		'dic':'Dec'
	}

	feed_url = ''

	title = ''
	audio_url = ''
	pub_date = ''
	description = ''

	def __init__(self, url=''):

		self.feed_url = url
		self.source_url = url.split('/')[2]

		response = urllib2.urlopen(url)
		self.html = response.read()
		self.soup = BS(self.html)

	def get_title(self):
		
		if self.source_url == 'espectador.com':
			title_tags = self.soup.findAll('title')
			if title_tags:
				self.title = title_tags[0].string.split('|')[0]

		if self.source_url == 'delsol.uy':
			title_tags = self.soup.findAll('title')
			if title_tags:
				self.title = title_tags[0].string.split('|')[0]


		if self.source_url == 'www.oceano.uy':
			h1_tags = self.soup.findAll('h1')
                        self.title = h1_tags
			for tag in h1_tags:
				if tag['class'] == 'ng-binding':
					self.title = tag.string

		return self.title

	def get_audio_url(self):

		self.audio_url = ''

		if self.source_url == 'espectador.com':
		
			source_tags = self.soup.findAll('source')
			if source_tags:
				self.audio_url = source_tags[0]['src']

		if self.source_url == 'delsol.uy':
			audio_tags = self.soup.findAll('audio')
                        if audio_tags:
                            source = audio_tags[0].contents[1]
                            self.audio_url = source['src'] 
		

		if self.source_url == 'www.oceano.uy':
			self.audio_url = ''

		return self.audio_url

	def get_pub_date(self):

		if self.source_url == 'espectador.com':
			div_tags = self.soup.findAll('div')

			for tag in div_tags:
				if tag.attrs and ('class' in tag.attrs[0]):
					if tag['class'] == 'articulo--fecha':
						fecha_em = tag.contents[1].contents[0]

			pub_date_d = int(fecha_em.split(' ')[2])
			pub_date_mn = self.month_abr[str(fecha_em.split(' ')[3]).lower()]
			pub_date_y = int(fecha_em.split(' ')[4])
			pub_date_m = datetime.datetime.strptime(pub_date_mn, '%b').month

		        pub_date = datetime.date(pub_date_y, pub_date_m, pub_date_d)
                        self.pub_date = '{:0>4}.{:0>2}.{:0>2}-12:00:00'.format( pub_date.strftime('%Y'), pub_date.strftime('%m'), pub_date.strftime('%d') )


		if self.source_url == 'delsol.uy':
			h6_tags = self.soup.findAll('h6')
                        date_span = h6_tags[0].contents[7].string

                        pub_date_d = int(date_span.split('/')[0]) 
                        pub_date_m = date_span.split('/')[1] 
                        pub_date_y = int(date_span.split('/')[2][0:4]) 
		
                        self.pub_date = '{:0>4}.{:0>2}.{:0>2}-12:00:00'.format( pub_date_y, pub_date_m, pub_date_d )


		if self.source_url == 'www.oceano.uy':
			pub_date_d = 1
			pub_date_y = 2019
			pub_date_m = 1			

		return self.pub_date

	
	def get_description(self):

		if self.source_url == 'espectador.com':
			h4_tags = self.soup.findAll('h4')

			if h4_tags:
				self.description = h4_tags[0].string

		if self.source_url == 'delsol.uy':
                        meta_tags = self.soup.findAll(attrs={"name": "description"})
                        if meta_tags:
			    self.description = meta_tags[0]['content']

		if self.source_url == 'www.oceano.uy':
			self.description = ''

		return self.description

