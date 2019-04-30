#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import Blueprint, request, abort, Response
from flask_api import status
import json

from db_model.user import get_user
from db_model.room import create_room, get_room, get_rooms
from db_model.player_entry import create_player_entry, delete_player_entry
from .utility.login_required import login_required

room_app = Blueprint('room_app', __name__)

# ルーム一覧取得
@room_app.route('/api/rooms', methods=['GET'])
def rooms():
    rooms = get_rooms()
    if rooms is None:
        abort(500, "Rooms Get Error!")
    result = []
    for room in rooms:
        result.append( room.to_dict() )
    return json.dumps({ "rooms": result })
    # return '''{ "rooms": [ {
    #             "room_id":3
    #             , "status" : "waiting"
    #             , "game_id":33
    #             , "owner_name" : "owner"
    #             , "created_at" : ""
    #             , "updated_at" : ""
    #        } ] }'''

# ルーム作成
@room_app.route('/api/rooms', methods=['POST'])
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
    entry = create_player_entry(user_id, room.id)
    if entry is None:
        print("player entry create failure")
        abort(500, "player entry create failure")
    result = {
        "room_id" : room.id
        , "player_entry_id" : entry.id
    }
    return json.dumps(result)
    # '''{ "room_id":3, "player_entry_id":1 }'''

# ルーム入室
@room_app.route('/api/rooms/<int:room_id>/player_entries', methods=['POST'])
@login_required
def player_entried(user_id, room_id):
    room = get_room(room_id)
    if room is None:
        print("Room is Not Found")
        abort(400, "Room is Not Found")

    # ルームが満員になっていないかチェック
    if room.is_full():
        return Response('''{"message":"Room is Full"}''', status.HTTP_400_BAD_REQUEST)

    entry = create_player_entry(user_id, room.id)
    if entry is None:
        print("player entry create failure")
        abort(500, "player entry create failure")
    result = {
        "player_entry_id" : entry.id
        , "room_id" : room.id
        , "user_id" : user_id # 用途不明
    }
    return json.dumps(result)
    # return '''{
    #             "player_entry_id":5
    #             , "room_id":45
    #             , "user_id":99
    #        }'''

# ルーム退室
@room_app.route('/api/player_entries/<int:entry_id>', methods=['DELETE'])
@login_required
def exit_room(user_id, entry_id):
    result = delete_player_entry(entry_id)
    if not result:
        abort(500, "exit failure")
    return ""

# ルーム状態取得
@room_app.route('/api/rooms/<int:room_id>', methods=['GET'])
def room(room_id):
    room = get_room(room_id)
    if room is None:
        abort(400, "Room Not Found")
    result = {
        "room_id": room.id
        , "status" : room.status
        , "game_id" : room.game_id
        , "owner_name" : room.created_user_name
    }
    return room.to_json()
    # return '''{
    #             "room_id":3
    #             , "status" : "playing"
    #             , "game_id":33
    #             , "owner_name" : "owner"
    #             , "created_at" : ""
    #             , "updated_at" : ""
    #        }'''
