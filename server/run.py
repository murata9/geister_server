#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import *
from peewee import *

import datetime
import jwt
import functools

import logging
import json

from geister.piece.piece import Piece
from geister.user.user import init_user, create_user, get_user

app = Flask(__name__)

def init_logger():
    logger = logging.getLogger('peewee')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

def init_database():
    init_user()

# 設定確認
# print(app.config)

app.config['ENV'] = "development"

@app.route('/')
def hello_world():
    return '<html><body><h1>sample</h1></body></html>'

gen_session_id = 0
def generate_session_id():
    global gen_session_id
    gen_session_id = gen_session_id + 1
    return gen_session_id

def login_required(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        header = request.headers.get('Authorization')
        _, token = header.split("=")
        token = str(token).strip("\"")
        try:
            decoded = jwt.decode(token, get_secret_key(), algorithms='HS256')
            user_id = decoded['user_id']
            print ("user_id:" + str(user_id))
            session_id = decoded['user_session_id']
        except jwt.DecodeError:
           print("token is not valid")
           abort(400, "Token is not valid.")
        except jwt.ExpiredSignatureError:
           print("token is expired")
           abort(400, "Token is expired.")

        return method(user_id, *args, **kwargs)
    return wrapper



# ユーザー新規登録
@app.route('/api/users', methods=['POST'])
def users():
    dic = request.json
    name = dic[u"name"]
    password = dic[u"password"]
    user = create_user(name, password)

    if user is None:
        # 既に作成済みのユーザー名
        abort(400, "Existed UserName")

    print ("username:" + str(user.name))
    print ("userid:" + str(user.id))
    result = {
                "user_id" : user.id,
                "name" : user.name
            }
    print (json.dumps(result))

    return json.dumps(result)
    # return '''{
    #             , "user_id":33
    #             , "user_name":"hogehoge"
    #        }'''


def get_secret_key():
  return "hogehoge" # TODO

# ログイン
@app.route('/api/user_sessions', methods=['POST'])
def user_sessions():
    dic = request.json
    name = dic[u"name"]
    password = dic[u"password"]
    user = get_user(name, password)
    if user is None:
        abort(400, "Login Failure")

    user_session_id = generate_session_id()

    # セッションの有効期限(1時間)
    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    encoded = jwt.encode({"user_session_id": user_session_id, "user_id":user.id, "exp":exp},
      get_secret_key(),
      algorithm=['HS256']
      )
    token = encoded.decode('utf-8')

    print ("token:" + str(token))

    result = {
                "user_session_id": user_session_id,
                "access_token": token,
                "user_id" : user.id
            }
    return json.dumps(result)

    # return '''{
    #             "user_session_id":3
    #             , "access_token":""
    #             , "user_id":33
    #        }'''

@app.route('/api/rooms', methods=['GET'])
def rooms():
    return '''{ "rooms": [ {
                "room_id":3
                , "status" : "waiting" 
                , "game_id":33
                , "owner_name" : "owner"
                , "created_at" : ""
                , "updated_at" : ""
           } ] }'''

@app.route('/api/rooms/<int:room_id>/player_entries', methods=['POST'])
@login_required
def player_entried(user_id, room_id):
    print ("room_id:" + str(room_id))
    return '''{
                "player_entry_id":5
                , "room_id":45
                , "user_id":99
           }'''

@app.route('/api/rooms/<int:room_id>', methods=['GET'])
def room(room_id):
    return '''{
                "room_id":3
                , "status" : "playing" 
                , "game_id":33
                , "owner_name" : "owner"
                , "created_at" : ""
                , "updated_at" : ""
           }'''

@app.route('/api/game/<int:game_id>', methods=['GET'])
def game(game_id):
    return '''{
                "room_id":3
                , "status" : "playing" 
                , "game_id":33
                , "owner_name" : "owner"
                , "created_at" : ""
                , "updated_at" : ""
           }'''

if __name__ == '__main__':
    init_logger()
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
    # app.run(host='0.0.0.0', port=5000)

