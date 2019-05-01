#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import Blueprint, request, abort
import json

from define.define import PIECE_MAX_COUNT_BY_PLAYER
from db_model.user import get_user
from db_model.game import get_game
from db_model.piece import create_piece
from .utility.login_required import login_required
from .utility.error_response import make_error_response

game_app = Blueprint('game_app', __name__)

@game_app.route('/api/games/<int:game_id>', methods=['GET'])
def game(game_id):
    game = get_game(game_id)
    if game is None:
        return make_error_response(400, "game not found")
    result = {
        "game_id" : game.id
        , "turn_mover_user_id" : game.get_turn_mover_user_id()
        , "turn_count" : game.turn_count
        , "winner_user_id" : game.winner_user_id
        , "first_mover_user_id" : game.first_mover_user_id
        , "last_mover_user_id" : game.last_mover_user_id
        , "status" : game.status
    }
    return json.dumps(result)
    # return '''{
    #             "game_id":3
    #             , "turn_mover_user_id" : 1
    #             , "turn_count":8
    #             , "winner_user_id" : 0
    #             , "first_mover_user_id" : 5
    #             , "last_mover_user_id" : 1
    #             , "status" : "preparing" # preparing, playing, finished
    #        }'''

def is_valid_prepare_position(x, y):
    if x < 2 or x > 5:
        return False
    if y < 5 or y > 6:
        return False
    return True

def reverse_position(x, y):
    x = 7 - x
    y = 7 - y
    return x, y

# 駒の初期配置
@game_app.route('/api/games/<int:game_id>/preparation', methods=['POST'])
@login_required
def preparing(user_id, game_id):
    user = get_user(user_id)
    if user is None:
        return make_error_response(400, "User Not Found")
    if len(user.pieces) != 0: # TODO:pieceが何らかの理由で消えないことがあると次のゲームができない
        return make_error_response(400, "User Already Preparation")

    game = get_game(game_id)
    if game is None:
        return make_error_response(400, "Game Not Found")
    if game.status != "preparing":
        return make_error_response(400, "Game Status Not Preparing")
    dic = request.json
    pieces = dic[u'piece_preparations']
    # データに不正がないかチェックする
    # データが8個であること
    # 座標が、x:2～5, y:5,6の範囲内であること
    # 座標に重複がないこと
    # goodとevilが4個づつであること
    if len(pieces) != PIECE_MAX_COUNT_BY_PLAYER:
        return make_error_response(400, "Invalid Piece Count")
    duplicate_checker = set()
    good_count = 0
    evil_count = 0
    for piece in pieces:
        x = piece[u'point_x']
        y = piece[u'point_y']
        kind = piece[u'kind']
        if not is_valid_prepare_position(x, y):
            return make_error_response(400, "Invalid Position")
        duplicate_checker.add((x, y))
        if kind == "good":
            good_count = good_count + 1
        elif kind == "evil":
            evil_count = evil_count + 1
        else:
            return make_error_response(400, "Invalid Piece Kind")
        print("x:" + str(x) + " y:" + str(y) + " kind:" + str(kind))
    if len(duplicate_checker) != PIECE_MAX_COUNT_BY_PLAYER:
        return make_error_response(400, "Duplicated Position")
    for piece in pieces:
        x = piece[u'point_x']
        y = piece[u'point_y']
        if game.first_mover_user_id != user.id:
            x, y = reverse_position(x, y) # 後手なら位置を逆にする必要がある
        kind = piece[u'kind']
        piece = create_piece(game.id, user.id, x, y, kind)
        if piece is None:
            return make_error_response(500, "Create Piece Failure")
    # TODO:両プレイヤーの初期配置が終わればゲームを進行中にする
    game.on_after_preparing_one_user()
    return json.dumps(dic) # クライアントでは使っていないが、配置情報をそのまま返す

