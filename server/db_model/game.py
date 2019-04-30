#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from peewee import *
from .database.database import db

class Game(Model):
    # idフィールドが暗黙に追加される
    status = CharField(default='prepare')

    class Meta:
            database = db

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
