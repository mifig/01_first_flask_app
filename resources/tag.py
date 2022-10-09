# Blueprint to create routes specific to a resource(aka model) in different files
from flask_smorest import abort, Blueprint
# MethodView to inherit routes functionality:
from flask.views import MethodView
# To throw specific db errors:
from sqlalchemy.exc import SQLAlchemyError

# db imports sqlalchemy:
from db import db
# imports the models:
from models import TagModel, StoreModel, ItemModel
# Imports the schema validations (marshmallow):
from schemas import TagSchema, ItemTagSchema

# Creates the blueprint:
blp = Blueprint("tags", __name__, description="Operations on tags")

@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
  @blp.response(200,TagSchema(many=True))
  def get(self, store_id):
    store = StoreModel.query.get_or_404(store_id)
    return store.tags.all()

  @blp.arguments(TagSchema)
  @blp.response(201, TagSchema)
  def post(self, data, store_id):
    # if (TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == data["name"])).first():
    #   abort(400, message="A tag with that name already exists for the store.")
    
    tag = TagModel(**data, store_id = store_id)

    try:
      db.session.add(tag)
      db.session.commit()
    except SQLAlchemyError as e:
      abort(500, message=str(e))

    return tag

@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagToItem(MethodView):
  @blp.response(201, TagSchema)
  def post(self, item_id, tag_id):
    item = ItemModel.query.get_or_404(item_id)
    tag = TagModel.query.get_or_404(tag_id)

    if item.store.id != tag.store.id:
      abort(400, message="Make sure item and tag belong to the same store.")

    item.tags.append(tag)

    try:
      db.session.add(item)
      db.session.commit()
    except SQLAlchemyError as e:
      abort(500, message=(str(e)))
    
    return tag
  
  @blp.response(200, ItemTagSchema)
  def delete(self, item_id, tag_id):
    item = ItemModel.query.get_or_404(item_id)
    tag = TagModel.query.get_or_404(tag_id)

    item.tags.remove(tag)

    try:
      db.session.add(item)
      db.session.commit()
    except SQLAlchemyError as e:
      abort(500, message=str(e))
    
    return  { "message": "Item removed from tag", 
              "item": item, 
              "tag": tag 
            }


@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
  @blp.response(200, TagSchema)
  def get(self, tag_id):
    tag = TagModel.query.get_or_404(tag_id)
    return tag
  
  @blp.response(202,
                description="Deletes a tag if no item is tagged with it.",
                example={ "message": "Tag deleted" }
                )
  @blp.alt_response(404, description="Tag not found.")
  @blp.alt_response(400, description="Returned if the tag is assigned to one or more items, in which case is not deleted.")
  def delete(self, tag_id):
    tag = TagModel.query.get_or_404(tag_id)

    if not tag.items:
      db.session.delete(tag)
      db.session.commit()
      return { "message": "Tag deleted" }
    
    abort(
      400,
      message="Could not delete tag. Make sure tag is not associated with any items."
    )
