#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from peewee import *
from .database.database import db
from .game import Game
from .user import User

class Piece(Model):
    # idフィールドが暗黙に追加される
    game = ForeignKeyField(Game, backref="pieces", column_name="game_id")
    owner = ForeignKeyField(User, backref="pieces", column_name="owner_id")
    x = IntegerField()
    y = IntegerField()
    kind = CharField() # good, evil
    captured = BooleanField(default=False)

    class Meta:
            database = db
            # 複合インデックスの指定
            indexes = (
                (("game_id", "x", "y"), False), # 取られた場合があるので、Unique=False
                (("game_id", "owner_id", "captured"), False),
            )

    def to_dict(self, user_id):
        # note:取られていない駒は所有者しか種別が分からない
        is_owner = user_id == self.owner.id
        show_kind = is_owner or self.captured
        return {
            "piece_id" : self.id
            , "point_x" : self.x
            , "point_y" : self.y
            , "owner_user_id" : self.owner.id
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
def create_piece(game, owner, x, y, kind):
    try:
        piece = Piece.create(
            game=game
            , owner=owner
            , x=x
            , y=y
            , kind=kind
        )
        return piece
    except Exception as e:
        print(type(e))
        print(e)
    return None

def delete_pieces_by_game_id(game_id):
    try:
        query = Piece.delete().where(Piece.game==game_id)
        query.execute()
        return True
    except Exception as e:
        print(type(e))
        print(e)
    return False

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
            Piece.game==game_id,
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

def get_alive_piece_by_user_id(game_id, user_id):
    try:
        pieces = Piece.select().where(
            Piece.game==game_id,
            Piece.owner==user_id,
            Piece.captured==False)
        return pieces
    except Exception as e:
        print(type(e))
        print(e)
    return None
