#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import Blueprint, request, abort
import json

from db_model.game import get_game
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
