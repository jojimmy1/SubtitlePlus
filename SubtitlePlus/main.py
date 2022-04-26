"""
Python backend. To start the server, do 'python main.py'
"""
from pydoc import describe
from unicodedata import decimal
import flask
import sqlite3
from datetime import datetime
from datetime import timedelta
import time
from flask import abort, redirect, url_for, render_template, request, jsonify, send_file
import os
import glob
import shutil
import ffmpeg

# Below for video upload
import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import httplib2
import random
import sys
from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
# Above for video upload

from video_split.video_split_submain import *

def hash_id(id):
    """Creates 8 digit hashcode (int)"""
    return abs(hash(id)) % (10 ** 8)

# def merge_video_subtitle(video_filename, subtitle_filename, output_filename):
#     """ this function merge video and subtitle
#      , input filenames and output filename """
#     video = ffmpeg.input(video_filename)
#     audio = video.audio
#     ffmpeg.concat(video.filter("subtitles", subtitle_filename), audio, v=1, a=1).output(output_filename).run()

def merge_video_subtitle(video_filename, subtitle_filename, output_filename,scale_w=None,scale_h=None,fps=None):
    """ this function merge video and subtitle
     , input filenames and output filename """
    video = ffmpeg.input(video_filename)
    audio = video.audio
    if fps != None:
        video = video.filter("fps",fps=fps,round='up')
    if scale_w != None:
        video = video.filter('scale',w=scale_w,h=scale_h)
    #.filter("fps",fps=5,round='up') can change the fps
    #.filter('scale',w=1920,h=1080) can scale the video
    ffmpeg.concat(video.filter("subtitles", subtitle_filename), audio, v=1, a=1).output(output_filename).run()

# app = flask.Flask(__name__)
app = flask.Flask(__name__, static_folder='static/')
"""Set the static folder"""

# Below for video upload
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = [ 'https://www.googleapis.com/auth/youtube.upload']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
app.secret_key = 'REPLACE ME - this value is here as a placeholder.'
called_from_upload = True

app.config['UPLOAD_FOLDER'] = "./serverfile"
@app.route('/upload_done', methods=['GET','POST'])
def test_api_request():
    global called_from_upload
    called_from_upload = True
    filename1 = 'merged.mp4'
    if flask.request.files:
        video = flask.request.files["video"]
        if (video.filename != ''):
            video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))

    title0 = flask.request.form['title']
    descr0 = flask.request.form['descr']
    tags0 = flask.request.form['tags']
    category0 = int(flask.request.form['category'])
    priv0 = flask.request.form['priv']
    sche0 = flask.request.form['sche']
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
    youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    if tags0 == "":
        tags0 = None
    body = None
    if sche0 == "":
        body=dict(
        snippet=dict(
            title=title0,
            description=descr0,
            tags=tags0,
            categoryId=category0
        ),
        status=dict(
            privacyStatus=priv0
        )
        )
    else:
        body=dict(
        snippet=dict(
            title=title0,
            description=descr0,
            tags=tags0,
            categoryId=category0
        ),
        status=dict(
            privacyStatus='private',
            publishAt = sche0
        )
        )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    media_body=MediaFileUpload("./serverfile/merged.mp4", chunksize=-1, resumable=True)
    )
    resumable_upload(insert_request)
    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    flask.session['credentials'] = credentials_to_dict(credentials)
    return 'Video uploaded'

