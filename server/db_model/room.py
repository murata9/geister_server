#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from peewee import *
from .database.database import db
from .user import User

class Room(Model):
    # idフィールドが暗黙に追加される
    # game_id = IntegerField(index=True, unique=True)
    game_id = IntegerField(index=True) # 不便なので一時的にunique制約を外す
    created_user_id = ForeignKeyField(User, backref='rooms') # 必要になる個所はないが念のため保存する
    created_user_name = CharField()
    status = CharField(default='waiting')


    class Meta:
            database = db

def init_room():
    db.create_tables([Room])

def create_room(user):
    try:
        game_id = 1 # TODO
        room = Room.create(created_user_id=user.id, created_user_name=user.name, game_id=game_id)
        return room
    except IntegrityError as e: # peewee.IntegrityError
        # DuplicateEntry
        print ("Room Duplicate Entry")
        return None
    except Exception as e:
        print(type(e))
        print(e)
        return None

def get_room(room_id):
    try:
        room = Room.get(Room.id==room_id)
        return room
    except Room.DoesNotExist:
        return None
    except Exception as e:
        print(type(e))
        print(e)
    return None

def get_rooms():
    try:
        rooms = Room.select().limit(20)
        return rooms
    except Exception as e:
        print(type(e))
        print(e)
    return None
