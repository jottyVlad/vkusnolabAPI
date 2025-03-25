from mongoengine import *

class Cart(Document):
    user_id = fields.StringField(required=True)
    count_in_grams = fields.IntField()
    ingredient_id = fields.StringField(required=True)

class Views(Document):
    user_id = fields.StringField(required=True)
    recipe_id = fields.StringField(required=True)