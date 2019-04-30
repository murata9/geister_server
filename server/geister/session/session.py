#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from peewee import *
from ..database.database import db

class Session(Model):
    # idフィールドが暗黙に追加される
    user_id = IntegerField() # TODO:外部キーにしてもよいかも
    # TODO:期限

    class Meta:
        database = db

def init_session():
    db.create_tables([Session])

def create_session(user_id):
    try:
        session = Session.create(user_id=user_id)
        return session
    except IntegrityError as e: # peewee.IntegrityError
        # DuplicateEntry
        return None
    except Exception as e:
        print(type(e))
        print(e)
        return None

def get_session(session_id):
    try:
        session = Session.get(id=session_id)
        return session
    except Session.DoesNotExist:
        return None
    except Exception as e:
        print(type(e))
        print(e)
    return None

