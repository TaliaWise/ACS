from flask import Flask
from datetime import datetime

app = Flask(__name__)


class response_timings:
 
	def __init__(self):
		self.idea_timing = []

	def get_time(self):
		return datetime.now()
 
 	#self.get_time is default but can also use browser time if changed :) 
	#def add_timing(self, val, time = ):
	#	print('get time,', time)
	#`	self.idea_timing.append([val, time])
	def add_timing(self, val, time = None):
		time = self.get_time()
		self.idea_timing.append([val, time])


	def new_idea(self):
		#send idea to database
		self.idea_timing = []

	
