from flask import Flask, request, url_for , session, redirect
from flask import render_template
from flask_pymongo import PyMongo
import json

# Initialize Flask
app = Flask(__name__)
# Define the index routediadrast

app.config["MONGO_URI"] = "mongodb://10.120.110.61:27017/diadrastiko"
app.secret_key = "this is a secret key"
mongo = PyMongo(app)

@app.route("/")
def index():
    logged_in ="username" in session
    return render_template("home.html", has_logged_in = logged_in)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_name = request.form["user"]
        password = request.form['pswd']
        print(user_name)
        print(password)
        users = mongo.db.users.find_one({'username':user_name, 'password':password})
        print(users)
        if users:
            session['username']  = user_name
            return redirect(url_for('home'))
        else:
            return render_template("login.html", message="Invalid  username or password")
    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout():

    del session["username"]

    return redirect(url_for('home'))

@app.route("/creator")
def creator():
    playlist = []
    for record in mongo.db.playlist.find():
        if record['creator']==session['username']:
            playlist.append({'title':record['title'], 'desc':record['desc'], 'creator':session['username'], 'id':record['_id']})
    return render_template("creator.html", playlist = playlist)

@app.route("/createPlaylist", methods=["POST"])
def createPlaylist():
    playlist_name = request.data.decode('utf-8')
    mongo.db.playlist.insert_one({'title':playlist_name, 'creator':session['username']})
    return redirect(url_for('creator'))

@app.route("/insertVideo", methods=["POST"])
def insertVideo():
    print('hello')
    r = json.loads(request.data)
    mongo.db.playlist.find_one_and_update({'title':r['title']},{'$push':{'vids':{'file_name':r['filename'], 'video_name':r['videoname']}}})    
    return "ok"


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user_name = request.form["user"]
        password = request.form['pswd']
        users = mongo.db.users.find_one({'username':user_name, 'password':password})
        if users:
            return render_template("login.html", message="Username already exists")
        else:
            mongo.db.users.insertOne({'username':user_name, 'password':password})
            return redirect_url('dashboard', message = "Please login")

    else:
        return render_template("signup.html")

@app.route("/playVideo/<videoID>")
def vid(videoID):
    return render_template("playVideo.html",video=videoID)

@app.route("/dashboard")
def home():

    logged_in = "username" in session

    return render_template("UI.html", has_logged_in = logged_in)


# Run Flask if the __name__ variable is equal to __main__
if __name__ == "__main__":
    app.run()