from flask import Flask, redirect, url_for, session, request, jsonify, Markup
from flask_oauthlib.client import OAuth
from flask import render_template
import pprint
import os
import json
#from bson.objectid import ObjectId
#import pymongo

 
app = Flask(__name__)
app.debug = True #Change this to False for production

app.secret_key = os.environ['SECRET_KEY'] #used to sign session cookies
oauth = OAuth(app)

github = oauth.remote_app(
	'github',
 	consumer_key=os.environ['GITHUB_CLIENT_ID'],
	consumer_secret=os.environ['GITHUB_CLIENT_SECRET'],
 	request_token_params={'scope': 'user:email'}, #request read-only access to the user's email.  For a list of possible scopes, see developer.github.com/apps/building-oauth-apps/scopes-for-oauth-apps
 	base_url='https://api.github.com/',
 	request_token_url=None,
 	access_token_method='POST',
 	access_token_url='https://github.com/login/oauth/access_token',  
 	authorize_url='https://github.com/login/oauth/authorize' #URL for github's OAuth login
)

@app.context_processor
def inject_logged_in():
	return {"logged_in":('github_token' in session)}

@app.route('/')
def home():
	log = False
	if 'user_data' in session:
		log = True
	return render_template('home.html', loggedIn = log)
   
@app.route('/find')
def findcar():
	log = False
	if 'user_data' in session:
		log = True
	return render_template('findacar.html', loggedIn = log, manufacturers = manufacturers_options(), fuel_type = fuel_type_options())
   
@app.route('/account')
def account():
	log = False
	if 'user_data' in session:
		log = True
	return render_template('account.html', loggedIn = log)

#manufacturers_options is finished
# def manufacturers_options():
# 	with open('cars.json') as cars_data:
# 		cars = json.load(cars_data)
# 	s = []
# 	for c in cars:
# 		if c['Identification']['Make'] not in s:
# 			s.append(c['Identification']['Make'])
# 	for o in s:
# 		options += Markup("<input type="checkbox" name="make1" value=\"" + o + "\">" + o + "<br>")
# 	return options

# #fuel_type_options is not finished
# def fuel_type_options():
# 	with open('cars.json') as cars_data:
# 		cars = json.load(cars_data)
# 	options = ""
# 	s = []
# 	for c in cars:
# 		if c['Fuel Information']['Fuel Type'] not in s:
# 		s.append(c['Fuel Information']['Fuel Type'])
# 		options += Markup("<option value=\"" + c["State"] + "\">" + c["State"] + "</option>")
# 	return options

# #way_range_options is finished
# def way_range_options():
# 	with open('cars.json') as cars_data:
# 		cars = json.load(cars_data)
# 	options = ""
# 	s = []
# 	min = c[0]['Fuel Information']['Highway mpg']
# 	max = c[0]['Fuel Information']['Highway mpg']
# 	for c in cars:
# 		if c['Fuel Information']['Highway mpg'] is < min:
# 			min =c['Fuel Information']['Highway mpg']
# 		if c['Fuel Information']['Highway mpg'] is > max:
# 			max =c['Fuel Information']['Highway mpg']
# 	return str(min) + str(",") + str(max)

# #city_range_options is not finished
# def city_range_options():
# 	with open('cars.json') as cars_data:
# 		cars = json.load(cars_data)
# 	options = ""
# 	s = []
# 	min = c[0]['Fuel Information']['City mph']
# 	max = c[0]['Fuel Information']['City mph']
# 	for c in cars:
# 		if c['Fuel Information']['City mph'] is < min:
# 			min = c['Fuel Information']['City mph']
# 		if c['Fuel Information']['City mph'] is > max:
# 			max = c['Fuel Information']['City mph']
# 	return str(min) + str(",") + str(max)
   
@app.route('/login')
def login():   
 	return github.authorize(callback=url_for('authorized', _external=True, _scheme='https')) #callback URL must match the pre-configured callback URL

@app.route('/logout')
def logout():
 	session.clear()
 	return render_template('message.html', message='You were logged out')

@app.route('/login/authorized')
def authorized():
 	resp = github.authorized_response()
 	if resp is None:
 		session.clear()
 		message = 'Access denied: reason=' + request.args['error'] + ' error=' + request.args['error_description'] + ' full=' + pprint.pformat(request.args)      
 	else:
 		try:
 			session['github_token'] = (resp['access_token'], '') #save the token to prove that the user logged in
 			session['user_data']=github.get('user').data
 			message='You were successfully logged in as ' + session['user_data']['login']
 		except Exception as inst:
 			session.clear()
 			print(inst)
 			message='Unable to login, please try again.  '
 	return redirect(url_for('home'))
    

@github.tokengetter
def get_github_oauth_token():
 	return session.get('github_token')
  
if __name__ == '__main__':
	app.run()