def resumable_upload(insert_request):
    """This method implements an exponential backoff strategy to resume a failed upload."""
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print( "Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print ("Video id '%s' was successfully uploaded." % response['id'])
                else:
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status,
                                                                    e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

    if error is not None:
        print(error)
        retry += 1
        if retry > MAX_RETRIES:
            exit("No longer attempting to retry.")

        max_sleep = 2 ** retry
        sleep_seconds = random.random() * max_sleep
        print("Sleeping %f seconds and then retrying..." % sleep_seconds)
        time.sleep(sleep_seconds)

@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state

    return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    global called_from_upload
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    # return flask.redirect(flask.url_for('test_api_request'))
    print("called from upload: ",called_from_upload)
    if called_from_upload:
        return flask.redirect(flask.url_for('test_api_request'))
    else:
        return redirect('/oneclick')

@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return flask.render_template("cleared.html")

def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/test">Test an API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
            '<td>Go directly to the authorization flow. If there are stored ' +
            '    credentials, you still might not be prompted to reauthorize ' +
            '    the application.</td></tr>' +
            '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
            '<td>Revoke the access token associated with the current user ' +
            '    session. After revoking credentials, if you go to the test ' +
            '    page, you should see an <code>invalid_grant</code> error.' +
            '</td></tr>' +
            '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
            '<td>Clear the access token currently stored in the user session. ' +
            '    After clearing the token, if you <a href="/test">test the ' +
            '    API request</a> again, you should go back to the auth flow.' +
            '</td></tr></table>')

# Above for video upload

@app.route("/", methods=['GET','POST'])
def frontpage():
    """Front page when user visit the website"""
    return flask.render_template("frontpage.html")

@app.route("/team", methods=['GET','POST'])
def team():
    """Team info"""
    return """Jimmy, Ray, Justin. Built in Spring 2022.
            Thanks for the support from Professor and ECE49595 course staffs."""

@app.route("/loc", methods=['GET','POST'])
def loc():
    """Location"""
    return "Purdue University"

@app.route("/license0", methods=['GET','POST'])
def license0():
    """License"""
    return """MPL-2.0
            new BSD License
            BSD-2-Clause
            ISC
            GPLv3
            LGPL
            PSF
            Apache-2.0 license
            MIT License
            BSD 3-Clause License or Apache License, Version 2.0
            MIT
            HPND
            3-Clause BSD License
            MPLv2.0, MIT Licences
            BSD-3-Clause
            Apache-2.0
            BSD-2-Clause or Apache-2.0
            Apache 2.0
            MIT - copyright Edinburgh Genome Foundry
            BSD
            """

@app.route("/mldata", methods=['GET','POST'])
def mldata():
    """Render the machine learning dataset extraction front end"""
    return flask.render_template("mldata.html")

@app.route("/export", methods=['GET','POST'])
def merge_data():
    """Render the export front end"""
    return flask.render_template("export.html")

@app.route("/upload", methods=['GET','POST'])
def uploadvideo():
    """Render upload front end"""
    global called_from_upload
    called_from_upload = True
    return flask.render_template("upload.html")

@app.route("/register", methods=['GET','POST'])
def register():
    """Render register front end"""
    return flask.render_template("register1.html")

@app.route("/oneclick", methods=['GET','POST'])
def oneclick():
    """Render register front end"""
    global called_from_upload
    called_from_upload = False
    return flask.render_template("oneclick.html")


def getSRT(startime, endtime, content):
    """Iterate over each line, return new string"""
    starlist = startime.splitlines()
    endlist = endtime.splitlines()
    conlist = content.splitlines()
    if (len(starlist) == len(endlist)) and (len(starlist) == len(conlist)):
        pass
    else:
        return "ERROR: The number of lines in the 3 strings doesn't match."
    
    res = ""
    for i in range(len(starlist)):
        star = int(float(starlist[i]))
        end = int(float(endlist[i]))
        con = conlist[i]
        star = time.strftime('%H:%M:%S', time.gmtime(star)) + ",000"
        end = time.strftime('%H:%M:%S', time.gmtime(end)) + ",000"
        inter = f'{i+1}\n' + star + f' --> ' + end + f'\n' + con + f'\n\n'
        res += inter
    return res

@app.route("/downloadsrt", methods=['GET','POST'])
def srtDownload():
    """Download the srt file generated by one click"""
    return send_file('./serverfile/oneclick.srt',as_attachment=True)

@app.route("/downloadml", methods=['GET','POST'])
def downloadml():
    """Download the ml zip file generated by one click"""
    return send_file('./serverfile/MLdata.zip',as_attachment=True)

@app.route("/downloadmerged", methods=['GET','POST'])
def downloadmerged():
    """Download the merged video generated by one click"""
    return send_file('./serverfile/merged.mp4',as_attachment=True)

