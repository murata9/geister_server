#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from flask import Blueprint, request
import json
import hashlib
import binascii
import os
import re

from db_model.user import create_user, login_user, load_hased_password
from db_model.session import create_session, get_session, disable_session
from .utility.login_required import login_required
from .utility.error_response import make_error_response

user_app = Blueprint('user_app', __name__)

def gen_salt():
    return os.urandom(16)

def load_salt(hashed_password):
    _, salt = hashed_password.split(':')
    return binascii.unhexlify(salt)

def password_to_hash(password, salt=None):
    # 以下くらい簡単な方が良いかも
    # hashed = hashlib.sha224(password.encode()).hexdigest()

    if salt is None:
        salt = gen_salt()

    iterations=100000
    dk = hashlib.pbkdf2_hmac(
        'sha224'
        , password.encode()
        , salt
        , iterations
    )
    hashed = binascii.hexlify(dk).decode('utf-8')
    str_salt = binascii.hexlify(salt).decode('utf-8')
    hashed = hashed + ':' + str_salt
    return hashed

# ユーザー新規登録
@user_app.route('/api/users', methods=['POST'])
def signup():
    dic = request.json

    invalid_pattern = re.compile(r'\W') # 英数字以外

    name = dic[u"name"]
    if len(name) < 4:
        return make_error_response(400, "name too short")
    if len(name) > 16:
        return make_error_response(400, "name too long")
    invalid = invalid_pattern.search(name)
    if invalid is not None:
        return make_error_response(400, "name invalid")

    password = dic[u"password"]
    if len(password) < 8:
        return make_error_response(400, "password too short")
    if len(password) > 16:
        return make_error_response(400, "password too long")
    invalid = invalid_pattern.search(password)
    if invalid is not None:
        return make_error_response(400, "password invalid")

    hashed_password = password_to_hash(password)
    user = create_user(name, hashed_password)

    if user is None:
        # 既に作成済みのユーザー名
        return make_error_response(400, "Existed UserName")

    result = {
                "user_id" : user.id,
                "name" : user.name
            }
    return json.dumps(result)
    # return '''{
    #             , "user_id":33
    #             , "user_name":"hogehoge"
    #        }'''

# ログイン
@user_app.route('/api/user_sessions', methods=['POST'])
def login():
    dic = request.json
    name = dic[u"name"]
    password = dic[u"password"]
    db_password = load_hased_password(name)
    if db_password is None:
        return make_error_response(400, "Login Failure")

    salt = load_salt(db_password)
    hashed_password = password_to_hash(password, salt)
    user = login_user(name, hashed_password)
    if user is None:
        return make_error_response(400, "Login Failure")

    session, token = create_session(user.id)
    if session is None or token is None:
        print("[error]Create Session Failure")
        return make_error_response(500, "Create Session Failure")

    result = {
                "user_session_id": session.id,
                "access_token": token,
                "user_id" : user.id
            }
    return json.dumps(result)
    # return '''{
    #             "user_session_id":3
    #             , "access_token":""
    #             , "user_id":33
    #        }'''

# ログアウト
@user_app.route('/api/user_sessions/<int:session_id>', methods=['DELETE'])
@login_required
def logout(user_id, session_id):
    print("[info]disable session_id:" + str(session_id))
    disable_session(session_id)
    return ""
