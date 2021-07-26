from flask import Flask, render_template, request, redirect, session
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from oauthlib.oauth2 import WebApplicationClient
from db import init_db_command
from user import User
from config import SSO_URL, AUTH_URL, VERIFY_URL, client_params, secret_key
import base64
import urllib, urllib.parse
import requests
#import json
#import os
import sqlite3

import swagger_client
from swagger_client.rest import ApiException
from swagger_client import Configuration

app = Flask(__name__)
app.secret_key = secret_key

login_manager = LoginManager()
login_manager.init_app(app)

# Naive database setup
try:
    init_db_command()
except sqlite3.OperationalError:
    # Assume it's already been created
    pass

client = WebApplicationClient(client_params['client_id'])

def user_logging(access_token):
    user_info_response = requests.get(url=VERIFY_URL, headers={'Authorization': 'Bearer {}'.format(access_token)})
    character_id = user_info_response.json()['CharacterID']
    character_name = user_info_response.json()['CharacterName']
    portrait = 'https://images.evetech.net/characters/{}/portrait'.format(character_id)
    print(portrait)
    user = User(id_=character_id, name=character_name, profile_pic=portrait)

    # Doesn't exist? Add it to the database.
    if not User.get(character_id):
        User.create(character_id, character_name, portrait)

    # Begin user session by logging the user 
    return user
    #login_user(user)
'''
def make_call(ACCESS_TOKEN):
    api = swagger_client.WalletApi()
    api.api_client.set_default_header('User-Agent', 'Character Industry and market management tool') # Set a relevant user agent so we know which software is actually using ESI
    api.api_client.host = "https://esi.evetech.net"
    Configuration().access_token = ACCESS_TOKEN # fill in your access token here
    try:
        print(current_user.id)
        response = api.get_characters_character_id_wallet(int(current_user.id)) # fill in the character id here
        print(response)
    except ApiException as e:
        print("Exception when calling Api->get_characters_character_id_wallet: %s\n" % e)
'''
def make_call(ACCESS_TOKEN):
    try:
        print(current_user.id)
        print(ACCESS_TOKEN)
        WALLET_URL = 'https://esi.evetech.net/latest/characters/{}/wallet/'.format(current_user.id)
        response = requests.get(url=WALLET_URL, headers={'Authorization': 'Bearer {}'.format(ACCESS_TOKEN)})
        print(response.json())
        return response.json()
    except ApiException as e:
        print("Exception when calling Api->get_characters_character_id_wallet: %s\n" % e)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index(): 
#    if current_user:
#        return  render_template('index.html', user_pic=User.profile_pic)
    return render_template('index.html')

@app.route('/login')
def login():
    if request.method == 'GET':
        return redirect(SSO_URL)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")    

@app.route('/oauth-callback', methods=['GET'])
def sso():
    if request.method == 'GET':
        sso_code = request.args.get('code')
        data_params = {'grant_type':'authorization_code', 'code':str(sso_code)}
        encoded_auth = base64.urlsafe_b64encode(('{}:{}'.format(client_params['client_id'], secret_key)).encode('utf-8'))
        print('Encoded parameter: ' + 'Authorization : Basic {}'.format((encoded_auth).decode('utf-8')))
        headers = { 'Authorization' : 'Basic {}'.format((encoded_auth).decode('utf-8')), 
                    'Content-Type':'application/x-www-form-urlencoded', 
                    'Host':'login.eveonline.com',}

        r = requests.post(url=AUTH_URL, headers=headers, data=data_params)
        print(r.json())
        ACCESS_TOKEN = r.json()['access_token']
        REFRESH_TOKEN = r.json()['refresh_token']
        #r = requests.get(url=VERIFY_URL, headers={'Authorization': 'Bearer {}'.format(ACCESS_TOKEN)})
        user = user_logging(ACCESS_TOKEN)
        login_user(user)
        session['access_token'] = ACCESS_TOKEN
        return redirect('/character')

@app.route("/character")
@login_required
def character():
    wallet_balance = make_call(session['access_token'])
    return render_template('character.html', wallet_balance = wallet_balance)

if __name__ == "__main__":
    app.run(debug=True)