def convert_non_blank_int(str0):
    """Convert string to integer if exist."""
    if str0 != "":
        return int(str0)
    return None

app.config['UPLOAD_FOLDER'] = "./serverfile"
@app.route("/oneclick_done", methods=['GET','POST'])
def oneclick_done():
    """Get things done in one click"""
    print("Now at oneclick")
    global called_from_upload
    called_from_upload = False
    filename1 = 'video.mp4'
    if flask.request.files:
        video = flask.request.files["video"]
        if (video.filename != ''):
            video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
            return redirect("/oneclick")

    # Capture info
    startime = flask.request.form['startime']
    endtime = flask.request.form['endtime']
    content = flask.request.form['content']
    
    # Generate srt files from string
    srtString = getSRT(startime, endtime, content)
    with open('./serverfile/oneclick.srt', 'w') as f:
        f.write(srtString)
    
    # Provide link to download it
    # return send_file('./serverfile/oneclick.srt',as_attachment=True)

    # Split for ML dataset
    # Need to clean the output before that
    shutil.rmtree('./serverfile/output')
    os.mkdir('./serverfile/output')
    subtitle_name = "./serverfile/oneclick.srt" #input data which is the srt text file
    video_name = "./serverfile/video.mp4" #input data which should be a mp4 file
    submain(subtitle_name, video_name, 0) # Oneclick will only do srt
    # Zip the folder
    shutil.make_archive("./serverfile/MLdata", 'zip', './serverfile/output')

    # Do the merging (require ffmpeg)
    width0 = convert_non_blank_int(flask.request.form['width0'])
    height0 = convert_non_blank_int(flask.request.form['height0'])
    fps0 = convert_non_blank_int(flask.request.form['fps0'])
    merge_video_subtitle("./serverfile/video.mp4", "./serverfile/oneclick.srt", "./serverfile/merged.mp4",width0, height0, fps0)
    
    # Do the upload
    title0 = flask.request.form['title']
    descr0 = flask.request.form['descr']
    tags0 = flask.request.form['tags']
    category0 = int(flask.request.form['category'])
    priv0 = flask.request.form['priv']
    sche0 = flask.request.form['sche']
    if 'credentials' not in flask.session:
        return flask.render_template("error.html")

    # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(**flask.session['credentials'])
    youtube = build(API_SERVICE_NAME, API_VERSION, credentials=credentials)
    if tags0 == "":
        tags0 = None
    body = None
    if sche0 == "":
        body=dict(
        snippet=dict(
            title=title0,
            description=descr0,
            tags=tags0,
            categoryId=category0
        ),
        status=dict(
            privacyStatus=priv0
        )
        )
    else:
        body=dict(
        snippet=dict(
            title=title0,
            description=descr0,
            tags=tags0,
            categoryId=category0
        ),
        status=dict(
            privacyStatus='private',
            publishAt = sche0
        )
        )

    # Call the API's videos.insert method to create and upload the video.
    insert_request = youtube.videos().insert(
    part=",".join(body.keys()),
    body=body,
    media_body=MediaFileUpload("./serverfile/merged.mp4", chunksize=-1, resumable=True)
    )
    resumable_upload(insert_request)
    # Save credentials back to session in case access token was refreshed.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    flask.session['credentials'] = credentials_to_dict(credentials)
    # Above upload completed

    return flask.render_template("download.html") # Download the files from new webpage, can select what to download

