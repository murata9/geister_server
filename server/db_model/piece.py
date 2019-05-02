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
    captured = BooleanField(default=False)

    class Meta:
            database = db
            indexes = (
                (("game_id", "x", "y"), False), # 取られた場合があるので、Unique=False
            )

    def to_dict(self, user_id):
        # note:取られていない駒は所有者しか種別が分からない
        is_owner = user_id == self.owner_id.id
        show_kind = is_owner or self.captured
        return {
            "piece_id" : self.id
            , "point_x" : self.x
            , "point_y" : self.y
            , "owner_user_id" : self.owner_id.id
            , "captured" : self.captured
            , "kind" : self.kind if show_kind else "unknown"
        }

    def update_position(self, x, y):
        self.x = x
        self.y = y
        self.save()

    def capture(self):
        self.captured = True
        self.save()

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

def get_piece(piece_id):
    try:
        piece = Piece.get(Piece.id==piece_id)
        return piece
    except Piece.DoesNotExist:
        return None
    except Exception as e:
        print(type(e))
        print(e)
    return None

def get_piece_by_pos(game_id, x, y):
    try:
        piece = Piece.get(
            Piece.game_id==game_id,
            Piece.x==x,
            Piece.y==y,
            Piece.captured==False)
        return piece
    except Piece.DoesNotExist:
        return None
    except Exception as e:
        print(type(e))
        print(e)
    return None
