#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from peewee import *
from .database.database import db
from .game import Game
from .user import User

class Piece(Model):
    # idフィールドが暗黙に追加される
    game_id = ForeignKeyField(Game, backref="pieces")
    owner_id = ForeignKeyField(User, backref="pieces")
    x = IntegerField()
    y = IntegerField()
    kind = CharField() # good, evil

    class Meta:
            database = db

def init_piece():
    db.create_tables([Piece])

# TODO:bulk insertで生成したほうが効率は良い
def create_piece(game_id, owner_id, x, y, kind):
    try:
        piece = Piece.create(
            game_id=game_id
            , owner_id=owner_id
            , x=x
            , y=y
            , kind=kind
        )
        return piece
    except Exception as e:
        print(type(e))
        print(e)
    return None
