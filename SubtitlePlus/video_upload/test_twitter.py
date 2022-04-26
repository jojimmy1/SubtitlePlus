import os
from flask import Flask, render_template, request, url_for, redirect
import oauth2 as oauth
import urllib.request
import urllib.parse
import urllib.error
import json

from requests_oauthlib import OAuth1Session
import tweepy
app = Flask(__name__)

app.debug = False

request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token'
authorize_url = 'https://api.twitter.com/oauth/authorize'
show_user_url = 'https://api.twitter.com/1.1/users/show.json'

# Support keys from environment vars (Heroku).
app.config['APP_CONSUMER_KEY'] = "S21k0RuDj0DC7Ki3vioxjz6zM" #os.getenv('TWAUTH_APP_CONSUMER_KEY', 'API_Key_from_Twitter')
app.config['APP_CONSUMER_SECRET'] = "I0nV5X0T3XnPFMi5fhWBSDsZkcDHKJatMvYbisj5wpZZCVrYxp" #os.getenv('TWAUTH_APP_CONSUMER_SECRET', 'API_Secret_from_Twitter')

# alternatively, add your key and secret to config.cfg
# config.cfg should look like:
# APP_CONSUMER_KEY = 'API_Key_from_Twitter'
# APP_CONSUMER_SECRET = 'API_Secret_from_Twitter'
app.config.from_pyfile('config.cfg', silent=True)

oauth_store = {}

payload = {"text": "How are you? my friend."}
fields = "created_at,description"
params = {"usernames": "TwitterDev,TwitterAPI", "user.fields": fields}
@app.route('/')
def hello():
    return print_index_table()


@app.route('/start')
def start():
    # note that the external callback URL must be added to the whitelist on
    # the developer.twitter.com portal, inside the app settings
    app_callback_url = url_for('callback', _external=True)

    # Generate the OAuth request tokens, then display them
    consumer = oauth.Consumer(
        app.config['APP_CONSUMER_KEY'], app.config['APP_CONSUMER_SECRET'])
    client = oauth.Client(consumer)
    resp, content = client.request(request_token_url, "POST", body=urllib.parse.urlencode({
                                   "oauth_callback": app_callback_url}))

    if resp['status'] != '200':
        error_message = 'Invalid response, status {status}, {message}'.format(
            status=resp['status'], message=content.decode('utf-8'))
        return error_message

    request_token = dict(urllib.parse.parse_qsl(content))
    oauth_token = request_token[b'oauth_token'].decode('utf-8')
    oauth_token_secret = request_token[b'oauth_token_secret'].decode('utf-8')

    oauth_store[oauth_token] = oauth_token_secret
    
    return redirect(authorize_url +f"?oauth_token={oauth_token}")


@app.route('/callback')
def callback():
    # Accept the callback params, get the token and call the API to
    # display the logged-in user's name and handle
    oauth_token = request.args.get('oauth_token')
    oauth_verifier = request.args.get('oauth_verifier')
    oauth_denied = request.args.get('denied')

    # if the OAuth request was denied, delete our local token
    # and show an error message
    if oauth_denied:
        if oauth_denied in oauth_store:
            del oauth_store[oauth_denied]
        return render_template('error.html', error_message="the OAuth request was denied by this user")

    if not oauth_token or not oauth_verifier:
        return render_template('error.html', error_message="callback param(s) missing")

    # unless oauth_token is still stored locally, return error
    if oauth_token not in oauth_store:
        return render_template('error.html', error_message="oauth_token not found locally")

    oauth_token_secret = oauth_store[oauth_token]

    # if we got this far, we have both callback params and we have
    # found this token locally

    consumer = oauth.Consumer(
        app.config['APP_CONSUMER_KEY'], app.config['APP_CONSUMER_SECRET'])
    token = oauth.Token(oauth_token, oauth_token_secret)
    token.set_verifier(oauth_verifier)
    client = oauth.Client(consumer, token)

    resp, content = client.request(access_token_url, "POST")
    access_token = dict(urllib.parse.parse_qsl(content))

    screen_name = access_token[b'screen_name'].decode('utf-8')
    user_id = access_token[b'user_id'].decode('utf-8')

    # These are the tokens you would store long term, someplace safe
    real_oauth_token = access_token[b'oauth_token'].decode('utf-8')
    real_oauth_token_secret = access_token[b'oauth_token_secret'].decode(
        'utf-8')

    # Call api.twitter.com/1.1/users/show.json?user_id={user_id}
    real_token = oauth.Token(real_oauth_token, real_oauth_token_secret)
    real_client = oauth.Client(consumer, real_token)


    oauth_test = OAuth1Session(
        app.config['APP_CONSUMER_KEY'],
        client_secret=app.config['APP_CONSUMER_SECRET'],
        resource_owner_key=real_oauth_token,
        resource_owner_secret=real_oauth_token_secret,
    )
    '''
    # authorization of consumer key and consumer secret
    auth = tweepy.OAuthHandler(app.config['APP_CONSUMER_KEY'], app.config['APP_CONSUMER_SECRET'])
    
    # set access to user's access key and access secret
    auth.set_access_token(real_oauth_token, real_oauth_token_secret)
    
    # calling the api
    api = tweepy.API(auth)
    
    # the name of the media file
    filename = "/Users/justinchen/Desktop/helloworld.mov"
    
    # upload the file
    media = api.media_upload(filename)
    
    file = open("/Users/justinchen/Desktop/helloworld.mov", 'rb')
    data = file.read()
    resource_url='https://upload.twitter.com/1.1/media/upload.json'
    upload_video={
        'media':data,
        'media_category':'tweet_video'}
    media_id=oauth_test.post(resource_url,params=upload_video)
    tweet_meta={ "media_id": media_id,
        "alt_text": {
        "text":"your_video_metadata_here" 
    }}

    metadata_url = 'https://upload.twitter.com/1.1/media/metadata/create.json'    
    real_resp = oauth_test.post(metadata_url,params=tweet_meta)
    '''
    
    real_resp = oauth_test.post(
    "https://api.twitter.com/2/tweets",
    json=payload,
    )
    
    #real_resp, real_content = real_client.request(
    #    show_user_url + '?user_id=' + user_id, "GET")
    if real_resp.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(real_resp.status_code, real_resp.text)
        )

    print("Response code: {}".format(real_resp.status_code))
    '''
    if real_resp['status'] != '200':
        error_message = "Invalid response from Twitter API GET users/show: {status}".format(
            status=real_resp['status'])
        return render_template('error.html', error_message=error_message)

    response = json.loads(real_content.decode('utf-8'))
    
    friends_count = response['friends_count']
    statuses_count = response['statuses_count']
    followers_count = response['followers_count']
    name = response['name']
    '''
    # don't keep this token and secret in memory any longer
    del oauth_store[oauth_token]

    return print_index_table()
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_message='uncaught exception'), 500
    
def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/start">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '</td></tr></table>')
  
if __name__ == '__main__':
      app.run('localhost', 8080, debug=True)