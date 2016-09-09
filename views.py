# FreqShow application views.
# These contain the majority of the application business logic.
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
import math
import sys

import pygame

import minimirror
import ui

import os.path
from datetime import datetime

class ViewBase(object):
	"""Base class for simple UI view which represents all the elements drawn
	on the screen.  Subclasses should override the render, and click functions.
	"""

	def render(self, screen):
		pass

	def click(self, location):
		pass

	def mouse_move(self, location):
		pass

	def view_showing(self):
		pass

class MessageDialog(ViewBase):
	"""Dialog which displays a message in the center of the screen with an OK
	and optional cancel button.
	"""

	def __init__(self, model, text, accept, cancel=None):
		self.accept = accept
		self.cancel = cancel
		self.buttons = ui.ButtonGrid(model.width, model.height, 4, 5)
		self.buttons.add(3, 4, 'OK', click=self.accept_click, 
			bg_color=minimirror.ACCEPT_BG)
		if cancel is not None:
			self.buttons.add(0, 4, 'CANCEL', click=self.cancel_click, 
				bg_color=minimirror.CANCEL_BG)
		self.label = ui.render_text(text, size=minimirror.NUM_FONT,
			fg=minimirror.BUTTON_FG, bg=minimirror.MAIN_BG)
		self.label_rect = ui.align(self.label.get_rect(),
			(0, 0, model.width, model.height))

	def render(self, screen):
		# Draw background, buttons, and text.
		screen.fill(minimirror.MAIN_BG)
		self.buttons.render(screen)
		screen.blit(self.label, self.label_rect)

	def click(self, location):
		self.buttons.click(location)

	def accept_click(self, button):
		self.accept()

	def cancel_click(self, button):
		self.cancel()

