#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import Blueprint, request, abort
import json

from define.define import PIECE_MAX_COUNT_BY_PLAYER, Victory
from db_model.user import get_user
from db_model.game import get_game
from db_model.piece import create_piece, get_piece, get_piece_by_pos, get_alive_piece_by_user_id
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

def is_valid_prepare_position(x, y, is_first_mover):
    if x < 2 or x > 5:
        return False
    if is_first_mover:
        if y < 1 or y > 2:
            return False
    else:
        if y < 5 or y > 6:
            return False

    return True

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
    is_first_mover = game.first_mover_user_id == user.id
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
        if not is_valid_prepare_position(x, y, is_first_mover):
            # debug
            for piece in pieces:
                x = piece[u'point_x']
                y = piece[u'point_y']
                print("x:" + str(x) + " y:" + str(y))
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
        kind = piece[u'kind']
        piece = create_piece(game, user, x, y, kind)
        if piece is None:
            return make_error_response(500, "Create Piece Failure")
    # 初期配置が終わればゲームを進行中にする
    game.on_after_preparing_one_user()
    return json.dumps(dic) # クライアントでは使っていないが、配置情報をそのまま返す

# 駒の位置情報取得
@game_app.route('/api/games/<int:game_id>/pieces', methods=['GET'])
@login_required
def get_piece_list(user_id, game_id):
    game = get_game(game_id)
    if game is None:
        return make_error_response(400, "Game Not Found")
    result = []
    pieces = game.pieces
    for piece in pieces:
        tmp = piece.to_dict(user_id)
        print(tmp)
        result.append(piece.to_dict(user_id))

    return json.dumps({"pieces" : result})

def is_goal_pos(x, y, kind, is_first_mover):
    if kind != "good": # 良いお化けしかゴールできない
        return False
    if is_first_mover:
        if y == 6:
            if x == 0 or x == 7:
                return True
        if y == 7:
            if x == 1 or x == 6:
                return True
    else: # not is_first_mover
        if y == 1:
            if x == 0 or x == 7:
                return True
        if y == 0:
            if x == 1 or x == 6:
                return True
    return False

def is_valid_position(x, y, kind, is_first_mover):
    if y > 0 and y < 7:
        if x > 0 and x < 7:
            return True
    # ゴールの場合の例外処理
    # note:今は上下方向にゴールすることは考慮していない
    if is_goal_pos(x, y, kind, is_first_mover):
        return True
    return False

# 一マスの移動かチェック
def is_valid_move_request(piece, x, y, user_id):
    if piece.captured:
        print("[warning]piece captured")
        return False
    if piece.owner.id != user_id:
        print("[warning]not owner")
        return False
    if piece.x == x and abs(piece.y - y) == 1:
        return True
    if piece.y == y and abs(piece.x - x) == 1:
        return True
    return False

# return Vectory
def check_victory_by_alive_enemy_piece(pieces):
    if len(pieces) > (PIECE_MAX_COUNT_BY_PLAYER / 2):
        return False # 駒が5個以上残っていれば勝敗はまだ付かない
    good_count = 0
    evil_count = 0
    for piece in pieces:
        if piece.kind == "good":
            good_count = good_count + 1
        elif piece.kind == "evil":
            evil_count = evil_count + 1
        else:
            raise Exception("Invalid Kind:" + str(piece.kind))
    if good_count == 0:
        # 相手の良いお化けをすべて取ったので勝ち
        return Victory.Win
    elif evil_count == 0:
        # 相手の悪いお化けをすべて取ったので負け
        return Victory.Lose
    return Victory.Undecided


# 駒の位置情報更新
@game_app.route('/api/pieces/<int:piece_id>', methods=['PUT'])
@login_required
def move_piece(user_id, piece_id):
    piece = get_piece(piece_id)
    if piece is None:
        return make_error_response(400, "Piece Not Found")
    game = piece.game

    dic = request.json
    x = dic[u'point_x']
    y = dic[u'point_y']

    if game.get_turn_mover_user_id() != user_id:
        return make_error_response(400, "Not Your Turn")
    is_first_mover = game.first_mover_user_id == user_id
    if not is_valid_move_request(piece, x, y, user_id):
        return make_error_response(400, "Invalid Move Request")
    if not is_valid_position(x, y, piece.kind, is_first_mover):
        return make_error_response(400, "Invalid Move Position")
    existed_piece = get_piece_by_pos(piece.game.id, x, y)
    if existed_piece is not None:
        if existed_piece.owner.id == piece.owner.id:
            return make_error_response(400, "Existed Piece")
        else:
            existed_piece.capture()
            # 勝敗チェック
            enemy_user_id = existed_piece.owner.id
            pieces = get_alive_piece_by_user_id(piece.game.id, enemy_user_id)
            victory = check_victory_by_alive_enemy_piece(pieces)
            if victory is Victory.Win:
                game.win(user_id)
            elif victory is Victory.Lose:
                game.win(enemy_user_id)

    if is_goal_pos(x, y, piece.kind, is_first_mover):
        game.win(user_id)
    piece.update_position(x, y)
    # ターンを更新
    game.next_turn()
    return json.dumps( piece.to_dict(user_id) )
