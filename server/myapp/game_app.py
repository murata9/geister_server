#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import Blueprint, request
import json

from geister.user.user import get_user
from .utility.login_required import login_required

game_app = Blueprint('game_app', __name__)

@game_app.route('/api/game/<int:game_id>', methods=['GET'])
def game(game_id):
    return '''{
                "room_id":3
                , "status" : "playing" 
                , "game_id":33
                , "owner_name" : "owner"
                , "created_at" : ""
                , "updated_at" : ""
           }'''
