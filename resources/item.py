from flask_smorest import abort, Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema

# Blueprint: to divide API in multiple segments
blp = Blueprint("items", __name__, description = "Operations on items")

@blp.route("/item/<int:item_id>")
class Item(MethodView):
  @blp.response(200, ItemSchema)
  def get(self, item_id):
    item = ItemModel.query.get_or_404(item_id)
    return item

  def delete(self, item_id):
    item = ItemModel.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return { "message": "Item deleted."}
      
  @blp.arguments(ItemUpdateSchema)
  @blp.response(200, ItemSchema)
  def put(self, data, item_id):
    item = ItemModel.query.get(item_id)
    
    if item:
      item.price = data["price"]
      item.name = data["name"]
    else:
      item = ItemModel(id=item_id, **data)
    
    db.session.add(item)
    db.session.commit()

    return item

@blp.route("/item")
class ItemList(MethodView):
  @blp.response(200, ItemSchema(many=True))
  def get(self):
    return ItemModel.query.all()

  @jwt_required()
  @blp.arguments(ItemSchema)
  @blp.response(201, ItemSchema)
  def post(self, data):
    item = ItemModel(**data)
    
    try:
      db.session.add(item)
      db.session.commit()
    except SQLAlchemyError:
      abort(500, message="An error occurred while inserting the item.")
    
    return item, 201