app.config["IMGU"] = "./static/pic"
@app.route("/createUser", methods=['POST'])
def submit_form():
    """Gather data from form and write to database."""
    
    conn = sqlite3.connect('static/data/database.db')
    """Connect to the sqlite3 database"""

    c = conn.cursor()
    first_name = flask.request.form['fname']
    last_name = flask.request.form['lname']
    userID = flask.request.form['userID']
    hashcode = hash_id(userID)
    
    filename1 = '0.jpg'
    # if flask.request.files:
    #     image = flask.request.files["image"]
    #     if (image.filename != ''):
    #         # filename = id + original file name. Add to database
    #         filename1 = userID + image.filename
    #         image.save(os.path.join(app.config["IMGU"], filename1))
    
    #if same id, link to already exist
    check1 = (c.execute("SELECT hashcode from users where userID = ?", (userID,)).fetchall())
    if (check1 != []):
        hashcode = check1[0][0]
        url1 = f"/{hashcode}/feed/1"
        return redirect(url1)
    
    print('Hashcode: ' + str(hashcode))
    
    if (filename1 != '0.jpg'):
        user = (first_name, last_name, userID, hashcode,filename1)
        c.execute('INSERT INTO users VALUES(?, ?, ?, ?,?)', user)
    else:
        user = (first_name, last_name, userID, hashcode,filename1)
        c.execute('INSERT INTO users VALUES(?, ?, ?, ?,?)', user)
    conn.commit()
    # return "User has been created." # TODO: this should link to Feed page
    url1 = f"/{hashcode}/feed/1"    
    return redirect(url1)

app.config["IMGU"] = "./static/pic"
@app.route("/upload_submit", methods=['POST'])
def upload_submit():
    """Submit the data gathered from front end"""
    
    # call function

    url1 = f"/upload"    
    return redirect(url1)

# from video_split import getTime
# from video_split.video_split_submain import *
# from video_split.videosplit import *
# from video_split.textsplit import *

# from video_split.video_split_submain import *
# app.config["IMGU"] = "./static/pic"
app.config['UPLOAD_FOLDER'] = "./serverfile"
@app.route("/mldata_submit", methods=['POST'])
def mldata_submit():
    """Process the videos and subtitles to generate machine learning dataset"""
    filename1 = 'video.mp4'
    if flask.request.files:
        video = flask.request.files["video"]
        if (video.filename != ''):
            video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
    filename1 = 'subtitle.txt'
    if flask.request.files:
        subtitle = flask.request.files["subtitle"]
        if (subtitle.filename != ''):
            subtitle.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
    
    subtype = int(flask.request.form['category'])

    # Split for ML dataset
    # Need to clean the output before that
    shutil.rmtree('./serverfile/output')
    os.mkdir('./serverfile/output')
    subtitle_name = "./serverfile/subtitle.txt" #input data which is the srt text file
    video_name = "./serverfile/video.mp4" #input data which should be a mp4 file
    submain(subtitle_name, video_name, subtype) # 0 srt, 1 lrc, 2 sbv
    # Zip the folder
    shutil.make_archive("./serverfile/MLdata", 'zip', './serverfile/output')

    url1 = f"/downloadml"    
    return redirect(url1)

app.config['UPLOAD_FOLDER'] = "./serverfile"
@app.route("/export_submit", methods=['POST'])
def export_submit():
    """Process the data necessary for exporting the videos"""
    filename1 = 'video.mp4'
    if flask.request.files:
        video = flask.request.files["video"]
        if (video.filename != ''):
            video.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
    filename1 = 'subtitle.txt'
    if flask.request.files:
        subtitle = flask.request.files["subtitle"]
        if (subtitle.filename != ''):
            subtitle.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
    
    # Merge the video and subtitle
    # call function
    # Do the merging (require ffmpeg)
    width0 = convert_non_blank_int(flask.request.form['width0'])
    height0 = convert_non_blank_int(flask.request.form['height0'])
    fps0 = convert_non_blank_int(flask.request.form['fps0'])
    merge_video_subtitle("./serverfile/video.mp4", "./serverfile/subtitle.txt", "./serverfile/merged.mp4",width0, height0, fps0)

    url1 = f"/downloadmerged"    
    return redirect(url1)

@app.route("/<hashedcode>/create", methods=['GET', 'POST'])
def create_post(hashedcode):
    """Create a request for each user"""
    conn = sqlite3.connect('./static/data/database.db')
    c = conn.cursor()
    
    name1 = (c.execute("SELECT first_name,last_name from users WHERE hashcode = ?", (hashedcode,)).fetchall())
    name2 = name1[0][0] + ' ' + name1[0][1]
    return flask.render_template("create_post.html",hashedcode = hashedcode,name2 = name2)

