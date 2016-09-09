# FreqShow main application model/state.
# Author: Tony DiCola (tony@tonydicola.com)
#
# The MIT License (MIT)
#
# Copyright (c) 2014 Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# https://github.com/maxmind/geoip-api-python/blob/master/examples/city.py
# https://github.com/csparpa/pyowm
# http://openweathermap.org/city/0
# https://github.com/csparpa/pyowm/wiki/Usage-examples

import os.path
import GeoIP
import pyowm
import ipgetter
from datetime import datetime

API_KEY = 'Your API KEY'

class MirrorModel(object):
	def __init__(self, width, height):
		"""Create main MiniMirror application model.  Must provide the width and
		height of the screen in pixels.
		"""
		self.imperial = True
		# Set properties that will be used by views.
		self.api_key = API_KEY
		self.width = width
		self.height = height

		myip = ipgetter.myip()
		if myip is not None:
			self.external_ip = myip
			print(myip)

		self.location_name = None

		fileName = os.path.join(os.path.dirname(__file__),"database/GeoLiteCity.dat")

		self.gi = GeoIP.open(fileName, GeoIP.GEOIP_STANDARD)

		gir = self.gi.record_by_addr(self.external_ip)
		#gir = self.gi.record_by_addr("66.102.9.104")
		if gir is not None and gir['city'] is not None:
			self.country_name = gir['country_name']
			self.city_name = gir['city']
			self.location_name = "{},{}".format(self.city_name, self.country_name)
			print gir
		else:
			self.location_name = "San Jose, USA"
		print self.location_name

		self.owm = pyowm.OWM(self.api_key)
		self.forecast = None
		self.weather = None
		self.weather_time = datetime.now()

		if self.location_name is not None:
			self.update_weather()

	def convertKelvin(self, temp):
		if self.imperial:
			return str(int(temp * 9/5 - 459.67)) + ' F'
		else:
			return str(int(temp - 273.15)) + ' C'

	def get_weather(self):
		return self.weather

	def get_time_string_and_update(self):
		time = datetime.now()
		time_diff = time - self.weather_time
		if time_diff.total_seconds() > 900:
			self.update_weather()
		return (time.strftime('%I:%M:%S'), time.strftime('%A, %B %d, %Y'), time.strftime('%p'))

	def update_weather(self):
		self.forecast = self.owm.daily_forecast(self.location_name)
		observation = self.owm.weather_at_place(self.location_name)
		self.weather = observation.get_weather()
		self.weather_time = datetime.now()

	def update_location(self):
		if gir is not None and gir['city'] is not None:
			self.country_name = gir['country_name']
			self.city_name = gir['city']
			self.location_name = "{},{}".format(self.city_name, self.country_name)
			print gir
		else:
			self.location_name = "San Jose, USA"
		print self.location_name

if __name__ == "__main__":
	print('Run from main')
	mirrormodel = MirrorModel(10, 10)








