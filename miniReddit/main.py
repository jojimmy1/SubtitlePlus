import flask
import sqlite3
# import datetime
from datetime import datetime
from datetime import timedelta
from flask import abort, redirect, url_for, render_template, request, jsonify
import os

######## HELPERS ############
def hash_id(id): # Creates 8 digit hashcode (int)
    return abs(hash(id)) % (10 ** 8)
#############################

# app = flask.Flask(__name__)
app = flask.Flask(__name__, static_folder='static/')

@app.route("/register", methods=['GET','POST'])
def register():
    return flask.render_template("register.html")

app.config["IMGU"] = "./static/pic"
@app.route("/createUser", methods=['POST'])
def submit_form():
    conn = sqlite3.connect('static/data/database.db')
    c = conn.cursor()
    first_name = flask.request.form['fname']
    last_name = flask.request.form['lname']
    userID = flask.request.form['userID']
    hashcode = hash_id(userID)
    
    filename1 = '0.jpg'
    if flask.request.files:
        print('111111111111111112222222222222')
        image = flask.request.files["image"]
        if (image.filename != ''):
            # filename = id + original file name. Add to database
            filename1 = userID + image.filename
            image.save(os.path.join(app.config["IMGU"], filename1))
    
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

@app.route("/<hashedcode>/create", methods=['GET', 'POST'])
def create_post(hashedcode):
    conn = sqlite3.connect('./static/data/database.db')
    c = conn.cursor()
    
    name1 = (c.execute("SELECT first_name,last_name from users WHERE hashcode = ?", (hashedcode,)).fetchall())
    name2 = name1[0][0] + ' ' + name1[0][1]
    return flask.render_template("create_post.html",hashedcode = hashedcode,name2 = name2)

@app.route("/create_done", methods=['POST'])
def create_post_done():
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
    # return "Post created" # TODO: Should redirect to profile
    url1 = f"/{hashedcode}/profile/1"
    return redirect(url1)

# read post
@app.route("/posts/<postid>/<hashedcode>", methods=['GET', 'POST'])
def display2(postid,hashedcode):
    postid = str(postid)
    conn = sqlite3.connect('./static/data/database.db')
    c = conn.cursor()
    
    name1 = (c.execute("SELECT first_name,last_name from users WHERE hashcode = ?", (hashedcode,)).fetchall())
    name2 = name1[0][0] + ' ' + name1[0][1]
    
    post9 = (c.execute("SELECT userID,title,content from posts where post_id = ?", (postid,)).fetchall())
    # hashid1 = (c.execute("SELECT hashcode from users where userID = ?", (post9[0][0],)).fetchall())
    # message = f"The user is {post9[0][0]}. Title is {post9[0][1]}. Content is {post9[0][2]}. "
    # return message # TODO: Read Post frontend
    # conn.commit()
    # conn.close()
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

# profile page (keeping the original commented just in case)
# @app.route("/<hashedcode>/profile", methods=['GET', 'POST'])
# def seeall(hashedcode): 
#     db_dict = {}
#     conn = sqlite3.connect('static/data/database.db')
#     c = conn.cursor()
    
#     #get id
#     id = (c.execute("SELECT * from users where hashcode = ?", (hashedcode,)).fetchall())
#     id = id[0][2]
    
#     name1 = (c.execute("SELECT first_name,last_name,filename1 from users WHERE userID = ?", (id,)).fetchall())
#     name2 = name1[0][0] + ' ' + name1[0][1]
#     filename1 = name1[0][2]
#     filename2 = "/static/../static/pic/" + filename1
#     filename1 = filename2
#     print(filename1)
    
#     fetchall = (c.execute("SELECT title,content,post_id from posts WHERE userID = ? ORDER BY create_time DESC", (id,)).fetchall())
#     for element in (fetchall):
#         db_dict.update({(element[0],element[2]): element[1]})
#     print(db_dict)
#     return flask.render_template('view2.html', data = db_dict, hashedcode = hashedcode, name2 = name2, filename1 = filename1)

# Profile page using pagination
@app.route("/<hashedcode>/profile/<pagenum>", methods=['GET', 'POST'])
def profilePagination(hashedcode, pagenum): 
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
        db_dict.update({(element[0],element[2]): (element[1],element[3],half30)})
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
    print(111111111111111111111111111)
    print(count1)
    
    dict9 ={}
    i1 = totalpage + 1
    # i1=9
    while i1 <= 10:
        dict9.update({i1+999: i1})
        i1 = i1 + 1
    
    return flask.render_template('view2.html', dict9 = dict9, data = db_dict, hashedcode = hashedcode, name2 = name2, filename1 = filename1, pagenum = pagenum)

