@app.route("/manage_user")
@token_required
def manage_user():
    if g.user["role"]=="admin":
        docs=db.collection("users").stream()
        users=[{"username":doc.id,"role":doc.to_dict().get('role')} for doc in docs]
        return render_template("manage_user.html",users=users)
    else:
        return render_template("error.html",msg="Only admins can view this..")