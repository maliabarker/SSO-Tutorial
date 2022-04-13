import flask
from http import client
from flask import Flask, redirect, request
import requests_oauthlib
import os
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

CLIENT_ID = os.environ.get("CLIENT_ID")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")

FB_CLIENT_ID = os.environ.get("FB_CLIENT_ID")
FB_CLIENT_SECRET = os.environ.get("FB_CLIENT_SECRET")

AUTHORIZATION_BASE_URL = "https://app.simplelogin.io/oauth2/authorize"
TOKEN_URL = "https://app.simplelogin.io/oauth2/token"
USERINFO_URL = "https://app.simplelogin.io/oauth2/userinfo"

FB_AUTHORIZATION_BASE_URL = "https://www.facebook.com/dialog/oauth"
FB_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"

FB_SCOPE = ["email"]

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app=Flask(__name__)

@app.route("/")
def index():
    return """
	<a href="/fb-login">Login with Facebook</a>
	"""

@app.route('/fb-login')
def login():
    # simplelogin = requests_oauthlib.OAuth2Session(
    #     CLIENT_ID, redirect_uri="http://localhost:5003/callback"
    #     )

    # authorization_url, _ = simplelogin.authorization_url(AUTHORIZATION_BASE_URL)
    # return redirect(authorization_url)
    facebook = requests_oauthlib.OAuth2Session(
        FB_CLIENT_ID, redirect_uri="http://localhost:5003/fb-callback", scope=FB_SCOPE
	)
    authorization_url, _ = facebook.authorization_url(FB_AUTHORIZATION_BASE_URL)

    return redirect(authorization_url)




@app.route('/fb-callback')
def callback():
    # simplelogin = requests_oauthlib.OAuth2Session(CLIENT_ID)
    
    # simplelogin.fetch_token(
    #     TOKEN_URL, client_secret=CLIENT_SECRET, authorization_response=flask.request.url
    # )

    # user_info = simplelogin.get(USERINFO_URL).json()
    facebook = requests_oauthlib.OAuth2Session(
        FB_CLIENT_ID, scope=FB_SCOPE, redirect_uri="http://localhost:5003/fb-callback"
    )

    facebook = facebook_compliance_fix(facebook)

    facebook.fetch_token(
        FB_TOKEN_URL,
        client_secret=FB_CLIENT_SECRET,
        authorization_response=request.url,
    )

	# Fetch a protected resource, i.e. user profile, via Graph API
    facebook_user_data = facebook.get(
        "https://graph.facebook.com/me?fields=id,name,email,picture{url}"
    ).json()

    email = facebook_user_data["email"]
    name = facebook_user_data["name"]
    picture_url = facebook_user_data.get("picture", {}).get("data", {}).get("url")
    
    return f"""
	User information: <br>
	Name: {name} <br>
	Email: {email} <br>
	Avatar <img src="{picture_url}"> <br>
	<a href="/">Home</a>
	"""



if __name__ == '__main__':
    app.run(debug=True, port=5003)

