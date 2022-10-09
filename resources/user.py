# Blueprint to create routes specific to a resource(aka model) in different files
from sqlite3 import IntegrityError
from flask_smorest import abort, Blueprint
# MethodView to inherit routes functionality:
from flask.views import MethodView
# Encoding password and saving that to the DB:
from passlib.hash import pbkdf2_sha256
# Create JWT:
from flask_jwt_extended import create_access_token

# db imports sqlalchemy:
from db import db
# imports the models:
from models import UserModel
# Imports the schema validations (marshmallow):
from schemas import UserSchema

# Creates the blueprint:
blp = Blueprint("Users", "users", description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
  @blp.arguments(UserSchema)
  def post(self, data):
    if UserModel.query.filter(UserModel.username == data["username"]).first():
      abort(409, message="Username already taken.")
    
    user = UserModel(
      username = data["username"],
      password = pbkdf2_sha256.hash(data["password"])
    )

    try:
      db.session.add(user)
      db.session.commit()

      return { "message": "User successfully created."}, 201
    except IntegrityError as e:
      abort(500, message=str(e))
    
@blp.route("/login")
class UserLogin(MethodView):
  @blp.arguments(UserSchema)
  def post(self, data):
    user = UserModel.query.filter(UserModel.username == data["username"]).first()

    if user and pbkdf2_sha256.verify(data["password"], user.password):
      access_token = create_access_token(identity=user.id)

      return { "access_token": access_token }

    abort(401, message="Invalid credentials.")

@blp.route("/user/<int:user_id>")
class User(MethodView):
  @blp.response(200, UserSchema)
  def get(self, user_id):
    return UserModel.query.get_or_404(user_id)
  
  def delete(self, user_id):
    user = UserModel.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()

    return { "message": "User deleted" }, 200