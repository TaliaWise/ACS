from flask import Flask
from flask import render_template, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
import re

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


ENV = 'production'
if not os.environ.get('ON_HEROKU'):
	ENV = 'dev'


if ENV == 'dev':

	# if you change this you also have to change the line in run.py

	
	#app.config['SQLALCHEMY_DATABASE_URI'] = 'your postgres database url here'
	
	#local database

else:
	#attempts to fix sqlalchemy connection issue
	uri = os.getenv("DATABASE_URL")  # or other relevant config var
	if uri.startswith("postgres://"):
		uri = uri.replace("postgres://", "postgresql://", 1)
	app.config['SQLALCHEMY_DATABASE_URI'] = 'your postgres database url here'

#creates database object
db = SQLAlchemy(app)



class an_idea(db.Model):
	__tablename__ = 'ideas'
	user_id = db.Column(db.Integer, primary_key=True) 
	aut_object = db.Column(db.String, primary_key=True) #this can be 'brick' or 'paperclip' or whatever
	idea_number = db.Column(db.Integer, primary_key=True) #the number indicating the order of ideas
	idea = db.Column(db.String) 
	time_submitted = db.Column(db.DateTime)
	prompt = db.Column(db.String)


	def __init__(self, user_id, aut_object, idea_number, idea, time_submitted, prompt):
		self.user_id = user_id
		self.aut_object = aut_object
		self.idea_number = idea_number
		self.idea = idea
		self.time_submitted = time_submitted
		self.prompt = prompt


class idea_timing(db.Model):
	__tablename__ = 'timing'
	user_id = db.Column(db.Integer, primary_key=True) 
	aut_object = db.Column(db.String, primary_key=True) #this can be 'brick' or 'paperclip' or whatever
	idea_number = db.Column(db.Integer, primary_key=True)
	dtime = db.Column(db.DateTime, primary_key=True)
	action = db.Column(db.String)

	def __init__(self, user_id, aut_object, idea_number, timing, action):
		self.user_id = user_id
		self.aut_object = aut_object
		self.idea_number = idea_number
		self.dtime = timing
		self.action = action


class user(db.Model):
	__tablename__ = 'users'
	user_id = db.Column(db.Integer, primary_key = True)
	user_token = db.Column(db.String)
	user_created_time = db.Column(db.DateTime)

	def __init__(self, user_id, user_token, user_created_time):
		self.user_id = user_id
		self.user_token = user_token
		self.user_created_time = user_created_time



class prompt(db.Model):
	__tablename__ = 'prompts'
	user_id = db.Column(db.Integer, primary_key = True)
	prompt_id = db.Column(db.Integer, primary_key = True)
	aut_object = db.Column(db.String)
	prompt_created_time = db.Column(db.DateTime)
	prompt_text = db.Column(db.String)
	prompt_distance = db.Column(db.String)
	

	def __init__(self, user_id, prompt_id, aut_object, prompt_created_time, prompt_text, prompt_distance):
		self.user_id = user_id
		self.prompt_id = prompt_id
		self.aut_object = aut_object
		self.prompt_created_time = prompt_created_time
		self.prompt_text = prompt_text
		self.prompt_distance = prompt_distance




class experiment(db.Model):
	__tablename__ = 'experiments'
	user_id = db.Column(db.Integer, primary_key=True)
	aut_object = db.Column(db.String)
	distance = db.Column(db.Integer)
	direction = db.Column(db.String)
	#optimized_or_random = db.Column(db.String)
	def __init__(self, user_id, aut_object, distance, direction):
		self.user_id = user_id
		self.aut_object = aut_object
		self.distance = distance
		self.direction = direction
		#self.optimized_or_random = optimized_or_random


def add_user_to_users_table(user_token, db):
	user_created_time = datetime.now()
	max_user_id = db.engine.execute("SELECT MAX(user_id) FROM users;").fetchone()

	if max_user_id[0] is not None:
		max_id = max_user_id[0]	
	else:
		max_id = 0

	user_id = max_id + 1
	data = user(user_id, user_token, user_created_time)
	return data, user_id


"""
from datetime import datetime

user_token = '5efb415638cbba0732c23908'

now = datetime.now()
user_id = db.engine.execute("SELECT MAX(user_id) FROM users WHERE user_token = %s", [user_token]).fetchone()[0]
print('136 timing', datetime.now() - now)
aut_object = db.engine.execute("SELECT aut_object FROM experiments WHERE user_id = %s", [user_id]).fetchone()[0]
print('138 timing', datetime.now() - now)
idea_number = db.engine.execute("SELECT MAX(idea_number) FROM ideas WHERE user_id = %s AND aut_object = %s",  [user_id, aut_object]).fetchone()
print('140 timing', datetime.now() - now)

now = datetime.now()
prev_distribution = db.engine.execute("SELECT COUNT(user_id), distance, direction, aut_object FROM experiments GROUP BY distance, direction, aut_object;").fetchall()
print('140 timing', datetime.now() - now)	

"""
