from flask import Flask, redirect, url_for, session, request, jsonify, Markup
from flask_oauthlib.client import OAuth
from flask import render_template
import pprint
import os
import json
import pymongo


 
app = Flask(__name__)
app.debug = True #Change this to False for production

app.secret_key = os.environ['SECRET_KEY'] #used to sign session cookies
oauth = OAuth(app)


url = 'mongodb://{}:{}@{}:{}/{}'.format(
        os.environ["MONGO_USERNAME"],
        os.environ["MONGO_PASSWORD"],
        os.environ["MONGO_HOST"],
        os.environ["MONGO_PORT"],
        os.environ["MONGO_DBNAME"])
client = pymongo.MongoClient(url)
db = client[os.environ["MONGO_DBNAME"]]
collection = db['collection']



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
	if 'q6' in request.args:
		print("this is working")
		dict = request.args.to_dict()
		print(request.args.getlist('q6'))
		print(dict)
		
		
	return render_template('findacar.html', loggedIn = log, manufacturers = manufacturers_options(), fuel_type = fuel_type_options(), cylinder=cylinder_options(), forward_gears=forward_gears_options())
   
@app.route('/account')
def account():
	log = False
	car = []
	num = 3
	s = "failedat"
	rets = "AAAAAA"
	with open('cars.json') as cars_data:
		cars = json.load(cars_data)
	
	if 'user_data' in session:
		log = True
		print(session['user_data'])
		#session
		#rets = collection()
	pprint.pprint(request.args)
	for i in cars:
		s = "aaaa"
		if ('q1' in request.args) and (i["Identification"]["Classification"] != request.args['q1']):
			continue
		if ('q2' in request.args) and (request.args['q2'] not in i["Engine Information"]["Engine Type"]):
			continue
		if ('q4' in request.args) and (i["Engine Information"]["Number of Forward Gears"] != int(request.args['q4'])):
			continue
		#print(request.args['q5'])
		#print(i["Engine Information"]["Driveline"])
		if ('q5' in request.args) and (i["Engine Information"]["Driveline"] != request.args['q5']):
			continue
		if 'q6' in request.args:
			m = request.args.getlist('q6')
			for d in m: 
				s = "make"
				if i["Identification"]["Make"] == d:
					w = i["Dimensions"]["Width"] / 12
					l = i["Dimensions"]["Length"] / 12
					h = i["Dimensions"]["Height"] / 12
					v = w*l*h
					if ('q7' in request.args) and ((request.args['q7'] != "small" and v > 130) or (request.args['q7'] != "medium" and v < 130 or v > 160) or (request.args['q7'] != "large" and v <160)):
						continue
		f = request.args.getlist('q8')
		for t in f:
			s = "fueltype"
			if i["Fuel Information"]["Fuel Type"]!= t:
				continue
		name = "" + i["Identification"]["ID"]
		car.append(name)
	print("god help me")
	print(car)
	
	if len(car) > 0:
		sets = str(car)
		ret = "Here are the results from your quiz: "  + sets
	else: 
		ret = "There were no cars that matched your requirements"
	print("it actually got here")
	return render_template('account.html', loggedIn = log, username =  rets, cars_results = ret)

def manufacturers_options():
	with open('cars.json') as cars_data:
		cars = json.load(cars_data)
	options = ""
	manufacturers= []
	for c in cars:
		if c['Identification']['Make'] not in manufacturers:
			manufacturers.append(c['Identification']['Make'])
	for o in manufacturers:
		options += Markup('<input type="checkbox" name="q6" value=\"' + o + "\">" + o + '<br>')
	return options


def fuel_type_options():
	with open('cars.json') as cars_data:
		cars = json.load(cars_data)
	options = ""
	fuels= []
	for c in cars:
		if c['Fuel Information']['Fuel Type'] not in fuels:
			fuels.append(c['Fuel Information']['Fuel Type'])
	for o in fuels:
		options += Markup('<input type="checkbox" name="q8" value=\"' + o + "\">" + o + '<br>')
	return options

def cylinder_options():
	with open('cars.json') as cars_data:
		cars = json.load(cars_data)
	options = ""
	cylinders= []
	for c in cars:
		if 'cylinder' in c['Engine Information']['Engine Type']:
			index=c['Engine Information']['Engine Type'].index('cylinder')
			char=c['Engine Information']['Engine Type'][index-2]
			if char not in cylinders:
				cylinders.append(c['Engine Information']['Engine Type'][index-2])
	for o in cylinders:
		if o == '0':
			o = '10'
			options += Markup('<input type="radio" name="q2" value=\"' + o + " cylinder \">" + o + " cylinders" + '<br>')
		else:
			options += Markup('<input type="radio" name="q2" value=\"' + o + " cylinder \">" + o + " cylinders" + '<br>')
	return options

def forward_gears_options():
	with open('cars.json') as cars_data:
		cars = json.load(cars_data)
	options= ""
	gears= []
	for c in cars:
		if str(c['Engine Information']['Number of Forward Gears']) not in gears:
			gears.append(str(c['Engine Information']['Number of Forward Gears']))
	for o in gears:
		options += Markup('<input type="radio" name="q4" value=\"' + o + "\">" + o + " forward gears" + '<br>')
	return options
	
   
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
