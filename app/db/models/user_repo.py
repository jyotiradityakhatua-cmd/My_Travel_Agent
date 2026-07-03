from app.db.models.user import User


def get_user_by_username(db, username):
    doc = db["users"].find_one({"username": username})
    if not doc:
        return None
    return User.from_doc(doc)


def create_user(db, username, password):
    user = User(username=username, password=password)
    db["users"].insert_one(user.to_doc())
    return user