#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from peewee import *
from .database.database import db
from .user import User
from .room import Room, get_room

class PlayerEntry(Model):
    # idフィールドが暗黙に追加される
    user = ForeignKeyField(User, column_name='user_id', unique=True)
    room = ForeignKeyField(Room, backref='player_entries', column_name='room_id')

    class Meta:
            database = db

def init_player_entry():
    db.create_tables([PlayerEntry])

def create_player_entry(user, room):
    try:
        player_entry = PlayerEntry.create(user=user, room=room)
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
        room = player_entry.room
        player_entry.delete_instance()
        room.on_after_entry_count_change()
        return True
    except Exception as e:
        print(type(e))
        print(e)
    return False

