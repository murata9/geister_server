#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import *

import logging
import json

from db_model.user import init_user
from db_model.room import init_room
from db_model.session import init_session
from db_model.game import init_game
from db_model.player_entry import init_player_entry
from db_model.piece import init_piece

from myapp.user_app import user_app
from myapp.room_app import room_app
from myapp.game_app import game_app

app = Flask(__name__)
app.register_blueprint(user_app)
app.register_blueprint(room_app)
app.register_blueprint(game_app)

def init_logger():
    logger = logging.getLogger('peewee')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

def init_database():
    init_user()
    init_session()
    init_game()
    init_room()
    init_player_entry()
    init_piece()

# 設定確認
# print(app.config)

app.config['ENV'] = "development"

@app.route('/')
def hello_world():
    return '<html><body><h1>sample</h1></body></html>'

if __name__ == '__main__':
    init_logger()
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
    # app.run(host='0.0.0.0', port=5000)

