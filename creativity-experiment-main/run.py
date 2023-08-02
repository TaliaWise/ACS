from flask import Flask
from flask import render_template, request, make_response, redirect, flash
from word_recommender import WordRecommender
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import random
import string
import os
import re
#from functions import aut_priorities, get_even_random_aut, ensure_even_distribution, get_distance_and_direction_aut
from models import an_idea, user, add_user_to_users_table, prompt, ENV, experiment, idea_timing, ENV, db
from experiment_parameters import aut_objects, number_of_prompts_allowed, distances, directions, number_of_words, percent_random, distance_direction_options, num_tasks
#from response_timing import response_timings
#from random_walker import WeightedRandomWalker


app = Flask(__name__)

#app.register_blueprint(random_walker)


app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


if ENV == 'dev':
	# if you change this you also have to change the line in models.py
	app.config['SQLALCHEMY_DATABASE_URI'] = 'your postgres database url here'
	#local database

else:
	#else in heroku:
	#attempts to fix sqlalchemy connection issue
	uri = os.getenv("DATABASE_URL")  # or other relevant config var
	if uri.startswith("postgres://"):
		uri = uri.replace("postgres://", "postgresql://", 1)
	# rest of connection code using the connection string `uri`
	#production database (HEROKU)
	app.config['SQLALCHEMY_DATABASE_URI'] = 'your postgres database url here'



#creates database object
db = SQLAlchemy(app)


#the routes

def exp_issue(location, e, user_token):
	print(e)
	timing = datetime.now()
	action = location + e
	user_id = db.engine.execute("SELECT MAX(user_id) FROM users WHERE user_token = %s", [user_token]).fetchone()[0]
	aut_object = db.engine.execute("SELECT aut_object FROM experiments WHERE user_id = %s", [user_id]).fetchone()[0]
	idea_number = db.engine.execute("SELECT MAX(idea_number) FROM ideas WHERE user_id = %s AND aut_object = %s",  [user_id, aut_object]).fetchone()
	if idea_number[0] == None:
		idea_number = 1
	else:
		idea_number = idea_number[0] + 1

	data = idea_timing(user_id, aut_object, idea_number, timing, action)
	db.session.add(data)
	db.session.commit()


def user_id_not_found(line_num):
	user_id = 11111
	timing = datetime.now()
	idea_number = random.choice(range(100000))
	action = line_num
	data = idea_timing(user_id, 'None', idea_number, timing, action)
	db.session.add(data)
	db.session.commit()




#THIS IS DONE YAY!!!!!!
@app.route('/instructions', methods=['GET'])
def instructions():
	prolific_id = request.args.get('prolific_id')
	resp = make_response(render_template('button-onclick.html'))
	resp.set_cookie('user_token', value=prolific_id)
	return resp

"""
@app.route('/second_run', methods=['GET'])
def second_run():
	resp = make_response(render_template('second_aut.html'))
	return resp
"""

def start_experiment_db(user_token, aut_object, distance, direction):
	data, user_id = add_user_to_users_table(user_token, db)
	db.session.add(data)
	db.session.commit()

	data = experiment(user_id, aut_object, distance, direction)
	db.session.add(data)

	action = 'start'
	idea_number = 1
	timing = datetime.now()
	data = idea_timing(user_id, aut_object, idea_number, timing, action)
	db.session.add(data)

	db.session.commit()


@app.route('/to_qualtrics')
def continue_to_qualtrics():
	user_token = request.cookies.get('user_token')
	qualtrics_url = 'https://technioniit.eu.qualtrics.com/jfe/form/SV_7WhYIIUkDGoHgCa?prolific_id=' + user_token
	return redirect(qualtrics_url)


#functions starts here



