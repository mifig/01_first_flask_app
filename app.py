import os
import secrets

from flask import Flask
from flask_smorest import Api
from flask_jwt_extended import JWTManager

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint

from db import db
import models

def create_app(db_url=None):
  # __name__ gives each file a unique name:
  app = Flask(__name__)

  app.config["PROPAGATE_EXCEPTIONS"] = True
  app.config["API_TITLE"] = "Stores REST API"
  app.config["API_VERSION"] = "v1"
  app.config["OPENAPI_VERSION"] = "3.0.3"
  app.config["OPENAPI_URL_PREFIX"] = "/"
  app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
  app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
  app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
  app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
  app.config["JWT_SECRET_KEY"] = "183341453026157660730873959897278630925"

  jwt = JWTManager(app)

  @jwt.expired_token_loader
  def expired_token_callback(jwt_header, jwt_payload):
    return (jsonify({"message": "The token has expired.", "error": "token_expired"}), 401)
  
  @jwt.invalid_token_loader
  def invalid_token_callback(error):
    return (jsonify({"message": "Signature verification failed.", "error": "invalid_token"}), 401)
  
  @jwt.unauthorized_loader
  def missing_token_callback(error):
    return (jsonify({"description": "Request does not contain an access token.", "error": "authorization_required"}), 401)

  db.init_app(app)

  api = Api(app)

  with app.app_context():
    db.create_all()

  # Importing blueprints:
  api.register_blueprint(ItemBlueprint)
  api.register_blueprint(StoreBlueprint)
  api.register_blueprint(TagBlueprint)
  api.register_blueprint(UserBlueprint)

  return app