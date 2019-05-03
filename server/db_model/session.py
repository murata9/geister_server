#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from peewee import *
import jwt
import datetime
from .database.database import db

class Session(Model):
    # idフィールドが暗黙に追加される
    user_id = IntegerField() # TODO:外部キーにしてもよいかも
    is_valid = BooleanField(default=True)
    # TODO:期限

    class Meta:
        database = db

def init_session():
    db.create_tables([Session])

# return session, access_token
def create_session(user_id):
    try:
        session = Session.create(user_id=user_id)
        token = create_access_token(session.id)
        return session, token
    except IntegrityError as e: # peewee.IntegrityError
        # DuplicateEntry
        return None, None
    except Exception as e:
        print(type(e))
        print(e)
        return None, None

def get_session(session_id):
    try:
        session = Session.get(id=session_id, is_valid=True)
        return session
    except Session.DoesNotExist:
        return None
    except Exception as e:
        print(type(e))
        print(e)
    return None

def disable_session(session_id):
    try:
        session = Session.get(id=session_id)
        session.is_valid = False
        session.save()
        return True
    except Exception as e:
        print(type(e))
        print(e)
    return False

def get_secret_key():
    return "hogehoge" # TODO:環境変数から読み込むなど、コードに埋め込まないようにする

def create_access_token(session_id):
    # セッションの有効期限(1時間) # TODO:有効期限を管理する方法は、時間を後から更新できるように検討し直した方が良い
    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    encoded = jwt.encode(
        {"user_session_id": session_id, "exp":exp},
        get_secret_key(),
        algorithm='HS256'
    )
    token = encoded.decode('utf-8')
    return token

# return user_id, error_message
def decode_access_token(token):
    try:
        decoded = jwt.decode(token, get_secret_key(), algorithms='HS256')
        session_id = decoded['user_session_id']
        session = get_session(session_id)
        if session is None:
            return None, "Session is deleted"
        return session.user_id, None
    except jwt.DecodeError:
        return None, "token is not valid"
    except jwt.ExpiredSignatureError:
        return None, "token is expired"
