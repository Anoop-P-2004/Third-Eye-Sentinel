import os
from dotenv import load_dotenv
import jwt
from flask import Flask,request,jsonify,render_template,g
from flask_bcrypt import Bcrypt
import firebase_admin
from firebase_admin import credentials,firestore,db
from functools import wraps

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'frontend', 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'frontend', 'static')

app=Flask(__name__,template_folder=TEMPLATE_DIR,static_folder=STATIC_DIR)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') #secret key is stored in .env file
bcrypt=Bcrypt(app)

cred = credentials.Certificate('backend/service_key.json')
firebase_admin.initialize_app(cred)
db=firestore.client()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('Authorization')
        if not token:
            return render_template("error.html",msg="Please login first"), 401
        try:
            decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            g.user = decoded_token
        except jwt.InvalidTokenError:
            return render_template("error.html",msg="invalid token"), 401
        return f(*args, **kwargs)
    return decorated

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(hashed_password,plain_password):
    return bcrypt.check_password_hash(hashed_password,plain_password)

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/admin")
@token_required
def admin():
    if g.user["role"]=="admin":
        return render_template("admin.html")
    else:
        return render_template("error.html",msg="Only admins can view this..")

@app.route("/demo")
@token_required
def demo():
    if g.user["role"]=="admin":
        return render_template("demo.html")
    else:
        return render_template("error.html",msg="Only admins can view this..")

@app.route("/signup/submit",methods=['POST'])
def signup_submit():
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

@app.route("/manage_user")
@token_required
def manage_user():
    if g.user["role"]=="admin":
        docs=db.collection("users").stream()
        users=[{"username":doc.id,"role":doc.to_dict().get('role')} for doc in docs]
        return render_template("manage_user.html",users=users)
    else:
        return render_template("error.html",msg="Only admins can view this..")

@app.route("/manage_cameras")
@token_required
def manage_cameras():
    if g.user["role"]=="admin":
        return render_template("manage_cameras.html")
    else:
        return render_template("error.html",msg="Only admins can view this..")

@app.route("/manage_admin")
@token_required
def manage_admin():
    if g.user["role"]=="admin":
        return render_template("manage_admin.html")
    else:
        return render_template("error.html",msg="Only admins can view this..")


@app.route("/view_report")
@token_required
def view_report():
        return render_template("view_report.html")

@app.route("/manage_user/delete_user")
@token_required
def delete_user():
    if g.user["role"]=="admin":
        username=request.args.get("username")
        db.collection("users").document(username).delete()
        return jsonify({"flag":0,"message":"Deleted User Successfully..."})
    else:
        return render_template("error.html",msg="Only admins can view this..")
    

@app.route("/manage_user/make_admin")
@token_required
def make_admin():
    if g.user["role"]=="admin":
        username=request.args.get("username")
        db.collection("users").document(username).update({"role":"admin"})
        return jsonify({"flag":0})
    else:
        return render_template("error.html",msg="Only admins can view this..")
    

if __name__=="__main__":
    app.run(debug=True)
