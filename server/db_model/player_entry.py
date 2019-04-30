#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from peewee import *
from .database.database import db
from .room import Room, get_room

class PlayerEntry(Model):
    # idフィールドが暗黙に追加される
    user_id = IntegerField() # TODO:unique?
    room_id = ForeignKeyField(Room, backref='player_entries')

    class Meta:
            database = db

def init_player_entry():
    db.create_tables([PlayerEntry])

def create_player_entry(user_id, room_id):
    try:
        room = get_room(room_id)
        if room is None:
            print ("Room Not Found! room_id:" + str(room_id))
            return None
        player_entry = PlayerEntry.create(user_id=user_id, room_id=room_id)
        room.on_after_entry_count_change()
        return player_entry
    except Exception as e:
        print(type(e))
        print(e)
        return None

def get_player_entry(player_entry_id):
    try:
        player_entry = PlayerEntry.get(PlayerEntry.id==player_entry_id)
        return player_entry
    except PlayerEntry.DoesNotExist:
        return None
    except Exception as e:
        print(type(e))
        print(e)
    return None

def delete_player_entry(player_entry_id):
    try:
        player_entry = get_player_entry(player_entry_id)
        if player_entry is None:
            return False
        room_id = player_entry.room_id
        player_entry.delete_instance()
        # 念のためルームがなくてもエラーにしないようにしておく
        room = get_room(room_id)
        if room is None:
            print ("Room Not Found! room_id:" + str(room_id))
        else:
            room.on_after_entry_count_change()
        return True
    except Exception as e:
        print(type(e))
        print(e)
    return False