#feed page 
# @app.route("/<hashedcode>/feed", methods=['GET', 'POST'])
# def feedpage(hashedcode): 
#     db_dict = {}
#     conn = sqlite3.connect('static/data/database.db')
#     c = conn.cursor()
    
#     #get id
#     id = (c.execute("SELECT * from users where hashcode = ?", (hashedcode,)).fetchall())
#     # list of tuple
#     id = id[0][2]
    
#     name1 = (c.execute("SELECT first_name,last_name from users WHERE userID = ?", (id,)).fetchall())
#     name2 = name1[0][0] + ' ' + name1[0][1]
#     print(name2)
    
#     fetchall = (c.execute("SELECT title,content,post_id,vote_count,create_time from posts WHERE userID != ? ORDER BY create_time DESC", (id,)).fetchall())
#     for element in (fetchall):
#         timeget = datetime.strptime(element[4], "%Y-%m-%d %H:%M:%S.%f")
#         now1 = datetime.now()
#         diff1 = now1 - timeget
#         daysec = 24 * 60 * 60 * (diff1.days)
#         totalsec = daysec + diff1.seconds
#         half60 = totalsec / 60 / 60
#         half30 = 0.5*round(half60/0.5)
#         db_dict.update({(element[0],element[2]): (element[1],element[3],half30)})
#     print(db_dict)
#     return flask.render_template('view3.html', data = db_dict, hashedcode = hashedcode, name2 = name2)

# Feed page using pagination
@app.route("/<hashedcode>/feed/<pagenum>", methods=['GET', 'POST'])
def feedpagePagination(hashedcode, pagenum): 
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

    fetchall = (c.execute("SELECT title,content,post_id,vote_count,create_time from posts WHERE userID != ? ORDER BY create_time DESC LIMIT 5 OFFSET ?", (id,offset)).fetchall())
    for element in (fetchall):
        timeget = datetime.strptime(element[4], "%Y-%m-%d %H:%M:%S.%f")
        now1 = datetime.now()
        diff1 = now1 - timeget
        daysec = 24 * 60 * 60 * (diff1.days)
        totalsec = daysec + diff1.seconds
        half60 = totalsec / 60 / 60
        half30 = 0.5*round(half60/0.5)
        db_dict.update({(element[0],element[2]): (element[1],element[3],half30)})
    print(db_dict)
    
    fetchall = (c.execute("SELECT title,content,post_id from posts WHERE userID != ? ORDER BY create_time DESC", (id,)).fetchall())
    count1 = 0
    for element in (fetchall):
        count1 = count1 + 1
    totalpage = count1 / 5
    totalpage = round(totalpage)
    if (totalpage * 5 < count1):
        totalpage = totalpage + 1
    print(111111111111111111111111111)
    print(count1)
    
    dict2 ={}
    i1 = totalpage + 1
    # i1=9
    while i1 <= 10:
        dict2.update({i1+999: i1})
        i1 = i1 + 1
    return flask.render_template('view3.html',dict2 = dict2, data = db_dict, hashedcode = hashedcode, name2 = name2, pagenum = pagenum)

@app.route('/vote', methods=['POST'])
def vote1():
    conn = sqlite3.connect('static/data/database.db')
    c = conn.cursor()
    userid = flask.request.form['userid']
    count1 = flask.request.form['count1']
    postid = flask.request.form['postid']
    
    
    id = (c.execute("SELECT userID from users where hashcode = ?", (userid,)).fetchall())
    userid = id[0][0]
    # print(userid,count1,postid)
    # return jsonify({'error' : 'Nope!'})
    
    check1 = (c.execute("SELECT post_id from vote where userID = ? AND post_id = ?", (userid,postid)).fetchall())
    if (check1 != []):
        return jsonify({'error' : 'Already voted!'})
    
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
    
    set1 = (newcount,postid)
    c.execute('UPDATE posts SET vote_count = ? WHERE post_id = ?', set1)
    conn.commit()
    conn.close()
    return jsonify({'count' : newcount})

@app.route('/delete', methods=['POST'])
def delete1():
    print('hiiiiiiiii')
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
    app.run(port=8001, host='127.0.0.1', debug=True, use_evalex=False)