def aut_priorities(prev_distribution_d_d, prev_auts):
	if len(prev_distribution_d_d) == num_tasks:
		prev_distribution_d_d.sort()
		for pre_a in prev_distribution_d_d:
			aut_object = pre_a[-1]
			if aut_object not in prev_auts and aut_object in aut_objects:
				return aut_object
	else:
		prevs_as = [x[-1] for x in prev_distribution_d_d]
		random.shuffle(aut_objects)
		for aut in aut_objects:
			if aut not in prev_auts and aut not in prevs_as:
				return aut
		for aut in aut_objects:
			if aut not in prev_auts:
				return aut
	#did not return aut object
	user_token = request.cookies.get('user_token')
	exp_issue('aut priorities ', 'aut object did not work' + 'prev_distribution_d_d: ' + str(prev_distribution_d_d) + 'prev_auts:' + str(prev_auts), user_token)
	return 'something went wrong with starting the experiment, please contact us by prolific message or email talia.wise1@gmail.com'



def get_even_random_aut(user_token, prev_distribution_d_d, db):
	prev_user_id = db.engine.execute("SELECT user_id FROM users WHERE user_token = %s", [user_token]).fetchall()
	if prev_user_id:
		#build query for prev aut objects
		query = "SELECT aut_object FROM experiments WHERE user_id = " + str(prev_user_id[0][0])
		if len(prev_user_id) > 1:
			for p_id in prev_user_id[1:]:
				query = query + ' OR user_id = ' + str(p_id[0])
		prev_aut = [x[0] for x in db.engine.execute(query).fetchall()]
		#print('30', prev_distribution_d_d, prev_aut)
		aut_object = aut_priorities(prev_distribution_d_d, prev_aut)
	else:
		aut_object = aut_priorities(prev_distribution_d_d, [])
	return aut_object


#test this
def get_d_d_from_counts(prev_distribution, prev_user_id_dd):
	#gets count of each pair and then choses randomly from least used pair
	counts = {}
	for p in prev_distribution:
	  if (p[1], p[2]) in counts.keys():
	    counts[(p[1], p[2])] = counts[(p[1], p[2])] + p[0]
	  else:
	    counts[(p[1], p[2])] = p[0]
	prev_c_d_d = [p[0] for p in counts.items() if p[1] == min(counts.values())]
	random.shuffle(prev_c_d_d)
	for d_d in prev_c_d_d:
		if d_d not in prev_user_id_dd:
			print('good 167')
			return d_d
	distance, direction =  random.choice(prev_c_d_d)
	print('bad 170')
	return distance, direction


def ensure_even_distribution(user_token, db):
	prev_distribution = db.engine.execute("SELECT COUNT(user_id), distance, direction, aut_object FROM experiments GROUP BY distance, direction, aut_object;").fetchall()
	#get prev experiments
	prev_user_id = db.engine.execute("SELECT user_id FROM users WHERE user_token = %s", [user_token]).fetchall()
	
	if prev_user_id:
		#build query for prev distance, direction objects
		query = "SELECT distance, direction FROM experiments WHERE user_id = " + str(prev_user_id[0][0])
		if len(prev_user_id) > 1:
			for p_id in prev_user_id[1:]:
				query = query + ' OR user_id = ' + str(p_id[0])
		prev_user_id_dd = db.engine.execute(query).fetchall()
		print(prev_user_id_dd)
	else:
		prev_user_id_dd = []

	if len(prev_distribution) > 0:
		got_d_d = False
		prev_d_d = list(set([(x[1], x[2]) for x in prev_distribution]))
		if len(prev_d_d) < len(distance_direction_options):
			random.shuffle(distance_direction_options)
			for distance_direction in distance_direction_options:
				if (distance_direction not in prev_d_d) and (distance_direction not in prev_user_id_dd):
					distance, direction = distance_direction
					got_d_d = True
					print('good', distance, direction, prev_user_id_dd)
					break
			if got_d_d == False:
				print('bad in false', distance, direction, prev_user_id_dd)
				distance, direction = get_d_d_from_counts(prev_distribution, prev_user_id_dd)
		else:
			#gets count of each pair and then choses randomly from least used pair
			distance, direction = get_d_d_from_counts(prev_distribution, prev_user_id_dd)

		prev_distribution_d_d = [x for x in prev_distribution if x[1] == distance and x[2] == direction]
		aut_object = get_even_random_aut(user_token, prev_distribution_d_d, db)
	else:
		distance = random.choice(distances)
		direction = random.choice(directions)
		aut_object = random.choice(aut_objects)
	
	print(distance, direction, aut_object)
	return distance, direction, aut_object


