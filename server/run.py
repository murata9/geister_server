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
from geister.user.user import init_user, create_user, get_user, login_user
from geister.room.room import init_room, create_room, get_room, get_rooms

app = Flask(__name__)

def init_logger():
    logger = logging.getLogger('peewee')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

def init_database():
    init_user()
    init_room()

# 設定確認
# print(app.config)

app.config['ENV'] = "development"

@app.route('/')
def hello_world():
    return '<html><body><h1>sample</h1></body></html>'

gen_session_id = 0
valid_sessions = set()
def generate_session_id():
    global gen_session_id
    gen_session_id = gen_session_id + 1
    valid_sessions.add(gen_session_id)
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
            if session_id not in valid_sessions:
                print("token is deleted")
                # 開発中はサーバーrestart時に面倒なのでセッションチェックを切っておく
                # abort(400, "Token is deleted.")
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
    user = login_user(name, password)
    if user is None:
        abort(400, "Login Failure")

    user_session_id = generate_session_id()

    # セッションの有効期限(1時間) # TODO:有効期限を管理する方法は、時間を後から更新できるように検討し直した方が良い
    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    encoded = jwt.encode({"user_session_id": user_session_id, "user_id":user.id, "exp":exp},
      get_secret_key(),
      algorithm='HS256'
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

# ログアウト
# TODO:ログアウト時はセッションの期限切れでも通してもよいかも？
@app.route('/api/user_sessions/<int:session_id>', methods=['DELETE'])
@login_required
def delete_session(user_id, session_id):
    print("delte session_id:" + str(session_id))
    valid_sessions.discard(session_id)
    return ""

# ルーム一覧取得
@app.route('/api/rooms', methods=['GET'])
def rooms():
    rooms = get_rooms()
    if rooms is None:
        abort(500, "Rooms Get Error!")
    result = []
    for room in rooms:
        result.append({
            "room_id": room.id
            , "status": room.status
            , "game_id": room.game_id
            , "owner_name": room.created_user_name
        })

    return json.dumps({ "rooms": result })
    # return '''{ "rooms": [ {
    #             "room_id":3
    #             , "status" : "waiting"
    #             , "game_id":33
    #             , "owner_name" : "owner"
    #             , "created_at" : ""
    #             , "updated_at" : ""
    #        } ] }'''

@app.route('/api/rooms', methods=['POST'])
@login_required
def create_new_room(user_id):
    user = get_user(user_id)
    if user is None:
        print ("user not found")
        abort(500, "user not found")
    room = create_room(user)
    if room is None:
        print("room create failure")
        abort(500, "room create failure")
    result = {
        "room_id" : room.id
        , "player_entry_id" : 99 # TODO
    }
    return json.dumps(result)
    # '''{ "room_id":3, "player_entry_id":1 }'''

@app.route('/api/rooms/<int:room_id>/player_entries', methods=['POST'])
@login_required
def player_entried(user_id, room_id):
    print ("room_id:" + str(room_id))
    return '''{
                "player_entry_id":5
                , "room_id":45
                , "user_id":99
           }'''

@app.route('/api/player_entries/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_player_entry(user_id, entry_id):
    return ""

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