class NumberDialog(ViewBase):
	"""Dialog which asks the user to enter a numeric value."""

	def __init__(self, model, label_text, unit_text, initial='0', accept=None,
		cancel=None, has_auto=False, allow_negative=False):
		"""Create number dialog for provided model and with given label and unit
		text.  Can provide an optional initial value (default to 0), an accept
		callback function which is called when the user accepts the dialog (and
		the chosen value will be sent as a single parameter), a cancel callback
		which is called when the user cancels, and a has_auto boolean if an
		'AUTO' option should be given in addition to numbers.
		"""
		self.value = str(initial)
		self.unit_text = unit_text
		self.model = model
		self.accept = accept
		self.cancel = cancel
		# Initialize button grid.
		self.buttons = ui.ButtonGrid(model.width, model.height, 4, 5)
		self.buttons.add(0, 1, '1', font_size=minimirror.NUM_FONT, click=self.number_click)
		self.buttons.add(1, 1, '2', font_size=minimirror.NUM_FONT, click=self.number_click)
		self.buttons.add(2, 1, '3', font_size=minimirror.NUM_FONT, click=self.number_click)
		self.buttons.add(0, 2, '4', font_size=minimirror.NUM_FONT, click=self.number_click)
		self.buttons.add(1, 2, '5', font_size=minimirror.NUM_FONT, click=self.number_click)
		self.buttons.add(2, 2, '6', font_size=minimirror.NUM_FONT, click=self.number_click)
		self.buttons.add(0, 3, '7', font_size=minimirror.NUM_FONT, click=self.number_click)
		self.buttons.add(1, 3, '8', font_size=minimirror.NUM_FONT, click=self.number_click)
		self.buttons.add(2, 3, '9', font_size=minimirror.NUM_FONT, click=self.number_click)
		self.buttons.add(1, 4, '0', font_size=minimirror.NUM_FONT, click=self.number_click)
		self.buttons.add(2, 4, '.', font_size=minimirror.NUM_FONT, click=self.decimal_click)
		self.buttons.add(0, 4, 'DELETE', click=self.delete_click)
		if not allow_negative:
			# Render a clear button if only positive values are allowed.
			self.buttons.add(3, 1, 'CLEAR', click=self.clear_click)
		else:
			# Render a +/- toggle if negative values are allowed.
			self.buttons.add(3, 1, '+/-', click=self.posneg_click)
		self.buttons.add(3, 3, 'CANCEL', click=self.cancel_click,
			bg_color=minimirror.CANCEL_BG)
		self.buttons.add(3, 4, 'ACCEPT', click=self.accept_click,
			bg_color=minimirror.ACCEPT_BG) 
		if has_auto:
			self.buttons.add(3, 2, 'AUTO', click=self.auto_click)
		# Build label text for faster rendering.
		self.input_rect = (0, 0, self.model.width, self.buttons.row_size)
		self.label = ui.render_text(label_text, size=minimirror.MAIN_FONT, 
			fg=minimirror.INPUT_FG, bg=minimirror.INPUT_BG)
		self.label_pos = ui.align(self.label.get_rect(), self.input_rect,
			horizontal=ui.ALIGN_LEFT, hpad=10)

	def render(self, screen):
		# Clear view and draw background.
		screen.fill(minimirror.MAIN_BG)
		# Draw input background at top of screen.
		screen.fill(minimirror.INPUT_BG, self.input_rect)
		# Render label and value text.
		screen.blit(self.label, self.label_pos)
		value_label = ui.render_text('{0} {1}'.format(self.value, self.unit_text),
			size=minimirror.NUM_FONT, fg=minimirror.INPUT_FG, bg=minimirror.INPUT_BG)
		screen.blit(value_label, ui.align(value_label.get_rect(), self.input_rect,
			horizontal=ui.ALIGN_RIGHT, hpad=-10))
		# Render buttons.
		self.buttons.render(screen)

	def click(self, location):
		self.buttons.click(location)

	# Button click handlers follow below.
	def auto_click(self, button):
		self.value = 'AUTO'

	def clear_click(self, button):
		self.value = '0'

	def delete_click(self, button):
		if self.value == 'AUTO':
			# Ignore delete in auto gain mode.
			return
		elif len(self.value) > 1:
			# Delete last character.
			self.value = self.value[:-1]
		else:
			# Set value to 0 if only 1 character.
			self.value = '0'

	def cancel_click(self, button):
		if self.cancel is not None:
			self.cancel()

	def accept_click(self, button):
		if self.accept is not None:
			self.accept(self.value)

	def decimal_click(self, button):
		if self.value == 'AUTO':
			# If in auto gain, assume user wants numeric gain with decimal.
			self.value = '0.'
		elif self.value.find('.') == -1:
			# Only add decimal if none is present.
			self.value += '.'

	def number_click(self, button):
		if self.value == '0' or self.value == 'AUTO':
			# Replace value with number if no value or auto gain is set.
			self.value = button.text
		else:
			# Add number to end of value.
			self.value += button.text

	def posneg_click(self, button):
		if self.value == 'AUTO':
			# Do nothing if value is auto.
			return
		else:
			if self.value[0] == '-':
				# Swap negative to positive by removing leading minus.
				self.value = self.value[1:]
			else:
				# Swap positive to negative by adding leading minus.
				self.value = '-' + self.value

class SettingsList(ViewBase):
	"""Setting list view. Allows user to modify some model configuration."""

	def __init__(self, model, controller):
		self.model      = model
		self.controller = controller
		# Create button labels with current model values.

		# Create buttons.
		self.buttons = ui.ButtonGrid(model.width, model.height, 4, 5)
		self.buttons.add(0, 4, 'BACK', click=self.controller.change_to_main)

	def render(self, screen):
		# Clear view and render buttons.
		screen.fill(minimirror.MAIN_BG)
		self.buttons.render(screen)

	def click(self, location):
		self.buttons.click(location)

