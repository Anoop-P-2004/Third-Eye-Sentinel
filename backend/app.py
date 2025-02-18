import os
from dotenv import load_dotenv
import jwt
from flask import Flask,request,jsonify,render_template
from flask_bcrypt import Bcrypt
import firebase_admin
from firebase_admin import credentials,firestore,db

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'frontend', 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'frontend', 'static')

app=Flask(__name__,template_folder=TEMPLATE_DIR,static_folder=STATIC_DIR)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') #secret key is stored in .env file
bcrypt=Bcrypt(app)

cred = credentials.Certificate('Third-Eye-Sentinel/backend/service_key.json')
firebase_admin.initialize_app(cred)
db=firestore.client()

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(hashed_password,plain_password):
    return bcrypt.check_password_hash(hashed_password,plain_password)

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/signup",methods=['POST'])
def signup():
    data=request.get_json()
    username=data["username"]
    password=data["password"]
    new_password=hash_password(password)

    #checking if username already exists..
    doc=db.collection("users").document(username).get()
    if doc.exists:
        return jsonify({"flag":1,"message":"Username already exists.."})
    else:
        user_data={
            "username": username,
            "password": new_password,
            "role":"user"
        }
        db.collection("users").document(username).set(user_data)
        return jsonify({"flag":0,"message":"Account created successfully..."})

@app.route("/login",methods=['POST'])
def login():
    data=request.get_json()
    username=data["username"]
    password=data["password"]
    query=db.collection("users").where("username","==",username).get()
    if query:
        user=query[0].to_dict()
    else:
        return jsonify({"flag":1,"message":"Username doesn't exists..."})
    if(check_password(user["password"],password)):
        payload={
            "username":user["username"],
            "role":user["role"]
        }
        token=jwt.encode(payload,app.config["SECRET_KEY"])
        return jsonify({"flag":0,"access-token":token,"role":user["role"]})
    else:
        return jsonify({"flag":1,"message":"Invalid credentials..."})


if __name__=="__main__":
    app.run(debug=True)
