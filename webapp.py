from flask import Flask, redirect, url_for, session, request, jsonify, Markup
from flask_oauthlib.client import OAuth
from flask import render_template
#please work 
import pprint
import os
import json
from bson.objectid import ObjectId
import pymongo
app.debug = True
 
app = Flask(__name__)

app.debug = True #Change this to False for production

app.secret_key = os.environ['SECRET_KEY'] #used to sign session cookies
oauth = OAuth(app)

#Set up GitHub as OAuth provider
github = oauth.remote_app(
    'github',
    consumer_key=os.environ['GITHUB_CLIENT_ID'], #your web app's "username" for github's OAuth
    consumer_secret=os.environ['GITHUB_CLIENT_SECRET'],#your web app's "password" for github's OAuth
    request_token_params={'scope': 'user:email'}, #request read-only access to the user's email.  For a list of possible scopes, see developer.github.com/apps/building-oauth-apps/scopes-for-oauth-apps
    base_url='https://api.github.com/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://github.com/login/oauth/access_token',  
    authorize_url='https://github.com/login/oauth/authorize' #URL for github's OAuth login
)

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
    return render_template('findacar.html', loggedIn = log)
   
@app.route('/account')
def account():
    log = False
    if 'user_data' in session:
        log = True
    return render_template('account.html', loggedIn = log)
   
 
  
 if __name__ == '__main__':
    app.run()