def get_distance_and_direction_aut(user_token, db):
	try:
		distance, direction, aut_object = ensure_even_distribution(user_token, db)
	except Exception as e:
		print(str(e))
		exp_issue('get_distance_and_direction', str(e), user_token)
		distance = 99
		direction = 'random'
		prev_user_id = db.engine.execute("SELECT user_id FROM users WHERE user_token = %s", [user_token]).fetchall()
		if prev_user_id:
			#build query for prev aut objects
			query = "SELECT aut_object FROM experiments WHERE user_id = " + str(prev_user_id[0][0])
			if len(prev_user_id) > 1:
				for p_id in prev_user_id[1:]:
					query = query + ' OR user_id = ' + str(p_id[0])
			prev_aut = [x[0] for x in db.engine.execute(query).fetchall()]
			for aut_object in aut_objects:
				if aut_object not in prev_aut:
					break
		else:
			aut_object = random.choice(aut_objects)
	return distance, direction, aut_object


#functions ends here



@app.route('/start')

def start_exp():
	aut_object = random.choice(aut_objects)
	user_token = request.cookies.get('user_token')
	if user_token is not None:
		try:
			distance, direction, aut_object = get_distance_and_direction_aut(user_token, db)
			start_experiment_db(user_token, aut_object, distance, direction)
			print(aut_object)
			return redirect("/")
		except Exception as e:
			db.session.rollback()
			print('225', str(e))
			exp_issue('start experiment', str(e), user_token)
			return 'There has been an issue, please contact us if this continues .'
	else:
		print('227 user token not found')
		user_id_not_found('user token is None')
		return 'Cookies must be enabled, and you must do the experiment in one browser only. If you are experiencing other issues please message us.'
	




	#should not happen...
	"""
	if 'user_token' not in request.cookies:
		print('not good')
		token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=30))
		resp = make_response(redirect('/'))
		resp.set_cookie('user_token', value=token)
		user_token = token
		distance, direction, aut_object = get_distance_and_direction_aut(user_token, db)
		start_experiment_db(user_token, aut_object, distance, direction)
		return resp
	"""



@app.route('/')
def exp():
	user_token = request.cookies.get('user_token')
	if not user_token: 
		user_id_not_found('route /')
		user_token = request.cookies.get('user_token')
	print(user_token)
	try: 
		user_id = db.engine.execute("SELECT MAX(user_id) FROM users WHERE user_token = %s", [user_token]).fetchone()[0]
		print(user_id)
		aut_object = db.engine.execute("SELECT aut_object FROM experiments WHERE user_id = %s", [user_id]).fetchone()[0]
		#rt.add_timing('start')
		return render_template('index.html', object_name = aut_object, temp_name = 'newspaper')
	except Exception as e:
		if not user_token:
			user_id_not_found('/ asked to return')
		else:
			exp_issue('/ asked to return', str(e), user_token)
		return 'There has been a technical issue, and it appears this experiment does not work on your desktop system. We kindly request that you return the experiment and contact us if you have any questions.'







@app.route('/submit-idea', methods=['POST'])

