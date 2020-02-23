from flask import Flask, request, url_for , session, redirect
from flask import render_template
from flask_pymongo import PyMongo
from code_processor import produceResponse
import json

# Initialize Flask
app = Flask(__name__)
# Define the index routediadrast

app.config["MONGO_URI"] = "mongodb://localhost:27017/diadrastiko"
app.secret_key = "this is a secret key"
mongo = PyMongo(app)

@app.route("/")
def index():
    logged_in = "username" in session
    return render_template("home.html", has_logged_in = logged_in)


@app.route("/login", methods=["GET", "POST"])
def login(msg=""):
    if request.method == "POST":
        user_name = request.form["user"]
        password = request.form['pswd']
        print(user_name)
        print(password)
        users = mongo.db.users.find_one({'username':user_name, 'password':password})
        print(users)
        if users:
            session['username']  = user_name
            return redirect(url_for('index'))
        else:
            return render_template("login.html", message="Invalid  username or password")
    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET"])
def logout():

    del session["username"]

    return redirect(url_for('index'))


@app.route("/creator")
def creator():
    playlist = []
    for record in mongo.db.playlist.find():
        if record['creator'] == session['username']:
            playlist.append({
                'title': record['title'],
                'desc': record['desc'],
                'creator': session['username'],
                'id': record['_id']
            })
    return render_template("creatorPage.html", playlist=playlist)


@app.route("/createPlaylist", methods=["POST"])
def createPlaylist():
    data = json.loads(request.data)
    mongo.db.playlist.insert_one({
        'title': data['title'],
        'desc': data['desc'],
        'creator': session['username']
    })
    return redirect(url_for('creator'))


@app.route("/insertVideo", methods=["POST"])
def insertVideo():
    print('hello')
    r = json.loads(request.data)

    size = mongo.db.videos.count()

    mongo.db.videos.insert_one({
        'file_name': r['filename'],
        'id': str(size)
    })

    mongo.db.playlist.find_one_and_update({'title': r['title']}, {
        '$push': {
            'vids': {
                'file_name': r['filename'],
                'video_name': r['videoname']
            }
        }
    })

    return str(size)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user_name = request.form["user"]
        password = request.form['pswd']
        users = mongo.db.users.find_one({'username':user_name, 'password':password})
        if users:
            return render_template("signup.html", message="Username already exists")
        else:
            mongo.db.users.insert_one({'username':user_name, 'password':password})
            return redirect(url_for('login', message = "Please login"))
    else:
        return render_template("signup.html")




@app.route("/createVideo/<videoID>", methods=["GET"])
def createVideo(videoID):

    video = mongo.db.videos.find_one({'id': videoID})

    return render_template("creator.html",
                           video={
                               'id': videoID,
                               'file_name': video['file_name']
                           })


@app.route("/playVideo/<videoID>")
def playVideo(videoID):

    obj = mongo.db.videos.find_one({'id': videoID})

    return render_template("playVideo.html", video = {
                                                    'id': videoID,
                                                    'file_name': obj['file_name'],
                                                    'commands': obj['commands'],
                                                    'audioBlob': obj['audioBlob'],
                                                    'total_duration': obj['total_duration']
                                                })


@app.route("/uploadVideo/<videoID>", methods=["POST"])
def uploadVideo(videoID):

    req = json.loads(request.data)

    commands = req["commands"]
    audioBlob = req['audioBlob']
    total_duration = req['total_duration']

    doc = mongo.db.videos.find_one({'id': videoID})

    mongo.db.videos.update_one( {'_id': doc['_id']}, {'$set': {'commands': commands, 'audioBlob': audioBlob, 'total_duration': total_duration}} )

    return "OK"


@app.route("/executeCode", methods=["POST"])
def executeCode():

    req = json.loads(request.data)

    src_code = req['src_code']
    file_name = req["file_name"]

    return json.dumps(produceResponse(src_code, file_name))


# Run Flask if the __name__ variable is equal to __main__
if __name__ == "__main__":
    app.run()