class NothingList(ViewBase):
	"""The main view for the list of Planes flying around."""
	def __init__(self, model, controller):
		self.model      = model
		self.controller = controller
		# Create button labels with current model values.

		# Create buttons.
		self.buttons = ui.ButtonGrid(model.width, model.height, 6, 5)
		self.buttons.add(0, 4, '.', click=self.controller.change_to_thing_list,
			bg_color=minimirror.MAIN_BG, fg_color=minimirror.BUTTON_BG)
		self.plane_buttons = None

	def render(self, screen):
		# Clear view and render buttons.
		screen.fill(minimirror.MAIN_BG)
		self.buttons.render(screen)

	def click(self, location):
		self.buttons.click(location)

	def quit_click(self, button):
		print "Clicked Quit"
		self.controller.message_dialog('QUIT: Are you sure?',
			accept=self.quit_accept)

	def quit_accept(self):
		sys.exit(0)

class ThingList(ViewBase):
	"""The main view for time and weather."""
	def __init__(self, model, controller):
		self.model      = model
		self.controller = controller
		# Create button labels with current model values.

		# Create buttons.
		self.buttons = ui.ButtonGrid(model.width, model.height, 6, 5)
		self.buttons.add(0, 0, 'X', click=self.quit_click,
			bg_color=minimirror.MAIN_BG, fg_color=minimirror.BUTTON_FG)
		self.buttons.add(0, 4, '.', click=self.controller.change_to_nothing,
			bg_color=minimirror.MAIN_BG, fg_color=minimirror.BUTTON_BG)
		self.buttons.add(4, 0, '', click=self.controller.change_to_weather_detail, rowspan=5,
			bg_color=minimirror.MAIN_BG, fg_color=minimirror.BUTTON_BG)
		self.plane_buttons = None

	def render_time(self, screen):
		#Time
		time = self.model.get_time_string_and_update()
		time_text = ui.render_text(time[0], size=minimirror.TIME_FONT,
			 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
		time_text = pygame.transform.rotate(time_text, 270)
		screen.blit(time_text, [self.model.width - minimirror.TIME_FONT, 20])

		#AMPM
		am_pm_text = ui.render_text(time[2], size=minimirror.SMALL_FONT,
			 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
		am_pm_text = pygame.transform.rotate(am_pm_text, 270)
		screen.blit(am_pm_text, [self.model.width - minimirror.TIME_FONT + 10, time_text.get_rect().height + 20])

		#Date
		date_text = ui.render_text(time[1], size=minimirror.SMALL_FONT,
			 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
		date_text = pygame.transform.rotate(date_text, 270)
		screen.blit(date_text, [self.model.width - minimirror.TIME_FONT - minimirror.SMALL_FONT, 20])

	def render_weather(self, screen):
		weather = self.model.get_weather()
		if weather is not None:
			weather_text = weather.get_detailed_status()
			text = ui.render_text(weather_text.capitalize(), size=minimirror.WEATHER_FONT,
			 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
			text = pygame.transform.rotate(text, 270)
			screen.blit(text, [self.model.width - minimirror.TIME_FONT - minimirror.WEATHER_FONT * 2, 20])

			fahrenheit = self.model.convertKelvin(weather.get_temperature()['temp'])
			tempurate = ui.render_text(fahrenheit, size=minimirror.NUM_FONT,
			 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
			tempurate = pygame.transform.rotate(tempurate, 270)
			screen.blit(tempurate, [self.model.width - minimirror.TIME_FONT - minimirror.WEATHER_FONT * 3 + 20, 20])

	def render(self, screen):
		# Clear view and render buttons.
		screen.fill(minimirror.MAIN_BG)
		self.buttons.render(screen)
		self.render_weather(screen)
		self.render_time(screen)

	def click(self, location):
		self.buttons.click(location)

	def quit_click(self, button):
		print "Clicked Quit"
		self.controller.message_dialog('QUIT: Are you sure?',
			accept=self.quit_accept)

	def quit_accept(self):
		sys.exit(0)

class WeatherDetail(ViewBase):
	"""The Details about the weather."""
	def __init__(self, model, controller):
		self.model      = model
		self.controller = controller
		# Create button labels with current model values.

		# Create buttons.
		self.buttons = ui.ButtonGrid(model.width, model.height, 6, 5)
		self.buttons.add(0, 0, '^', click=self.controller.change_to_main,
			bg_color=minimirror.MAIN_BG, fg_color=minimirror.BUTTON_BG)
		self.plane_buttons = None

	def render_weather(self, screen):
		weather = self.model.get_weather()

		#print weather
		# print "status: " + str(weather.get_status())
		# print "detailed status: " + str(weather.get_detailed_status())
		# print "temp: " + str(weather.get_temperature())
		# print "current temp: " + str(self.model.convertKelvin(weather.get_temperature()['temp']))
		# print "humidity: " + str(weather.get_humidity())
		# print "wind: " + str(weather.get_wind())
		# print "rain: " + str(weather.get_rain())
		# print "clouds: " + str(weather.get_clouds())

		weather_header = ui.render_text(self.model.location_name.split(',')[0], size=minimirror.TIME_FONT,
			 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
		weather_header = pygame.transform.rotate(weather_header, 270)
		screen.blit(weather_header, [self.model.width - minimirror.TIME_FONT, 20])

		# where_weather = ui.render_text(self.model.location_name, size=minimirror.MAIN_FONT,
		# 	 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
		# where_weather = pygame.transform.rotate(where_weather, 270)
		# screen.blit(where_weather, [self.model.width - 80, 20])

		if weather is not None:
			weather_text = weather.get_detailed_status()
			text = ui.render_text(weather_text.capitalize(), size=minimirror.MAIN_FONT,
			 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
			text = pygame.transform.rotate(text, 270)
			screen.blit(text, [self.model.width - 130, 30])

			fahrenheit = "currently {}f".format(weather.get_temperature('fahrenheit')['temp'])
			max_temp = weather.get_temperature('fahrenheit')['temp_max']
			min_temp = weather.get_temperature('fahrenheit')['temp_min']
			min_max_temp_string = "min {}f, max {}f".format(min_temp, max_temp)

			tempurate = ui.render_text(fahrenheit, size=minimirror.MAIN_FONT,
			 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
			tempurate = pygame.transform.rotate(tempurate, 270)
			screen.blit(tempurate, [self.model.width - 160, 30])

			min_max_tempurate = ui.render_text(min_max_temp_string, size=minimirror.MAIN_FONT,
			 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
			min_max_tempurate = pygame.transform.rotate(min_max_tempurate, 270)
			screen.blit(min_max_tempurate, [self.model.width - 190, 30])

			humidity = ui.render_text('Humidity ' + str(weather.get_humidity()) + '%', size=minimirror.MAIN_FONT,
			 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
			humidity = pygame.transform.rotate(humidity, 270)
			screen.blit(humidity, [self.model.width - 220, 30])

			windSpeed = ui.render_text('Windspeed ' + str(weather.get_wind().get('speed')) + ' knots', size=minimirror.MAIN_FONT,
			 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
			windSpeed = pygame.transform.rotate(windSpeed, 270)
			screen.blit(windSpeed, [self.model.width - 250, 30])

			windDirection = ui.render_text('Direction ' + str(weather.get_wind().get('deg')) + ' degrees', size=minimirror.MAIN_FONT,
			 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
			windDirection = pygame.transform.rotate(windDirection, 270)
			screen.blit(windDirection, [self.model.width - 280, 30])

			if str(weather.get_rain()) is not {}:
				rain = ui.render_text('Rain ' + str(weather.get_rain()), size=minimirror.MAIN_FONT,
				 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
				rain = pygame.transform.rotate(rain, 270)
				screen.blit(rain, [self.model.width - 310, 30])

			clouds = ui.render_text('Cloud cover ' + str(weather.get_clouds()) + '%', size=minimirror.MAIN_FONT,
			 fg=minimirror.BUTTON_BG, bg=minimirror.MAIN_BG)
			clouds = pygame.transform.rotate(clouds, 270)
			screen.blit(clouds, [self.model.width - 340, 30])

	def render(self, screen):
		# Clear view and render buttons.
		self.model.get_time_string_and_update()
		screen.fill(minimirror.MAIN_BG)
		self.buttons.render(screen)
		self.render_weather(screen)

	def click(self, location):
		self.buttons.click(location)