def submit_an_idea():
	try:
		idea = request.form.get('submitted_idea')
		user_token = request.cookies.get('user_token')
		if not user_token: 
			user_id_not_found('route /')
		print(user_token, 'submit idea')
		user_id = db.engine.execute("SELECT MAX(user_id) FROM users WHERE user_token = %s", [user_token]).fetchone()[0]
		cur_time = datetime.now()

		#autoincrements idea number
		aut_object = db.engine.execute("SELECT aut_object FROM experiments WHERE user_id = %s", [user_id]).fetchone()[0]
		max_idea_query = db.engine.execute("SELECT MAX(idea_number) FROM ideas WHERE user_id = %s AND aut_object = %s",  [user_id, aut_object]).fetchone()

		if max_idea_query[0] == None:
			idea_number = 1
		else:
			idea_number = max_idea_query[0] + 1
		
		#get latest prompt
		prompt = db.engine.execute("SELECT prompt_text, prompt_id FROM prompts WHERE user_id = %s AND aut_object= %s", [user_id, aut_object]).fetchall()

		if len(prompt) > 1:
			num = 0
			for p in prompt:
				if p[1] > num:
					prompt = p[0]
					num = p[1]

		#send submit idea timing
		timing = datetime.now()
		data = idea_timing(user_id, aut_object, idea_number, timing, 'submit')
		db.session.add(data)
		#send start of new idea timing
		#send idea to idea database
		data = an_idea(user_id, aut_object, idea_number, idea, cur_time, str(prompt))
		db.session.add(data)
		db.session.commit()
		return idea
	except Exception as e:
		user_token = request.cookies.get('user_token')
		db.session.rollback()
		exp_issue('submit idea', str(e), user_token)



@app.route('/get-prompt', methods=['POST'])


def getprompt():
	try:
		user_token = request.cookies.get('user_token')
		if not user_token: 
			user_id_not_found('getprompt')
		user_id = db.engine.execute("SELECT MAX(user_id) FROM users WHERE user_token = %s", [user_token]).fetchone()[0]

		aut_object, direction, distance = db.engine.execute("SELECT aut_object, direction, distance FROM experiments WHERE user_id = %s", [user_id]).fetchone()

		if direction == 'towards_previous_ideas':
			direction_w = True
		else:
			direction_w = False

		now = datetime.now()

		prev_ideas = db.engine.execute("SELECT idea FROM ideas WHERE user_id = %s AND aut_object = %s", [user_id, aut_object]).fetchall()
		if len(prev_ideas) == 0:
			return 'You have not submitted any ideas. Are you sure you already want a hint?'
		prev_ideas = [i[0] for i in prev_ideas]


		#todo: add to random walker: if lemma of word in network add lemma of word to prev list (can use s, ing, ings, able, etc...)

		w = WordRecommender(previous_phrases=prev_ideas, directed_towards_previous_ideas = direction_w, start_word = aut_object)

		#print('word recommender:', datetime.now() - now, w.prev)

		#todo: add distance and direction seperately to database
		if direction == 'random':
			words = []
			for g_word in range(number_of_words):
				word = random.choice(list(w.name_dict.keys()))
				words.append((word, 88))
			prompts = words
		else:
			prompts = w.get_words(distance, number_of_words)

		#print('got word', direction, prompts)
		#print('after get words;', datetime.now() - now)

		#we want: the time they get the prompt, the prompt, and the userid, and aut object
		prompt_created_time = datetime.now()

		prev_prompt_id = db.engine.execute("SELECT MAX(prompt_id) FROM prompts WHERE user_id = %s AND aut_object = %s", [user_id, aut_object]).fetchone()[0]
		
		if prev_prompt_id == None:
			prompt_id = 1
		else:
			prompt_id = prev_prompt_id + 1
		
		prompt_text = [w[0] for w in prompts]
		prompt_distance = [w[1] for w in prompts]
		#print('prompt text:', prompt_text)

		if prompt_id > number_of_prompts_allowed:
			return "If you ran out of ideas again, please click on 'I am completely out of ideas'"
		else:
			data = prompt(user_id, prompt_id, aut_object, prompt_created_time, prompt_text, prompt_distance)
			db.session.add(data)
			db.session.commit()

			#todo: i think this only works for two prompts
			if not sum([word == 'no suggestions could be found' for word in prompt_text]):
				if len(prompt_text) == 1:
	  				return(prompt_text[0])
				else:
					return(', '.join(prompt_text[:-1]) + ' and ' + prompt_text[-1])
			else:
				return 'No word suggestions could be found'
	except Exception as e:
		db.session.rollback()
		user_token = request.cookies.get('user_token')
		exp_issue('get prompt', str(e), user_token)