@app.route("/create_done", methods=['POST'])
def create_post_done():
    """Write the request into database"""
    conn = sqlite3.connect('./static/data/database.db')
    c = conn.cursor()
    
    #get user id
    hashedcode = flask.request.form['id2']
    id = (c.execute("SELECT * from users where hashcode = ?", (hashedcode,)).fetchall())
    id = id[0][2]
    print(id)
    
    #capture info
    title1 = flask.request.form['title1']
    content1 = flask.request.form['content1']
    time1 = datetime.now()
    time1 = str(time1)
    vote_count = 0
    
    # generate id, make sure unique
    post_id = hash_id(time1)
    post_str = str(post_id)
    check1 = (c.execute("SELECT * from posts where post_id = ?", (post_str,)).fetchall())
    while (check1 != []):
        post_id = post_id + 1
        post_str = str(post_id)
        check1 = (c.execute("SELECT * from posts where post_id = ?", (post_str,)).fetchall())
    
    #insert
    tobeInserted = (post_str,title1,content1,time1,vote_count,id)
    c.execute('INSERT INTO posts VALUES(?, ?, ?, ?, ?, ?)', tobeInserted)
    
    conn.commit()
    conn.close()
    url1 = f"/{hashedcode}/profile/1"
    return redirect(url1)

# read post
@app.route("/posts/<postid>/<hashedcode>", methods=['GET', 'POST'])
def display2(postid,hashedcode):
    """Read the request created"""
    postid = str(postid)
    conn = sqlite3.connect('./static/data/database.db')
    c = conn.cursor()
    
    name1 = (c.execute("SELECT first_name,last_name from users WHERE hashcode = ?", (hashedcode,)).fetchall())
    name2 = name1[0][0] + ' ' + name1[0][1]
    
    post9 = (c.execute("SELECT userID,title,content from posts where post_id = ?", (postid,)).fetchall())
    fetchall = (c.execute("SELECT vote_count,create_time from posts WHERE post_id = ?", (postid,)).fetchall())
    for element in (fetchall):
        timeget = datetime.strptime(element[1], "%Y-%m-%d %H:%M:%S.%f")
        now1 = datetime.now()
        diff1 = now1 - timeget
        daysec = 24 * 60 * 60 * (diff1.days)
        totalsec = daysec + diff1.seconds
        half60 = totalsec / 60 / 60
        half30 = 0.5*round(half60/0.5)
        count99 = element[0]
    return flask.render_template('view_post.html',postid = postid,count99 = count99,half30 = half30, content1 = post9[0][2], id1 = post9[0][0], title1 = post9[0][1], hashid1 = hashedcode, hashedcode = hashedcode, name2 = name2)

# Profile page using pagination
@app.route("/<hashedcode>/profile/<pagenum>", methods=['GET', 'POST'])
def profilePagination(hashedcode, pagenum): 
    """Set the pagination for the requests created by current user"""
    db_dict = {}
    conn = sqlite3.connect('static/data/database.db')
    c = conn.cursor()
    
    #get id
    id = (c.execute("SELECT * from users where hashcode = ?", (hashedcode,)).fetchall())
    id = id[0][2]
    
    name1 = (c.execute("SELECT first_name,last_name,filename1 from users WHERE userID = ?", (id,)).fetchall())
    name2 = name1[0][0] + ' ' + name1[0][1]
    filename1 = name1[0][2]
    filename2 = "/static/../static/pic/" + filename1
    filename1 = filename2
    print(filename1)

    offset = (int(pagenum) - 1) * 5
    
    # fetchall = (c.execute("SELECT title,content,post_id from posts WHERE userID = ? ORDER BY create_time DESC LIMIT 5 OFFSET ?", (id,offset)).fetchall())
    # for element in (fetchall):
        # db_dict.update({(element[0],element[2]): element[1]})
    
    fetchall = (c.execute("SELECT title,content,post_id,vote_count,create_time from posts WHERE userID = ? ORDER BY create_time DESC LIMIT 5 OFFSET ?", (id,offset)).fetchall())
    for element in (fetchall):
        timeget = datetime.strptime(element[4], "%Y-%m-%d %H:%M:%S.%f")
        now1 = datetime.now()
        diff1 = now1 - timeget
        daysec = 24 * 60 * 60 * (diff1.days)
        totalsec = daysec + diff1.seconds
        half60 = totalsec / 60 / 60
        half30 = 0.5*round(half60/0.5)

        newVoteCount = "Closed"
        if element[3] == 0:
            newVoteCount = "Open"
        db_dict.update({(element[0],element[2]): (element[1],newVoteCount,half30)})
    print(db_dict)
    
    ######################
    fetchall = (c.execute("SELECT title,content,post_id from posts WHERE userID = ? ORDER BY create_time DESC", (id,)).fetchall())
    count1 = 0
    for element in (fetchall):
        count1 = count1 + 1
    totalpage = count1 / 5
    totalpage = round(totalpage)
    if (totalpage * 5 < count1):
        totalpage = totalpage + 1
    
    dict9 ={}
    i1 = totalpage + 1
    # i1=9
    while i1 <= 10:
        dict9.update({i1+999: i1})
        i1 = i1 + 1
    
    return flask.render_template('view2.html', dict9 = dict9, data = db_dict, hashedcode = hashedcode, name2 = name2, filename1 = filename1, pagenum = pagenum)

