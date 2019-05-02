#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from peewee import *
import json
from .database.database import db
from .user import User
from .game import Game, create_game, get_game
from .piece import delete_pieces_by_game_id

class Room(Model):
    # idフィールドが暗黙に追加される
    game = ForeignKeyField(Game, index=True, unique=True, column_name='game_id')
    created_user = ForeignKeyField(User, backref='rooms', column_name='created_user_id') # 必要になる個所はないが念のため保存する
    created_user_name = CharField()
    status = CharField(default='waiting')

    class Meta:
            database = db

    def to_dict(self):
        return {
            "room_id": self.id
            , "status" : self.status
            , "game_id" : self.game.id
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

    # ルームへの入退場が発生したとき適切な処理を行う
    def on_after_entry_count_change(self):
        if self.is_full():
            self.on_full()
        elif self.is_empty():
            self.on_empty()
        else:
            self.on_exit_user()

    def on_full(self):
        if self.status != "waiting":
            return
        # 満員になったらplayingにする
        self.status = "playing"
        self.save()
        entries = [p for p in self.player_entries]
        self.game.start_game(entries)

    def on_empty(self):
        # 空になったらルームと関連する情報をすべて削除する
        delete_pieces_by_game_id(self.game.id)
        self.delete_instance()
        self.game.delete_instance()

    def on_exit_user(self):
        if self.status != "playing":
            return
        # ゲーム開始後、離脱が発生したら残ったプレイヤーが勝ちとする
        if len(self.player_entries) == 1:
            for entry in self.player_entries:
                self.game.win(entry.user.id)

def init_room():
    db.create_tables([Room])

def create_room(user):
    try:
        game = create_game()
        if game is None:
            return None
        room = Room.create(created_user=user, created_user_name=user.name, game=game)
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
