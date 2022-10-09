from flask_smorest import abort, Blueprint
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from db import db
from models import StoreModel
from schemas import StoreSchema

# Blueprint: to divide API in multiple segments
blp = Blueprint("stores", __name__, description = "Operations on stores")

@blp.route("/store/<int:store_id>")
class Store(MethodView):
  @blp.response(200, StoreSchema)
  def get(self, store_id):
    store = StoreModel.query.get_or_404(store_id)
    return store

  def delete(self, store_id):
    store = StoreModel.query.get_or_404(store_id)
    db.session.delete(store)
    db.session.commit()
    return { "message": "Store deleted."}

@blp.route("/store")
class StoreList(MethodView):
  @blp.response(200, StoreSchema(many=True))
  def get(self):
    return StoreModel.query.all()

  @blp.arguments(StoreSchema)
  @blp.response(200, StoreSchema)
  def post(self, data):
    store = StoreModel(**data)

    try:
      db.session.add(store)
      db.session.commit()
    except IntegrityError:
      abort(400, message="A store with that name already exists.")
    except SQLAlchemyError:
      abort(500, message="An error occurred creating the store.")
    
    return store, 201