# Feed page using pagination
@app.route("/<hashedcode>/feed/<pagenum>", methods=['GET', 'POST'])
def feedpagePagination(hashedcode, pagenum): 
    """Set the pagination for the requests created by other user"""
    db_dict = {}
    conn = sqlite3.connect('static/data/database.db')
    c = conn.cursor()
    
    #get id
    id = (c.execute("SELECT * from users where hashcode = ?", (hashedcode,)).fetchall())
    # list of tuple
    id = id[0][2]
    
    name1 = (c.execute("SELECT first_name,last_name from users WHERE userID = ?", (id,)).fetchall())
    name2 = name1[0][0] + ' ' + name1[0][1]
    print(name2)

    offset = (int(pagenum) - 1) * 5

    # Modified AND condition
    # fetchall = (c.execute("SELECT title,content,post_id,vote_count,create_time from posts WHERE userID != ? AND vote_count == 0 ORDER BY create_time DESC LIMIT 5 OFFSET ?", (id,offset)).fetchall())
    fetchall = (c.execute("SELECT title,content,post_id,vote_count,create_time from posts WHERE userID != ? ORDER BY create_time DESC LIMIT 5 OFFSET ?", (id,offset)).fetchall())
    for element in (fetchall):
        timeget = datetime.strptime(element[4], "%Y-%m-%d %H:%M:%S.%f")
        now1 = datetime.now()
        diff1 = now1 - timeget
        daysec = 24 * 60 * 60 * (diff1.days)
        totalsec = daysec + diff1.seconds
        half60 = totalsec / 60 / 60
        half30 = 0.5*round(half60/0.5)
        
        newVoteCount = "Closed"
        if element[3] == 0:
            newVoteCount = "Open"
        db_dict.update({(element[0],element[2]): (element[1],newVoteCount,half30)})
    print(db_dict)
    
    # Modified AND condition
    # fetchall = (c.execute("SELECT title,content,post_id from posts WHERE userID != ? AND vote_count == 0 ORDER BY create_time DESC", (id,)).fetchall())
    fetchall = (c.execute("SELECT title,content,post_id from posts WHERE userID != ? ORDER BY create_time DESC", (id,)).fetchall())
    count1 = 0
    for element in (fetchall):
        count1 = count1 + 1
    totalpage = count1 / 5
    totalpage = round(totalpage)
    if (totalpage * 5 < count1):
        totalpage = totalpage + 1
    
    dict2 ={}
    i1 = totalpage + 1
    # i1=9
    while i1 <= 10:
        dict2.update({i1+999: i1})
        i1 = i1 + 1
    return flask.render_template('view3.html',dict2 = dict2, data = db_dict, hashedcode = hashedcode, name2 = name2, pagenum = pagenum)

