#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from peewee import *
import json
from .database.database import db
from .user import User
from .game import create_game, get_game

class Room(Model):
    # idフィールドが暗黙に追加される
    # game_id = IntegerField(index=True, unique=True)
    game_id = IntegerField(index=True) # 不便なので一時的にunique制約を外す
    created_user_id = ForeignKeyField(User, backref='rooms') # 必要になる個所はないが念のため保存する
    created_user_name = CharField()
    status = CharField(default='waiting')

    class Meta:
            database = db

    def to_dict(self):
        return {
            "room_id": self.id
            , "status" : self.status
            , "game_id" : self.game_id
            , "owner_name" : self.created_user_name
        }

    def to_json(self):
        return json.dumps( self.to_dict() )

    def get_entry_count(self):
        count = len(self.player_entries) # player_entry.pyでbackrefが定義されている
        return count

    def is_full(self):
        return self.get_entry_count() >= 2

    def is_empty(self):
        return self.get_entry_count() == 0 # TODO:もし観戦機能も作るなら観戦者も考慮する

    def on_after_entry_count_change(self):
        if self.is_full():
            if self.status == "waiting":
                # 満員になったらplayingにする
                self.status = "playing"
                self.save()
                game = get_game(self.game_id)
                if game is None:
                    print("[logic error]game not found! game_id:" + str(self.game_id))
                    return
                entries = [p for p in self.player_entries]
                game.start_game(entries)
        elif self.is_empty():
            # 空になったらルームを削除する
            self.delete_instance()
        elif self.status == "playing":
            # ゲーム開始後、離脱が発生したらwaitingに戻す(仮) TODO:敗北にする
            self.status = "waiting"
            self.save()

def init_room():
    db.create_tables([Room])

def create_room(user):
    try:
        game = create_game()
        if game is None:
            return None
        room = Room.create(created_user_id=user.id, created_user_name=user.name, game_id=game.id)
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
