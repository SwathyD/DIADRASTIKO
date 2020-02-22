from flask import Flask, request, url_for , session, redirect
from flask import render_template
from flask_pymongo import PyMongo

# Initialize Flask
app = Flask(__name__)
# Define the index routediadrast

app.config["MONGO_URI"] = "mongodb://192.168.43.191:27017/diadrastiko"
app.secret_key = "this is a secret key"
mongo = PyMongo(app)

@app.route("/")
def index():
    return "Hello from Flask!"


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

@app.route("/dashboard")
def home():
    return render_template("dashboard.html")


# Run Flask if the __name__ variable is equal to __main__
if __name__ == "__main__":
    app.run()