# Check open request
@app.route("/<hashedcode>/feed/<pagenum>/open", methods=['GET', 'POST'])
def openrequest(hashedcode, pagenum): 
    """Set the pagination for the requests created by other user"""
    db_dict = {}
    conn = sqlite3.connect('static/data/database.db')
    c = conn.cursor()
    
    #get id
    id = (c.execute("SELECT * from users where hashcode = ?", (hashedcode,)).fetchall())
    # list of tuple
    id = id[0][2]
    
    name1 = (c.execute("SELECT first_name,last_name from users WHERE userID = ?", (id,)).fetchall())
    name2 = name1[0][0] + ' ' + name1[0][1]
    print(name2)

    offset = (int(pagenum) - 1) * 5

    # Modified AND condition
    fetchall = (c.execute("SELECT title,content,post_id,vote_count,create_time from posts WHERE userID != ? AND vote_count == 0 ORDER BY create_time DESC LIMIT 5 OFFSET ?", (id,offset)).fetchall())
    # fetchall = (c.execute("SELECT title,content,post_id,vote_count,create_time from posts WHERE userID != ? ORDER BY create_time DESC LIMIT 5 OFFSET ?", (id,offset)).fetchall())
    for element in (fetchall):
        timeget = datetime.strptime(element[4], "%Y-%m-%d %H:%M:%S.%f")
        now1 = datetime.now()
        diff1 = now1 - timeget
        daysec = 24 * 60 * 60 * (diff1.days)
        totalsec = daysec + diff1.seconds
        half60 = totalsec / 60 / 60
        half30 = 0.5*round(half60/0.5)
        
        newVoteCount = "Closed"
        if element[3] == 0:
            newVoteCount = "Open"
        db_dict.update({(element[0],element[2]): (element[1],newVoteCount,half30)})
    print(db_dict)
    
    # Modified AND condition
    fetchall = (c.execute("SELECT title,content,post_id from posts WHERE userID != ? AND vote_count == 0 ORDER BY create_time DESC", (id,)).fetchall())
    # fetchall = (c.execute("SELECT title,content,post_id from posts WHERE userID != ? ORDER BY create_time DESC", (id,)).fetchall())
    count1 = 0
    for element in (fetchall):
        count1 = count1 + 1
    totalpage = count1 / 5
    totalpage = round(totalpage)
    if (totalpage * 5 < count1):
        totalpage = totalpage + 1
    
    dict2 ={}
    i1 = totalpage + 1
    # i1=9
    while i1 <= 10:
        dict2.update({i1+999: i1})
        i1 = i1 + 1
    return flask.render_template('viewopen.html',dict2 = dict2, data = db_dict, hashedcode = hashedcode, name2 = name2, pagenum = pagenum)

# Check closed request
@app.route("/<hashedcode>/feed/<pagenum>/closed", methods=['GET', 'POST'])
def closedrequest(hashedcode, pagenum): 
    """Set the pagination for the requests created by other user"""
    db_dict = {}
    conn = sqlite3.connect('static/data/database.db')
    c = conn.cursor()
    
    #get id
    id = (c.execute("SELECT * from users where hashcode = ?", (hashedcode,)).fetchall())
    # list of tuple
    id = id[0][2]
    
    name1 = (c.execute("SELECT first_name,last_name from users WHERE userID = ?", (id,)).fetchall())
    name2 = name1[0][0] + ' ' + name1[0][1]
    print(name2)

    offset = (int(pagenum) - 1) * 5

    # Modified AND condition
    fetchall = (c.execute("SELECT title,content,post_id,vote_count,create_time from posts WHERE userID != ? AND vote_count == 1 ORDER BY create_time DESC LIMIT 5 OFFSET ?", (id,offset)).fetchall())
    # fetchall = (c.execute("SELECT title,content,post_id,vote_count,create_time from posts WHERE userID != ? ORDER BY create_time DESC LIMIT 5 OFFSET ?", (id,offset)).fetchall())
    for element in (fetchall):
        timeget = datetime.strptime(element[4], "%Y-%m-%d %H:%M:%S.%f")
        now1 = datetime.now()
        diff1 = now1 - timeget
        daysec = 24 * 60 * 60 * (diff1.days)
        totalsec = daysec + diff1.seconds
        half60 = totalsec / 60 / 60
        half30 = 0.5*round(half60/0.5)
        
        newVoteCount = "Closed"
        if element[3] == 0:
            newVoteCount = "Open"
        db_dict.update({(element[0],element[2]): (element[1],newVoteCount,half30)})
    print(db_dict)
    
    # Modified AND condition
    fetchall = (c.execute("SELECT title,content,post_id from posts WHERE userID != ? AND vote_count == 1 ORDER BY create_time DESC", (id,)).fetchall())
    # fetchall = (c.execute("SELECT title,content,post_id from posts WHERE userID != ? ORDER BY create_time DESC", (id,)).fetchall())
    count1 = 0
    for element in (fetchall):
        count1 = count1 + 1
    totalpage = count1 / 5
    totalpage = round(totalpage)
    if (totalpage * 5 < count1):
        totalpage = totalpage + 1
    print(count1)
    
    dict2 ={}
    i1 = totalpage + 1
    # i1=9
    while i1 <= 10:
        dict2.update({i1+999: i1})
        i1 = i1 + 1
    return flask.render_template('viewclosed.html',dict2 = dict2, data = db_dict, hashedcode = hashedcode, name2 = name2, pagenum = pagenum)

