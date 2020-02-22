from flask import Flask, request, url_for 
from flask import render_template
from flask_pymongo import PyMongo

# Initialize Flask
app = Flask(__name__)
# Define the index route

app.config["MONGO_URI"] = "mongodb://192.168.43.191:27017/diadrastiko"
mongo = PyMongo(app)

@app.route("/")
def index():
    return "Hello from Flask!"


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_name = request.form["user"]
        password = request.form['pswd']
        users = mongo.db.users.find_one({'username':user_name, 'password':password})
        if users:
            session['username']  = user_name
            return redirect_url('dashboard.html', user = {'username':user_name})
        else:
            return render_template("login.html", message="Invalid  username or password")
    else:
        return render_template("login.html")


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
            return redirect_url('login.html', message = "Please login")
            
    else:
        return render_template("signup.html")


# Run Flask if the __name__ variable is equal to __main__
if __name__ == "__main__":
    app.run()