#todo: add start time of each text area input (in javascript)
#if no ideas then add a line to start idea time:
#maybe can save cookie with start time of text area then send to back end at submit :) and update on next change...
#if it already exists then do nothing, if none exists then add the cookie, if submit then send first time with submit + delete the cookie
#if no new idea since 
@app.route('/get-time', methods=['POST'])
def get_time():
	return str(datetime.now())

"""


@app.route('/test_issues')
def test_issues():
	try: 
		raise Exception("in here")
	except Exception as e:
		user_token = request.cookies.get('user_token')
		exp_issue('test issues', str(e), user_token)
	return 'success'

@app.route('/finished', methods=['GET'])
def finish():
	#i guess add 'end time' to experiment table here
	user_token = request.form.get('user_token')
	print(user_token)
	return 'finished'
"""


@app.route('/text_area_focus', methods=['POST'])

def text_area_focus():
	timing = datetime.now()
	action = request.form.get('val')
	user_token = request.cookies.get('user_token')
	user_id = db.engine.execute("SELECT MAX(user_id) FROM users WHERE user_token = %s", [user_token]).fetchone()[0]
	aut_object = db.engine.execute("SELECT aut_object FROM experiments WHERE user_id = %s", [user_id]).fetchone()[0]
	idea_number = db.engine.execute("SELECT MAX(idea_number) FROM ideas WHERE user_id = %s AND aut_object = %s",  [user_id, aut_object]).fetchone()
	if idea_number[0] == None:
		idea_number = 1
	else:
		idea_number = idea_number[0] + 1

	data = idea_timing(user_id, aut_object, idea_number, timing, action)
	db.session.add(data)
	db.session.commit()
	return 'success'


@app.route('/text_area_input', methods=['POST'])

def text_area_input():
	timing = datetime.now()
	action = request.form.get('val')
	user_token = request.cookies.get('user_token')
	user_id = db.engine.execute("SELECT MAX(user_id) FROM users WHERE user_token = %s", [user_token]).fetchone()[0]
	aut_object = db.engine.execute("SELECT aut_object FROM experiments WHERE user_id = %s", [user_id]).fetchone()[0]
	idea_number = db.engine.execute("SELECT MAX(idea_number) FROM ideas WHERE user_id = %s AND aut_object = %s",  [user_id, aut_object]).fetchone()
	if idea_number[0] == None:
		idea_number = 1
	else:
		idea_number = idea_number[0] + 1
	data = idea_timing(user_id, aut_object, idea_number, timing, action)
	db.session.add(data)
	db.session.commit()
	return 'success'



@app.route('/done', methods=['GET'])

# check if submitted last idea? 
#if idea in val but not submitted ask user if they want to submit it in alert?
def done():
	try:
		user_token = request.cookies.get('user_token')
		print(user_token)
		if not user_token:
			user_id_not_found('/done')
			user_token = request.cookies.get('user_token')
			if not user_token:
				user_id_not_found('/done asked to return')
				return 'There has been a technical issue. We kindly request that you return the experiment and contact us for partial compensation.'
		user_ids = db.engine.execute("SELECT user_id FROM users WHERE user_token = %s", [user_token]).fetchall()
		
		#add to timing table
		action = 'completed'
		idea_number = 1000
		timing = datetime.now()
		user_id = max(user_ids)[0]
		aut_object = db.engine.execute("SELECT aut_object FROM experiments WHERE user_id = %s", [user_id]).fetchone()[0]
		data = idea_timing(user_id, aut_object, idea_number, timing, action)
		db.session.add(data)
		db.session.commit()

		if len(user_ids) < num_tasks:
			resp = make_response(render_template('second_aut.html', attempts=len(user_ids)))
			return resp
		else:
			return render_template('finished.html')
	except Exception as e:
		db.session.rollback()
		user_token = request.cookies.get('user_token')
		exp_issue('done', str(e), user_token)


#this is important

if __name__ == '__main__':
    app.run()