@app.route('/vote', methods=['POST'])
def vote1():
    """Upvote and downvote for a request"""
    conn = sqlite3.connect('static/data/database.db')
    c = conn.cursor()
    userid = flask.request.form['userid']
    count1 = flask.request.form['count1']
    postid = flask.request.form['postid']
    
    id = (c.execute("SELECT userID from users where hashcode = ?", (userid,)).fetchall())
    userid = id[0][0]
    
    # check1 = (c.execute("SELECT post_id from vote where userID = ? AND post_id = ?", (userid,postid)).fetchall())
    # if (check1 != []):
    #     return jsonify({'error' : 'Already voted!'})
    
    time1 = datetime.now()
    time1 = str(time1)
    idx = hash_id(time1)
    idx_str = str(idx)
    #check if id unique
    check1 = (c.execute("SELECT * from vote where idx = ?", (idx_str,)).fetchall())
    while (check1 != []):
        idx = idx + 1
        idx_str = str(idx)
        check1 = (c.execute("SELECT * from vote where idx = ?", (idx_str,)).fetchall())
    
    tobeInserted = (postid,userid,idx)
    c.execute('INSERT INTO vote VALUES(?, ?,?)', tobeInserted)
    
    count1 = int(count1)
    newcount = (c.execute("SELECT vote_count from posts where post_id = ?", (postid,)).fetchall())
    newcount = newcount[0][0]
    newcount = newcount + count1
    if (newcount > 1):
        return jsonify({'error' : 'Request already accepted.'})
    if (newcount < 0):
        return jsonify({'error' : 'Request was not accepted and can not be canceled.'})
    
    set1 = (newcount,postid)
    c.execute('UPDATE posts SET vote_count = ? WHERE post_id = ?', set1)
    conn.commit()
    conn.close()
    new_newcount = "Closed"
    if newcount == 0:
        new_newcount = "Open"
    return jsonify({'count' : new_newcount})

@app.route('/delete', methods=['POST'])
def delete1():
    """Delete a request"""
    conn = sqlite3.connect('static/data/database.db')
    c = conn.cursor()
    postid = flask.request.form['postid']
    
    #check if id unique
    check1 = (c.execute("SELECT * from posts where post_id = ?", (postid,)).fetchall())
    while (check1 == []):
        return jsonify({'error' : 'Already deleted!'})
    
    d1 = (postid,)
    c.execute('DELETE FROM vote WHERE post_id=?', d1)
    c.execute('DELETE FROM posts WHERE post_id=?', d1)
    
    con1 = 1
    conn.commit()
    conn.close()
    return jsonify({'count' : con1})

if __name__ == '__main__':
    # Start the server
    # app.run(port=8001, host='127.0.0.1', debug=True, use_evalex=False)

    # Below is the one used for docker
    # app.run(port=8001, host='0.0.0.0', debug=True, use_evalex=False)
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(port=80, host='0.0.0.0', debug=True, use_evalex=False)
