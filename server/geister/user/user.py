#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from peewee import *
from ..database.database import db

class User(Model):
    # idフィールドが暗黙に追加される
    name = CharField(index=True, unique=True)
    password = CharField()

    class Meta:
            database = db

def init_user():
    db.create_tables([User])

def create_user(user_name, password):
    try:
        user = User.create(name=user_name, password=password)
        return user
    except IntegrityError as e: # peewee.IntegrityError
        # DuplicateEntry
        return None
    except Exception as e:
        print(type(e))
        print(e)
        return None

def get_user(user_name, password):
    try:
        user = User.get(User.name==user_name, User.password==password)
        return user
    except User.DoesNotExist:
        return None
    except Exception as e:
        print(type(e))
        print(e)
    return None

