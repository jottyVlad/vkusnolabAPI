from django.shortcuts import render
from pymongo import MongoClient

def get_db_handle():
    """get mongoDB"""
    client = MongoClient(host="mongodb://localhost", port=27017)
    db_handle = client.djangoTutorial.to_do_item
    return db_handle
