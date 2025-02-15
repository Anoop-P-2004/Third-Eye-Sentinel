from flask import Flask,request,jsonify
from flask_bcrypt import Bcrypt
import firebase_admin
from firebase_admin import credentials,firestore,db

app=Flask(__name__)
bcrypt=Bcrypt(app)

cred = credentials.Certificate('backend/service_key.json')
firebase_admin.initialize_app(cred)
db=firestore.client()

def hash_password(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

def check_password(hashed_password,plain_password):
    return bcrypt.check_password_hash(hashed_password,plain_password)

@app.route("/signup",methods=['POST'])
def signup():
    data=request.get_json()
    username=data["username"]
    password=data["password"]
    new_password=hash_password(password)

    #checking if username already exists..
    doc=db.collection("users").document(username).get()
    if doc.exists:
        return jsonify({"flag":0,"message":"Username already exists.."})
    else:
        user_data={
            "username": username,
            "password": new_password,
            "role":"user"
        }
        db.collection("users").document(username).set(user_data)
        return jsonify({"flag":1,"message":"Account created successfully..."})

if __name__=="__main__":
    app.run(debug=True)
