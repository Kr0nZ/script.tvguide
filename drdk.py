import simplejson
import datetime
import time

from danishaddons import *
import source

CHANNELS_URL = 'http://www.dr.dk/tjenester/programoversigt/dbservice.ashx/getChannels?type=tv'
PROGRAMS_URL = 'http://www.dr.dk/tjenester/programoversigt/dbservice.ashx/getSchedule?channel_source_url=%s&broadcastDate=%s'

STREAMS = {
	'dr.dk/mas/whatson/channel/DR1' : source.STREAM_DR1,
	'dr.dk/mas/whatson/channel/DR2' : source.STREAM_DR2,
	'dr.dk/mas/whatson/channel/TVR' : source.STREAM_DRRAMASJANG,
	'dr.dk/mas/whatson/channel/TVK' : source.STREAM_DRK,
	'dr.dk/external/ritzau/channel/dru' : source.STREAM_DRUPDATE
}

class Source(source.Source):

	def __init__(self):
		super(Source, self).__init__(False)
		self.date = datetime.datetime.today()

	def getChannelList(self):
		jsonChannels = simplejson.loads(web.downloadAndCacheUrl(CHANNELS_URL, os.path.join(ADDON_DATA_PATH, 'drdk-channels.json'), 60))
		channels = []

		for channel in jsonChannels['result']:
			channels.append({
				'id' : channel['source_url'],
				'title' : channel['name']
			})
	
		return channels
	
	def getProgramList(self, channelId):
		url = PROGRAMS_URL % (channelId.replace('+', '%2b'), self.date.strftime('%Y-%m-%dT%H:%M:%S'))
		cachePath = os.path.join(ADDON_DATA_PATH, 'drdk-' + channelId.replace('/', '')) 
		jsonPrograms = simplejson.loads(web.downloadAndCacheUrl(url, cachePath, 60))
		programs = []

		for program in jsonPrograms['result']:
			if(program.has_key('ppu_description')):
				description = program['ppu_description']
			else:
				description = 'Ingen beskrivelse'

			programs.append({
				'channel_id' : channelId,
				'title' : program['pro_title'],
				'start_date' : self._parseDate(program['pg_start']),
				'end_date' : self._parseDate(program['pg_stop']),
				'description' : description
			})

		return programs

	def getStreamURL(self, channelId):
		if(STREAMS.has_key(channelId)):
			return STREAMS[channelId]
		else:
			return None

	def _parseDate(self, dateString):
		t = time.strptime(dateString[:19], '%Y-%m-%dT%H:%M:%S')
		return datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

			
	