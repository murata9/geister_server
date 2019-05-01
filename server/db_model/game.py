#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import random
from peewee import *
from .database.database import db
from define.define import PIECE_MAX_COUNT_BY_PLAYER

class Game(Model):
    # idフィールドが暗黙に追加される
    first_mover_user_id = IntegerField(default=0)
    last_mover_user_id = IntegerField(default=0)
    turn_count = IntegerField(default=1)
    winner_user_id = IntegerField(default=0)
    status = CharField(default='preparing')

    class Meta:
            database = db

    def get_turn_mover_user_id(self):
        if self.turn_count % 2 == 1:
            return self.first_mover_user_id
        else:
            return self.last_mover_user_id

    def start_game(self, player_entries):
        # ゲーム開始時にランダムにスタートプレイヤーを決定する
        if len(player_entries) != 2:
            print("Invalid Player Entries len:" + str(len(player_entries)))
            return
        r = random.randint(0, 1)
        self.first_mover_user_id = player_entries[r].user_id
        self.last_mover_user_id = player_entries[1-r].user_id
        self.save()

    def on_after_preparing_one_user(self):
        if self.status != "preparing":
            return
        if len(self.pieces) >= 2 * PIECE_MAX_COUNT_BY_PLAYER:
            self.status = "playing"
            self.save()

def init_game():
    db.create_tables([Game])

def create_game():
    try:
        game = Game.create()
        return game
    except Exception as e:
        print(type(e))
        print(e)
        return None

def get_game(game_id):
    try:
        game = Game.get(Game.id==game_id)
        return game
    except Game.DoesNotExist:
        return None
    except Exception as e:
        print(type(e))
        print(e)
    return None
