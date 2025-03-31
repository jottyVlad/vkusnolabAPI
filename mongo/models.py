from mongoengine import fields, Document

class Views(Document):
    user_id = fields.StringField(required=True)
    recipe_id = fields.StringField(required=True)