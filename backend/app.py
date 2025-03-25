import os
import threading
from dotenv import load_dotenv
import jwt
from flask import Flask,request,jsonify,render_template,g
from flask_bcrypt import Bcrypt
import firebase_admin
from firebase_admin import credentials,firestore,db,storage
from functools import wraps
from camera import startapplication
from lime_explainer import LIMEExplainer
import base64
import cv2
import uuid
import datetime
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend before importing pyplot
import matplotlib.pyplot as plt

load_dotenv()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'frontend', 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'frontend', 'static')

app=Flask(__name__,template_folder=TEMPLATE_DIR,static_folder=STATIC_DIR)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') #secret key is stored in .env file
bcrypt=Bcrypt(app)

cred = credentials.Certificate('backend/service_key.json')
firebase_admin.initialize_app(cred, {"storageBucket": "third-eye-sentinel.firebasestorage.app"})
db=firestore.client()
bucket = storage.bucket()

class LIMEExplainerThread(threading.Thread):
    def __init__(self, frame):
        super().__init__()
        self.frame = frame

    def run(self):
        # Generate a unique filename
        unique_id = str(uuid.uuid4())[:8]
        filename = f"lime_{unique_id}.png"
        local_path = f"lime_images/{filename}"

        # Run LIME explanation
        explainer = LIMEExplainer(self.frame)
        fig = explainer.explain()
        fig.savefig(local_path) 

        # Upload to Firebase Storage
        blob = bucket.blob(f"lime_images/{filename}")
        blob.upload_from_filename(local_path)
        blob.make_public()

        # Get public URL
        image_url = blob.public_url

        accident_data = {
            "id":unique_id,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S"),
            "createdAt": datetime.now(),
            "image_url": image_url
        }
        db.collection("Accident").document(unique_id).set(accident_data)
        os.remove(local_path)


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
            "role":user["role"],
            "exp": datetime.utcnow() + timedelta(hours=1)
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
        docs=db.collection("cameras").stream()
        cameras=[{"name":doc.id} for doc in docs]
        return render_template("manage_cameras.html",cameras=cameras)
    else:
        return render_template("error.html",msg="Only admins can view this..")

@app.route("/manage_cameras/add_camera",methods=["POST"])
@token_required
def add_camera():
    if g.user["role"]=="admin":
        data=request.get_json()
        cameraName=data["name"]
        camera={
            "name": cameraName,
            "location":"Palakkad"
        }
        db.collection("cameras").document(cameraName).set(camera)
        return jsonify({"flag":0,"message":"Camera added successfully..."})
       
    else:
        return render_template("error.html",msg="Only admins can view this..")

@app.route("/manage_cameras/delete_camera",methods=["POST"])
@token_required
def delete_camera():
    if g.user["role"]=="admin":
        data=request.get_json()
        cameraName=data["name"]
        db.collection("cameras").document(cameraName).delete()
        return jsonify({"flag":0,"message":"Camera deleted successfully..."})
       
    else:
        return render_template("error.html",msg="Only admins can view this..")

@app.route("/manage_admin")
@token_required
def manage_admin():
    if g.user["role"]=="admin":
        docs=db.collection("users").where("role","==","admin").stream()
        users=[{"username":doc.id,"role":doc.to_dict().get('role')} for doc in docs]
        return render_template("manage_admin.html",users=users)
    else:
        return render_template("error.html",msg="Only admins can view this..")

@app.route("/manage_admin/delete_admin")
@token_required
def delete_admin():
    if g.user["role"]=="admin":
        username=request.args.get("username")
        db.collection("users").document(username).delete()
        return jsonify({"flag":0,"message":"Deleted Admin Successfully..."})
    else:
        return render_template("error.html",msg="Only admins can view this..")

@app.route("/manage_admin/remove_admin")
@token_required
def remove_admin():
    if g.user["role"]=="admin":
        username=request.args.get("username")
        db.collection("users").document(username).update({"role":"user"})
        return jsonify({"flag":0})
    else:
        return render_template("error.html",msg="Only admins can view this..")

@app.route("/view_report")
@token_required
def view_report():
        docs = db.collection("Accident").order_by("createdAt", direction=firestore.Query.DESCENDING).stream()
        accidents=[{"id":doc.id} for doc in docs]
        return render_template("view_report.html",reports=accidents)
@app.route("/view_report/get_details")
@token_required
def get_details():
        accident_id=request.args.get("id")
        doc = db.collection("Accident").document(accident_id).get()
        doc_dict = doc.to_dict()
        return jsonify(doc_dict)

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
    
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
@token_required
def upload_video():
    if g.user["role"]=="admin":
        if 'video' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        video_file = request.files['video']
        
        if video_file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        video_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
        video_file.save(video_path)

        # Call the function from camera.py
        pred, frame = startapplication(video_path)

        if frame is None:
            return jsonify({"message": "No accident detected", "frame": None})

        lime_thread = LIMEExplainerThread(frame)
        lime_thread.start()

        # Encode frame as JPEG
        #_, buffer = cv2.imencode('.jpg', frame)
        #encoded_frame = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            "message": "Accident detected",
            "pred": pred
        })
    else:
        return render_template("error.html",msg="Only admins can view this..")


if __name__=="__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)